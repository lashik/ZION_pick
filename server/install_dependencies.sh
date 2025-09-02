#!/bin/bash
# Pickleball AI Server - Dependency Installation Script
# This script installs only the missing packages to avoid conflicts
# Fixed for NumPy 2.x compatibility issues

echo "🚀 Installing Pickleball AI Server Dependencies"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Run this script from the server directory."
    exit 1
fi

echo "🔍 Checking NumPy version..."
NUMPY_VERSION=$(python -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "not_installed")

if [[ "$NUMPY_VERSION" == not_installed ]]; then
    echo "📦 Installing NumPy 1.x for OpenCV compatibility..."
    pip install "numpy<2.0.0"
elif [[ "$NUMPY_VERSION" == 2.* ]]; then
    echo "⚠️  NumPy $NUMPY_VERSION detected - incompatible with OpenCV 4.8.1.78"
    echo "🔄 Downgrading to NumPy 1.x for compatibility..."
    pip install "numpy<2.0.0" --force-reinstall
else
    echo "✅ NumPy $NUMPY_VERSION is compatible"
fi

echo "📦 Installing GPU monitoring tools..."
pip install nvidia-ml-py3 GPUtil

echo "🌐 Installing web framework dependencies..."
# Install Flask and related packages, ignoring blinker conflicts
pip install --ignore-installed blinker Flask Flask-SocketIO eventlet

echo "🤖 Installing AI dependencies..."
pip install ultralytics

echo "🔌 Installing WebSocket support..."
pip install python-socketio

echo "🧪 Installing development tools (optional)..."
pip install pytest pytest-flask

echo ""
echo "✅ Installation complete!"
echo ""
echo "🔍 Verifying installation..."
python -c "
import sys
packages = ['flask', 'flask_socketio', 'ultralytics', 'torch', 'cv2', 'numpy']
missing = []

for package in packages:
    try:
        if package == 'cv2':
            import cv2
            print(f'✅ {package} {cv2.__version__}')
        elif package == 'numpy':
            import numpy as np
            print(f'✅ {package} {np.__version__}')
        else:
            __import__(package)
            print(f'✅ {package}')
    except ImportError as e:
        missing.append(package)
        print(f'❌ {package}: {e}')
    except Exception as e:
        print(f'⚠️  {package}: {e}')

if missing:
    print(f'\n⚠️  Missing packages: {missing}')
    print('Run: pip install ' + ' '.join(missing))
else:
    print('\n🎉 All packages installed successfully!')
"

echo ""
echo "🚀 Next steps:"
echo "1. Run GPU setup: python gpu_setup.py"
echo "2. Start server: python -m app.server"
echo "3. Monitor GPU: python gpu_monitor.py"
