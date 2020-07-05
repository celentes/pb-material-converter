#!/bin/bash
mkdir jdr_material_converter
cp jdr_material_converter.py jdr_material_converter
cp __init__.py jdr_material_converter
cp eevee.py jdr_material_converter
cp octane.py jdr_material_converter
cp ../texture_mapping.py jdr_material_converter
#cp texture_mapping.py blender_pbmc
rm *.zip
zip -r jdr_material_converter.zip jdr_material_converter
rm -rf jdr_material_converter
