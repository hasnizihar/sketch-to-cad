# CADCraft MCP Capabilities Reference

> Discovered and verified against CADCraft CLI MCP server v0.8.0.

## 1. Server Metadata
- **Server Name**: `cadcraft`
- **Server Title**: `CADCraft`
- **Version**: `0.8.0`
- **Protocol Version**: `2024-11-05`
- **Capabilities**: `tools`, `resources`
- **Coordinate System**: Drawing units, Cartesian 2D/3D (X right, Y up, Z towards viewer).

## 2. Connection Modes
1. **Headless Mode (`cadcraft-cli mcp`)**:
   - Launches an isolated, headless CADCraft drafting engine over stdio.
   - Recommended for repeatable automated agent workflows, batch generation, and tests.
   - Independent drawing session in memory.
2. **Connected-App Mode (`cadcraft-cli mcp --connect 127.0.0.1:7979`)**:
   - Bridges to a live CADCraft desktop GUI application running with `--control 7979`.
   - Allows human visual inspection in real-time as the agent issues commands.
   - Fails if the desktop application is not open and listening.

---

## 3. Discovered MCP Tools & Exact Schemas

### 3.1 Session & File Management

#### `new_drawing`
Create a fresh in-memory drawing session.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "metric": { "type": "boolean", "description": "Create metric drawing (default is imperial)" }
    }
  }
  ```
- **Returns**: `{"index": number, "title": string}` (e.g. `Drawing2`).

#### `open`
Open an existing DXF drawing file.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "required": ["path"],
    "properties": {
      "path": { "type": "string", "description": "Absolute or relative path to DXF file" }
    }
  }
  ```

#### `save`
Save the active drawing to DXF/DWG or export to visual formats based on extension.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "path": { "type": "string", "description": "Destination file path" }
    }
  }
  ```
- **Supported Formats**:
  - `.dxf`: AutoCAD Drawing Exchange Format (text/binary DXF).
  - `.dwg`: Native DWG binary drawing.
  - `.png`: High-resolution raster preview export.
  - `.svg`: Scalable vector graphics export.
  - `.pdf`: Portable document format export.
- **Note**: When exporting `.png`, `.svg`, or `.pdf`, CADCraft performs an export without altering the active drawing's underlying path or dirty state.

---

### 3.2 Geometry & Command Execution

#### `command_line`
Type one line at the CADCraft command line, exactly like an AutoCAD prompt.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "required": ["text"],
    "properties": {
      "text": { "type": "string" }
    }
  }
  ```
- **Syntax**:
  - Supports AutoCAD standard commands and aliases (`LINE`, `L`, `PLINE`, `PL`, `RECTANG`, `REC`, `CIRCLE`, `C`, `ARC`, `OFFSET`, `TRIM`, `EXTEND`, `FILLET`, `CHAMFER`, `MOVE`, `COPY`, `ROTATE`, `SCALE`, `MIRROR`, `ARRAY`, `HATCH`, `ZOOM`, `DIMLINEAR`, etc.).
  - Spaces act as Enter: `circle 22,3 1` creates a circle centered at (22, 3) with radius 1 in a single tool call.
  - Relative coordinates: `@dx,dy`
  - Polar coordinates: `@dist<angle`
  - Keywords: `c` (close), `u` (undo), etc.
- **Returns**: Prompt buffer, command history, and output strings.

#### `script`
Run a multi-line script (identical to AutoCAD `.scr` file execution).
- **Input Schema**:
  ```json
  {
    "type": "object",
    "required": ["text"],
    "properties": {
      "text": { "type": "string" }
    }
  }
  ```
- **Syntax**: One command or input per line; blank line acts as Enter.

#### `execute`
Execute commands directly with structured JSON parameters (bypasses interactive prompts).
- **Input Schema**:
  ```json
  {
    "type": "object",
    "required": ["command"],
    "properties": {
      "command": { "type": "string" },
      "params": { "type": "object" }
    }
  }
  ```
