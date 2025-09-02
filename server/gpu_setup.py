#!/usr/bin/env python3
"""
GPU Setup and Verification Script for Pickleball AI Server
Updated for PyTorch dev build with CUDA 12.8
"""

import sys
import subprocess
import os

def check_cuda_installation():
    """Check if CUDA is properly installed"""
    print("🔍 Checking CUDA installation...")
    
    try:
        # Check CUDA version
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            cuda_version = result.stdout.split('release ')[-1].split(',')[0]
            print(f"✅ CUDA {cuda_version} found")
            return cuda_version
        else:
            print("❌ CUDA compiler (nvcc) not found")
            return None
    except FileNotFoundError:
        print("❌ CUDA compiler (nvcc) not found in PATH")
        return None

def check_gpu_devices():
    """Check available GPU devices"""
    print("\n🔍 Checking GPU devices...")
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            print(f"✅ {gpu_count} GPU device(s) available")
            
            for i in range(gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print(f"   GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
            
            return gpu_count
        else:
            print("❌ PyTorch CUDA not available")
            return 0
    except ImportError:
        print("❌ PyTorch not installed")
        return 0

def check_pytorch_cuda():
    """Verify PyTorch CUDA support"""
    print("\n🔍 Checking PyTorch CUDA support...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} installed")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.version.cuda}")
            print(f"✅ cuDNN version: {torch.backends.cudnn.version()}")
            
            # Test CUDA tensor operations
            x = torch.randn(1000, 1000).cuda()
            y = torch.randn(1000, 1000).cuda()
            z = torch.mm(x, y)
            print("✅ CUDA tensor operations working")
            
            # Check CUDA version compatibility
            cuda_version = torch.version.cuda
            if cuda_version.startswith('12'):
                print(f"✅ CUDA {cuda_version} - Excellent for performance!")
            elif cuda_version.startswith('11'):
                print(f"✅ CUDA {cuda_version} - Good performance")
            else:
                print(f"⚠️  CUDA {cuda_version} - Consider upgrading for better performance")
            
            return True
        else:
            print("❌ PyTorch CUDA not available")
            return False
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    except Exception as e:
        print(f"❌ CUDA test failed: {e}")
        return False

def check_ultralytics_gpu():
    """Check Ultralytics GPU support"""
    print("\n🔍 Checking Ultralytics GPU support...")
    
    try:
        from ultralytics import YOLO
        print("✅ Ultralytics installed")
        
        # Check if CUDA is available for Ultralytics
        if hasattr(YOLO, 'device'):
            print("✅ Ultralytics CUDA support available")
            return True
        else:
            print("⚠️  Ultralytics CUDA support unclear")
            return False
    except ImportError:
        print("❌ Ultralytics not installed")
        return False

def check_opencv_gpu():
    """Check OpenCV GPU support"""
    print("\n🔍 Checking OpenCV GPU support...")
    
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__} installed")
        
        # Check if CUDA is available in OpenCV
        cuda_devices = cv2.cuda.getCudaEnabledDeviceCount()
        if cuda_devices > 0:
            print(f"✅ OpenCV CUDA support: {cuda_devices} device(s)")
            return True
        else:
            print("⚠️  OpenCV CUDA support not available (CPU only)")
            return False
    except ImportError:
        print("❌ OpenCV not installed")
        return False

