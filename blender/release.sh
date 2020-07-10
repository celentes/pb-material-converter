#!/bin/bash
mkdir pbmc_blender
cp jdr_material_converter.py pbmc_blender
cp __init__.py pbmc_blender
cp eevee.py pbmc_blender
cp octane.py pbmc_blender
cp ../common/texture_mapping.py pbmc_blender
#cp texture_mapping.py blender_pbmc
rm *.zip
zip -r pbmc_blender.zip pbmc_blender
rm -rf pbmc_blender