- **Examples**:
  - Create Line: `execute(command="line", params={"points": [[0, 0], [10, 0]]})`
  - Create Circle: `execute(command="circle", params={"center": [0, 0], "radius": 5})`
  - Create Layer: `execute(command="layer.new", params={"name": "A-WALL", "color": "red", "current": true})`
  - Move Entity: `execute(command="move", params={"handles": ["10A"], "delta": [5, 0]})`
  - Zoom Extents: `execute(command="zoom", params={"mode": "extents"})`

#### `list_commands`
List available commands, aliases, parameter structures, and menu paths.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "filter": { "type": "string" }
    }
  }
  ```

#### `cancel`
Cancel any active command prompt or clear current selection (equivalent to pressing `Escape`).
- **Input Schema**: `{ "type": "object", "properties": {} }`

---

### 3.3 Inspection, Querying & Rendering

#### `inspect_drawing`
Get full architectural summary of the active drawing.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "entities": { "type": "boolean", "description": "Include full list of entities with handles and geometry" },
      "limit": { "type": "integer" }
    }
  }
  ```
- **Returns**:
  - `entityCount`: Total number of drawing entities
  - `counts`: Dict of entity counts per type (`Line`, `Polyline`, `Circle`, `Dimension`, `MText`, `Hatch`, etc.)
  - `extents`: Bounding box `[[min_x, min_y], [max_x, max_y]]`
  - `layers`: List of layer objects (`name`, `color`, `linetype`, `locked`, `frozen`, `on`)
  - `currentLayer`: Name of active layer
  - `dimStyles`, `textStyles`, `linetypes`, `blocks`, `layouts`
  - `view`: Current viewport center and height
  - `entities`: (when `entities: true`) List of entities with `handle`, `type`, `layer`, `color`, and `geometry` definitions

#### `query_entities`
Query entities filtered by type, layer, or spatial window.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "type": { "type": "string", "description": "Entity type: Line, Polyline, Circle, Dimension, etc." },
      "layer": { "type": "string", "description": "Filter by layer name" },
      "window": {
        "type": "array",
        "minItems": 2,
        "maxItems": 2,
        "items": { "type": "array", "minItems": 2, "maxItems": 2, "items": { "type": "number" } },
        "description": "[[x0, y0], [x1, y1]] bounding box"
      },
      "crossing": { "type": "boolean", "description": "If false, entity must be strictly inside window; if true, crossing is allowed" },
      "limit": { "type": "integer", "minimum": 0 },
      "offset": { "type": "integer", "minimum": 0 }
    }
  }
  ```

#### `find_text`
Search and extract texts (`TEXT`, `MTEXT`, block attributes, multileaders) across the drawing.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "contains": { "type": "string", "description": "Case-insensitive substring search" },
      "layer": { "type": "string" },
      "window": { "type": "array", "minItems": 2, "maxItems": 2, "items": { "type": "array", "minItems": 2, "maxItems": 2, "items": { "type": "number" } } },
      "limit": { "type": "integer", "minimum": 0 },
      "offset": { "type": "integer", "minimum": 0 }
    }
  }
  ```

#### `render`
Render a visual preview of the drawing directly as an image (MCP image resource).
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "fit": { "type": "boolean", "description": "Fit the entire drawing extents" },
      "path": { "type": "string", "description": "Optional local file path to write PNG file to" },
      "width": { "type": "integer", "minimum": 16 },
      "height": { "type": "integer", "minimum": 16 },
      "window": { "type": "array", "minItems": 2, "maxItems": 2, "items": { "type": "array", "minItems": 2, "maxItems": 2, "items": { "type": "number" } } }
    }
  }
  ```
- **Returns**: Image content object with `mimeType: "image/png"` and base64 image data, or saved PNG file if `path` is specified.

---

## 4. Key Limitations & Operational Rules
1. **Never guess handles**: Query handles using `inspect_drawing(entities=true)` or `query_entities` before calling modification commands (`move`, `erase`, `rotate`).
2. **Space character semantics in command_line**: Space serves as `Enter` in `command_line` text unless handled within quoted strings.
3. **Layer creation**: Use `execute(command="layer.new", params={"name": "A-WALL", "color": "1"})` or `command_line("-LAYER N A-WALL C 1 A-WALL ")`.
4. **Drawing Reset**: Always invoke `new_drawing(metric=true)` before generating a new plan so that residual entities from previous tasks do not pollute the output.
