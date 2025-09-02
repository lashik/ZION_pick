# 🚀 GPU Setup Guide for Pickleball AI Server

This guide ensures your RunPod server can fully utilize GPU acceleration for optimal AI inference performance.

## 🎯 **GPU Requirements**

### **Minimum Requirements**
- **GPU**: NVIDIA GPU with CUDA support (RTX 3060 or better)
- **VRAM**: 8GB+ (16GB+ recommended for multiple models)
- **CUDA**: Version 11.8 or higher
- **Driver**: Latest NVIDIA drivers

### **Recommended Setup**
- **GPU**: RTX 4090, RTX 3090, or A100
- **VRAM**: 24GB+ for optimal performance
- **CUDA**: Version 12.1 or higher
- **Storage**: NVMe SSD for fast model loading

## 🔧 **Installation Steps**

### **1. Verify CUDA Installation**
```bash
# Check CUDA version
nvcc --version

# Check GPU devices
nvidia-smi

# Expected output:
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 525.105.17   Driver Version: 525.105.17   CUDA Version: 12.0    |
# +-----------------------------------------------------------------------------+
```

### **2. Install PyTorch with CUDA Support**

#### **For CUDA 11.8:**
```bash
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

#### **For CUDA 12.1:**
```bash
pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0+cu121 --index-url https://download.pytorch.org/whl/cu121
```

#### **For CUDA 12.4:**
```bash
pip install torch==2.1.2+cu124 torchvision==0.16.2+cu124 torchaudio==2.1.2+cu124 --index-url https://download.pytorch.org/whl/cu124
```

### **3. Install Other Dependencies**
```bash
# Install GPU monitoring tools
pip install nvidia-ml-py3 GPUtil

# Install other requirements
pip install -r requirements.txt
```

### **4. Verify GPU Support**
```bash
# Run GPU verification script
python gpu_setup.py

# Expected output:
# ✅ CUDA 12.1 found
# ✅ 1 GPU device(s) available
#    GPU 0: NVIDIA RTX 4090 (24.0 GB)
# ✅ PyTorch 2.1.0+cu121 installed
# ✅ CUDA available: 12.1
# ✅ cuDNN version: 8902
# ✅ CUDA tensor operations working
# ✅ Ultralytics CUDA support available
```

## 🎮 **GPU Optimization Settings**

### **Automatic Optimization**
The server automatically applies these optimizations:
- **cuDNN Benchmarking**: Enabled for optimal performance
- **Memory Management**: Uses 90% of available GPU memory
- **Half Precision**: FP16 inference for faster processing
- **Device Selection**: Automatically selects best available GPU

### **Manual Configuration**
Edit `server/app/config.py`:
```python
# GPU Optimization Settings
GPU_ENABLED = True
GPU_MEMORY_FRACTION = 0.9
CUDNN_BENCHMARK = True
GPU_DEVICE = "auto"  # or "cuda:0", "cuda:1"

# YOLO Model Settings
YOLO_DEVICE = "auto"
YOLO_HALF_PRECISION = True

# GRU Model Settings
GRU_DEVICE = "auto"
```

## 📊 **GPU Monitoring**

### **Real-time Monitoring**
```bash
# Start GPU monitoring
python gpu_monitor.py

# Monitor specific interval
python gpu_monitor.py --interval 10

# Show metrics once
python gpu_monitor.py --once
```

### **Command Line Monitoring**
```bash
# Basic GPU status
nvidia-smi

# Continuous monitoring
watch -n 1 nvidia-smi

# Detailed GPU info
nvidia-smi -q
```

## 🚀 **Performance Optimization**

### **Model Loading Optimization**
```python
# In your inference code
import torch

# Enable optimizations
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.deterministic = False

# Set memory fraction
torch.cuda.set_per_process_memory_fraction(0.9)

# Use mixed precision for faster inference
from torch.cuda.amp import autocast
```

### **Batch Processing**
```python
# Process multiple frames together
def process_batch(frames):
    with autocast():
        # Convert frames to tensor
        batch = torch.stack([torch.from_numpy(frame) for frame in frames])
        batch = batch.cuda()
        
        # Run inference
        results = model(batch)
        
        return results.cpu().numpy()
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **1. CUDA Out of Memory**
```bash
# Reduce memory usage
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Or modify config.py
GPU_MEMORY_FRACTION = 0.7  # Use 70% instead of 90%
```

#### **2. PyTorch CUDA Not Available**
```bash
# Check PyTorch installation
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall with correct CUDA version
pip uninstall torch torchvision torchaudio
pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 --index-url https://download.pytorch.org/whl/cu121
```

#### **3. Model Loading Errors**
```bash
# Check model file permissions
ls -la /workspace/models/

# Verify model compatibility
python -c "from ultralytics import YOLO; model = YOLO('/workspace/models/best.pt')"
```

### **Performance Issues**

#### **1. Slow Inference**
- Enable half precision: `YOLO_HALF_PRECISION = True`
- Increase batch size if memory allows
- Use TensorRT optimization (advanced)

#### **2. High Memory Usage**
- Reduce `GPU_MEMORY_FRACTION` to 0.7
- Process frames individually instead of batches
- Clear GPU cache between inferences

## 📈 **Performance Benchmarks**

### **Expected Performance (RTX 4090)**
- **YOLO Inference**: 15-25ms per frame
- **GRU Processing**: 5-10ms per sequence
- **Total Latency**: 20-35ms per decision
- **Throughput**: 30-50 FPS sustained

### **Performance Monitoring**
```bash
# Monitor FPS
python -c "
import time
from ultralytics import YOLO
model = YOLO('/workspace/models/best.pt')
start = time.time()
for i in range(100):
    model('test_image.jpg')
end = time.time()
print(f'Average FPS: {100/(end-start):.1f}')
"
```

## 🔒 **Security Considerations**

### **GPU Access Control**
```bash
# Restrict GPU access to specific users
sudo usermod -a -G video $USER

# Set GPU persistence mode
sudo nvidia-smi -pm 1
```

### **Memory Protection**
```bash
# Prevent GPU memory exhaustion
export CUDA_LAUNCH_BLOCKING=1
export CUDA_MEMORY_FRACTION=0.9
```

## 📚 **Additional Resources**

### **Documentation**
- [PyTorch CUDA Guide](https://pytorch.org/docs/stable/notes/cuda.html)
- [Ultralytics GPU Guide](https://docs.ultralytics.com/guides/training/#gpu-training)
- [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)

### **Tools**
- **NVIDIA Nsight**: GPU debugging and profiling
- **TensorRT**: Model optimization
- **PyTorch Profiler**: Performance analysis

## ✅ **Verification Checklist**

- [ ] CUDA toolkit installed and working
- [ ] PyTorch with CUDA support installed
- [ ] GPU devices detected and accessible
- [ ] Models load without errors
- [ ] GPU monitoring working
- [ ] Performance meets expectations
- [ ] Memory usage within limits

## 🎯 **Next Steps**

1. **Run GPU setup script**: `python gpu_setup.py`
2. **Start GPU monitoring**: `python gpu_monitor.py`
3. **Test model inference**: Load and run your models
4. **Monitor performance**: Check FPS and memory usage
5. **Optimize settings**: Adjust configuration based on results

Your server should now be fully optimized for GPU acceleration! 🚀
