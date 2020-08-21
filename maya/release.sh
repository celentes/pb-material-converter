#!/bin/bash
rm -rf plug-ins
mkdir plug-ins
mkdir plug-ins/PhotobashMaterialConverter
cp PhotobashMaterialConverter.py plug-ins
cp arnold_rnd.py plug-ins/PhotobashMaterialConverter
cp logic.py plug-ins/PhotobashMaterialConverter
cp ui.py plug-ins/PhotobashMaterialConverter
cp ../common/texture_mapping.py plug-ins/PhotobashMaterialConverter

#cp icon_pbmc.png pbmc_maya
#cp CHANGELOG.txt pbmc_maya
#mkdir pbmc_maya/res
#python2 -m compileall physical.py arnold.py octane.py vray.py ui.py ../common/texture_mapping.py -b
#mv ../common/texture_mapping.pyc .
#mv *.pyc pbmc_maya/res
