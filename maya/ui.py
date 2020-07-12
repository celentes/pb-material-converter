import maya.cmds as mc
import maya.utils
import sys

from . import logic

def update(input):
    print(input)

def create_ui():
    windowID = "Photobash Material Converter"
    wWidth = 600
    wHeight = 470

    window = mc.window(windowID, title=windowID, sizeable=False, mxb=False, rtf=False, width=300, h=470)

    # master layout
    col = mc.columnLayout(width=300)

    # bindings sublayout
    bdgsOffset = 20
    bdgsFrame = mc.frameLayout(label="View Material Links", mw=bdgsOffset, mh=0, collapsable=True, collapse=True, p=col, width=wWidth)
    bdgsCol = mc.columnLayout(w=wWidth-bdgsOffset, p=bdgsFrame)
    mat1Frame = mc.frameLayout(label="Mat1", collapsable=True, collapse=True, p=bdgsCol, width=wWidth-bdgsOffset)
    mat2Frame = mc.frameLayout(label="Mat2", collapsable=True, collapse=True, p=bdgsCol, width=wWidth-bdgsOffset)

    # directory sublayout
    dirFrame = mc.frameLayout(label="Edit Texture Folder", collapsable=True, collapse=True, p=col, width=wWidth)
    dirRow = mc.rowLayout(numberOfColumns=1, columnWidth3=(80,75,150), adjustableColumn=1, p=dirFrame, width=wWidth)

    mc.textField('PBMCtextfield', width=100, height=25, bgc=[0.25, 0.25, 0.25], cc=update)
    mc.showWindow()
