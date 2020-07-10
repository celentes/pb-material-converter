import os
import re

SUPPORTED_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".psd",
    ".tiff",
    ".tif",
    ".tga",
    ".bmp",
    ".png",
    ".b3d",
    ".iff",
    ".exr",
]

TEXTURE_TYPE_DICT = {
    # DIFFUSE
    "diffuse" : "Diffuse",
    "color" : "Diffuse",
    "basecolor" : "Diffuse",
    "albedo" : "Diffuse",
    # SPECULAR
    "spec" : "Specular",
    "specular" : "Specular",
    # METALNESS
    "metal" : "Metalness",
    "metallic" : "Metalness",
    "metalness" : "Metalness",
    # ROUGHNESS
    "rough" : "Roughness",
    "roughness" : "Roughness",
    "gloss" : "Roughness", # add quirks too
    # BUMP
    "bump" : "Bump",
    # NORMAL
    "normal" : "Normal",
    # DISPLACEMENT
    "height" : "Displacement",
    "displacement" : "Displacement",
    # OPACITY
    "opacity" : "Opacity",
    "alpha" : "Opacity",
    "transparency" : "Opacity",
    # EMISSION
    "emission" : "Emission",
    "emissive" : "Emission",
    "luminosity" : "Emission",
    # AMBIENT OCCLUSION
    "ao" : "AmbientOcclusion",
    "ambientocclusion" : "AmbientOcclusion",
}

NOTMAPPED_STR = "NOT MAPPABLE"

def get_directory_hints(texture_paths_list):
    if texture_paths_list == None:
        return []
    dir_hints = {os.path.dirname(x) for x in texture_paths_list}
    return [x for x in dir_hints]

def get_texture_filenames(directories, material_name=None):
    files = []
    for dir in directories:
        if not os.path.exists(dir):
            continue
        files.extend([os.path.join(dir,f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir,f))])
    # filter out accepted formats
    files = [x for x in files if os.path.splitext(x)[1].lower() in SUPPORTED_EXTENSIONS]
    if material_name is None:
        return files
    else:
        return [x for x in files if re.search(material_name, os.path.basename(x), flags=re.IGNORECASE)]

def get_texture_type(material_name, texture_path):
    texname, ext = os.path.splitext(os.path.basename(texture_path))
    i_cutoff = texname.find(material_name) + len(material_name)
    if texname[i_cutoff] == '_':
        i_cutoff += 1
    textype = texname[i_cutoff:]
    if textype.lower() in TEXTURE_TYPE_DICT:
        return TEXTURE_TYPE_DICT[textype.lower()]
    else:
        return textype

