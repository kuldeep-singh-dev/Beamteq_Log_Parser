# Conversion helper functions
def mm_to_feet(mm: float) -> float:
    """Convert millimeters to linear feet."""
    inches = mm / 25.4
    feet = inches / 12
    return round(feet, 3)

def mm_to_inches(mm: float) -> float:
    """Convert millimeters to inches."""
    return round(mm / 25.4, 2)
