#!/bin/bash
# Quick run script for Conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate arxml-viewer-pro
cd ..
python -m arxml_viewer.main "$@"
