# Pickleball AI Court Monitor System

A complete AI-powered system for monitoring pickleball courts using computer vision to detect ball bounces and determine in/out calls automatically.

## System Overview

The system consists of three main components:

1. **Server (RunPod)**: AI inference server with YOLO ball detection and GRU bounce detection models
2. **Camera Clients (Raspberry Pi)**: Webcam clients that capture and stream video to the server
3. **Web Application**: Real-time monitoring interface for viewing court feeds and managing the system

## Features

- **Real-time Ball Detection**: YOLO model detects pickleball in video streams
- **Bounce Detection**: GRU model identifies when ball bounces occur
- **In/Out Calls**: Automatic determination of ball position relative to court boundaries
- **Multi-Camera Support**: Support for multiple cameras per court
- **Live Streaming**: Real-time video feeds from all connected cameras
- **Replay System**: 5-second and 10-second replay functionality
- **Admin Panel**: Court and camera management interface
- **Theme System**: Customizable color themes (max 8 colors as requested)
- **Auto-reconnection**: Automatic reconnection on network issues
- **Zero Human Intervention**: Fully automated operation

## System Requirements

### Server (RunPod)
- Python 3.8+
- CUDA-compatible GPU (recommended)
- 8GB+ RAM
- 50GB+ storage

### Camera Clients (Raspberry Pi)
- Raspberry Pi 4 (recommended) or Pi 3B+
- 2GB+ RAM
- USB webcam or CSI camera
- WiFi/Ethernet connection
- 16GB+ SD card

### Web Application
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection to access the server

## Installation

### 1. Server Setup (RunPod)

The server code is already provided in the `server/` directory. Ensure you have:

1. **Models**: Place your YOLO and GRU models in `server/models/`
   - `best.pt` - YOLO ball detection model
   - `bounce_model.pt` - GRU bounce detection model

2. **Dependencies**: Install required Python packages
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**: Update `server/app/config.py` with your paths

4. **Run Server**:
   ```bash
   cd server
   python -m app.server
   ```

### 2. Raspberry Pi Camera Client Setup

#### Quick Installation
```bash
# Download and run the installation script
wget https://raw.githubusercontent.com/your-repo/pickleball-ai/main/install_raspberry_pi.sh
chmod +x install_raspberry_pi.sh
sudo ./install_raspberry_pi.sh
```

#### Manual Installation
1. **Install Dependencies**:
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-opencv
   pip3 install opencv-python-headless python-socketio requests
   ```

2. **Copy Files**:
   ```bash
   sudo mkdir -p /opt/pickleball_camera
   sudo cp raspberry_camera_client.py /opt/pickleball_camera/
   ```

3. **Configure Camera**:
   ```bash
   sudo /opt/pickleball_camera/configure_camera.sh
   ```

4. **Start Service**:
   ```bash
   sudo systemctl start pickleball-camera
   sudo systemctl enable pickleball-camera
   ```

### 3. Web Application Setup

1. **Copy Files**: Copy the `webapp/` directory to your web server
2. **Update Configuration**: Edit `webapp/app.js` and change `serverUrl` to your RunPod server URL
3. **Serve Files**: Use any web server (nginx, Apache, or Python's built-in server)

#### Quick Test with Python
```bash
cd webapp
python3 -m http.server 8080
# Access at http://localhost:8080
```

## Configuration

### Camera Client Configuration

Edit `/opt/pickleball_camera/camera_config.json`:

```json
{
    "server_url": "http://your-runpod-server.com:8000",
    "court_id": "court_1",
    "camera_id": 1,
    "camera_name": "Camera 1",
    "camera_position": "north",
    "fps": 30,
    "reconnect_delay": 5,
    "heartbeat_interval": 10
}
```

### Server Configuration

Edit `server/app/config.py`:

```python
# Model paths
BALL_MODEL_PATH = "/workspace/models/best.pt"
BOUNCE_MODEL_PATH = "/workspace/models/bounce_model.pt"

