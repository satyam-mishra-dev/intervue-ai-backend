# Eye Tracking WebSocket Service

A real-time eye tracking service that monitors user attention during video calls using computer vision and WebSocket communication.

## Features

- 🎯 Real-time eye tracking and face detection
- 📡 WebSocket-based communication
- 🔄 Automatic camera detection and fallback
- 🛡️ Graceful error handling and recovery
- 📊 Confidence scoring for detection accuracy
- 🚀 Production-ready for cloud deployment

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the service:**
   ```bash
   python eye_gaze.py
   ```

3. **Connect via WebSocket:**
   ```
   ws://localhost:5000
   ```

### Production Deployment on Render

#### Option 1: Direct Deployment (Recommended)

1. **Connect your repository to Render**
2. **Create a new Web Service**
3. **Configure the service:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python eye_gaze.py`
   - **Environment Variables:**
     - `HOST`: `0.0.0.0`
     - `PORT`: `5000` (or let Render assign automatically)

#### Option 2: Using render.yaml

1. **Push your code with the `render.yaml` file**
2. **Render will automatically detect and deploy the service**

## WebSocket API

### Connection
Connect to the WebSocket endpoint to start monitoring:
```
ws://your-render-url.onrender.com
```

### Message Types

#### Start Tracking
```json
{
  "type": "start_tracking"
}
```

#### Stop Tracking
```json
{
  "type": "stop_tracking"
}
```

#### Ping/Pong
```json
{
  "type": "ping"
}
```

#### Status Check
```json
{
  "type": "status"
}
```

### Response Messages

#### Eye Tracking Data
```json
{
  "type": "eye_data",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "face_detected": true,
  "eye_count": 2,
  "looking_away": false,
  "confidence": 1.0,
  "face_count": 1
}
```

#### Connection Status
```json
{
  "type": "connection",
  "message": "Eye tracking connected",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "server_info": {
    "version": "1.0.0",
    "capabilities": ["eye_tracking", "face_detection"]
  }
}
```

#### Error Messages
```json
{
  "type": "error",
  "message": "Error description",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `5000` | Server port number |
| `LOG_LEVEL` | `INFO` | Logging level |

## Health Check

Run the health check script to verify your setup:
```bash
python health_check.py
```

## Production Considerations

### Render Deployment
- ✅ Uses `0.0.0.0` as default host for cloud compatibility
- ✅ Graceful shutdown handling
- ✅ Environment variable configuration
- ✅ Production logging
- ✅ Error handling and recovery

### Security
- 🔒 WebSocket connections are stateless
- 🔒 No persistent data storage
- 🔒 Input validation on all messages

### Performance
- ⚡ Optimized camera detection
- ⚡ Configurable frame processing rate
- ⚡ Memory-efficient image processing

## Troubleshooting

### Common Issues

1. **Camera not found:**
   - Ensure camera permissions are granted
   - Check if camera is being used by another application

2. **OpenCV cascade files missing:**
   - Run `python health_check.py` to verify installation
   - Reinstall OpenCV if needed: `pip install opencv-python-headless`

3. **WebSocket connection issues:**
   - Verify the service is running on the correct host/port
   - Check firewall settings
   - Ensure client supports WebSocket protocol

### Logs
Monitor application logs for detailed error information:
```bash
# View Render logs
render logs --service your-service-name
```

## Development

### Adding New Features
1. Extend the `EyeTracker` class
2. Add new message types to `process_message()`
3. Update the API documentation

### Testing
Test the WebSocket connection using tools like:
- [WebSocket King](https://websocketking.com/)
- [Postman](https://www.postman.com/) (WebSocket support)
- Browser WebSocket API

## License

This project is licensed under the MIT License. 