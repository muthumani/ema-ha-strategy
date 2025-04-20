"""
Health check endpoint for the EMA Heikin Ashi Strategy.
Provides a simple HTTP server that returns the health status of the application.
"""

import http.server
import socketserver
import json
import threading
import os
import sys
import time
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, Any, Optional, List, Tuple

from utils.logger import setup_logger
from utils.version import __version__

# Set up logger
logger = setup_logger(name="health_check", log_level=logging.INFO)

class HealthStatus:
    """Health status tracker for the application"""
    
    def __init__(self):
        """Initialize health status"""
        self.status = "OK"
        self.last_check = datetime.now()
        self.components = {
            "data_folder": True,
            "results_folder": True,
            "logs_folder": True,
            "disk_space": True
        }
        self.messages = []
        self.version = __version__
    
    def check_health(self) -> bool:
        """
        Check the health of the application
        
        Returns:
            True if healthy, False otherwise
        """
        self.last_check = datetime.now()
        self.messages = []
        
        # Check data folder
        data_folder = Path("data/market_data")
        self.components["data_folder"] = data_folder.exists() and data_folder.is_dir()
        if not self.components["data_folder"]:
            self.messages.append("Data folder not found")
        
        # Check results folder
        results_folder = Path("data/results")
        self.components["results_folder"] = results_folder.exists() and results_folder.is_dir()
        if not self.components["results_folder"]:
            self.messages.append("Results folder not found")
        
        # Check logs folder
        logs_folder = Path("logs")
        self.components["logs_folder"] = logs_folder.exists() and logs_folder.is_dir()
        if not self.components["logs_folder"]:
            self.messages.append("Logs folder not found")
        
        # Check disk space (at least 100MB free)
        try:
            if sys.platform == "win32":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p("."), None, None, ctypes.pointer(free_bytes))
                free_mb = free_bytes.value / (1024 * 1024)
            else:
                import os
                stat = os.statvfs(".")
                free_mb = stat.f_bavail * stat.f_frsize / (1024 * 1024)
            
            self.components["disk_space"] = free_mb >= 100
            if not self.components["disk_space"]:
                self.messages.append(f"Low disk space: {free_mb:.2f} MB free")
        except Exception as e:
            self.components["disk_space"] = False
            self.messages.append(f"Error checking disk space: {e}")
        
        # Update overall status
        if all(self.components.values()):
            self.status = "OK"
            return True
        else:
            self.status = "ERROR"
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current health status
        
        Returns:
            Dictionary with health status information
        """
        return {
            "status": self.status,
            "version": self.version,
            "timestamp": self.last_check.isoformat(),
            "components": self.components,
            "messages": self.messages
        }


class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for health check endpoint"""
    
    def __init__(self, *args, health_status: HealthStatus, **kwargs):
        self.health_status = health_status
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/health" or self.path == "/":
            # Check health
            is_healthy = self.health_status.check_health()
            status_data = self.health_status.get_status()
            
            # Send response
            self.send_response(200 if is_healthy else 503)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(status_data).encode())
        else:
            self.send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        """Override log_message to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")


def start_health_check_server(port: int = 8080) -> Tuple[threading.Thread, HealthStatus]:
    """
    Start the health check server in a separate thread
    
    Args:
        port: Port to listen on
        
    Returns:
        Tuple of (server thread, health status object)
    """
    health_status = HealthStatus()
    
    # Create handler with health status
    handler = lambda *args, **kwargs: HealthCheckHandler(*args, health_status=health_status, **kwargs)
    
    # Create server
    server = socketserver.TCPServer(("", port), handler)
    
    # Start server in a thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    logger.info(f"Health check server started on port {port}")
    return server_thread, health_status


if __name__ == "__main__":
    # Start health check server
    thread, status = start_health_check_server()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down health check server")
        sys.exit(0)
