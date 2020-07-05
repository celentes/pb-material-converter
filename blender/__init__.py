bl_info = {
    "name":        "Photobash Material Converter",
    "description": "Upgrade materials with missing texture nodes",
    "author":      "Tim Talashok, t.talashok@gmail.com",
    "version":     (0, 2, 0),
    "blender":     (2, 82, 0),
    "category": "Material"
}

if "bpy" in locals():
    import importlib
    importlib.reload(jdr_material_converter)
    importlib.reload(octane)
    importlib.reload(eevee)
    importlib.reload(texture_mapping)
else:
    from . import jdr_material_converter
    from . import octane
    from . import eevee
    from . import texture_mapping

import bpy

def register():
    jdr_material_converter.register()

def unregister():
    jdr_material_converter.unregister()

if __name__ == "__main__":
    register()
