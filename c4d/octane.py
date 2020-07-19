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

OCTANE_BINDINGS = {
    "Diffuse" : binding("Albedo", c4d.OCT_MATERIAL_DIFFUSE_LINK),
    "Specular" : binding("Specular", c4d.OCT_MATERIAL_SPECULAR_LINK),
    "Metalness" : binding("Metallic", c4d.OCT_MAT_SPECULAR_MAP_LINK),
    "Roughness" : binding("Roughness", c4d.OCT_MATERIAL_ROUGHNESS_LINK),
    "Bump" : binding("Bump", c4d.OCT_MATERIAL_BUMP_LINK),
    "Normal" : binding("Normal", c4d.OCT_MATERIAL_NORMAL_LINK),
    "Displacement" : binding("Displacement", c4d.OCT_MATERIAL_DISPLACEMENT_LINK),
    "Opacity" : binding("Opacity", c4d.OCT_MATERIAL_OPACITY_LINK),
    "Emission" : binding("Emission", c4d.OCT_MATERIAL_EMISSION),
}

def get_binding(tex_type):
    if tex_type in OCTANE_BINDINGS:
        return OCTANE_BINDINGS[tex_type]
    else:
        return None

def get_binding_name(tex_type):
    binding = get_binding(tex_type)
    if binding is not None:
        return binding.name()
    else:
        return tm.NOTMAPPED_STR

def create_texture(filename):
    ID_OCTANE_IMAGETEXTURE = 1029508
    shd = c4d.BaseShader(ID_OCTANE_IMAGETEXTURE)
    shd[c4d.IMAGETEXTURE_FILE] = filename
    return shd

def create_material(name):
    ID_OCTANE_MATERIAL=1029501
    mat = c4d.BaseMaterial(ID_OCTANE_MATERIAL)
    mat[c4d.OCT_MATERIAL_TYPE] = c4d.OCT_MAT_UNIVERSAL
    mat[c4d.OCT_MAT_BRDF_MODEL] = c4d.OCT_MAT_BRDF_OCTANE
    mat[c4d.OCT_MAT_USE_DISPLACEMENT] = 0
    mat[c4d.OCT_MAT_SPECULAR_MAP_FLOAT] = 0.0
    mat.SetName(name)
    return mat

def bind_texture(mat, tex_path, binding):
    # Emission quirk
    if binding.name() == "Emission":
        ID_EMISSION_SHADER = 1029642
        emi_shd = c4d.BaseShader(ID_EMISSION_SHADER)
        emi_shd.SetName("Texture Emission")

        img_shd = create_texture(tex_path)
        img_shd.SetName(binding.name())

        mat.InsertShader(emi_shd)
        mat[binding.id()] = emi_shd

        mat.InsertShader(img_shd)
        emi_shd[c4d.TEXEMISSION_EFFIC_OR_TEX] = img_shd
        return

    if binding.name() == "Metallic":
        mat[c4d.OCT_MAT_SPECULAR_MAP_FLOAT] = 1.0

    # Displacement quirk
    if binding.name() == "Displacement":
        ID_DISPLACEMENT_SHADER = 1031901
        dis_shd = c4d.BaseShader(ID_DISPLACEMENT_SHADER)
        dis_shd.SetName("Displacement")
        dis_shd[c4d.DISPLACEMENT_AMOUNT] = 1.0
        dis_shd[c4d.DISPLACEMENT_MID] = 0.5
        dis_shd[c4d.DISPLACEMENT_LEVELOFDETAIL] = 12

        img_shd = create_texture(tex_path)
        img_shd.SetName(binding.name())

        #mat[c4d.OCT_MAT_USE_DISPLACEMENT] = 1
        mat.InsertShader(dis_shd)
        mat[binding.id()] = dis_shd

        mat.InsertShader(img_shd)
        dis_shd[c4d.DISPLACEMENT_TEXTURE] = img_shd
        return

    shd = create_texture(tex_path)
    shd.SetName(binding.name())
    mat.InsertShader(shd)
    mat[binding.id()] = shd
    return

def upgrade_material(mat, directories):
    name = mat.GetName()
    texfiles = tm.get_texture_filenames(directories, name)

    oct_mat = create_material(name)
    for tex_path in texfiles:
        tex_type = tm.get_texture_type(name,tex_path)
        binding = get_binding(tex_type)
        if binding is None:
            continue
        else:
            bind_texture(oct_mat, tex_path, binding)
    doc = c4d.documents.GetActiveDocument()
    doc.InsertMaterial(oct_mat)
    return oct_mat
