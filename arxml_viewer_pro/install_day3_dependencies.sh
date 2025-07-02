#!/bin/bash
# Install Day 3 Dependencies Script
# Installs all required dependencies for ARXML Viewer Pro Day 3

echo "🔧 Installing Day 3 Dependencies for ARXML Viewer Pro"
echo "=" * 60

# Check if we're in conda environment
if [[ "$CONDA_DEFAULT_ENV" != "" ]]; then
    echo "✅ Conda environment detected: $CONDA_DEFAULT_ENV"
else
    echo "⚠️  No conda environment detected"
    echo "💡 Activating arxml-viewer-pro environment..."
    source activate arxml-viewer-pro 2>/dev/null || conda activate arxml-viewer-pro 2>/dev/null
fi

echo ""
echo "📦 Installing Core Dependencies..."

# Install PyQt5 (GUI Framework)
echo "Installing PyQt5..."
pip install PyQt5==5.15.7

# Install pydantic (Data Models)
echo "Installing pydantic..."
pip install pydantic>=2.4.0

# Install additional Day 3 dependencies
echo "Installing additional dependencies..."
pip install lxml>=4.9.3
pip install pandas>=2.1.0
pip install matplotlib>=3.7.2
pip install networkx>=3.1
pip install click>=8.1.7
pip install loguru>=0.7.2
pip install numba>=0.58.0
pip install numpy>=1.24.0
pip install Pillow>=10.0.0

echo ""
echo "🧪 Testing Installation..."

# Test PyQt5
python -c "import PyQt5.QtWidgets; print('✅ PyQt5 working')" 2>/dev/null || echo "❌ PyQt5 failed"

# Test pydantic
python -c "import pydantic; print('✅ pydantic working')" 2>/dev/null || echo "❌ pydantic failed"

# Test other core imports
python -c "import lxml; print('✅ lxml working')" 2>/dev/null || echo "❌ lxml failed"
python -c "import pandas; print('✅ pandas working')" 2>/dev/null || echo "❌ pandas failed"

echo ""
echo "✅ Day 3 dependencies installation complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Run: python validate_day3_fixed.py"
echo "2. Or run: python -m arxml_viewer.main"