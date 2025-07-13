import cv2
import numpy as np
import json
import asyncio
import os
import signal
import sys
from datetime import datetime
import logging
from websockets.server import serve
from websockets.exceptions import ConnectionClosed
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Get host and port from environment variables (for cloud hosting)
HOST = os.getenv('HOST', '0.0.0.0')  # Changed to 0.0.0.0 for cloud deployment
PORT = int(os.getenv('PORT', 5000))

# Graceful shutdown handling
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class EyeTracker:
    def __init__(self):
        try:
            # Load cascade classifiers with error handling
            # Use cv2.data.haarcascades for better compatibility
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            
            if not os.path.exists(face_cascade_path):
                logger.error(f"❌ Face cascade file not found: {face_cascade_path}")
                raise FileNotFoundError(f"Face cascade file not found: {face_cascade_path}")
                
            if not os.path.exists(eye_cascade_path):
                logger.error(f"❌ Eye cascade file not found: {eye_cascade_path}")
                raise FileNotFoundError(f"Eye cascade file not found: {eye_cascade_path}")
            
            self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
            self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
            
            # Check if cascade classifiers loaded successfully
            if self.face_cascade.empty():
                logger.error("❌ Failed to load face cascade classifier")
                raise RuntimeError("Failed to load face cascade classifier")
                
            if self.eye_cascade.empty():
                logger.error("❌ Failed to load eye cascade classifier")
                raise RuntimeError("Failed to load eye cascade classifier")
                
            logger.info("✅ Cascade classifiers loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing cascade classifiers: {e}")
            raise
            
        self.connected_clients = set()
        self.is_running = False
        self.server = None
        
    async def start_server(self):
        """Start the WebSocket server"""
        try:
            self.server = await serve(
                self.handle_client, 
                HOST, 
                PORT,
                ping_interval=20,
                ping_timeout=20,
                max_size=1024 * 1024  # 1MB max message size
            )
            logger.info(f"🚀 Eye tracking server started on {HOST}:{PORT}")
            logger.info(f"📡 WebSocket endpoint: ws://{HOST}:{PORT}")
            
            # Keep the server running until shutdown signal
            await shutdown_event.wait()
            
            # Graceful shutdown
            logger.info("🛑 Shutting down server...")
            self.server.close()
            await self.server.wait_closed()
            logger.info("✅ Server shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Failed to start server: {e}")
            raise

    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections"""
        try:
            self.connected_clients.add(websocket)
            logger.info(f"✅ Client connected. Total clients: {len(self.connected_clients)}")
            
            # Send welcome message
            await websocket.send(json.dumps({
                "type": "connection",
                "message": "Eye tracking connected",
                "timestamp": datetime.now().isoformat(),
                "server_info": {
                    "version": "1.0.0",
                    "capabilities": ["eye_tracking", "face_detection"]
                }
            }))
            
            # Keep connection alive and handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(websocket, data)
                except json.JSONDecodeError:
                    logger.warning("❌ Invalid JSON received")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.now().isoformat()
                    }))
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"Internal server error: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }))
                    
        except ConnectionClosed:
            logger.info("🔌 Client disconnected normally")
        except Exception as e:
            logger.error(f"❌ Client error: {e}")
        finally:
            self.connected_clients.discard(websocket)
            logger.info(f"👋 Client disconnected. Total clients: {len(self.connected_clients)}")

    async def process_message(self, websocket, data):
        """Process incoming WebSocket messages"""
        message_type = data.get('type')
        
        if message_type == 'start_tracking':
            logger.info("🎯 Starting eye tracking...")
            await self.start_eye_tracking(websocket)
        elif message_type == 'stop_tracking':
            logger.info("⏹️ Stopping eye tracking...")
            self.is_running = False
        elif message_type == 'ping':
            await websocket.send(json.dumps({
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            }))
        elif message_type == 'status':
            await websocket.send(json.dumps({
                "type": "status",
                "is_tracking": self.is_running,
                "connected_clients": len(self.connected_clients),
                "timestamp": datetime.now().isoformat()
            }))
        else:
            logger.warning(f"❓ Unknown message type: {message_type}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Unknown message type: {message_type}",
                "timestamp": datetime.now().isoformat()
            }))

    async def start_eye_tracking(self, websocket):
        """Start eye tracking and send results via WebSocket"""
        self.is_running = True
        
        # Initialize camera with multiple fallback options
        cap = None
        camera_index = 0
        
        # Try different camera indices
        for i in range(3):  # Try indices 0, 1, 2
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    logger.info(f"📹 Camera initialized successfully on index {i}")
                    break
                else:
                    cap.release()
            except Exception as e:
                logger.warning(f"❌ Failed to open camera on index {i}: {e}")
                if cap:
                    cap.release()
        
        if not cap or not cap.isOpened():
            logger.error("❌ Could not open camera on any index")
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Could not open camera - no camera available",
                "timestamp": datetime.now().isoformat()
            }))
            return

        logger.info("📹 Camera initialized successfully")
        
        try:
            while self.is_running and not shutdown_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    logger.warning("❌ Failed to read frame")
                    continue

                # Convert to grayscale for detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces with adjusted parameters for better detection
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(30, 30)
                )
                
                eye_data = {
                    "type": "eye_data",
                    "timestamp": datetime.now().isoformat(),
                    "face_detected": len(faces) > 0,
                    "eye_count": 0,
                    "looking_away": False,
                    "confidence": 0.0,
                    "face_count": len(faces)
                }
                
                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = frame[y:y+h, x:x+w]
                    
                    # Detect eyes within the face region
                    eyes = self.eye_cascade.detectMultiScale(
                        roi_gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(20, 20)
                    )
                    eye_data["eye_count"] = len(eyes)
                    
                    # Calculate confidence based on face and eye detection
                    if len(faces) > 0 and len(eyes) >= 2:
                        eye_data["confidence"] = min(1.0, len(eyes) / 2.0)
                    elif len(faces) > 0:
                        eye_data["confidence"] = 0.5
                    else:
                        eye_data["confidence"] = 0.0
                
                # Determine if user is looking away
                if len(faces) == 0 or eye_data["eye_count"] < 2:
                    eye_data["looking_away"] = True
                
                # Send data to client
                try:
                    await websocket.send(json.dumps(eye_data))
                except ConnectionClosed:
                    logger.info("🔌 Client disconnected during tracking")
                    break
                except Exception as e:
                    logger.error(f"❌ Error sending data: {e}")
                    break
                
                # Add small delay to prevent overwhelming the client
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"❌ Eye tracking error: {e}")
        finally:
            if cap:
                cap.release()
            logger.info("📹 Camera released")

async def main():
    """Main function to start the server"""
    try:
        tracker = EyeTracker()
        await tracker.start_server()
    except Exception as e:
        logger.error(f"❌ Fatal server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)
