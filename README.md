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

### 2. Install Python Dependencies

```bash
pip install fastmcp
```

### 3. Clone and Run

```bash
git clone https://github.com/yourusername/openscad-mcp-server.git
cd openscad-mcp-server
python openscad_mcp_server.py
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

## 🐛 Troubleshooting

### Common Issues

**OpenSCAD not found:**
```bash
# Verify OpenSCAD is in PATH
openscad --version
```

**Render timeout:**
- Reduce model complexity
- Decrease `$fn` value for faster rendering
- Check for infinite loops in recursive modules

**STL export fails:**
- Ensure model is manifold (watertight)
- Check for overlapping geometry
- Verify valid OpenSCAD syntax

**Permission errors:**
- Check write permissions in working directory
- Ensure OpenSCAD can create temporary files

## 🤝 Contributing

We welcome contributions! Please feel free to:

- 🐛 Report bugs via GitHub Issues
- 💡 Suggest new features or improvements  
- 🔧 Submit pull requests with enhancements
- 📖 Improve documentation and examples
- 🧪 Add test cases and validation

### Development Setup

```bash
git clone https://github.com/yourusername/openscad-mcp-server.git
cd openscad-mcp-server

# Install dependencies
pip install fastmcp

# Run tests
python -m pytest tests/

# Start development server
python openscad_mcp_server.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenSCAD](https://openscad.org/) - The powerful 3D modeling engine that makes this possible
- [FastMCP](https://github.com/jlowin/fastmcp) - Simple and elegant MCP server framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - Enabling seamless AI tool integration

## 🔗 Links

- [OpenSCAD Documentation](https://openscad.org/documentation.html)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [3D Printing Guide](https://www.printables.com/model/123456-getting-started-with-3d-printing)

---

**Ready to turn your ideas into 3D reality? Start describing and start creating!** 🎯