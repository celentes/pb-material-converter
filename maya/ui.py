import maya.cmds as mc
import sys
import os
import re

#from . import logic

def update(input):
    print(input)

def truncate_material_name(mat):
    name = mat
    if re.search("_ncl1_1", mat):
        name = mat[:-7]
    idx = name.rfind(":")
    if idx != -1:
        name = name[-idx+1:]
    return name

def fill_material_frame(mat):
    texture_paths = get_material_texture_paths(mat) # logic
    # TODO: move dir hints out
    dir_hints = get_directory_hints(texture_paths) # tm
    name = truncate_material_name(mat)

    textures = get_texture_filenames(dir_hints, name) # tm

    for t in textures:
        mc.text(t, align='left')
        mc.text(get_texture_type(name, t), align='left')

def colorify(string, color):
    return "<font color=%s>%s</font>" % (color, string)

def create_layout(master, width, materials, directory):
    bdgsOffset = 20
    bdgsFrame = mc.frameLayout(label="View Material Links", mw=bdgsOffset, mh=1, collapsable=True, collapse=True, p=master, width=width)
    bdgsCol = mc.columnLayout(w=width-bdgsOffset, p=bdgsFrame, rs=2)

    for m in materials:
        frame = mc.frameLayout(label="%s" % m, collapsable=True, collapse=True, p=bdgsCol, width=width-bdgsOffset)
        name = truncate_material_name(m)
        for t in get_texture_filenames([directory], name): # tm
            mc.text(os.path.basename(t), align='left', font='boldLabelFont')
            mc.text(colorify(get_texture_type(name, t), 'grey'), align='left', font='boldLabelFont')

    # directory sublayout
    dirFrame = mc.frameLayout(label="Edit Texture Folder", collapsable=True, collapse=True, p=master, width=width)
    dirRow = mc.rowLayout(numberOfColumns=1, columnWidth3=(80,75,150), adjustableColumn=1, p=dirFrame, width=width)
    mc.text(directory, align='left', bgc=[0.25, 0.25, 0.25], font='smallFixedWidthFont')

def create_ui():
    windowID = "Photobash Material Converter"
    wWidth = 600
    wHeight = 470

    materials = None
    dir = None

    window = mc.window(windowID, title=windowID, sizeable=False, mxb=False, rtf=False, width=wWidth, h=wHeight)

    # master layout
    col = mc.columnLayout(width=wWidth)

    lambda scan_mats: materials, dir = get_materials_and_directory() # logic

    mc.separator('sep')
    # scan materials
    mc.button(label='Scan Materials', width=wWidth, height=20)
    mc.separator()

    scan_mats()
    create_layout(col, wWidth, materials, directory)
    # bindings sublayout
#    bdgsOffset = 20
#    bdgsFrame = mc.frameLayout(label="View Material Links", mw=bdgsOffset, mh=1, collapsable=True, collapse=True, p=col, width=wWidth)
#    bdgsCol = mc.columnLayout(w=wWidth-bdgsOffset, p=bdgsFrame, rs=2)
#
#    mats, dir = get_materials_and_directory() # logic
#    for m in mats:
#        frame = mc.frameLayout(label="%s" % m, collapsable=True, collapse=True, p=bdgsCol, width=wWidth-bdgsOffset)
#        name = truncate_material_name(m)
#        for t in get_texture_filenames([dir], name): # tm
#            mc.text(os.path.basename(t), align='left', font='boldLabelFont')
#            mc.text(colorify(get_texture_type(name, t), 'grey'), align='left', font='boldLabelFont')
#
#    # directory sublayout
#    dirFrame = mc.frameLayout(label="Edit Texture Folder", collapsable=True, collapse=True, p=col, width=wWidth)
#    dirRow = mc.rowLayout(numberOfColumns=1, columnWidth3=(80,75,150), adjustableColumn=1, p=dirFrame, width=wWidth)
#    mc.text(dir, align='left', bgc=[0.25, 0.25, 0.25], font='smallFixedWidthFont')

    mc.showWindow()
