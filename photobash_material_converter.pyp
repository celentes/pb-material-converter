import c4d
from c4d import gui
import os
import re

import TextureMapping
import UI

PLUGIN_ID = 1055192 # PhotobashMaterialConverter

class PBMC_CommandData(c4d.plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = UI.PBMC_Dialog()
        
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=300, defaulth=500, xpos=-2, ypos=-2)

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = UI.PBMC_Dialog()

        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)


# Execute main()
if __name__=='__main__':
    c4d.plugins.RegisterCommandPlugin(
        id=PLUGIN_ID,
        str="Photobash Material Converter",
        help="",
        info=0,
        dat=PBMC_CommandData(),
        icon=None
    )