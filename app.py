"""
Alternative entry point for production deployment with gunicorn
This file provides a WSGI-compatible interface for the WebSocket server
"""

import asyncio
import os
import sys
from eye_gaze import EyeTracker, shutdown_event

# Global tracker instance
tracker = None

def create_app():
    """Create and return the application instance"""
    global tracker
    tracker = EyeTracker()
    return tracker

def run_server():
    """Run the WebSocket server"""
    global tracker
    if tracker is None:
        tracker = create_app()
    
    try:
        asyncio.run(tracker.start_server())
    except Exception as e:
        print(f"❌ Fatal server error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_server() 