# Detection confidence
YOLO_CONF = 0.25

# Event recording
EVENT_CLIP_SEC_BEFORE = 3
EVENT_CLIP_SEC_AFTER = 3
```

### Web Application Configuration

Edit `webapp/app.js`:

```javascript
this.serverUrl = 'http://your-runpod-server.com:8000'; // CHANGE THIS
```

## Usage

### 1. Initial Setup

1. **Start the server** on your RunPod instance
2. **Configure courts and cameras** using the admin panel (username: `admin`, password: `admin123`)
3. **Connect camera clients** to the server
4. **Access the web application** to monitor courts

### 2. Admin Panel

- **Login**: Use admin credentials to access management features
- **Add Courts**: Create new pickleball courts
- **Add Cameras**: Configure cameras for each court
- **Monitor Status**: View system health and active streams

### 3. Court Monitoring

- **Live Feeds**: View real-time camera feeds
- **Decisions**: See automatic in/out calls
- **Replays**: Request 5s or 10s replay clips
- **Zoom**: Toggle zoomed view for out-of-bounds analysis

### 4. Camera Management

- **Auto-discovery**: Cameras automatically connect to the server
- **Status Monitoring**: Real-time camera status indicators
- **Reconnection**: Automatic reconnection on network issues

## Troubleshooting

### Common Issues

1. **Camera Not Connecting**:
   - Check network connectivity
   - Verify server URL in configuration
   - Check camera permissions

2. **Poor Detection**:
   - Ensure good lighting
   - Check camera positioning
   - Verify model files are correct

3. **Web App Not Loading**:
   - Check server URL configuration
   - Verify CORS settings
   - Check browser console for errors

### Logs and Debugging

#### Server Logs
```bash
# View server logs
tail -f /var/log/pickleball_server.log
```

#### Camera Client Logs
```bash
# View camera client logs
sudo journalctl -u pickleball-camera.service -f

# Check camera client status
sudo /opt/pickleball_camera/status.sh
```

#### Web Application
- Open browser developer tools (F12)
- Check Console tab for errors
- Check Network tab for connection issues

## Security Notes

⚠️ **Important**: The default admin credentials are:
- Username: `admin`
- Password: `admin123`

**Change these immediately in production!**

Edit `server/app/server.py`:
```python
ADMIN_USERNAME = "your_secure_username"
ADMIN_PASSWORD_HASH = hashlib.sha256("your_secure_password".encode()).hexdigest()
```

## Performance Optimization

### Server
- Use GPU acceleration for YOLO inference
- Adjust frame buffer sizes based on memory
- Monitor CPU/GPU usage

### Camera Clients
- Reduce FPS if network bandwidth is limited
- Use appropriate image quality settings
- Monitor Pi temperature and performance

### Web Application
- Enable auto-refresh for real-time updates
- Use appropriate theme for your environment
- Monitor browser performance

## Development and Customization

### Adding New Features
The system is designed for easy extension:
- **Server**: Add new endpoints in `server.py`
- **Camera Client**: Extend `PickleballCameraClient` class
- **Web App**: Add new UI components and functionality

### Theme Customization
Edit `webapp/styles.css` to modify colors:
```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
    /* ... other colors */
}
```

### Model Integration
- Replace YOLO model with your own ball detection model
- Integrate different bounce detection algorithms
- Add additional AI models for enhanced analysis

## Support and Maintenance

### Regular Maintenance
- Monitor system logs for errors
- Check camera connections and status
- Update models and dependencies as needed
- Backup configuration files

### Updates
- Keep Python packages updated
- Monitor for security updates
- Test new features in staging environment

## License

This project is provided as-is for educational and development purposes.

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Contact

For support or questions, please refer to the project documentation or create an issue in the repository.

---

**Note**: This system requires proper setup and testing before production use. Ensure all components are working correctly in your environment before deploying.
