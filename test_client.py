#!/usr/bin/env python3
"""
Test client for the Eye Tracking WebSocket Service
Use this to test your deployment on Render
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

async def test_websocket(url):
    """Test WebSocket connection and basic functionality"""
    print(f"🔗 Connecting to {url}...")
    
    try:
        async with websockets.connect(url) as websocket:
            print("✅ Connected successfully!")
            
            # Wait for connection message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 Received: {data}")
            except asyncio.TimeoutError:
                print("⚠️  No initial message received")
            except json.JSONDecodeError:
                print("⚠️  Received non-JSON message")
            
            # Test ping
            print("\n🏓 Testing ping...")
            await websocket.send(json.dumps({"type": "ping"}))
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 Pong received: {data}")
            except asyncio.TimeoutError:
                print("❌ No pong response")
            
            # Test status
            print("\n📊 Testing status...")
            await websocket.send(json.dumps({"type": "status"}))
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 Status received: {data}")
            except asyncio.TimeoutError:
                print("❌ No status response")
            
            # Test start tracking (briefly)
            print("\n🎯 Testing start tracking (5 seconds)...")
            await websocket.send(json.dumps({"type": "start_tracking"}))
            
            # Listen for eye tracking data for 5 seconds
            start_time = datetime.now()
            message_count = 0
            
            while (datetime.now() - start_time).seconds < 5:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    message_count += 1
                    if data.get("type") == "eye_data":
                        print(f"📹 Eye data #{message_count}: face_detected={data.get('face_detected')}, eyes={data.get('eye_count')}")
                    else:
                        print(f"📨 Other message: {data}")
                except asyncio.TimeoutError:
                    continue
                except json.JSONDecodeError:
                    print("⚠️  Received non-JSON message")
            
            # Stop tracking
            print("\n⏹️  Stopping tracking...")
            await websocket.send(json.dumps({"type": "stop_tracking"}))
            
            print(f"\n✅ Test completed! Received {message_count} messages during tracking.")
            
    except websockets.exceptions.InvalidURI:
        print(f"❌ Invalid WebSocket URL: {url}")
        print("   Make sure the URL starts with 'ws://' or 'wss://'")
    except websockets.exceptions.ConnectionClosed:
        print("❌ Connection closed unexpectedly")
    except Exception as e:
        print(f"❌ Connection error: {e}")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python test_client.py <websocket_url>")
        print("Example: python test_client.py ws://localhost:5000")
        print("Example: python test_client.py wss://your-app.onrender.com")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Add ws:// prefix if not present
    if not url.startswith(('ws://', 'wss://')):
        url = f"ws://{url}"
    
    print("🧪 Eye Tracking WebSocket Test Client")
    print("=====================================")
    print(f"🎯 Testing URL: {url}")
    print("")
    
    asyncio.run(test_websocket(url))

if __name__ == "__main__":
    main() 