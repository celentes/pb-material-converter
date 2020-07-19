import c4d
import texture_mapping as tm

class binding:
    def __init__(self, name, id):
        self._name = name
        self._id = id
    def id(self):
        return self._id
    def name(self):
        return self._name

VRAY_BINDINGS = {
    "Diffuse" : binding("Diffuse", c4d.VRAYSTDMATERIAL_DIFFUSECOLOR_TEX),
    "Specular" : binding("Reflection", c4d.VRAYSTDMATERIAL_REFLECTCOLOR_TEX),
    "Roughness" : binding("RGlossiness", c4d.VRAYSTDMATERIAL_REFLECTGLOSSINESS_TEX),
    "Bump" : binding("Bump", c4d.VRAYSTDMATERIAL_BUMP_BUMPMAP),
    "Opacity" : binding("Opacity", c4d.VRAYSTDMATERIAL_OPACITY_TEX),
    "Emission" : binding("Self-Illumination", c4d.VRAYSTDMATERIAL_SELFILLUMCOLOR_TEX),
    "Normal" : binding("Normal", c4d.VRAYSTDMATERIAL_BUMP_NORMALMAP),
}

def get_binding(tex_type):
    if tex_type in VRAY_BINDINGS:
        return VRAY_BINDINGS[tex_type]
    else:
        return None

def get_binding_name(tex_type):
    binding = get_binding(tex_type)
    if binding is not None:
        return binding.name()
    else:
        return tm.NOTMAPPED_STR

def create_texture(filename):
    shd = c4d.BaseShader(c4d.Xbitmap)
    shd[c4d.BITMAPSHADER_FILENAME] = filename
    return shd

def create_material(name):
    ID_VRAY_STANDARD_MATERIAL = 1038954
    mat = c4d.BaseMaterial(ID_VRAY_STANDARD_MATERIAL)
    mat.SetName(name)
    return mat

def bind_texture(mat, tex_path, binding):
    shd = create_texture(tex_path)
    shd.SetName(binding.name())

    # Gloss = 1/Roughness
    if binding.name() == "RGlossiness":
        shd[c4d.BITMAPSHADER_BLACKPOINT] = 1
        shd[c4d.BITMAPSHADER_WHITEPOINT] = 0
        #mat[c4d.VRAYSTDMATERIAL_BRDFUSEROUGHNESS] = 1
    if binding.name() == "Normal":
        mat[c4d.VRAYSTDMATERIAL_BUMP_TYPE] = 1
        pass

    mat.InsertShader(shd)
    mat[binding.id()] = shd
    return

def upgrade_material(mat, directories):
    name = mat.GetName()
    texfiles = tm.get_texture_filenames(directories, name)

    vray_mat = create_material(name)
    for tex_path in texfiles:
        tex_type = tm.get_texture_type(name,tex_path)
        binding = get_binding(tex_type)
        if binding is None:
            continue
        else:
            bind_texture(vray_mat, tex_path, binding)
    doc = c4d.documents.GetActiveDocument()
    doc.InsertMaterial(vray_mat)
    return vray_mat
