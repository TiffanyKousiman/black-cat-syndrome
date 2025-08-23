import re
from typing import List
import pandas as pd
import re
from collections import defaultdict


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

# test colour classifier
def test_color_mapping(df):
    """Test the mapping function with sample data"""

    MULTI_COLOR_DATA = df[df['color_str'].str.contains(r'\|')]['color_str'].unique()
    
    test_cases = MULTI_COLOR_DATA
    
    for test_case in test_cases:
        result = color_classifier(test_case)
        print(f"{test_case:<100} -> {result}")


def print_color_comparison(df, original_col_to_compare='colors_primary'):
    """
    Helper function to print colour distribution after standardisation and imputation methods are applied
    to the dataset.
    """
    print(f"Color Distribution Comparison: {original_col_to_compare} vs Cleaned vs After Imputation")
    print("=" * 120)
    
    # Get value counts and percentages for both columns
    original_counts = df[original_col_to_compare].value_counts()
    original_pcts = df[original_col_to_compare].value_counts(normalize=True) * 100
    
    cleaned_counts = df['cleaned_color'].value_counts()
    cleaned_pcts = df['cleaned_color'].value_counts(normalize=True) * 100

    # after imputation
    final_counts = df['final_color'].value_counts()
    final_pcts = df['final_color'].value_counts(normalize=True) * 100
    
    # Get all unique colors from both columns
    all_colors = set(original_counts.index) | set(cleaned_counts.index) | set(final_counts.index)
    
    print(f"{'Color':<30} {'Original Count':<15} {'Original %':<12} {'Cleaned Count':<15} {'Cleaned %':<12} {'Final Count (after impute)':<25} {'Final %':<12}")
    print("-" * 120)
    
    # Sort by final color count (descending)
    sorted_colors = sorted(all_colors, key=lambda x: final_counts.get(x, 0), reverse=True)
    
    for color in sorted_colors:
        original_count = original_counts.get(color, 0)
        original_pct = original_pcts.get(color, 0)
        cleaned_count = cleaned_counts.get(color, 0)
        cleaned_pct = cleaned_pcts.get(color, 0)
        final_count = final_counts.get(color, 0)
        final_pct = final_pcts.get(color, 0)
        
        print(f"{color:<30} {original_count:<15} {original_pct:<12.1f} {cleaned_count:<15} {cleaned_pct:<12.1f} {final_count:<25} {final_pct:<12.1f}")