def optimize_gpu_settings():
    """Set optimal GPU settings"""
    print("\n🔧 Optimizing GPU settings...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            # Enable cuDNN benchmarking for optimal performance
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
            
            # Set memory fraction (use 90% of GPU memory)
            torch.cuda.set_per_process_memory_fraction(0.9)
            
            # Enable TensorFloat-32 for better performance on Ampere+ GPUs
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            print("✅ GPU optimization settings applied")
            print("   - cuDNN benchmarking enabled")
            print("   - Memory fraction set to 90%")
            print("   - TF32 enabled for better performance")
            
            return True
        else:
            print("⚠️  No GPU available for optimization")
            return False
    except Exception as e:
        print(f"❌ GPU optimization failed: {e}")
        return False

def create_gpu_config():
    """Create GPU configuration file"""
    print("\n📝 Creating GPU configuration...")
    
    config_content = """# GPU Configuration for Pickleball AI Server
# Auto-generated for CUDA 12.8 + PyTorch dev build

[GPU]
# Enable GPU acceleration
use_gpu = true

# GPU memory fraction (0.0 to 1.0)
memory_fraction = 0.9

# Enable cuDNN optimization
cudnn_benchmark = true

# Enable TF32 for better performance
allow_tf32 = true

# Number of GPU workers
gpu_workers = 1

[YOLO]
# YOLO model device (auto, cuda:0, cuda:1, cpu)
device = auto

# Batch size for inference
batch_size = 1

# Use half precision for faster inference
half = true

[GRU]
# GRU model device
device = auto

# Sequence length for bounce detection
sequence_length = 30

[Performance]
# Enable optimizations
cudnn_benchmark = true
cudnn_deterministic = false
allow_tf32 = true
"""
    
    try:
        with open('gpu_config.ini', 'w') as f:
            f.write(config_content)
        print("✅ GPU configuration file created: gpu_config.ini")
        return True
    except Exception as e:
        print(f"❌ Failed to create config file: {e}")
        return False

def check_system_compatibility():
    """Check system compatibility"""
    print("\n🔍 Checking system compatibility...")
    
    try:
        import torch
        import cv2
        import numpy as np
        
        # Check PyTorch build info
        print(f"✅ PyTorch build: {torch.__version__}")
        print(f"✅ CUDA version: {torch.version.cuda}")
        print(f"✅ cuDNN version: {torch.backends.cudnn.version()}")
        
        # Check OpenCV
        print(f"✅ OpenCV version: {cv2.__version__}")
        
        # Check NumPy
        print(f"✅ NumPy version: {np.__version__}")
        
        # Check CUDA compute capability
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            compute_cap = f"{props.major}.{props.minor}"
            print(f"✅ Compute capability: {compute_cap}")
            
            if props.major >= 8:
                print("✅ RTX 30/40 series or A100 - Excellent performance!")
            elif props.major >= 7:
                print("✅ RTX 20 series - Good performance")
            else:
                print("⚠️  Older GPU - Performance may be limited")
        
        return True
    except Exception as e:
        print(f"❌ System compatibility check failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Pickleball AI Server - GPU Setup")
    print("Updated for PyTorch dev + CUDA 12.8")
    print("=" * 60)
    
    # Check system requirements
    cuda_version = check_cuda_installation()
    gpu_count = check_gpu_devices()
    pytorch_cuda = check_pytorch_cuda()
    ultralytics_gpu = check_ultralytics_gpu()
    opencv_gpu = check_opencv_gpu()
    system_compat = check_system_compatibility()
    
    # Optimize settings
    optimization_success = optimize_gpu_settings()
    
    # Create configuration
    config_success = create_gpu_config()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SETUP SUMMARY")
    print("=" * 60)
    
    if cuda_version and gpu_count > 0 and pytorch_cuda and ultralytics_gpu:
        print("🎉 GPU setup complete! Your server is ready for GPU acceleration.")
        print(f"   - CUDA {cuda_version}")
        print(f"   - {gpu_count} GPU device(s)")
        print(f"   - PyTorch CUDA: ✅")
        print(f"   - Ultralytics GPU: ✅")
        print(f"   - OpenCV GPU: {'✅' if opencv_gpu else '⚠️'}")
    else:
        print("⚠️  GPU setup incomplete. Some components may not work optimally.")
        if not cuda_version:
            print("   - Install CUDA toolkit")
        if gpu_count == 0:
            print("   - Check GPU drivers")
        if not pytorch_cuda:
            print("   - Install PyTorch with CUDA support")
        if not ultralytics_gpu:
            print("   - Check Ultralytics installation")
    
    print("\n💡 Next steps:")
    print("   1. Start the server: python -m app.server")
    print("   2. Monitor GPU usage with: nvidia-smi")
    print("   3. Check logs for GPU utilization")
    print("   4. Run GPU monitor: python gpu_monitor.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
