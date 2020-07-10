#!/bin/bash
mkdir pbmc_blender
cp __init__.py pbmc_blender
python3.7 -m compileall eevee.py octane.py jdr_material_converter.py ../common/texture_mapping.py -b
mv ../common/texture_mapping.pyc .
mv *.pyc pbmc_blender
rm *.zip
zip -r pbmc_blender.zip pbmc_blender
rm -rf pbmc_blender
