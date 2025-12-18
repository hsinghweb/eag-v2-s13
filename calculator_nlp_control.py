"""
Direct Calculator Control using Natural Language
Simpler interface that directly uses the calculator controller
"""
from mcp_calculator_server import CalculatorController, CalculatorInstructionParser


def main():
    """Example: Control calculator with natural language"""
    print("🧮 Calculator Natural Language Control")
    print("=" * 60)
    
    # Initialize controller and parser
    calculator = CalculatorController()
    parser = CalculatorInstructionParser()
    
    # Open calculator
    print("\n🚀 Opening Calculator...")
    result = calculator.open_calculator()
    if not result.get("success"):
        print(f"❌ Failed to open calculator: {result.get('error')}")
        return
    
    print("✅ Calculator opened!")
    
    # Example instruction
    instruction = "Add 2 and 3 and then find the square of the result"
    print(f"\n📝 Instruction: {instruction}")
    
    # Parse instruction
    buttons = parser.parse(instruction)
    print(f"🔢 Parsed button sequence: {' → '.join(buttons)}")
    
    # Safety check: Ensure "=" is clicked before square/root operations
    # This ensures we get the result first
    if "square" in buttons or "√" in buttons:
        # Find the index of square/root
        square_idx = None
        for i, btn in enumerate(buttons):
            if btn in ["square", "√"]:
                square_idx = i
                break
        
        if square_idx is not None and square_idx > 0:
            # Check if "=" is before square/root
            if buttons[square_idx - 1] != "=":
                # Check if there's an operation before square
                has_operation = any(op in buttons[:square_idx] for op in ["+", "-", "×", "÷"])
                if has_operation:
                    print(f"⚠️  Adding '=' before square operation to get result first")
                    buttons.insert(square_idx, "=")
                    print(f"🔢 Updated sequence: {' → '.join(buttons)}")
    
    # Execute sequence
    print("\n🖱️ Executing clicks...")
    print("⏱️  Note: 4 second pause between clicks for visibility")
    for i, button in enumerate(buttons, 1):
        print(f"\n  {i}/{len(buttons)}. Processing '{button}'...")
        result = calculator.click_button(button)
        if result.get("success"):
            print(f"     ✅ Success")
        else:
            print(f"     ❌ Failed: {result.get('error')}")
    
    print("\n✅ Calculation complete!")
    print("👀 Check the calculator window to see the result")


if __name__ == "__main__":
    main()

