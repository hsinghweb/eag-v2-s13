"""
MCP Server for Calculator Control
Exposes tools to control Windows Calculator using natural language instructions
"""
import json
import re
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys
import os

# Add utils to path
project_root = Path(__file__).parent
fdom_path = project_root / "utils" / "fdom"
utils_path = project_root / "utils"

if str(fdom_path) not in sys.path:
    sys.path.insert(0, str(fdom_path))
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

# Import modules
from app_controller import AppController
from config_manager import ConfigManager
from screen_manager import ScreenManager
from gui_controller import SimpleWindowAPI


class CalculatorController:
    """Controls Windows Calculator using fdom.json"""
    
    def __init__(self, fdom_path: str = "apps/calc/fdom.json"):
        self.fdom_path = Path(fdom_path)
        self.fdom_data = None
        self.app_controller = None
        self.gui_api = SimpleWindowAPI()
        self.window_id = None
        self.window_pos = None
        self._load_fdom()
        
    def _load_fdom(self):
        """Load fdom.json file"""
        try:
            with open(self.fdom_path, 'r', encoding='utf-8') as f:
                self.fdom_data = json.load(f)
            print(f"✅ Loaded fdom.json with {len(self.fdom_data.get('states', {}).get('root', {}).get('nodes', {}))} nodes")
        except Exception as e:
            print(f"❌ Error loading fdom.json: {e}")
            raise
    
    def _find_node_by_name(self, name: str, state_id: str = "root") -> Optional[str]:
        """Find node ID by button name (e.g., '2', '+', '=')"""
        state = self.fdom_data.get("states", {}).get(state_id, {})
        nodes = state.get("nodes", {})
        
        # Normalize name for matching
        name_lower = name.lower().strip()
        
        for node_id, node_data in nodes.items():
            icon_name = node_data.get("g_icon_name", "").lower()
            brief = node_data.get("g_brief", "").lower()
            
            # Match by exact button name
            if name_lower in icon_name or name_lower in brief:
                # Check for specific patterns
                if name_lower == "2" and "2 button" in icon_name:
                    return node_id
                elif name_lower == "3" and "3 button" in icon_name:
                    return node_id
                elif name_lower == "+" and ("+ button" in icon_name or "addition" in brief):
                    return node_id
                elif name_lower == "=" and ("= button" in icon_name or "equals" in brief):
                    return node_id
                elif name_lower == "square" and ("x²" in icon_name or "square" in brief):
                    return node_id
                elif name_lower in ["×", "*", "multiply"] and ("×" in icon_name or "multiplication" in brief):
                    return node_id
                elif name_lower in ["÷", "/", "divide"] and ("÷" in icon_name or "division" in brief):
                    return node_id
                elif name_lower == "-" and ("-" in icon_name or "minus" in brief or "subtract" in brief):
                    return node_id
                elif name_lower.isdigit() and f"{name_lower} button" in icon_name:
                    return node_id
        
        return None
    
    def open_calculator(self) -> Dict[str, Any]:
        """Open Windows Calculator"""
        try:
            # Check if calculator is already open
            window_id = self.gui_api.find_window("calculator")
            if window_id:
                print("✅ Calculator already open")
                self.window_id = window_id
                self._update_window_position()
                return {"success": True, "message": "Calculator already open", "window_id": window_id}
            
            # Launch calculator
            print("🚀 Launching Calculator...")
            config = ConfigManager()
            screen_manager = ScreenManager(config)
            
            # Use calc.exe (Windows built-in)
            self.app_controller = AppController(
                app_path="calc.exe",
                target_screen=1,
                config=config
            )
            self.app_controller.screen_manager = screen_manager
            
            result = self.app_controller.launch_app()
            
            if result.get("success"):
                self.window_id = result["app_info"]["window_id"]
                time.sleep(2)  # Wait for window to stabilize
                self._update_window_position()
                return {"success": True, "message": "Calculator opened", "window_id": self.window_id}
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_window_position(self):
        """Update window position for click calculations"""
        if not self.window_id:
            return
        
        window_info = self.gui_api.get_window_info(self.window_id)
        if window_info:
            pos = window_info['window_data']['position']
            self.window_pos = {'left': pos['x'], 'top': pos['y']}
        else:
            # Fallback: try to find window again
            self.window_id = self.gui_api.find_window("calculator")
            if self.window_id:
                self._update_window_position()
    
    def click_button(self, button_name: str) -> Dict[str, Any]:
        """Click a calculator button by name"""
        try:
            if not self.window_id:
                result = self.open_calculator()
                if not result.get("success"):
                    return result
            
            # Find node ID for the button
            node_id = self._find_node_by_name(button_name)
            if not node_id:
                return {"success": False, "error": f"Button '{button_name}' not found"}
            
            # Get node data from fdom
            state = self.fdom_data.get("states", {}).get("root", {})
            node_data = state.get("nodes", {}).get(node_id)
            
            if not node_data:
                return {"success": False, "error": f"Node data not found for {node_id}"}
            
            # Update window position
            self._update_window_position()
            if not self.window_pos:
                return {"success": False, "error": "Could not get window position"}
            
            # Calculate absolute coordinates
            bbox = node_data.get("bbox", [])
            if len(bbox) != 4:
                return {"success": False, "error": f"Invalid bbox for {node_id}"}
            
            x1, y1, x2, y2 = bbox
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            abs_x = self.window_pos['left'] + center_x
            abs_y = self.window_pos['top'] + center_y
            
            # Focus window first
            self.gui_api.focus_window(self.window_id)
            time.sleep(0.2)
            
            # Click the button
            print(f"🖱️ Clicking {button_name} ({node_id}) at ({abs_x}, {abs_y})")
            success = self.gui_api.click(abs_x, abs_y)
            
            if success:
                time.sleep(0.5)  # Wait for UI to update
                return {"success": True, "message": f"Clicked {button_name}", "node_id": node_id}
            else:
                return {"success": False, "error": f"Failed to click {button_name}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


class CalculatorInstructionParser:
    """Parses natural language calculator instructions"""
    
    def __init__(self):
        self.number_map = {
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
        }
        self.operation_map = {
            "add": "+", "plus": "+", "addition": "+",
            "subtract": "-", "minus": "-", "subtraction": "-",
            "multiply": "×", "times": "×", "multiplication": "×",
            "divide": "÷", "division": "÷",
            "equals": "=", "equal": "=",
            "square": "square", "squared": "square",
            "square root": "√", "sqrt": "√"
        }
    
    def parse(self, instruction: str) -> List[str]:
        """Parse natural language instruction into sequence of button clicks"""
        instruction = instruction.lower().strip()
        buttons = []
        
        # Replace word numbers with digits
        for word, digit in self.number_map.items():
            instruction = re.sub(rf'\b{word}\b', digit, instruction)
        
        # Handle "then" clauses - split into parts
        if "then" in instruction:
            parts = instruction.split("then")
            first_part = parts[0].strip()
            second_part = " then ".join(parts[1:]).strip()
            
            # Parse first part recursively
            first_buttons = self._parse_single_operation(first_part)
            buttons.extend(first_buttons)
            
            # Parse second part (operates on result)
            if "square" in second_part and "root" not in second_part:
                buttons.append("square")
            elif "square root" in second_part or "sqrt" in second_part or "√" in second_part:
                buttons.append("√")
            elif "find" in second_part and "square" in second_part:
                # "find the square of the result"
                buttons.append("square")
            else:
                # Try to parse as another operation
                second_buttons = self._parse_single_operation(second_part)
                buttons.extend(second_buttons)
        else:
            # Single operation
            buttons = self._parse_single_operation(instruction)
        
        return buttons
    
    def _parse_single_operation(self, instruction: str) -> List[str]:
        """Parse a single operation (no 'then' clauses)"""
        buttons = []
        
        # Find all numbers (including multi-digit)
        numbers = re.findall(r'\d+', instruction)
        
        # Determine operation
        operation = None
        if "add" in instruction or "plus" in instruction:
            operation = "+"
        elif "subtract" in instruction or "minus" in instruction:
            operation = "-"
        elif "multiply" in instruction or "times" in instruction or "by" in instruction:
            # "multiply 5 by 7" or "5 times 7"
            operation = "×"
        elif "divide" in instruction:
            operation = "÷"
        
        # Handle "and" keyword - typically means two operands
        # "add 2 and 3" -> 2, +, 3
        if "and" in instruction and operation:
            # Split by "and" to get operands
            parts = re.split(r'\band\b', instruction)
            if len(parts) >= 2:
                # Extract numbers from each part
                left_numbers = re.findall(r'\d+', parts[0])
                right_numbers = re.findall(r'\d+', parts[1])
                
                if left_numbers and right_numbers:
                    # Click left number
                    for digit in left_numbers[0]:
                        buttons.append(digit)
                    # Add operation
                    buttons.append(operation)
                    # Click right number
                    for digit in right_numbers[0]:
                        buttons.append(digit)
                    # Add equals
                    buttons.append("=")
                    return buttons
        
        # Build button sequence (fallback to original logic)
        if operation and len(numbers) >= 2:
            # For multi-digit numbers, click each digit
            for i, num_str in enumerate(numbers):
                for digit in num_str:
                    buttons.append(digit)
                if i < len(numbers) - 1:  # Add operation between numbers
                    buttons.append(operation)
            buttons.append("=")  # Add equals at the end
        elif len(numbers) == 1:
            # Single number - click each digit
            for digit in numbers[0]:
                buttons.append(digit)
            # Check if there's an operation on this single number
            if "square" in instruction and "root" not in instruction:
                buttons.append("square")
            elif "square root" in instruction or "sqrt" in instruction:
                buttons.append("√")
        elif not numbers and "square" in instruction:
            # Just square operation (on existing result)
            buttons.append("square")
        elif not numbers and ("square root" in instruction or "sqrt" in instruction):
            buttons.append("√")
        
        return buttons


# MCP Server Implementation
class CalculatorMCPServer:
    """MCP Server for Calculator Control"""
    
    def __init__(self):
        self.calculator = CalculatorController()
        self.parser = CalculatorInstructionParser()
    
    def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        if method == "tools/list":
            return {
                "tools": [
                    {
                        "name": "open_calculator",
                        "description": "Opens Windows Calculator application",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "execute_calculation",
                        "description": "Executes a natural language calculation instruction (e.g., 'Add 2 and 3 and then find the square of the result')",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "instruction": {
                                    "type": "string",
                                    "description": "Natural language instruction for the calculation"
                                }
                            },
                            "required": ["instruction"]
                        }
                    },
                    {
                        "name": "click_button",
                        "description": "Clicks a specific calculator button",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "button": {
                                    "type": "string",
                                    "description": "Button name (e.g., '2', '+', '=', 'square')"
                                }
                            },
                            "required": ["button"]
                        }
                    }
                ]
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "open_calculator":
                result = self.calculator.open_calculator()
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }]
                }
            
            elif tool_name == "execute_calculation":
                instruction = arguments.get("instruction", "")
                if not instruction:
                    return {
                        "content": [{
                            "type": "text",
                            "text": json.dumps({"success": False, "error": "No instruction provided"}, indent=2)
                        }]
                    }
                
                # Parse instruction
                buttons = self.parser.parse(instruction)
                
                # Open calculator if not open
                open_result = self.calculator.open_calculator()
                if not open_result.get("success"):
                    return {
                        "content": [{
                            "type": "text",
                            "text": json.dumps(open_result, indent=2)
                        }]
                    }
                
                # Execute button sequence
                results = []
                for button in buttons:
                    result = self.calculator.click_button(button)
                    results.append({"button": button, "result": result})
                    time.sleep(0.3)  # Small delay between clicks
                
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps({
                            "success": True,
                            "instruction": instruction,
                            "button_sequence": buttons,
                            "results": results
                        }, indent=2)
                    }]
                }
            
            elif tool_name == "click_button":
                button = arguments.get("button", "")
                if not button:
                    return {
                        "content": [{
                            "type": "text",
                            "text": json.dumps({"success": False, "error": "No button provided"}, indent=2)
                        }]
                    }
                
                result = self.calculator.click_button(button)
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }]
                }
        
        return {"error": {"code": -32601, "message": "Method not found"}}


def main():
    """Run MCP server (stdio mode)"""
    import sys
    
    server = CalculatorMCPServer()
    
    # Read from stdin, write to stdout
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get("method", "")
            params = request.get("params", {})
            
            response = server.handle_request(method, params)
            response["id"] = request.get("id")
            response["jsonrpc"] = "2.0"
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()

