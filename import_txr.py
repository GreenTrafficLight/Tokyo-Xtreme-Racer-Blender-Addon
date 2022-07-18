import bpy
import bmesh

import gzip
import os
import struct

from math import *

from .ivx import *
from .mdl import *
from .Utilities import *
from .Blender import*

def build_ivx(data, filename):

    bpy.ops.object.empty_add(type='PLAIN_AXES')
    parent = bpy.context.active_object
    parent.empty_display_size = 0.1
    parent.name = filename

    for mesh_ivx in range(len(data.positions)): #len(data.positions)

        bpy.ops.object.empty_add(type='PLAIN_AXES')
        empty = bpy.context.active_object
        empty.empty_display_size = 0.1
        empty.name = "mesh_" + str(mesh_ivx)

        empty.parent = parent

        meshPositions = data.positions[mesh_ivx]
        meshTexCoords = data.texCoords[mesh_ivx]
        meshTexCoords2 = data.texCoords2[mesh_ivx]
        meshNormals = data.normals[mesh_ivx]
        meshFaces = data.faces[mesh_ivx]
        meshMaterials = data.materials[mesh_ivx]

        for submesh in range(len(meshPositions)): # len(meshPositions)

            mesh = bpy.data.meshes.new(str(empty.name + "_" + str(submesh)))
            obj = bpy.data.objects.new(str(empty.name + "_" + str(submesh)), mesh)
            obj.rotation_euler = (radians(90), 0, 0)

            if bpy.app.version >= (2, 80, 0):
                empty.users_collection[0].objects.link(obj)
            else:
                empty.users_collection[0].objects.link(obj)

            obj.parent = empty

            subMeshPositions = meshPositions[submesh]
            subMeshTexCoords = meshTexCoords[submesh]
            subMeshTexCoords2 = meshTexCoords2[submesh]
            subMeshNormals = meshNormals[submesh]
            subMeshFaces = meshFaces[submesh]
            subMeshMaterial = meshMaterials[submesh]

            vertexList = {}
            normals = []

            bm = bmesh.new()
            bm.from_mesh(mesh)

            for j in range(len(subMeshPositions)):

                vertex = bm.verts.new(subMeshPositions[j])

                if subMeshNormals != []:
                    vertex.normal = subMeshNormals[j]
                    normals.append(subMeshNormals[j])

                vertex.index = j

                vertexList[j] = vertex

            for j in range(len(subMeshFaces)):
                try:
                    face = bm.faces.new([vertexList[subMeshFaces[j][0]], vertexList[subMeshFaces[j][1]], vertexList[subMeshFaces[j][2]]])
                    face.smooth = True
                except:
                    pass

            # Set uv
            for f in bm.faces:
                uv_layer1 = bm.loops.layers.uv.verify()
                for l in f.loops:
                    l[uv_layer1].uv =  [subMeshTexCoords[l.vert.index][0], 1 - subMeshTexCoords[l.vert.index][1]]
                        
            bm.to_mesh(mesh)
            bm.free()

            mesh.use_auto_smooth = True
            if normals != []:
                mesh.normals_split_custom_set_from_vertices(normals)

            material = bpy.data.materials.get(empty.name + "_" + str(submesh))
            if not material:
                material = bpy.data.materials.new(empty.name + "_" + str(submesh))

                material.use_nodes = True

                bsdf =  material.node_tree.nodes["Principled BSDF"]

                bsdf.inputs['Base Color'].default_value = (subMeshMaterial[0], subMeshMaterial[1], subMeshMaterial[2], subMeshMaterial[3])

            mesh.materials.append(material)

def build_mdl(data, filename):

    bpy.ops.object.empty_add(type='PLAIN_AXES')
    parent = bpy.context.active_object
    parent.empty_display_size = 0.1
    parent.name = filename
    parent.rotation_euler = (radians(90), 0, 0)

    for mesh_ivx in range(len(data.positions)): #len(data.positions)

        bpy.ops.object.empty_add(type='PLAIN_AXES')
        empty = bpy.context.active_object
        empty.empty_display_size = 0.1
        empty.name = "mesh_" + str(mesh_ivx)

        empty.parent = parent

        meshPositions = data.positions[mesh_ivx]
        meshTexCoords = data.texCoords[mesh_ivx]
        meshTexCoords2 = data.texCoords2[mesh_ivx]
        meshNormals = data.normals[mesh_ivx]
        meshFaces = data.faces[mesh_ivx]

        mesh = bpy.data.meshes.new(str(empty.name))
        obj = bpy.data.objects.new(str(empty.name), mesh)
        
        if bpy.app.version >= (2, 80, 0):
            empty.users_collection[0].objects.link(obj)
        else:
            empty.users_collection[0].objects.link(obj)

        obj.parent = empty

        vertexList = {}
        facesList = []
        normals = []

        bm = bmesh.new()
        bm.from_mesh(mesh)

        if meshTexCoords != []:
            uv_layer1 = bm.loops.layers.uv.new()
        if meshTexCoords2 != []:
            uv_layer2 = bm.loops.layers.uv.new()

        for j in range(len(meshPositions)):

            vertex = bm.verts.new(meshPositions[j])

            if meshNormals != []:
                if meshNormals[j] != None:
                    vertex.normal = meshNormals[j]
                    normals.append(meshNormals[j])

            vertex.index = j

            vertexList[j] = vertex

        # Set faces
        for j in range(len(meshFaces)):
            try:
                face = bm.faces.new([vertexList[meshFaces[j][0]], vertexList[meshFaces[j][1]], vertexList[meshFaces[j][2]]])
                face.smooth = True
            except:
                for Face in facesList:
                    if set([vertexList[meshFaces[j][0]], vertexList[meshFaces[j][1]], vertexList[meshFaces[j][2]]]) == set(Face[1]):
                        face = Face[0].copy(verts=False, edges=True)
                        face.normal_flip()
                        face.smooth = True
                        break
                    
            facesList.append([face, [vertexList[meshFaces[j][0]], vertexList[meshFaces[j][1]], vertexList[meshFaces[j][2]]]])

        # Set uv
        if meshTexCoords != []:
            for f in bm.faces:
                #uv_layer1 = bm.loops.layers.uv.verify()
                for l in f.loops:
                    l[uv_layer1].uv =  [meshTexCoords[l.vert.index][0], 1 - meshTexCoords[l.vert.index][1]]

        if meshTexCoords2 != []:
            for f in bm.faces:
                #uv_layer2 = bm.loops.layers.uv.verify()
                for l in f.loops:
                    l[uv_layer2].uv =  [meshTexCoords2[l.vert.index][0], 1 - meshTexCoords2[l.vert.index][1]]
                    
        bm.to_mesh(mesh)
        bm.free()

        mesh.use_auto_smooth = True
        if normals != []:
            mesh.normals_split_custom_set_from_vertices(normals)

        material = bpy.data.materials.get(str(data.ivx_header.materials[mesh_ivx]))
        if not material:
            material = bpy.data.materials.new(str(data.ivx_header.materials[mesh_ivx]))

        mesh.materials.append(material)

def main(filepath, clear_scene, game_face_generation):
    if clear_scene:
        clearScene()

    f = open(filepath, "rb")
    br = BinaryReader(f)

    header = br.bytesToString(br.readBytes(4)).replace("\0", "")
    br.seek(0, 0)

    filename = filepath.split("\\")[-1]

    if header == "0IVX":
        ivx = IVX(br, game_face_generation)
        build_ivx(ivx, filename)
    else:
        mdl = MDL(br)
        build_mdl(mdl, filename)
