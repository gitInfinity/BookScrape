import re

def normalise_price(price_text: str) -> float:
    """Convert price text to a float value in GBP."""
    match = re.search(r"£(\d+\.\d{2})", price_text)
    if not match:
        raise ValueError(f"Price text does not match expected format: {price_text}")
    return float(match.group(1))