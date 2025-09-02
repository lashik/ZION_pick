# 🚀 Quick Install Guide for Your Environment

Your system already has most packages installed! Here's how to get the remaining dependencies without conflicts.

## ⚠️ **IMPORTANT: NumPy Compatibility Issue**

You have **NumPy 2.3.2** installed, but **OpenCV 4.8.1.78** was compiled against **NumPy 1.x**. This causes crashes.

### **Quick Fix (Recommended)**
```bash
cd server
python fix_numpy_compatibility.py
```

### **Manual Fix**
```bash
# Downgrade NumPy to 1.x for OpenCV compatibility
pip install "numpy<2.0.0" --force-reinstall

# Verify fix
python -c "import cv2; print('OpenCV working!')"
```

## ✅ **What You Already Have**
- **PyTorch**: 2.8.0.dev + CUDA 12.8 ✅
- **OpenCV**: 4.8.1.78 ✅ (but needs NumPy 1.x)
- **NumPy**: 2.3.2 ❌ (incompatible with OpenCV)
- **SciPy**: 1.16.1 ✅
- **Shapely**: 2.0.2 ✅
- **Requests**: 2.32.3 ✅
- **psutil**: 7.0.0 ✅
- **All CUDA libraries**: nvidia-cublas-cu12, nvidia-cudnn-cu12, etc. ✅

## 📦 **What You Need to Install**

### **Step 1: Fix NumPy Compatibility**
```bash
# Run the compatibility fix script
python fix_numpy_compatibility.py

# OR manually fix
pip install "numpy<2.0.0" --force-reinstall
```

### **Step 2: Install Missing Dependencies**
```bash
# Use the install script (recommended)
chmod +x install_dependencies.sh
./install_dependencies.sh

# OR manual installation
pip install nvidia-ml-py3 GPUtil
pip install --ignore-installed blinker Flask Flask-SocketIO eventlet
pip install ultralytics python-socketio
```

## 🔍 **Verify Installation**
```bash
# Test NumPy and OpenCV compatibility
python -c "
import numpy as np
import cv2
print(f'✅ NumPy {np.__version__}')
print(f'✅ OpenCV {cv2.__version__}')
print('🎉 Compatibility issue resolved!')
"

# Run GPU setup verification
python gpu_setup.py
```

## 🚀 **Start the Server**
```bash
# Start the server
python -m app.server

# In another terminal, monitor GPU usage
python gpu_monitor.py
```

## 🎯 **Why This Approach Works**

1. **Fixes NumPy Issue**: Downgrades to compatible version
2. **Avoids Blinker Conflict**: Uses `--ignore-installed` flag
3. **Leverages Your Setup**: Your PyTorch dev build + CUDA 12.8 is excellent
4. **Minimal Installation**: Only installs what's missing

## 🐛 **If You Still Get Errors**

### **NumPy Issue Persists**
```bash
# Try alternative OpenCV version
pip uninstall opencv-python
pip install opencv-python-headless>=4.9.0

# Or use conda
conda install opencv numpy<2.0.0
```

### **Blinker Issue Persists**
```bash
# Force reinstall blinker
pip install --force-reinstall blinker

# Or skip blinker entirely
pip install Flask Flask-SocketIO eventlet --no-deps
pip install Werkzeug Jinja2 itsdangerous click
```

### **Permission Issues**
```bash
# Use user installation
pip install --user "numpy<2.0.0" nvidia-ml-py3 GPUtil Flask Flask-SocketIO eventlet ultralytics
```

## 📊 **Expected Performance with Your Setup**

- **CUDA 12.8**: Latest CUDA version for maximum performance
- **PyTorch Dev**: Cutting-edge optimizations
- **GPU Memory**: Full utilization of your GPU VRAM
- **Inference Speed**: 20-40ms per frame (depending on GPU model)

## 🔧 **Troubleshooting Steps**

1. **Run compatibility fix**: `python fix_numpy_compatibility.py`
2. **Install dependencies**: `./install_dependencies.sh`
3. **Verify GPU setup**: `python gpu_setup.py`
4. **Test server**: `python -m app.server`

## 🎉 **You're Ready!**

After fixing the NumPy compatibility issue, your environment will be fully GPU-accelerated and ready for the pickleball AI server!

## 📚 **Additional Resources**

- **NumPy 2.x Migration Guide**: https://numpy.org/devdocs/numpy_2_0_migration_guide.html
- **OpenCV Compatibility**: https://docs.opencv.org/
- **PyTorch CUDA Guide**: https://pytorch.org/docs/stable/notes/cuda.html
