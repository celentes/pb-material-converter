import c4d
from c4d import gui
import os
import re

import TextureMapping
reload(TextureMapping)

import octane
reload(octane)

import UI
reload(UI)

import arnold
reload(arnold)

# TODO: bloody specs

# Main function
def main():
    folder = "C:\Users\\ttala\Documents\\fbx-testscene\Test Scene Materials Plugin.fbm\\"
    #albedo = folder + "ScifiCube_01_Diffuse.jpg"
    #normal = folder + "ScifiCube_01_Normal.jpg"
    #roughness = folder + "ScifiCube_01_Rough.jpg"
    #metalness = folder + "ScifiCube_01_Metalness.jpg"
    #spec = folder + "ScifiCube_01_Spec.jpg"
    #emission = folder + "ScifiCube_01_Emissive.jpg"
    #displacement = folder + "ScifiCube_01_Height.jpg"
    
    #mat, ss = arnold.create_material("bobo")

    #arnold.set_base_color(mat, albedo, ss)
    #arnold.set_metalness(mat, metalness, ss)
    #arnold.set_roughness(mat, roughness, ss)
    #arnold.set_normal(mat, normal, ss)
    #arnold.set_specular(mat, spec, ss)
    #arnold.set_emission(mat, emission, ss)
    #arnold.set_displacement(mat, displacement)
    #arnold.set_opacity(mat, metalness, ss)

    #doc.InsertMaterial(mat)
    #mats = [x for x in doc.GetMaterials() if x.GetType() == c4d.Mmaterial]
    #for mat in mats:
    #    arnold.upgrade_material(mat, [folder])
    #c4d.EventAdd(c4d.EVENT_FORCEREDRAW)
    pbmc = UI.PBMC_Dialog()
    pbmc.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE, defaultw=300, defaulth=500, xpos=-2, ypos=-2)

# Execute main()
if __name__=='__main__':
    main()