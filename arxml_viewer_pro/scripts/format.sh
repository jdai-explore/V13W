#!/bin/bash
# Code formatting script for Conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate arxml-viewer-pro
cd ..
echo "Running black..."
black src/ tests/
echo "Running isort..."
isort src/ tests/
echo "Code formatted!"
