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
    pbmc = UI.PBMC_Dialog()
    pbmc.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE, defaultw=300, defaulth=500, xpos=-2, ypos=-2)

# Execute main()
if __name__=='__main__':
    main()