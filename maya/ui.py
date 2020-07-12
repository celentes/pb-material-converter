import maya.cmds as mc
import maya.utils
import sys

def update(input):
    print(input)

def create_ui():
    windowID = "Photobash Material Converter"

    window = mc.window(windowID, title=windowID, sizeable=False, mxb=False, rtf=False, width=300, h=470)

    # master layout
    col = mc.columnLayout(width=300)

    # bindings sublayout

    bdgsFrame = mc.frameLayout(label="View Material Links", mw=20, mh=0, collapsable=True, collapse=True, p=col, width=300)
    bdgsCol = mc.columnLayout(w=280, p=bdgsFrame)
    mat1Frame = mc.frameLayout(label="Mat1", li=50, collapsable=True, collapse=True, p=bdgsCol, width=280)
    mat2Frame = mc.frameLayout(label="Mat2", li=50, collapsable=True, collapse=True, p=bdgsCol, width=280)

    # directory sublayout
    dirFrame = mc.frameLayout(label="Edit Texture Folder", collapsable=True, collapse=True, p=col, width=300)
    dirRow = mc.rowLayout(numberOfColumns=1, columnWidth3=(80,75,150), adjustableColumn=1, p=dirFrame, width=300)

    mc.textField('PBMCtextfield', width=100, height=25, bgc=[0.25, 0.25, 0.25], cc=update)
    mc.showWindow()
