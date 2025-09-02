#!/usr/bin/env python3
"""
NumPy Compatibility Fix Script for Pickleball AI Server
Fixes NumPy 2.x compatibility issues with OpenCV
"""

import subprocess
import sys
import os

def check_numpy_version():
    """Check current NumPy version"""
    try:
        import numpy as np
        version = np.__version__
        print(f"🔍 Current NumPy version: {version}")
        return version
    except ImportError:
        print("❌ NumPy not installed")
        return None

def check_opencv_compatibility():
    """Check OpenCV compatibility"""
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️  OpenCV compatibility issue: {e}")
        return False

def fix_numpy_compatibility():
    """Fix NumPy compatibility issues"""
    print("\n🔧 Fixing NumPy compatibility...")
    
    try:
        # Check if we're in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if in_venv:
            print("✅ Virtual environment detected")
        else:
            print("⚠️  No virtual environment detected - consider using one")
        
        # Downgrade NumPy to 1.x
        print("📦 Downgrading NumPy to 1.x for OpenCV compatibility...")
        
        # First, uninstall current NumPy
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "numpy", "-y"], 
                      capture_output=True, text=True)
        
        # Install NumPy 1.x
        result = subprocess.run([sys.executable, "-m", "pip", "install", "numpy<2.0.0"], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ NumPy downgraded successfully")
        else:
            print(f"❌ NumPy downgrade failed: {result.stderr}")
            return False
        
        # Verify the fix
        print("\n🔍 Verifying compatibility fix...")
        new_version = check_numpy_version()
        
        if new_version and new_version.startswith('1.'):
            print("✅ NumPy 1.x installed successfully")
            
            # Test OpenCV import
            if check_opencv_compatibility():
                print("🎉 Compatibility issue resolved!")
                return True
            else:
                print("⚠️  OpenCV still has issues - may need additional fixes")
                return False
        else:
            print("❌ NumPy version not properly downgraded")
            return False
            
    except Exception as e:
        print(f"❌ Error during compatibility fix: {e}")
        return False

def alternative_solutions():
    """Provide alternative solutions"""
    print("\n💡 Alternative Solutions:")
    print("1. Use OpenCV with NumPy 2.x support:")
    print("   pip uninstall opencv-python")
    print("   pip install opencv-python-headless>=4.9.0")
    
    print("\n2. Use conda for better dependency management:")
    print("   conda install opencv numpy<2.0.0")
    
    print("\n3. Create a new virtual environment:")
    print("   python -m venv pickleball_env")
    print("   source pickleball_env/bin/activate  # Linux/Mac")
    print("   pickleball_env\\Scripts\\activate    # Windows")
    print("   pip install -r requirements.txt")

def main():
    """Main function"""
    print("🚀 NumPy Compatibility Fix for Pickleball AI Server")
    print("=" * 60)
    
    # Check current state
    current_version = check_numpy_version()
    
    if current_version and current_version.startswith('2.'):
        print(f"⚠️  NumPy {current_version} detected - incompatible with OpenCV 4.8.1.78")
        
        # Try to fix automatically
        if fix_numpy_compatibility():
            print("\n🎉 Success! Your system is now compatible.")
            print("You can now run: python -m app.server")
        else:
            print("\n❌ Automatic fix failed. Trying alternative solutions...")
            alternative_solutions()
    else:
        print("✅ NumPy version is compatible")
        
        # Test OpenCV anyway
        if check_opencv_compatibility():
            print("🎉 Everything is working correctly!")
        else:
            print("⚠️  OpenCV has other issues - check installation")
    
    print("\n" + "=" * 60)
    print("📚 For more help, see QUICK_INSTALL.md")

if __name__ == "__main__":
    main()
