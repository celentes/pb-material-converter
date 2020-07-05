bl_info = {
    "name":        "JDR Material Converter",
    "description": "Upgrade materials with missing texture nodes",
    "author":      "Tim Talashok, t.talashok@gmail.com",
    "version":     (0, 2, 0),
    "blender":     (2, 83, 0),
    "category": "Material"
}

if "bpy" in locals():
    import importlib
    importlib.reload(jdr_material_converter)
else:
    from . import jdr_material_converter

import bpy

def register():
    jdr_material_converter.register()

def unregister():
    jdr_material_converter.unregister()

if __name__ == "__main__":
    register()
