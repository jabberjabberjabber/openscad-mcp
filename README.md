# OpenSCAD MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Model Context Protocol (MCP) server that provides seamless integration between Large Language Models and OpenSCAD for collaborative 3D modeling and rapid prototyping.

## 🚀 Features

- **Natural Language to 3D Models**: Describe your design in plain English and get working OpenSCAD code
- **Live Visual Feedback**: Real-time rendering with base64 PNG images optimized for vision models
- **Instant 3D Printing**: Direct STL export ready for your 3D printer
- **Persistent Workspace**: Scratchpad maintains your work across sessions
- **Multiple Camera Views**: Inspect your models from all angles (isometric, front, back, left, right, top, bottom)
- **Error Handling**: Comprehensive error reporting and logging for debugging

## 🎯 Use Cases

- **Rapid Prototyping**: Quickly iterate on mechanical parts and assemblies
- **Educational Tools**: Learn 3D modeling through conversational interfaces
- **Parametric Design**: Generate families of related objects with simple parameter changes
- **Accessibility**: 3D modeling for users who prefer text-based interfaces
- **Automation**: Integrate 3D model generation into larger workflows

## 📋 Requirements

- **Python 3.8+**
- **OpenSCAD** (installed and accessible via command line)
- **fastmcp** library

## 🛠️ Installation

### 1. Install OpenSCAD

**Windows:**
```bash
# Download from https://openscad.org/downloads.html
# Or via Chocolatey:
choco install openscad
```

**macOS:**
```bash
brew install openscad
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install openscad
```
### 2. Clone and Run

```bash
git clone https://github.com/jabberjabberjabber/openscad-mcp
cd openscad-mcp
uv run --with fastmcp fastmcp dev main.py
```
### 3. Install

**Add this to your client's MCP config:**
```json
  "mcpServers": {
    "openscad-mcp": {
      "command": "uv",
      "args": [
		"run",
		"--with",
		"fastmcp",
		"fastmcp",
		"run",
        "c:/path/to/openscad-mcp/main.py"
      ],
      "env": {
        "OPENSCAD_WORK_DIR": "c:/path/to/openscad-mcp/"
      }
    }
    },
```

## 🎮 Usage

The server provides five main tools for 3D modeling workflows:

### Available Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `show_openscad_script` | Display current script | None |
| `create_openscad_script` | Create/update script | `script_content: str` |
| `view_render` | Render PNG image | `view: str` (optional) |
| `export_model_to_stl` | Export for 3D printing | `filename: str` |
| `save_openscad_script` | Save script to file | `filename: str` |

### Example Workflow

```python
# 1. Create a model
create_openscad_script("""
// Simple cube with rounded corners
$fn = 32;
minkowski() {
    cube([20, 20, 10], center=true);
    sphere(r=2);
}
""")

# 2. View the result
view_render("isometric")  # Returns base64 PNG

# 3. Export for printing
export_model_to_stl("rounded_cube")

# 4. Save the source
save_openscad_script("rounded_cube")
```

### Camera Views

- `isometric` (default) - 3D perspective view
- `front` - Front orthographic view  
- `back` - Back orthographic view
- `left` - Left side view
- `right` - Right side view
- `top` - Top-down view
- `bottom` - Bottom-up view

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   LLM Client    │───▶│  MCP Server      │───▶│   OpenSCAD      │
│                 │    │                  │    │   Engine        │
│ Natural Language│    │ • Script Storage │    │ • Rendering     │
│ Descriptions    │    │ • State Mgmt     │    │ • STL Export    │
│                 │◀───│ • Error Handling │◀───│ • Validation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Components

- **Persistent State**: JSON-based scratchpad for session continuity
- **OpenSCAD Integration**: Subprocess calls with timeout protection
- **Image Generation**: Base64 PNG encoding for vision model compatibility
- **File Management**: Organized output to configurable working directory
- **Error Handling**: Comprehensive logging and graceful failure modes

## 🎨 Example Projects

### Hollow Sphere (Vase Mode)
```openscad
$fn = 64;
difference() {
    sphere(r=15);      // 30mm diameter
    sphere(r=12);      // 3mm wall thickness
}
```

### Parametric Gear
```openscad
module gear(teeth=20, height=5) {
    linear_extrude(height=height) {
        for (i = [0:teeth-1]) {
            rotate([0, 0, i*360/teeth]) {
                translate([8, 0, 0]) circle(r=1);
            }
        }
        circle(r=7);
    }
}
gear(teeth=16, height=8);
```

### Customizable Bracket
```openscad
width = 30;
depth = 20; 
height = 15;
thickness = 3;

difference() {
    cube([width, depth, height]);
    translate([thickness, thickness, thickness])
        cube([width-2*thickness, depth-thickness, height]);
}
```

## ⚙️ Configuration

### Environment Variables

- `OPENSCAD_WORK_DIR`: Working directory for files (default: server directory)

### Logging

Logs are written to `openscad_mcp.log` with detailed operation information:
- Script updates and validations
- Rendering operations and timing
- Export operations and file sizes
- Error conditions and recovery

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
