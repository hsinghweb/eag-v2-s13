"""
Test the parser to verify it adds = correctly
"""
from mcp_calculator_server import CalculatorInstructionParser

parser = CalculatorInstructionParser()

# Test the instruction
instruction = "Add 2 and 3 and then find the square of the result"
print(f"Instruction: {instruction}")
print("=" * 60)

buttons = parser.parse(instruction)
print(f"\nParsed button sequence: {buttons}")
print(f"Sequence: {' → '.join(buttons)}")

# Verify the sequence
expected = ["2", "+", "3", "=", "square"]
print(f"\nExpected sequence: {expected}")
print(f"Expected: {' → '.join(expected)}")

if buttons == expected:
    print("\n✅ Parser is correct!")
else:
    print("\n❌ Parser output doesn't match expected!")
    print(f"Missing: {set(expected) - set(buttons)}")
    print(f"Extra: {set(buttons) - set(expected)}")

