"""
MCP Client for Calculator Control
Example client that uses the calculator MCP server
"""
import json
import subprocess
import sys
from pathlib import Path


class CalculatorMCPClient:
    """Client for interacting with Calculator MCP Server"""
    
    def __init__(self, server_script: str = "mcp_calculator_server.py"):
        self.server_script = server_script
        self.request_id = 1
    
    def _send_request(self, method: str, params: dict = None) -> dict:
        """Send JSON-RPC request to MCP server"""
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        self.request_id += 1
        
        # Start server process
        process = subprocess.Popen(
            [sys.executable, self.server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send request
        request_json = json.dumps(request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=30)
        
        if stderr:
            print(f"Server error: {stderr}", file=sys.stderr)
        
        try:
            response = json.loads(stdout.strip())
            return response
        except json.JSONDecodeError as e:
            return {"error": {"message": f"Failed to parse response: {e}", "stdout": stdout}}
    
    def list_tools(self) -> dict:
        """List available tools"""
        return self._send_request("tools/list")
    
    def open_calculator(self) -> dict:
        """Open calculator"""
        return self._send_request("tools/call", {
            "name": "open_calculator",
            "arguments": {}
        })
    
    def execute_calculation(self, instruction: str) -> dict:
        """Execute a natural language calculation"""
        return self._send_request("tools/call", {
            "name": "execute_calculation",
            "arguments": {
                "instruction": instruction
            }
        })
    
    def click_button(self, button: str) -> dict:
        """Click a specific button"""
        return self._send_request("tools/call", {
            "name": "click_button",
            "arguments": {
                "button": button
            }
        })


def main():
    """Example usage"""
    client = CalculatorMCPClient()
    
    print("🧮 Calculator MCP Client")
    print("=" * 50)
    
    # List available tools
    print("\n📋 Available tools:")
    tools_response = client.list_tools()
    if "tools" in tools_response:
        for tool in tools_response["tools"]:
            print(f"  - {tool['name']}: {tool['description']}")
    
    # Example: Open calculator
    print("\n🚀 Opening Calculator...")
    open_result = client.open_calculator()
    print(f"Result: {json.dumps(open_result, indent=2)}")
    
    # Example: Execute calculation
    print("\n🧮 Executing: 'Add 2 and 3 and then find the square of the result'")
    calc_result = client.execute_calculation("Add 2 and 3 and then find the square of the result")
    
    if "content" in calc_result:
        for content in calc_result["content"]:
            if content["type"] == "text":
                result_data = json.loads(content["text"])
                print(f"\n✅ Calculation Result:")
                print(f"  Instruction: {result_data.get('instruction', 'N/A')}")
                print(f"  Button Sequence: {' → '.join(result_data.get('button_sequence', []))}")
                print(f"  Success: {result_data.get('success', False)}")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()

