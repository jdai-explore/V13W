#!/bin/bash
# Activate the conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate arxml-viewer-pro
echo "Conda environment 'arxml-viewer-pro' activated!"
echo "You can now run:"
echo "  python -m arxml_viewer.main"
echo "  pytest"
echo "  black src/ tests/"
