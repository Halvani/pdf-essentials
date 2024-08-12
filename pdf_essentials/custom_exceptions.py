class InvalidColorNameError(Exception):
    """
    Custom exception raised when an invalid human-readable color name is provided.

    Args:
        color_name (str): The invalid color name that caused the exception.

    Attributes:
        message (str): Explanation of the error, including the invalid color name.
    """

    def __init__(self, color_name: str):
        super().__init__(f"'{color_name}' is not a valid color name. Please use a standard color name (e.g., 'red', 'blue', 'green').")