class CatColorImputer:
    def __init__(self):
        """
        A class for imputing cat colors based on hierarchical matching rules.

        Attributes:
            multicolor_keywords (Dict[str, Dict]): Rules for identifying multicolor patterns.
            tabby_keywords (Dict[str, Dict]): Rules for identifying tabby patterns.
            point_keywords (Dict[str, List[str]]): Keywords for identifying point patterns.
            solid_keywords (Dict[str, List[str]]): Keywords for identifying solid colors.
        """
        # Level 1: Multi-color/pattern keywords (highest priority)
        self.multicolor_keywords = {
            'Black & White / Tuxedo': {
                'required_all': [
                    # Must contain indicators of BOTH black AND white
                    ['black', 'white'], ['tuxedo'], ['tux'], 
                    ['black and white'], ['black & white'], ['b&w'], ['bw'],
                    ['black/white'], ['black-white'], ['cow cat'], ['cow pattern']
                ],
                'required_any': [
                    'black with white', 'white with black', 'black markings white',
                    'white markings black', 'black patches white', 'white patches black',
                    'tuxedo pattern', 'formal wear', 'dressed up', 'black bib',
                    'white bib', 'white chest black', 'white paws black', 
                    'white socks black', 'white mittens black', 'black mask white',
                    'masked black white', 'bicolor black white'
                ],
                'exclude_if_present': ['tabby', 'striped', 'calico', 'tortie', 'tortoiseshell']
            },
            
            'Orange & White': {
                'required_all': [
                    ['orange', 'white'], ['ginger', 'white'], ['red', 'white'],
                    ['orange and white'], ['orange & white'], ['o&w'],
                    ['orange/white'], ['orange-white'], ['ginger and white'],
                    ['ginger & white'], ['red and white'], ['red & white']
                ],
                'required_any': [
                    'orange with white', 'white with orange', 'ginger with white',
                    'white with ginger', 'red with white', 'white with red',
                    'orange markings white', 'white markings orange',
                    'orange patches white', 'white patches orange',
                    'bicolor orange', 'orange bicolor', 'creamsicle'
                ],
                'exclude_if_present': ['tabby', 'striped', 'calico', 'tortie']
            },
            
            'Gray & White': {
                'required_all': [
                    ['gray', 'white'], ['grey', 'white'], ['blue', 'white'],
                    ['silver', 'white'], ['gray and white'], ['grey and white'],
                    ['gray & white'], ['grey & white'], ['g&w'],
                    ['blue and white'], ['blue & white'], ['silver and white']
                ],
                'required_any': [
                    'gray with white', 'grey with white', 'white with gray',
                    'white with grey', 'blue with white', 'white with blue',
                    'silver with white', 'white with silver',
                    'gray markings white', 'grey markings white',
                    'bicolor gray', 'bicolor grey', 'blue bicolor'
                ],
                'exclude_if_present': ['tabby', 'striped', 'calico', 'tortie']
            },
            
            'Buff & White': {
                'required_all': [
                    ['buff', 'white'], ['tan', 'white'], ['fawn', 'white'],
                    ['beige', 'white'], ['buff and white'], ['tan and white'],
                    ['fawn and white'], ['beige and white']
                ],
                'required_any': [
                    'buff with white', 'tan with white', 'fawn with white',
                    'white with buff', 'white with tan', 'white with fawn',
                    'bicolor buff', 'bicolor tan', 'buff bicolor'
                ],
                'exclude_if_present': ['tabby', 'striped', 'calico', 'tortie']
            },
            
            'Calico': {
                'required_any': [
                    'calico', 'callie', 'cali', 'tri-color', 'tricolor',
                    'tri color', 'three color', 'three-color', 'patches',
                    'patchwork', 'calico pattern', 'calico markings'
                ],
                'required_all': [],
                'exclude_if_present': ['dilute calico', 'muted calico', 'soft calico']
            },
            
            'Dilute Calico': {
                'required_any': [
                    'dilute calico', 'muted calico', 'soft calico', 'pastel calico',
                    'light calico', 'pale calico', 'subtle calico', 'faded calico',
                    'diluted tricolor', 'dilute tri-color', 'dilute patches'
                ],
                'required_all': [],
                'exclude_if_present': []
            },
            
            'Tortoiseshell': {
                'required_any': [
                    'tortoiseshell', 'tortie', 'tort', 'tortoise shell',
                    'tortoise-shell', 'torty', 'torti', 'brindle', 'mottled',
                    'tortoiseshell pattern', 'tortie pattern'
                ],
                'required_all': [],
                'exclude_if_present': ['dilute tortie', 'dilute tortoiseshell', 'tabby tortie', 'torbie']
            },
            
            'Dilute Tortoiseshell': {
                'required_any': [
                    'dilute tortoiseshell', 'dilute tortie', 'dilute tort',
                    'muted tortoiseshell', 'soft tortie', 'pastel tortoiseshell',
                    'blue cream tortie', 'blue and cream', 'blue & cream'
                ],
                'required_all': [],
                'exclude_if_present': ['tabby']
            },
            
            'Torbie': {
                'required_any': [
                    'torbie', 'tortie tabby', 'tortoiseshell tabby', 'tort tabby',
                    'tabby tortie', 'tabby tortoiseshell', 'striped tortie',
                    'patched tabby', 'torbie pattern'
                ],
                'required_all': [],
                'exclude_if_present': []
            },
            
            'Blue Cream': {
                'required_any': [
                    'blue cream', 'blue and cream', 'blue & cream', 'blue/cream',
                    'blue-cream', 'cream and blue', 'cream & blue'
                ],
                'required_all': [],
                'exclude_if_present': ['tabby']
            }
        }
        
        # Level 2: Tabby patterns (medium priority)
        self.tabby_keywords = {
            'Tabby (Gray / Blue / Silver)': {
                'base_colors': ['gray', 'grey', 'silver', 'blue'],
                'pattern_words': ['tabby', 'striped', 'tiger', 'mackerel', 'classic'],
                'specific_phrases': [
                    'gray tabby', 'grey tabby', 'silver tabby', 'blue tabby',
                    'gray striped', 'grey striped', 'silver striped', 'blue striped',
                    'gray tiger', 'grey tiger', 'silver tiger', 'blue tiger'
                ]
            },
            
            'Tabby (Brown / Chocolate)': {
                'base_colors': ['brown', 'chocolate', 'bronze', 'copper'],
                'pattern_words': ['tabby', 'striped', 'tiger', 'mackerel', 'classic'],
                'specific_phrases': [
                    'brown tabby', 'chocolate tabby', 'brown striped',
                    'chocolate striped', 'brown tiger', 'chocolate tiger'
                ]
            },
            
            'Tabby (Orange / Red)': {
                'base_colors': ['orange', 'red', 'ginger', 'marmalade', 'flame', 'rust'],
                'pattern_words': ['tabby', 'striped', 'tiger', 'mackerel', 'classic'],
                'specific_phrases': [
                    'orange tabby', 'red tabby', 'ginger tabby', 'orange striped',
                    'red striped', 'ginger striped', 'marmalade tabby'
                ]
            },
            
            'Tabby (Buff / Tan / Fawn)': {
                'base_colors': ['buff', 'tan', 'fawn', 'beige', 'sand', 'wheat', 'cream'],
                'pattern_words': ['tabby', 'striped', 'tiger', 'mackerel', 'classic'],
                'specific_phrases': [
                    'buff tabby', 'tan tabby', 'fawn tabby', 'beige tabby',
                    'sand tabby', 'wheat tabby', 'cream tabby'
                ]
            },
            
            'Tabby (Tiger Striped)': {
                'base_colors': [],  # Any color can be tiger striped
                'pattern_words': [],
                'specific_phrases': [
                    'tiger striped', 'tiger stripe', 'tiger pattern', 'tiger tabby',
                    'tiger cat', 'bold stripes', 'dramatic stripes', 'thick stripes',
                    'wide stripes', 'prominent stripes', 'classic tiger'
                ]
            },
            
            'Tabby (Leopard / Spotted)': {
                'base_colors': [],  # Any color can be spotted
                'pattern_words': ['spotted', 'leopard'],
                'specific_phrases': [
                    'spotted', 'spotted tabby', 'leopard', 'leopard pattern',
                    'leopard spotted', 'spots', 'speckled', 'rosettes',
                    'bengal-like', 'jungle spots'
                ]
            }
        }
        
        # Level 3: Point patterns (medium priority)
        self.point_keywords = {
            'Seal Point': [
                'seal point', 'sealpoint', 'seal colored points', 'seal point siamese'
            ],
            'Blue Point': [
                'blue point', 'bluepoint', 'blue colored points', 'blue point siamese'
            ],
            'Chocolate Point': [
                'chocolate point', 'chocolatepoint', 'chocolate colored points',
                'chocolate point siamese'
            ],
            'Lilac Point': [
                'lilac point', 'lilacpoint', 'lilac colored points', 'lavender point',
                'lilac point siamese', 'frost point'
            ],
            'Flame Point': [
                'flame point', 'flamepoint', 'red point', 'orange point',
                'flame colored points', 'flame point siamese', 'red point siamese'
            ],
            'Cream Point': [
                'cream point', 'creampoint', 'cream colored points',
                'cream point siamese', 'dilute flame point'
            ]
        }
        
        # Level 4: Solid colors (lowest priority)
        self.solid_keywords = {
            'Black': [
                'black', 'ebony', 'coal', 'midnight', 'raven', 'jet', 'onyx',
                'charcoal', 'void', 'shadow', 'pitch', 'solid black', 'all black',
                'pure black', 'jet black', 'coal black', 'midnight black'
            ],
            
            'White': [
                'white', 'snow', 'ivory', 'pearl', 'alabaster', 'cotton',
                'cloud', 'angel', 'ghost', 'pure white', 'snow white',
                'solid white', 'all white', 'bright white', 'pristine white'
            ],
            
            'Gray / Blue / Silver': [
                'gray', 'grey', 'ash', 'pewter', 'steel', 'slate', 'storm',
                'blue', 'powder blue', 'slate blue', 'steel blue',
                'silver', 'platinum', 'chrome', 'mercury', 'solid gray',
                'solid grey', 'solid blue', 'solid silver', 'russian blue'
            ],
            
            'Orange / Red': [
                'orange', 'ginger', 'marmalade', 'tangerine', 'peach', 'pumpkin',
                'red', 'crimson', 'scarlet', 'cherry', 'rust', 'copper',
                'solid orange', 'solid red', 'bright orange', 'deep red'
            ],
            
            'Brown / Chocolate': [
                'brown', 'chocolate', 'cocoa', 'coffee', 'mocha', 'chestnut',
                'mahogany', 'bronze', 'solid brown', 'solid chocolate',
                'milk chocolate', 'dark chocolate'
            ],
            
            'Buff / Tan / Fawn': [
                'buff', 'tan', 'fawn', 'beige', 'wheat', 'sand', 'champagne',
                'biscuit', 'camel', 'buff colored', 'fawn colored', 'tan colored'
            ],
            
            'Cream / Ivory': [
                'cream', 'ivory', 'eggshell', 'vanilla', 'custard', 'butter',
                'buttercream', 'off-white', 'antique white', 'cream colored',
                'ivory colored', 'cream point'
            ],
            
            'Smoke': [
                'smoke', 'smoky', 'smokey', 'smoke colored', 'smoke pattern',
                'silver smoke', 'black smoke', 'blue smoke', 'smoked'
            ]
        }
    
    def _check_multicolor_match(self, text, color_rules):
        """Check if text matches multicolor pattern rules"""
        text_lower = text.lower()
        
        # Check exclusions first
        if 'exclude_if_present' in color_rules:
            for exclude_word in color_rules['exclude_if_present']:
                if exclude_word in text_lower:
                    return False
        
        # Check required_all patterns (must match at least one set)
        required_all_match = False
        if color_rules['required_all']:
            for required_set in color_rules['required_all']:
                if isinstance(required_set, list):
                    # All words in this set must be present
                    if all(word in text_lower for word in required_set):
                        required_all_match = True
                        break
                else:
                    # Single phrase
                    if required_set in text_lower:
                        required_all_match = True
                        break
        
        # Check required_any patterns
        required_any_match = False
        if color_rules['required_any']:
            for phrase in color_rules['required_any']:
                if phrase in text_lower:
                    required_any_match = True
                    break
        
        # Must match either required_all or required_any (or both if both exist)
        if color_rules['required_all'] and not color_rules['required_any']:
            return required_all_match
        elif color_rules['required_any'] and not color_rules['required_all']:
            return required_any_match
        elif color_rules['required_all'] and color_rules['required_any']:
            return required_all_match or required_any_match
        
        return False
    
    def _check_tabby_match(self, text, tabby_rules):
        """Check if text matches tabby pattern"""
        text_lower = text.lower()
        
        # First check specific phrases
        for phrase in tabby_rules['specific_phrases']:
            if phrase in text_lower:
                return True
        
        # Then check base_color + pattern_word combinations
        if tabby_rules['base_colors'] and tabby_rules['pattern_words']:
            base_color_found = any(color in text_lower for color in tabby_rules['base_colors'])
            pattern_found = any(pattern in text_lower for pattern in tabby_rules['pattern_words'])
            return base_color_found and pattern_found
        
        # Special case for tiger striped and spotted (no base color requirement)
        if not tabby_rules['base_colors']:
            return any(phrase in text_lower for phrase in tabby_rules['specific_phrases'])
        
        return False
    
    def extract_color_from_text(self, text, field_name="description"):
        """
        Extract color using hierarchical matching
        """
        if pd.isna(text) or text == "":
            return None
        
        text = str(text).lower()
        
        # Level 1: Check multicolor patterns first (highest priority)
        for color, rules in self.multicolor_keywords.items():
            if self._check_multicolor_match(text, rules):
                return color
        
        # Level 2: Check tabby patterns
        for color, rules in self.tabby_keywords.items():
            if self._check_tabby_match(text, rules):
                return color
        
        # Level 3: Check point patterns
        for color, keywords in self.point_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return color
        
        # Level 4: Check solid colors (lowest priority)
        for color, keywords in self.solid_keywords.items():
            for keyword in keywords:
                # Use word boundaries to avoid false matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text):
                    return color
        
        return None
    
    def extract_color_from_name(self, name):
        """Extract color specifically from pet names"""
        return self.extract_color_from_text(name, "name")
    
    def extract_color_from_description(self, description):
        """Extract color specifically from descriptions"""
        return self.extract_color_from_text(description, "description")
    
    def impute_colors(self, df, description_col='description', name_col='name', 
                     color_col='colors_primary'):
        """
        Validates the imputation approach on a sample of data.
        """
    
        results = []
        confidence_scores = []
        methods_used = []
        
        for idx, row in df.iterrows():
            # Skip if color is already known
            if pd.notna(row[color_col]):
                results.append(row[color_col])
                confidence_scores.append(1.0)
                methods_used.append('original')
                continue
            
            # Try description first
            color_from_desc = self.extract_color_from_description(row[description_col])
            if color_from_desc:
                results.append(color_from_desc)
                confidence_scores.append(0.9)
                methods_used.append('description')
                continue
            
            # # Try name
            # color_from_name = self.extract_color_from_name(row[name_col])
            # if color_from_name:
            #     results.append(color_from_name)
            #     confidence_scores.append(0.7)
            #     methods_used.append('name')
            #     continue
            
            # No match found
            results.append(None)
            confidence_scores.append(0.0)
            methods_used.append('none')
        
        return results, confidence_scores, methods_used
    
    def validate_imputation(self, df, test_fraction=0.1, color_col='cleaned_color',
                           description_col='description', name_col='name'):
        """
        Validate the imputation approach on known data
        """
        # Get sample with known colors
        known_colors = df[(df[color_col].notna()) & (df[color_col] != '')].copy()
        
        if len(known_colors) == 0:
            return None
        
        # Sample for testing
        test_size = min(int(len(known_colors) * test_fraction), 100000)
        test_sample = known_colors.sample(n=test_size, random_state=42)
        
        # Temporarily hide the colors
        test_sample_hidden = test_sample.copy()
        test_sample_hidden[color_col] = None
        
        # Try to predict them
        predicted_colors, confidence, methods = self.impute_colors(
            test_sample_hidden, description_col, name_col, color_col
        )
        
        # Calculate accuracy
        correct_predictions = 0
        total_predictions = 0
        
        accuracy_by_method = defaultdict(lambda: {'correct': 0, 'total': 0})
        accuracy_by_color = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for i, (actual, predicted, method) in enumerate(zip(
            test_sample[color_col].values, predicted_colors, methods
        )):
            if predicted is not None:
                total_predictions += 1
                accuracy_by_method[method]['total'] += 1
                accuracy_by_color[actual]['total'] += 1
                
                if actual == predicted:
                    correct_predictions += 1
                    accuracy_by_method[method]['correct'] += 1
                    accuracy_by_color[actual]['correct'] += 1
        
        overall_accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        # Calculate accuracy by method
        method_accuracies = {}
        for method, stats in accuracy_by_method.items():
            if stats['total'] > 0:
                method_accuracies[method] = stats['correct'] / stats['total']
        
        # Calculate accuracy by color
        color_accuracies = {}
        for color, stats in accuracy_by_color.items():
            if stats['total'] > 0:
                color_accuracies[color] = stats['correct'] / stats['total']
        

        results_df = pd.DataFrame({
                        'actual': test_sample[color_col].values,
                        'predicted': predicted_colors,
                        'method_used': methods,
                        'desc': test_sample[description_col].values,
                        'name':test_sample[name_col].values,
                    })
    
        return {
            'overall_accuracy': overall_accuracy,
            'total_tested': len(test_sample),
            'total_predicted': total_predictions,
            'method_accuracies': method_accuracies,
            'color_accuracies': color_accuracies
        }, results_df
