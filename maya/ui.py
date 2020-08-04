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
    # layouts
    bindingsLayout = None

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

    def selected_materials(self):
        return [x for x in self.mats if self.selection[x] == True]

pbmc_props = None

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

def redraw_bindings():
    w = pbmc_props.windowWidth - 20
    for m in pbmc_props.mats:
        if mc.layout("%s_bindings" % m, ex=True):
            mc.deleteUI("%s_bindings" % m, layout=True)
        frame = mc.frameLayout("%s_bindings" % m, label="%s" % m, collapsable=True, collapse=True, p=pbmc_props.bindingsLayout, width=w)
        name = truncate_material_name(m) # logic
        for t in get_texture_filenames([pbmc_props.dir], name): # tm
            tex_type = get_texture_type(name, t) # tm
            tex_binding = get_binding_name(tex_type) # arnold
            mc.text(os.path.basename(t), align='left', font='boldLabelFont')
            mc.text(colorify(tex_binding, 'grey'), align='left', font='boldLabelFont')

def select_folder():
    global pbmc_props

    selected = mc.fileDialog2(fm=3, dir=pbmc_props.dir)
    if not selected:
        return

    pbmc_props.dir = selected[0]
    mc.text('dir_text', e=True, label=pbmc_props.dir)
    redraw_bindings()

def upgrade_materials():
    global pbmc_props
    #for x in pbmc_props.selected_materials():
    mat = pbmc_props.selected_materials()[1]
    upgrade_material(mat, pbmc_props.dir) # arnold
    pass

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
    msFrame = mc.frameLayout(label="Material Selection", mh=1, collapsable=True, collapse=True, p=master, width=pbmc_props.windowWidth)
    msCol = mc.columnLayout(w=pbmc_props.windowWidth, rs=2, p=msFrame)
    for m in pbmc_props.mats:
        matRow = mc.rowLayout(numberOfColumns=4, columnWidth4=[w1,w2,w3,w4], p=msCol)
        mc.text("1", visible=False) # skip child
        mc.text(m, al='left', w=w2, font='boldLabelFont')
        mc.text("2", visible=False) # skip child
        mc.checkBox("%s_select" % m, label="", width=w4, value=pbmc_props.selection[m], changeCommand=partial(select_mat_update, m))

    # bindings sublayout
    bdgsOffset = 20
    bdgsFrame = mc.frameLayout(label="View Material Links", mw=bdgsOffset, mh=1, collapsable=True, collapse=True, p=master, width=pbmc_props.windowWidth)
    pbmc_props.bindingsLayout = mc.columnLayout("bindings_layout", w=pbmc_props.windowWidth-bdgsOffset, p=bdgsFrame, rs=2)

    redraw_bindings()

    # directory sublayout
    dirFrame = mc.frameLayout(label="Edit Texture Folder", collapsable=True, collapse=True, p=master, width=pbmc_props.windowWidth)
    dirCol = mc.columnLayout(p=dirFrame, width=pbmc_props.windowWidth-6)
    mc.separator()
    mc.rowLayout(numberOfColumns=2, columnWidth2=[pbmc_props.windowWidth-26, 20], p=dirCol)
    mc.text('dir_text', label=pbmc_props.dir, align='left', bgc=[0.25, 0.25, 0.25])
    mc.button(label='...', width=20, height=20, command=lambda _: select_folder())

    # upgrade materials button
    mc.separator(p=master)
    mc.button(label='Upgrade Selected Materials', width=pbmc_props.windowWidth, height=20, command=lambda _: upgrade_materials(), p = master)

def scan_materials_upd(master):
    global pbmc_props

    materials, directory = get_materials_and_directory() # logic
    pbmc_props.fill_materials(materials)
    pbmc_props.dir = directory
    create_layout(master)

def delete_ui():
    global pbmc_props

    if mc.window(pbmc_props.window, ex=True):
        mc.deleteUI(pbmc_props.window)

def create_ui():
    global pbmc_props

    windowID = "Photobash Material Converter"

    if pbmc_props:
        delete_ui()

    pbmc_props = PBMC_props()
    pbmc_props.windowWidth = 500
    pbmc_props.windowHeight = 600

    pbmc_props.window = mc.window(windowID, title=windowID, sizeable=True, mxb=False, rtf=False, width=pbmc_props.windowWidth, h=pbmc_props.windowHeight)

    # master layout
    col = mc.columnLayout(width=pbmc_props.windowWidth)

    mc.separator('sep')
    # scan materials
    mc.button(label='Scan Materials', width=pbmc_props.windowWidth, height=20, command=lambda _: scan_materials_upd(col))
    mc.separator()

    mc.showWindow()
