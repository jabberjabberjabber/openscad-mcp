#!/usr/bin/env python3
"""
OpenSCAD MCP Server using fastmcp
Provides tools for creating, viewing, and exporting OpenSCAD models
"""

import asyncio
import base64
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

from fastmcp import FastMCP

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('openscad_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Server directory setup
SERVER_DIR = Path(__file__).parent
WORK_DIR = Path(os.getenv('OPENSCAD_WORK_DIR', SERVER_DIR))
WORK_DIR.mkdir(exist_ok=True)

STATE_FILE = WORK_DIR / 'scratchpad_state.json'

# Predefined camera views for OpenSCAD
CAMERA_VIEWS = {
    'isometric': '--camera=10,10,10,60,0,45,25',
    'front': '--camera=0,0,10,0,0,0,25',
    'back': '--camera=0,0,-10,0,0,180,25',
    'left': '--camera=-10,0,0,0,0,90,25',
    'right': '--camera=10,0,0,0,0,270,25',
    'top': '--camera=0,0,10,0,0,0,25',
    'bottom': '--camera=0,0,-10,0,0,0,25'
}

class OpenSCADState:
    """Manages the persistent scratchpad state"""
    
    def __init__(self):
        self.script_content = ""
        self.load_state()
    
    def load_state(self):
        """Load state from JSON file"""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    self.script_content = data.get('script_content', '')
                logger.info("State loaded from file")
            else:
                logger.info("No existing state file, starting fresh")
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            self.script_content = ""
    
    def save_state(self):
        """Save current state to JSON file"""
        try:
            data = {'script_content': self.script_content}
            with open(STATE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("State saved to file")
        except Exception as e:
            logger.error(f"Error saving state: {e}")

# Global state instance
state = OpenSCADState()

# Initialize FastMCP
mcp = FastMCP("OpenSCAD MCP Server")

@mcp.tool()
def show_openscad_script() -> str:
    """Show the current OpenSCAD script from the scratchpad"""
    try:
        if not state.script_content.strip():
            return "No script content in scratchpad"
        return f"Current OpenSCAD script:\n\n{state.script_content}"
    except Exception as e:
        logger.error(f"Error showing script: {e}")
        return f"Error retrieving script: {e}"

@mcp.tool()
def create_openscad_script(script_content: str) -> str:
    """Create or update the OpenSCAD script in the scratchpad
    
    Args:
        script_content: The OpenSCAD script content
    """
    try:
        state.script_content = script_content
        state.save_state()
        lines = len(script_content.split('\n'))
        chars = len(script_content)
        logger.info(f"Script updated: {lines} lines, {chars} characters")
        return f"OpenSCAD script updated successfully ({lines} lines, {chars} characters)"
    except Exception as e:
        logger.error(f"Error creating script: {e}")
        return f"Error updating script: {e}"

@mcp.tool()
def view_render(view: str = "isometric") -> str:
    """Render the current OpenSCAD script and return as base64 PNG
    
    Args:
        view: Camera view - options: isometric, front, back, left, right, top, bottom
    """
    try:
        if not state.script_content.strip():
            return "No script content to render"
        
        if view not in CAMERA_VIEWS:
            return f"Invalid view '{view}'. Available views: {', '.join(CAMERA_VIEWS.keys())}"
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scad', delete=False) as scad_file:
            scad_file.write(state.script_content)
            scad_path = scad_file.name
        
        png_path = scad_path.replace('.scad', '.png')
        
        try:
            # Run OpenSCAD to generate PNG
            cmd = [
                'openscad',
                CAMERA_VIEWS[view],
                '--imgsize=1024,1024',
                '--render',
                '-o', png_path,
                scad_path
            ]
            
            logger.info(f"Running OpenSCAD command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                error_msg = f"OpenSCAD error: {result.stderr}"
                logger.error(error_msg)
                return error_msg
            
            # Read and encode the PNG
            if not Path(png_path).exists():
                return "Render failed: No output file generated"
            
            with open(png_path, 'rb') as f:
                png_data = f.read()
            
            base64_data = base64.b64encode(png_data).decode('utf-8')
            
            logger.info(f"Render successful: {view} view, {len(base64_data)} bytes base64")
            return f"data:image/png;base64,{base64_data}"
            
        finally:
            # Cleanup temporary files
            for temp_path in [scad_path, png_path]:
                try:
                    if Path(temp_path).exists():
                        os.unlink(temp_path)
                except Exception as e:
                    logger.warning(f"Failed to cleanup {temp_path}: {e}")
                    
    except subprocess.TimeoutExpired:
        logger.error("OpenSCAD render timeout")
        return "Render timeout - script may be too complex"
    except Exception as e:
        logger.error(f"Error during render: {e}")
        return f"Render error: {e}"

@mcp.tool()
def export_model_to_stl(filename: str) -> str:
    """Export the current OpenSCAD script to STL file
    
    Args:
        filename: Output filename (without .stl extension)
    """
    try:
        if not state.script_content.strip():
            return "No script content to export"
        
        # Ensure filename doesn't have extension and add .stl
        filename = filename.replace('.stl', '') + '.stl'
        stl_path = WORK_DIR / filename
        
        # Create temporary SCAD file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scad', delete=False) as scad_file:
            scad_file.write(state.script_content)
            scad_path = scad_file.name
        
        try:
            # Run OpenSCAD to generate STL
            cmd = [
                'openscad',
                '--render',
                '-o', str(stl_path),
                scad_path
            ]
            
            logger.info(f"Exporting STL: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                error_msg = f"OpenSCAD export error: {result.stderr}"
                logger.error(error_msg)
                return error_msg
            
            if not stl_path.exists():
                return "Export failed: No STL file generated"
            
            file_size = stl_path.stat().st_size
            logger.info(f"STL exported successfully: {stl_path} ({file_size} bytes)")
            return f"STL exported successfully to {stl_path} ({file_size} bytes)"
            
        finally:
            # Cleanup temporary SCAD file
            try:
                if Path(scad_path).exists():
                    os.unlink(scad_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup {scad_path}: {e}")
                
    except subprocess.TimeoutExpired:
        logger.error("OpenSCAD export timeout")
        return "Export timeout - script may be too complex"
    except Exception as e:
        logger.error(f"Error during export: {e}")
        return f"Export error: {e}"

@mcp.tool()
def save_openscad_script(filename: str) -> str:
    """Save the current OpenSCAD script to a file
    
    Args:
        filename: Output filename (without .scad extension)
    """
    try:
        if not state.script_content.strip():
            return "No script content to save"
        
        # Ensure filename doesn't have extension and add .scad
        filename = filename.replace('.scad', '') + '.scad'
        script_path = WORK_DIR / filename
        
        with open(script_path, 'w') as f:
            f.write(state.script_content)
        
        lines = len(state.script_content.split('\n'))
        logger.info(f"Script saved: {script_path} ({lines} lines)")
        return f"Script saved to {script_path} ({lines} lines)"
        
    except Exception as e:
        logger.error(f"Error saving script: {e}")
        return f"Save error: {e}"

def main():
    """Run the MCP server"""
    logger.info("Starting OpenSCAD MCP Server")
    logger.info(f"Working directory: {WORK_DIR}")
    logger.info(f"State file: {STATE_FILE}")
    
    # Test OpenSCAD availability
    try:
        result = subprocess.run(['openscad', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info("OpenSCAD is available")
        else:
            logger.warning("OpenSCAD may not be properly installed")
    except Exception as e:
        logger.error(f"OpenSCAD not found: {e}")
    
    # Run the server
    mcp.run()

if __name__ == "__main__":
    main()
