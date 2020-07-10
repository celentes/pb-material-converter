#!/bin/bash
rm -rf c4d_pbmc
mkdir c4d_pbmc
cp photobash_material_converter.pyp c4d_pbmc
mkdir c4d_pbmc/res
python2 -m compileall arnold.py octane.py vray.py UI.py ../common/texture_mapping.py -b
mv ../common/texture_mapping.pyc .
mv *.pyc c4d_pbmc/res
