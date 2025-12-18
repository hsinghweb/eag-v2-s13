# Calculator MCP Server & Client

This system allows you to control Windows Calculator using natural language instructions through an MCP (Model Context Protocol) server.

## Features

- 🧮 **Natural Language Control**: Give instructions like "Add 2 and 3 and then find the square of the result"
- 🖱️ **Visual Execution**: All clicks are visible on screen in real-time
- 📋 **FDOM Integration**: Uses the `apps/calc/fdom.json` file to know exact button positions
- 🔧 **MCP Protocol**: Standard MCP server/client architecture

## Files

- `mcp_calculator_server.py` - MCP server with calculator control tools
- `mcp_calculator_client.py` - MCP client example
- `calculator_nlp_control.py` - Direct usage (simpler, no MCP overhead)

## Quick Start

### Option 1: Direct Usage (Simplest)

```bash
python calculator_nlp_control.py
```

This will:
1. Open Windows Calculator
2. Parse the instruction: "Add 2 and 3 and then find the square of the result"
3. Execute the clicks: 2 → + → 3 → = → square
4. Show the result on screen

### Option 2: MCP Client

```bash
python mcp_calculator_client.py
```

### Option 3: Custom Instruction

Edit `calculator_nlp_control.py` and change the instruction:

```python
instruction = "Multiply 5 by 7"
# or
instruction = "Divide 100 by 4"
# or
instruction = "Add 10 and 20 and then find the square root"
```

## Supported Instructions

### Basic Operations
- "Add 2 and 3" → Clicks: 2, +, 3, =
- "Subtract 10 from 20" → Clicks: 20, -, 10, =
- "Multiply 5 by 7" → Clicks: 5, ×, 7, =
- "Divide 100 by 4" → Clicks: 100, ÷, 4, =

### Complex Operations
- "Add 2 and 3 and then find the square of the result" → Clicks: 2, +, 3, =, square
- "Multiply 4 by 5 and then find the square root" → Clicks: 4, ×, 5, =, √

### Number Formats
- Supports both digits ("2", "3") and words ("two", "three")
- Supports multi-digit numbers ("25", "100")

## MCP Server Tools

The MCP server exposes three tools:

1. **open_calculator** - Opens Windows Calculator
2. **execute_calculation** - Executes a natural language instruction
3. **click_button** - Clicks a specific button by name

## How It Works

1. **FDOM Loading**: Loads `apps/calc/fdom.json` which contains all button positions
2. **Natural Language Parsing**: Parses instructions like "Add 2 and 3" into button sequences
3. **Button Mapping**: Maps button names to node IDs using `g_icon_name` and `g_brief` fields
4. **Coordinate Calculation**: Calculates absolute screen coordinates from bbox + window position
5. **Click Execution**: Uses Windows GUI API to click buttons visually

## Example Usage in Code

```python
from mcp_calculator_server import CalculatorController, CalculatorInstructionParser

# Initialize
calculator = CalculatorController()
parser = CalculatorInstructionParser()

# Open calculator
calculator.open_calculator()

# Parse and execute
instruction = "Add 2 and 3 and then find the square of the result"
buttons = parser.parse(instruction)

for button in buttons:
    calculator.click_button(button)
```

## Requirements

- Windows OS (uses Windows Calculator)
- Python 3.8+
- Dependencies from the main project (fdom, gui_controller, etc.)
- `apps/calc/fdom.json` file (already created)

## Troubleshooting

### Calculator doesn't open
- Make sure `calc.exe` is available in Windows PATH
- Check that no other instance is blocking

### Buttons not clicking correctly
- Verify `apps/calc/fdom.json` exists and is valid
- Check that calculator window is visible and not minimized
- Ensure window position detection is working

### Parsing errors
- Use simple, clear instructions
- Supported operations: add, subtract, multiply, divide, square, square root
- Use digits (2, 3) or words (two, three)

## Architecture

```
User Instruction
    ↓
CalculatorInstructionParser.parse()
    ↓
Button Sequence ["2", "+", "3", "=", "square"]
    ↓
CalculatorController.click_button() for each
    ↓
Find node ID from fdom.json
    ↓
Calculate absolute coordinates
    ↓
Windows GUI API click
    ↓
Visible on screen!
```

## Future Enhancements

- Support for more complex expressions
- Memory operations (MC, MR, M+, etc.)
- History navigation
- Error handling and validation
- Support for scientific calculator mode

