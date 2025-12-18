"""
Test button matching to debug the + button issue
"""
import json
from pathlib import Path

# Load fdom.json
fdom_path = Path("apps/calc/fdom.json")
with open(fdom_path, 'r', encoding='utf-8') as f:
    fdom_data = json.load(f)

state = fdom_data.get("states", {}).get("root", {})
nodes = state.get("nodes", {})

# Test finding the + button
print("Testing button matching for '+'")
print("=" * 60)

# Show all buttons that contain "+"
print("\nButtons containing '+':")
for node_id, node_data in nodes.items():
    icon_name = node_data.get("g_icon_name", "").lower()
    brief = node_data.get("g_brief", "").lower()
    if "+" in icon_name or "+" in brief:
        print(f"  {node_id}: {node_data.get('g_icon_name', '')} - {node_data.get('g_brief', '')}")

# Test the matching logic
print("\nTesting matching logic:")
name = "+"
name_lower = name.lower().strip()

button_mappings = {
    "+": ["+ button", "addition"],
}

if name_lower in button_mappings:
    patterns = button_mappings[name_lower]
    print(f"Patterns to match: {patterns}")
    
    # Test new logic for +
    if name_lower == "+":
        print("\nUsing new logic for '+' button:")
        for node_id, node_data in nodes.items():
            icon_name = node_data.get("g_icon_name", "").lower()
            brief = node_data.get("g_brief", "").lower()
            # Check for exact "+ button" match (starts with +)
            if icon_name.startswith("+ button") or (icon_name == "+ button" or "addition" in brief):
                # Make sure it's not M+ Button
                if not icon_name.startswith("m"):
                    print(f"MATCH: {name} -> {node_id}")
                    print(f"   Icon name: {node_data.get('g_icon_name', '')}")
                    print(f"   Brief: {node_data.get('g_brief', '')}")
                    print(f"   Bbox: {node_data.get('bbox', [])}")
    else:
        # Old logic for other buttons
        for node_id, node_data in nodes.items():
            icon_name = node_data.get("g_icon_name", "").lower()
            brief = node_data.get("g_brief", "").lower()
            for pattern in patterns:
                if pattern in icon_name or pattern in brief:
                    print(f"MATCH: {name} -> {node_id}")
                    print(f"   Icon name: {node_data.get('g_icon_name', '')}")
                    print(f"   Brief: {node_data.get('g_brief', '')}")
                    print(f"   Bbox: {node_data.get('bbox', [])}")
                    break

