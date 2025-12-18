"""
Visualize FDOM nodes on screenshot with bounding boxes and labels
Helps identify which node ID corresponds to which UI element
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def visualize_fdom_nodes(fdom_path: str, output_path: str = None):
    """
    Create a visualization of all nodes from fdom.json on the screenshot
    
    Args:
        fdom_path: Path to fdom.json file
        output_path: Optional output path for the visualization
    """
    # Load fdom.json
    with open(fdom_path, 'r', encoding='utf-8') as f:
        fdom_data = json.load(f)
    
    # Get root state
    root_state = fdom_data.get('states', {}).get('root', {})
    screenshot_path = root_state.get('image')
    nodes = root_state.get('nodes', {})
    
    if not screenshot_path or not os.path.exists(screenshot_path):
        print(f"ERROR: Screenshot not found: {screenshot_path}")
        return
    
    # Load screenshot
    img = Image.open(screenshot_path)
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 12)
        font_bold = ImageFont.truetype("arial.ttf", 14)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 12)
            font_bold = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
        except:
            font = ImageFont.load_default()
            font_bold = ImageFont.load_default()
    
    # Colors for different node types
    colors = {
        'icon': (255, 0, 0),      # Red
        'text': (0, 255, 0),      # Green
        'unknown': (0, 0, 255),   # Blue
    }
    
    print(f"Visualizing {len(nodes)} nodes on screenshot...")
    
    # Draw each node
    for node_id, node_data in nodes.items():
        bbox = node_data.get('bbox', [])
        if len(bbox) != 4:
            continue
        
        x1, y1, x2, y2 = bbox
        node_type = node_data.get('type', 'unknown')
        color = colors.get(node_type, colors['unknown'])
        
        # Draw bounding box
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
        
        # Draw semi-transparent fill
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([x1, y1, x2, y2], fill=(*color, 30))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # Prepare label text
        label_parts = [node_id]
        icon_name = node_data.get('g_icon_name', '')
        if icon_name and icon_name != 'Unknown':
            label_parts.append(icon_name)
        
        label = '\n'.join(label_parts)
        
        # Calculate label position (top-left of bbox)
        label_x = x1 + 2
        label_y = y1 - 25 if y1 > 25 else y1 + 2
        
        # Get text size for background
        bbox_text = draw.textbbox((label_x, label_y), label, font=font)
        
        # Draw label background
        draw.rectangle(
            [bbox_text[0]-2, bbox_text[1]-2, bbox_text[2]+2, bbox_text[3]+2],
            fill='white',
            outline=color,
            width=1
        )
        
        # Draw label text
        draw.text((label_x, label_y), label, fill=color, font=font)
    
    # Determine output path
    if not output_path:
        screenshot_dir = os.path.dirname(screenshot_path)
        output_path = os.path.join(screenshot_dir, 'fdom_nodes_visualization.png')
    
    # Save visualization
    img.save(output_path)
    print(f"Visualization saved to: {output_path}")
    print(f"Open this image to see which node IDs correspond to which UI elements")
    
    return output_path

if __name__ == "__main__":
    # Default path
    fdom_path = "apps/calc/fdom.json"
    
    if len(os.sys.argv) > 1:
        fdom_path = os.sys.argv[1]
    
    visualize_fdom_nodes(fdom_path)

