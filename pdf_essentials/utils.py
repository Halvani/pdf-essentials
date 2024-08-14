import matplotlib.colors as mcolors
from typing import Union

from .custom_exceptions import InvalidColorNameError


def convert_to_rgb(color: Union[str, tuple[int, int, int]]) -> tuple[float, float, float]:
    """
    Converts a color to an RGB tuple in normalized float values.

    Args:
        color (Union[str, tuple[int, int, int]]): The color to convert. It can be in hex format, human-readable color name, or an RGB tuple.

    Returns:
        tuple[float, float, float]: The color in RGB format as a tuple of floats (0 to 1 range).
    """
    if isinstance(color, str):
        # Convert named or hex color to RGB
        rgb = mcolors.to_rgb(color)
        return rgb  # Returns as normalized floats (0 to 1)
    elif isinstance(color, tuple) and len(color) == 3:
        # If already an RGB tuple, normalize the values to 0-1 range
        return tuple(c / 255 for c in color)
    else:
        raise ValueError(f"Invalid color format: {color}")

