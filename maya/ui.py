import maya.cmds as mc
from functools import partial
import sys
import os
import re

#from . import logic

class PBMC_props:
    mats = None
    dir = None
    selection = dict()
    windowWidth = 0
    windowHeight = 0
    window = None

    def all_mats_selected(self):
        return all(self.selection.values())

    def fill_materials(self, materials):
        self.mats = [x for x in materials]
        for x in self.mats:
            self.selection[x] = True

    def select_all(self):
        all_selected = self.all_mats_selected()
        for x in self.mats:
            self.selection[x] = not all_selected

    def select_mat(self, mat):
        self.selection[mat] = not self.selection[mat]

pbmc_props = None

def truncate_material_name(mat):
    name = mat
    if re.search("_ncl1_1", mat):
        name = mat[:-7]
    idx = name.rfind(":")
    if idx != -1:
        name = name[-idx+1:]
    return name

def colorify(string, color):
    return "<font color=%s>%s</font>" % (color, string)

def upd_select_all():
    global pbmc_props

    mc.checkBox("select_all", e=True, v=pbmc_props.all_mats_selected())
    for m in pbmc_props.mats:
        mc.frameLayout("%s_bindings" % m, e=True, visible=pbmc_props.selection[m])

def select_mat_update(mat, _):
    global pbmc_props

    pbmc_props.select_mat(mat)
    upd_select_all()

def select_all_update(_):
    global pbmc_props

    pbmc_props.select_all()
    for m in pbmc_props.mats:
        mc.checkBox("%s_select" % m, e=True, v=pbmc_props.selection[m])
    upd_select_all()

def create_layout(master):
    global pbmc_props

    w1, w2, w3, w4 = 30, pbmc_props.windowWidth - 160, 100, 30

    # materials found sublayout
    mfCol = mc.columnLayout(w=pbmc_props.windowWidth, rs=2, p=master, bgc=[0.15, 0.15, 0.15])
    mc.rowLayout(numberOfColumns=4, columnWidth4=[w1,w2,w3,w4], p=mfCol)
    mc.text("") # skip child
    mc.text("<b>%i</b> Materials Found" % len(pbmc_props.mats), al='left', w=w2)
    mc.text("Select All", al='center', w=w3)
    mc.checkBox("select_all", label="", width=w4, value=pbmc_props.all_mats_selected(), changeCommand=partial(select_all_update))

    # material selection sublayout
    msCol = mc.columnLayout(w=pbmc_props.windowWidth, rs=2, p=master)
    for m in pbmc_props.mats:
        matRow = mc.rowLayout(numberOfColumns=4, columnWidth4=[w1,w2,w3,w4], p=msCol)
        mc.text("1", visible=False) # skip child
        mc.text(m, al='left', w=w2, font='boldLabelFont')
        mc.text("2", visible=False) # skip child
        mc.checkBox("%s_select" % m, label="", width=w4, value=pbmc_props.selection[m], changeCommand=partial(select_mat_update, m))

    # bindings sublayout
    bdgsOffset = 20
    bdgsFrame = mc.frameLayout(label="View Material Links", mw=bdgsOffset, mh=1, collapsable=True, collapse=True, p=master, width=pbmc_props.windowWidth)
    bdgsCol = mc.columnLayout(w=pbmc_props.windowWidth-bdgsOffset, p=bdgsFrame, rs=2)

    for m in pbmc_props.mats:
        frame = mc.frameLayout("%s_bindings" % m, label="%s" % m, collapsable=True, collapse=True, p=bdgsCol, width=pbmc_props.windowWidth-bdgsOffset)
        name = truncate_material_name(m)
        for t in get_texture_filenames([pbmc_props.dir], name): # tm
            mc.text(os.path.basename(t), align='left', font='boldLabelFont')
            mc.text(colorify(get_texture_type(name, t), 'grey'), align='left', font='boldLabelFont')

    # query mc.checkBox(select_all, q=True, v=True)
    # set mc.checkBox(select_all, e=True, v=False)

    # directory sublayout
    dirFrame = mc.frameLayout(label="Edit Texture Folder", collapsable=True, collapse=True, p=master, width=pbmc_props.windowWidth)
    dirCol = mc.columnLayout(p=dirFrame, width=pbmc_props.windowWidth)
    mc.separator()
    mc.text(pbmc_props.dir, align='left', bgc=[0.25, 0.25, 0.25])

def scan_materials_upd(master):
    global pbmc_props

    materials, directory = get_materials_and_directory() # logic
    pbmc_props.fill_materials(materials)
    pbmc_props.dir = directory
    create_layout(master)

def delete_ui():
    global pbmc_props

    if pbmc_props.window:
        mc.deleteUI(pbmc_props.window)

def create_ui():
    global pbmc_props

    windowID = "Photobash Material Converter"

    if pbmc_props:
        delete_ui()

    pbmc_props = PBMC_props()
    pbmc_props.windowWidth = 500
    pbmc_props.windowHeight = 600

    pbmc_props.window = mc.window(windowID, title=windowID, sizeable=False, mxb=False, rtf=False, width=pbmc_props.windowWidth, h=pbmc_props.windowHeight)

    # master layout
    col = mc.columnLayout(width=pbmc_props.windowWidth)

    mc.separator('sep')
    # scan materials
    mc.button(label='Scan Materials', width=pbmc_props.windowWidth, height=20, command=lambda _: scan_materials_upd(col))
    mc.separator()

    mc.showWindow()
