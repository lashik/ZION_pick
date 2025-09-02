#!/usr/bin/env python3
"""
GPU Monitoring Script for Pickleball AI Server
Monitors GPU usage, memory, and performance metrics
"""

import time
import psutil
import threading
from datetime import datetime
import json

try:
    import torch
    import nvidia_ml_py3 as nvml
    GPU_MONITORING_AVAILABLE = True
except ImportError:
    GPU_MONITORING_AVAILABLE = False
    print("⚠️  GPU monitoring not available. Install nvidia-ml-py3 for full monitoring.")

class GPUMonitor:
    def __init__(self, log_file="gpu_metrics.log", interval=5):
        self.log_file = log_file
        self.interval = interval
        self.running = False
        self.monitor_thread = None
        
        if GPU_MONITORING_AVAILABLE:
            try:
                nvml.nvmlInit()
                self.gpu_count = nvml.nvmlDeviceGetCount()
                print(f"✅ GPU monitoring initialized for {self.gpu_count} GPU(s)")
            except Exception as e:
                print(f"❌ GPU monitoring initialization failed: {e}")
                self.gpu_count = 0
        else:
            self.gpu_count = 0
    
    def get_gpu_metrics(self):
        """Get current GPU metrics"""
        if not GPU_MONITORING_AVAILABLE or self.gpu_count == 0:
            return None
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'gpus': []
        }
        
        try:
            for i in range(self.gpu_count):
                handle = nvml.nvmlDeviceGetHandleByIndex(i)
                
                # Memory info
                mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                
                # GPU utilization
                util = nvml.nvmlDeviceGetUtilizationRates(handle)
                
                # Temperature
                temp = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
                
                # Power usage
                power = nvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to Watts
                
                gpu_metrics = {
                    'gpu_id': i,
                    'name': nvml.nvmlDeviceGetName(handle).decode('utf-8'),
                    'memory': {
                        'total': mem_info.total / 1024**3,  # GB
                        'used': mem_info.used / 1024**3,   # GB
                        'free': mem_info.free / 1024**3,   # GB
                        'utilization': (mem_info.used / mem_info.total) * 100
                    },
                    'utilization': util.gpu,
                    'temperature': temp,
                    'power': power
                }
                
                metrics['gpus'].append(gpu_metrics)
                
        except Exception as e:
            print(f"❌ Error getting GPU metrics: {e}")
            return None
        
        return metrics
    
    def get_system_metrics(self):
        """Get system-level metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
    
    def log_metrics(self, metrics):
        """Log metrics to file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(metrics) + '\n')
        except Exception as e:
            print(f"❌ Error logging metrics: {e}")
    
    def print_metrics(self, metrics):
        """Print metrics to console"""
        if not metrics:
            return
        
        print(f"\n📊 GPU Metrics - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        if 'gpus' in metrics:
            for gpu in metrics['gpus']:
                print(f"GPU {gpu['gpu_id']}: {gpu['name']}")
                print(f"  Memory: {gpu['memory']['used']:.1f}/{gpu['memory']['total']:.1f} GB ({gpu['memory']['utilization']:.1f}%)")
                print(f"  Utilization: {gpu['utilization']}% | Temp: {gpu['temperature']}°C | Power: {gpu['power']:.1f}W")
        
        if 'cpu_percent' in metrics:
            print(f"System: CPU {metrics['cpu_percent']}% | RAM {metrics['memory_percent']}% | Disk {metrics['disk_percent']}%")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Get GPU metrics
                gpu_metrics = self.get_gpu_metrics()
                system_metrics = self.get_system_metrics()
                
                # Combine metrics
                combined_metrics = {
                    'gpu': gpu_metrics,
                    'system': system_metrics
                }
                
                # Log and display
                self.log_metrics(combined_metrics)
                self.print_metrics(gpu_metrics)
                
                # Wait for next interval
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(self.interval)
    
    def start(self):
        """Start GPU monitoring"""
        if self.running:
            print("⚠️  Monitoring already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        print(f"🚀 GPU monitoring started (interval: {self.interval}s)")
    
    def stop(self):
        """Stop GPU monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("🛑 GPU monitoring stopped")
    
    def get_summary(self):
        """Get a summary of current GPU status"""
        gpu_metrics = self.get_gpu_metrics()
        if not gpu_metrics:
            return "No GPU metrics available"
        
        summary = []
        for gpu in gpu_metrics['gpus']:
            gpu_summary = f"GPU {gpu['gpu_id']}: {gpu['utilization']}% util, {gpu['memory']['utilization']:.1f}% mem, {gpu['temperature']}°C"
            summary.append(gpu_summary)
        
        return " | ".join(summary)

def main():
    """Main function for standalone GPU monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GPU Monitor for Pickleball AI Server')
    parser.add_argument('--interval', type=int, default=5, help='Monitoring interval in seconds')
    parser.add_argument('--log-file', default='gpu_metrics.log', help='Log file path')
    parser.add_argument('--once', action='store_true', help='Show metrics once and exit')
    
    args = parser.parse_args()
    
    monitor = GPUMonitor(log_file=args.log_file, interval=args.interval)
    
    if args.once:
        # Show metrics once
        metrics = monitor.get_gpu_metrics()
        monitor.print_metrics(metrics)
        return
    
    try:
        # Start continuous monitoring
        monitor.start()
        
        print("Press Ctrl+C to stop monitoring...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping GPU monitor...")
        monitor.stop()

if __name__ == "__main__":
    main()
