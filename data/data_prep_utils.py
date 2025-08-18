import re
from typing import List


def color_classifier(color_combination: str) -> str:
    """
    Using only the primary color would lead to overclassification of 
    single-colored cats when secondary colors provide important pattern information. For 
    example, a Tuxedo cat with 'Black' in the primary color column might be incorrectly 
    classified as simply 'Black' if the secondary 'White' color is ignored, when it should 
    be classified as 'Black & White / Tuxedo'.

    Hence, this function considers all primary, secondary, and tertiary colors and applies 
    hierarchical mapping rules to determine the most appropriate single category.
    
    Args:
        color_combination (str): Concatenated colour string from primary, secondary and tertiary colours separated by ' | '
            Examples:
            - "Black" <------- unary colour
            - "Black | White" 
            - "Tabby (Brown / Chocolate) | White"
            - "Seal Point | Chocolate Point"
            - "Calico | Dilute | White"
    
    Returns:
        str: Single standardized color category from Petfinder's color taxonomy.
             Possible return values include:
             - Point colors: 'Seal Point', 'Flame Point', 'Chocolate Point', etc.
             - Patterns: 'Calico', 'Dilute Calico', 'Tortoiseshell', 'Torbie', 'Smoke'
             - Combinations: 'Black & White / Tuxedo', 'Gray & White', 'Orange & White'
             - Tabby types: 'Tabby (Brown / Chocolate)', 'Tabby (Gray / Blue / Silver)', etc.
             - Solid colors: 'Black', 'Gray / Blue / Silver', 'Orange / Red', etc.
             - 'Unknown' if no colors provided or parsing fails
             - `color_combination`: if it only has unary colour.
    
    Raises:
        None: Function handles all edge cases gracefully, returning 'Unknown' for invalid input.
    
    Examples:
        >>> color_classifier("Black | White")
        'Black & White / Tuxedo'
        
        >>> color_classifier("Black | Tabby (Brown / Chocolate) | White")
        'Tabby (Brown / Chocolate)
        
        >>> color_classifier("Seal Point | White")
        'Seal Point'
    """

    # Single colour
    if '|' not in color_combination:
        return color_combination.strip()
    
    # Input validation
    if not color_combination or not isinstance(color_combination, str):
        return 'Unknown'
    
    # Split the color combination and clean up
    colors: List[str] = [color.strip() for color in color_combination.split('|')]
    
    if not colors:
        return 'Unknown'
    
    # Convert to set for faster membership testing
    color_set = set(colors)
    
    ## ====================================================
    ## Rule 1: Point colors take highest precedence
    ## ====================================================
    for color in colors:
        if 'Point' in color:
            return color
    
    ## ====================================================
    ## Rule 2: Special pattern combinations (high priority)
    ## ====================================================
    
    # Black & White / Tuxedo combinations
    if 'Black & White / Tuxedo' in color_set:
        return 'Black & White / Tuxedo'
    
    PATTERN_OVERRIDE_REGEX = re.compile(r'^(Tabby|Calico|Tortoiseshell|Torbie)\b')
    if 'Black' in color_set and 'White' in color_set:
        # Check for patterns that override Black & White
        for color in colors:
            if PATTERN_OVERRIDE_REGEX.match(color):
                return color
        return 'Black & White / Tuxedo'

    # Calico patterns (multi-color with specific combinations)
    if 'Calico' in color_combination:
        if 'Dilute' in color_combination:
            return 'Dilute Calico'
        return 'Calico'
    
    # Tortoiseshell patterns
    if 'Tortoiseshell' in color_combination:
        if 'Dilute' in color_combination:
            return 'Dilute Tortoiseshell'
        return 'Tortoiseshell'
    
    # Torbie (Tortoiseshell + Tabby)
    if ('Torbie' in colors or 
        ('Tortoiseshell' in color_combination and 'Tabby' in color_combination)):
        return 'Torbie'
    
    # Tabby patterns - return the first tabby found by order of colour type
    tabby_types: List[str] = [color for color in colors if color.startswith('Tabby')]
    if tabby_types:
        return tabby_types[0]
    
    # Smoke
    if 'Smoke' in colors:
        return 'Smoke'
    
    ## ====================================================
    ## Rule 3: Solid color + White combinations
    ## ====================================================

    SOLID_TO_WHITE_MAPPING = {
        'Gray / Blue / Silver': 'Gray & White',
        'Blue Cream': 'Gray & White',
        'Orange / Red': 'Orange & White',
        'Buff / Tan / Fawn': 'Buff & White',
        'Cream / Ivory': 'Buff & White',
        'Brown / Chocolate': 'Brown & White'
    }
    
    if 'White' in color_combination:
        for solid_color, white_combination in SOLID_TO_WHITE_MAPPING.items():
            if solid_color in color_set:
                return white_combination

    ## ====================================================
    ## Rule 4: Secondary Color takes precedence if Black is the primary colour
    ## ====================================================
    if len(colors) >= 2 and colors[0] == 'Black':
        return colors[1]

    
    ## ====================================================
    ## Rule 6: Return the primary colour (first color in the list)
    ## ====================================================
    return colors[0] if colors else 'Unknown'

