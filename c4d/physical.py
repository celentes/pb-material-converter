import c4d
import texture_mapping as tm

def get_binding_name(tex_type):
    if tex_type == "Diffuse":
        return "PBR Diffuse Layer => Color"
    if tex_type == "Metalness":
        return "PBR Metallic layer"
    if tex_type == "Specular":
        return "PBR Specular layer => Color"
    if tex_type == "Roughness":
        return "PBR Diffuse layer => Roughness"
    if tex_type == "Normal":
        return "Normal"
    if tex_type == "Emission":
        return "Luminance"
    if tex_type == "Displacement":
        return "Displacement"
    if tex_type == "Opacity":
        return "Alpha"
    return tm.NOTMAPPED_STR

def create_texture(filename):
    shd = c4d.BaseShader(c4d.Xbitmap)
    shd[c4d.BITMAPSHADER_FILENAME] = filename
    return shd

def create_material(name):
    mat = c4d.Material()
    mat.SetName(name)
    mat[c4d.MATERIAL_USE_COLOR] = 0
    mat.RemoveReflectionLayerIndex(0)

    specLayer = mat.AddReflectionLayer()
    specLayer.SetName("Default Specular")
    mat[specLayer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION] = 3

    diffuseLayer = mat.AddReflectionLayer()
    diffuseLayer.SetName("Default Diffuse")
    mat[diffuseLayer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION] = 7

    return mat

def bind_emissive(mat, tex_path):
    shd = create_texture(tex_path)
    shd.SetName("Luminance")
    mat[c4d.MATERIAL_USE_LUMINANCE] = 1
    mat[c4d.MATERIAL_LUMINANCE_SHADER] = shd

    mat.InsertShader(shd)
    return

REFLECTION_LAYER_MAIN_VALUE_ROUGHNESSLINK = 40
def bind_roughness(mat, tex_path):
    shd = create_texture(tex_path)
    shd.SetName("Roughness")

    specLayer = mat.GetReflectionLayerIndex(1)
    mat[specLayer.GetDataID() + REFLECTION_LAYER_MAIN_VALUE_ROUGHNESSLINK] = shd
    mat.InsertShader(shd)

def bind_diffuse(mat, tex_path):
    shd = create_texture(tex_path)
    shd.SetName("Diffuse")

    diffuseLayer = mat.GetReflectionLayerIndex(0)
    mat[diffuseLayer.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE] = shd
    mat.InsertShader(shd)

def bind_normal(mat, tex_path):
    shd = create_texture(tex_path)
    shd.SetName("Normal")

    mat[c4d.MATERIAL_USE_NORMAL] = 1
    mat[c4d.MATERIAL_NORMAL_SHADER] = shd
    mat.InsertShader(shd)

def bind_metallic(mat, tex_path):
    shd = create_texture(tex_path)
    shd.SetName("Metallic")

    metallicLayer = mat.AddReflectionLayer()
    metallicLayer.SetName("Metallic")
    mat[metallicLayer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION] = 3
    mat[metallicLayer.GetDataID() + c4d.REFLECTION_LAYER_FRESNEL_MODE] = 2
    mat[metallicLayer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_ADDITIVE] = 4
    mat[metallicLayer.GetDataID() + c4d.REFLECTION_LAYER_TRANS_TEXTURE] = shd
    mat.InsertShader(shd)

    diffuseLayer = mat.GetReflectionLayerIndex(1)
    _colorShd = mat[diffuseLayer.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE]
    if _colorShd:
        colorShd = _colorShd.GetClone()
        mat[metallicLayer.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE] = colorShd
        mat.InsertShader(colorShd)

    specLayer = mat.GetReflectionLayerIndex(2)
    _roughnessShd = mat[specLayer.GetDataID() + REFLECTION_LAYER_MAIN_VALUE_ROUGHNESSLINK]
    if _roughnessShd:
        roughnessShd = _roughnessShd.GetClone()
        mat[metallicLayer.GetDataID() + REFLECTION_LAYER_MAIN_VALUE_ROUGHNESSLINK] = roughnessShd
        mat.InsertShader(roughnessShd)

def bind_alpha(mat, tex_path):
    shd = create_texture(tex_path)
    shd.SetName("Alpha")

    mat[c4d.MATERIAL_USE_ALPHA] = 1
    mat[c4d.MATERIAL_ALPHA_SHADER] = shd
    mat.InsertShader(shd)

def bind_spec(mat, tex_path):
    shd = create_texture(tex_path)
    shd.SetName("Specular")

    specLayer = mat.GetReflectionLayerIndex(1)
    mat[specLayer.GetDataID() + c4d.REFLECTION_LAYER_COLOR_TEXTURE] = shd
    mat.InsertShader(shd)

def bind_displacement(mat, tex_path):
    shd = create_texture(tex_path)
    shd.SetName("Displacement")

    mat[c4d.MATERIAL_DISPLACEMENT_SHADER] = shd
    mat.InsertShader(shd)

def bind_texture(mat, tex_path, tex_type):
    if tex_type == "Diffuse":
        return bind_diffuse(mat, tex_path)
    if tex_type == "Metalness":
        return bind_metallic(mat, tex_path)
    if tex_type == "Specular":
        return bind_spec(mat, tex_path)
    if tex_type == "Roughness":
        return bind_roughness(mat, tex_path)
    if tex_type == "Normal":
        return bind_normal(mat, tex_path)
    if tex_type == "Emission":
        return bind_emissive(mat, tex_path)
    if tex_type == "Displacement":
        return bind_displacement(mat, tex_path)
    if tex_type == "Opacity":
        return bind_alpha(mat, tex_path)

def upgrade_material(mat, directories):
    name = mat.GetName()
    texfiles = tm.get_texture_filenames(directories, name)

    material = create_material(name)
    tex_metallic = None
    for tex_path in texfiles:
        tex_type = tm.get_texture_type(name, tex_path)
        if tex_type == "Metalness":
            tex_metallic = tex_path
            continue
        binding = get_binding_name(tex_type)
        if binding == tm.NOTMAPPED_STR:
            continue
        else:
            bind_texture(material, tex_path, tex_type)

    if tex_metallic:
        bind_texture(material, tex_metallic, "Metalness")

    doc = c4d.documents.GetActiveDocument()
    doc.InsertMaterial(material)
    return material
