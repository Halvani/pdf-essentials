import webcolors
import colorsys

import custom_exceptions


def convert_to_rgb(color_input: str | tuple[int, ...]) -> list[int]:
    """
    Convert various color formats to an RGB list.

    This function handles conversion from several color formats, including:
    - RGB tuple (already in RGB format)
    - Hexadecimal color codes (both 3-digit and 6-digit)
    - Human-readable color names (e.g., "red", "blue", "green")
    - CMYK tuple (Cyan, Magenta, Yellow, Black)
    - HSL tuple (Hue, Saturation, Lightness)

    Args:
        color_input (str or tuple): The input color in various formats:
            - RGB tuple (e.g., (255, 0, 0))
            - Hex string (e.g., "#FF0000" or "#F00")
            - Human-readable color name (e.g., "red")
            - CMYK tuple (e.g., (0, 1, 1, 0))
            - HSL tuple (e.g., (0.0, 1.0, 0.5))

    Returns:
        list[int]: A list of three integers representing the RGB values [R, G, B].

    Raises:
        InvalidColorNameError: If an invalid human-readable color name is provided.

    Example:
        convert_to_rgb("#FF0000") # Returns: [255, 0, 0]
        convert_to_rgb("red")     # Returns: [255, 0, 0]
        convert_to_rgb((0, 1, 1, 0)) # Returns: [255, 0, 0]
    """
    
    # If it's already in RGB format (tuple of 3 values)
    if isinstance(color_input, tuple) and len(color_input) == 3:
        return list(color_input)

    # Convert from hex format (#RRGGBB or #RGB)
    if isinstance(color_input, str):
        # Handle 6-digit hex
        if color_input.startswith("#") and len(color_input) == 7:
            return [int(color_input[i:i+2], 16) for i in (1, 3, 5)]
        
        # Handle 3-digit hex
        if color_input.startswith("#") and len(color_input) == 4:
            return [int(color_input[i]*2, 16) for i in (1, 2, 3)]

        # Convert human-readable color names to RGB
        try:
            return list(webcolors.name_to_rgb(color_input))
        except ValueError:
            raise custom_exceptions.InvalidColorNameError(color_input)

    # Convert CMYK to RGB
    if isinstance(color_input, tuple) and len(color_input) == 4:
        c, m, y, k = color_input
        r = 255 * (1 - c) * (1 - k)
        g = 255 * (1 - m) * (1 - k)
        b = 255 * (1 - y) * (1 - k)
        return [int(r), int(g), int(b)]
    
    # Convert HSL to RGB
    if isinstance(color_input, tuple) and len(color_input) == 3 and isinstance(color_input[0], float):
        h, s, l = color_input
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return [int(r * 255), int(g * 255), int(b * 255)]
    
    # If the color format is unrecognized, default to black
    return [0, 0, 0]
