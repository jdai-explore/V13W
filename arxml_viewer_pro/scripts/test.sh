#!/bin/bash
# Quick test script for Conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate arxml-viewer-pro
cd ..
pytest "$@"
