import c4d, os, re, sys, imp

PLUGIN_ID = 1055192 # PhotobashMaterialConverter

PLUGIN_PATH = os.path.split(__file__)[0]
imp.load_compiled("texture_mapping", os.path.join(PLUGIN_PATH, "res", "texture_mapping.pyc"))
imp.load_compiled("UI", os.path.join(PLUGIN_PATH, "res", "UI.pyc"))
imp.load_compiled("physical", os.path.join(PLUGIN_PATH, "res", "physical.pyc"))

import UI, texture_mapping, physical

if c4d.plugins.FindPlugin(1041569) is not None:
  imp.load_compiled("octane", os.path.join(PLUGIN_PATH, "res", "octane.pyc"))
  import octane

if c4d.plugins.FindPlugin(1038954) is not None:
  imp.load_compiled("vray", os.path.join(PLUGIN_PATH, "res", "vray.pyc"))
  import vray

if c4d.plugins.FindPlugin(1033991) is not None:
  imp.load_compiled("arnold", os.path.join(PLUGIN_PATH, "res", "arnold.pyc"))
  import arnold

class PBMC_CommandData(c4d.plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = UI.PBMC_Dialog()

        return self.dialog.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE, pluginid=PLUGIN_ID, defaultw=300, defaulth=500, xpos=-2, ypos=-2)

# Execute main()
if __name__=='__main__':
    icon = c4d.bitmaps.BaseBitmap()
    icon.InitWith(os.path.join(PLUGIN_PATH, "icon_pbmc.png"))

    c4d.plugins.RegisterCommandPlugin(
        id=PLUGIN_ID,
        str="Photobash Material Converter",
        help="",
        info=0,
        dat=PBMC_CommandData(),
        icon=icon
    )
