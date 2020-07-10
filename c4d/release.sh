#!/bin/bash
rm -rf c4d_pbmc
mkdir c4d_pbmc
cp photobash_material_converter.pyp c4d_pbmc
mkdir c4d_pbmc/res
cp ../common/texture_mapping.py .
python2 -m compileall arnold.py octane.py vray.py UI.py texture_mapping.py -b
rm texture_mapping.py
mv *.pyc c4d_pbmc/res
