bl_info = {
	"name": "Import Tokyo Xtreme Racer Models format",
	"description": "Import Tokyo Xtreme Racer Model",
	"author": "GreenTrafficLight",
	"version": (1, 0),
	"blender": (2, 92, 0),
	"location": "File > Import > Tokyo Xtreme Racer Importer",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"support": "COMMUNITY",
	"category": "Import-Export"}

import bpy

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class ImportTXR(Operator, ImportHelper):
    """Load a Tokyo Xtreme Racer model file"""
    bl_idname = "import_scene.txr_data"
    bl_label = "Import Tokyo Xtreme Racer Data"

    filename_ext = ""
    filter_glob: StringProperty(default="*", options={'HIDDEN'}, maxlen=255,)

    clear_scene: BoolProperty(
        name="Clear scene",
        description="Clear everything from the scene",
        default=False,
    )

    post_kb2_face_generation: BoolProperty(
        name="Post Kaido Battle 2 Face Generation",
        description="Face Generation for PS2 games post Kaido Battle 2",
        default=False,
    ) # To change ?

    def execute(self, context):
        from . import  import_txr
        import_txr.main(self.filepath, self.clear_scene, self.post_kb2_face_generation)
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportTXR.bl_idname, text="Tokyo Xtreme Racer")


def register():
    bpy.utils.register_class(ImportTXR)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportTXR)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()