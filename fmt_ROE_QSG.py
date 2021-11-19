# Rinf of Elysium
# Noesis script by zaramot, PeterZ(48464385)
# 2021.10.6 v1:Add MESH (.QSG) & SKELETON (.QSS) support.Skeleton weight & some Vertex normal support.

from inc_noesis import *
import noesis
import rapi
import os
import glob


def registerNoesisTypes():
    handle = noesis.register("Ring of Elysium", ".QSG")
    noesis.setHandlerTypeCheck(handle, BDCheckType)
    # see also noepyLoadModelRPG
    noesis.setHandlerLoadModel(handle, BDLoadModel)
    noesis.logPopup()
    return 1


def BDCheckType(data):
    bs = NoeBitStream(data)
    idMagic = bs.readInt()
    return 1


def find(searchList, elem): return [
    [i for i, x in enumerate(searchList) if x == e] for e in elem]


def BDLoadModel(data, mdlList):
    ctx = rapi.rpgCreateContext()
    trans = NoeMat43((NoeVec3((1, 0, 0)),
                      NoeVec3((0, 0, 1)),
                      NoeVec3((0, -1, 0)),
                      NoeVec3((0, 0, 0))))
    # used to rotate vertices to match skeleton

    bs = NoeBitStream(data)
    boneList = []
    QSSboneNames = []
    idMagic = bs.readUShort()

    meshCount = bs.readUInt()

    if(True):#Load Skeleton(QSS File)
        test = rapi.getDirForFilePath(rapi.getInputName())
        os.chdir(test)
        test = glob.glob("*.QSS")
        try:
            skelfile = rapi.getDirForFilePath(
                rapi.getInputName()) + test[0]
        except:
            skelfile = ""
        if (rapi.checkFileExists(skelfile)):  # Load Skeleton
            ss = rapi.loadIntoByteArray(skelfile)
            ss = NoeBitStream(ss)
            boneCount = ss.readUInt()
            for i in range(0, boneCount):
                boneBlockSize = ss.readUByte()
                boneName = noeStrFromBytes(ss.readBytes(boneBlockSize-192))
                QSSboneNames.append(boneName)
                boneParent = ss.readInt()
                boneMtxLocal = NoeMat43.fromBytes(ss.readBytes(48))
                boneScaleLocal = NoeVec3.fromBytes(ss.readBytes(12))
                boneMtx = NoeMat43.fromBytes(ss.readBytes(48))
                boneScale = NoeVec3.fromBytes(ss.readBytes(12))
                boneMtx[3] *= boneScale
                BoneQuat = NoeQuat.fromBytes(ss.readBytes(16))
                newBone = NoeBone(
                    i, boneName, boneMtx, None, boneParent)
                boneList.append(newBone)
                print('QSS Bones')
                print('%-3s' % i, '%-3s' % boneParent, boneName)
    for a in range(0, meshCount):  # Load Mesh
        QSGboneNames = []
        BoneMap = []
        MatCount = bs.readShort()
        # Face Block
        FaceCount = bs.readUInt()
        #print('FaceCount', str(FaceCount))
        FaceSize = bs.readUInt()
        faceBuff = bs.readBytes(FaceCount)
        # Vertex Block
        VertexSecSize = bs.readUInt()
        VertexSize = bs.readUInt()
        vertCount = int(VertexSecSize/VertexSize)
        vertBuff = bs.readBytes(VertexSize * vertCount)
        bs.readUInt()
        meshNameSize = int(bs.readUByte()-192)
        meshName = noeStrFromBytes(bs.readBytes(meshNameSize))
        print('Mesh'+str(a),meshName)
        bs.readUShort()
        # LongCount1 = bs.readUInt();[bs.readUInt() for i in range(LongCount1-1)]
        bs.read("I" * (bs.readUInt()-1))
        # LongCount2 = bs.readUInt();[bs.readUByte() for i in range(LongCount2*12)]
        bs.read("B" * (bs.readUInt()*12))
        # Bone Block
        boneCount = bs.readUInt()
        #print('QSG boneCount', str(boneCount))
        print('QSG Bones')
        for i in range(boneCount):
            boneNameSize = int(bs.readUByte()-192)
            boneName = noeStrFromBytes(bs.readBytes(boneNameSize))
            QSGboneNames.append(boneName)
            print(boneName)
        # Bone mapping
        for a in range(len(QSGboneNames)):
            for i in range(len(QSSboneNames)):
                if QSSboneNames[i] == QSGboneNames[a]:
                    BoneMap.append(i)
                    break
        if(BoneMap):
            rapi.rpgSetBoneMap(BoneMap)
        #
        print('VertexSize', str(VertexSize))
        print('QSS BoneNum', str(len(boneList)))
        print('QSG BoneNum', str(boneCount))
        print('Using BoneNum', str(len(BoneMap)))
        if(boneCount!=len(BoneMap)):
            print("This QSG file uses bones that don't exist in QSS file! Maybe mismatch skeleton file! ")
        print(BoneMap)
        # Bones transforms (useless)
        boneCount = bs.readUInt()
        #print('QSG boneCount', str(boneCount))
        for i in range(boneCount):
            boneMtx1 = NoeMat43.fromBytes(bs.readBytes(48))
            boneScale = NoeVec3.fromBytes(bs.readBytes(12))
        # unknown
        [bs.readUByte() for i in range(40)]
        #
        # Build Model
        if(VertexSize == 72):
            rapi.rpgSetTransform(trans)
        if(VertexSize == 104):
            rapi.rpgBindPositionBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 0)
            rapi.rpgBindUV1BufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 12)
            rapi.rpgBindBoneIndexBufferOfs(
                vertBuff, noesis.RPGEODATA_UBYTE, VertexSize, 72, 3)
            rapi.rpgBindBoneWeightBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 76, 3)
        elif(VertexSize == 96):
            rapi.rpgBindPositionBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 0)
            rapi.rpgBindUV1BufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 12)
            rapi.rpgBindBoneIndexBufferOfs(
                vertBuff, noesis.RPGEODATA_UBYTE, VertexSize, 64, 3)
            rapi.rpgBindBoneWeightBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 68, 3)
        elif(VertexSize == 88):
            rapi.rpgBindPositionBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 0)
            rapi.rpgBindUV1BufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 12)
            rapi.rpgBindBoneIndexBufferOfs(
                vertBuff, noesis.RPGEODATA_UBYTE, VertexSize, 72, 4)
            rapi.rpgBindBoneWeightBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 76, 3)
        elif(VertexSize == 80):
            rapi.rpgBindPositionBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 0)
            rapi.rpgBindUV1BufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 12)
            rapi.rpgBindBoneIndexBufferOfs(
                vertBuff, noesis.RPGEODATA_UBYTE, VertexSize, 64, 4)
            rapi.rpgBindBoneWeightBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 68, 3)
        elif(VertexSize == 72):
            rapi.rpgBindPositionBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 0)
            rapi.rpgBindUV1BufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 12)
            rapi.rpgBindNormalBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 20)  # NOT SURE
            rapi.rpgBindBoneIndexBufferOfs(
                vertBuff, noesis.RPGEODATA_UBYTE, VertexSize, 56, 3)
            rapi.rpgBindBoneWeightBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 60, 3)
        elif(VertexSize == 64):
            rapi.rpgBindPositionBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 0)
            rapi.rpgBindUV1BufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 12)
            '''
            rapi.rpgBindBoneIndexBufferOfs(
                vertBuff, noesis.RPGEODATA_UBYTE, VertexSize, 56, 3)
            rapi.rpgBindBoneWeightBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 60, 3)
            '''
        elif(VertexSize == 56):
            rapi.rpgBindPositionBufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 0)
            rapi.rpgBindUV1BufferOfs(
                vertBuff, noesis.RPGEODATA_FLOAT, VertexSize, 12)
        elif(VertexSize == 40 or VertexSize == 36):
            rapi.rpgBindPositionBufferOfs(
                vertBuff, noesis.RPGEODATA_HALFFLOAT, VertexSize, 0)
            rapi.rpgBindUV1BufferOfs(
                vertBuff, noesis.RPGEODATA_HALFFLOAT, VertexSize, 8)
            rapi.rpgBindBoneIndexBufferOfs(
                vertBuff, noesis.RPGEODATA_UBYTE, VertexSize, 28, 4)
            rapi.rpgBindBoneWeightBufferOfs(
                vertBuff, noesis.RPGEODATA_UBYTE, VertexSize, 32, 4)
        elif(VertexSize == 34 or VertexSize == 32):
            rapi.rpgBindPositionBufferOfs(
                vertBuff, noesis.RPGEODATA_HALFFLOAT, VertexSize, 0)
            rapi.rpgBindUV1BufferOfs(
                vertBuff, noesis.RPGEODATA_HALFFLOAT, VertexSize, 8)
            rapi.rpgBindBoneIndexBufferOfs(
                vertBuff, noesis.RPGEODATA_UBYTE, VertexSize, 24, 4)
            rapi.rpgBindBoneWeightBufferOfs(
                vertBuff, noesis.RPGEODATA_UBYTE, VertexSize, 28, 4)
        elif(VertexSize == 28 or VertexSize == 24):
            rapi.rpgBindPositionBufferOfs(
                vertBuff, noesis.RPGEODATA_HALFFLOAT, VertexSize, 0)
            rapi.rpgBindUV1BufferOfs(
                vertBuff, noesis.RPGEODATA_HALFFLOAT, VertexSize, 8)
            '''
            rapi.rpgBindBoneIndexBufferOfs(
                vertBuff, noesis.RPGEODATA_UBYTE, VertexSize, 16, 4)
            rapi.rpgBindBoneWeightBufferOfs(
                vertBuff, noesis.RPGEODATA_UBYTE, VertexSize, 20, 4)
            '''
        rapi.rpgSetName(meshName)
        rapi.rpgCommitTriangles(
            faceBuff, noesis.RPGEODATA_USHORT, FaceCount//2, noesis.RPGEO_TRIANGLE, 1)
        rapi.rpgClearBufferBinds()
    mdl = rapi.rpgConstructModel()
    # rapi.rpgOptimize()
    #mdl.setModelMaterials(NoeModelMaterials(texList, matList))
    mdlList.append(mdl)
    mdl.setBones(boneList)
    return 1
