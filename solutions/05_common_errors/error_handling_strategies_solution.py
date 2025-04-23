"""
Exercise 2 Solution: Error Handling and Prevention Strategies

This solution demonstrates effective error handling and prevention strategies in Python,
including proper exception handling, defensive programming, context managers, 
and type hinting.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Union, TypeVar, Callable, Set
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='data_processor.log'  # Log to a file
)
logger = logging.getLogger("data_processor")

# =====================================================================
# PART 1: Basic Exception Handling
# =====================================================================

def divide_numbers(a: Union[int, float], b: Union[int, float]) -> Optional[float]:
    """
    Divide a by b with proper exception handling.
    
    Args:
        a: The numerator
        b: The denominator
        
    Returns:
        The result of a/b or None if division is not possible
    """
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        logger.warning(f"Attempted division by zero: {a}/{b}")
        return None
    except TypeError:
        logger.warning(f"Invalid types for division: {type(a)}, {type(b)}")
        return None

def parse_json_data(json_string: str) -> Dict[str, Any]:
    """
    Parse a JSON string into a Python dictionary with error handling.
    
    Args:
        json_string: A string containing JSON data
        
    Returns:
        A dictionary parsed from the JSON string, or empty dict if invalid
    """
    try:
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return {}

def get_element_safely(items: List[Any], index: int) -> Optional[Any]:
    """
    Get an element from a list at the specified index with error handling.
    
    Args:
        items: A list of items
        index: The index to access
        
    Returns:
        The element at the specified index or None if index is out of bounds
    """
    try:
        return items[index]
    except IndexError:
        logger.debug(f"Index {index} out of bounds for list of length {len(items)}")
        return None
    except TypeError:
        logger.error(f"Cannot index into {type(items)}")
        return None

# =====================================================================
# PART 2: Defensive Programming
# =====================================================================

def calculate_average(numbers: Optional[List[Union[int, float]]]) -> Optional[float]:
    """
    Calculate the average of a list of numbers with defensive programming.
    
    Args:
        numbers: A list of numbers
        
    Returns:
        The average of the numbers, 0 for empty lists, or None for invalid inputs
    """
    # Check if input is None
    if numbers is None:
        logger.warning("calculate_average received None input")
        return None
    
    # Check if input is a list
    if not isinstance(numbers, list):
        logger.warning(f"calculate_average expected a list, got {type(numbers)}")
        return None
    
    # Handle empty list
    if not numbers:
        logger.info("calculate_average received empty list")
        return 0
    
    # Filter out non-numeric elements
    valid_numbers = []
    for item in numbers:
        if isinstance(item, (int, float)):
            valid_numbers.append(item)
        else:
            logger.warning(f"Non-numeric item in list: {item}")
    
    # Calculate average if we have valid numbers
    if valid_numbers:
        total = sum(valid_numbers)
        average = total / len(valid_numbers)
        return average
    else:
        logger.warning("No valid numeric items in list")
        return 0

def process_user_data(user_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Process user data to create a user profile with validation.
    
    Args:
        user_dict: Dictionary containing user data
        
    Returns:
        A processed user profile or None if validation fails
    """
    # Check if input is a dictionary
    if not isinstance(user_dict, dict):
        logger.error(f"Expected dict, got {type(user_dict)}")
        return None
    
    # Validate required fields
    required_fields = {'name', 'age', 'email'}
    missing_fields = required_fields - set(user_dict.keys())
    if missing_fields:
        logger.error(f"Missing required fields: {missing_fields}")
        return None
    
    # Validate field types and values
    name = user_dict['name']
    age = user_dict['age']
    email = user_dict['email']
    
    # Validate name
    if not isinstance(name, str) or not name:
        logger.error(f"Invalid name: {name}")
        return None
    
    # Validate age
    if not isinstance(age, (int, float)) or age < 0:
        logger.error(f"Invalid age: {age}")
        return None
    
    # Validate email
    if not isinstance(email, str) or '@' not in email:
        logger.error(f"Invalid email: {email}")
        return None
    
    # Create and return profile if all validations pass
    profile = {
        'name': name,
        'age': age,
        'email': email,
        'is_adult': age >= 18,
        'processed_at': datetime.now().isoformat()
    }
    
    logger.info(f"User profile created for {name}")
    return profile

def normalize_and_sort(text_list: Optional[List[str]]) -> List[str]:
    """
    Normalize and sort a list of strings with defensive programming.
    
    Args:
        text_list: A list of strings
        
    Returns:
        Normalized and sorted list, or empty list for invalid inputs
    """
    # Handle None input
    if text_list is None:
        logger.warning("normalize_and_sort received None input")
        return []
    
    # Handle non-list input
    if not isinstance(text_list, list):
        logger.warning(f"normalize_and_sort expected list, got {type(text_list)}")
        return []
    
    # Handle empty list
    if not text_list:
        logger.info("normalize_and_sort received empty list")
        return []
    
    # Process valid items and filter out non-strings
    normalized = []
    for i, item in enumerate(text_list):
        if isinstance(item, str):
            normalized.append(item.lower())
        else:
            logger.warning(f"Non-string item at index {i}: {item}")
    
    return sorted(normalized)

# =====================================================================
# PART 3: Resource Management with Context Managers
# =====================================================================

def count_lines_in_file(filename: str) -> Union[int, str]:
    """
    Count the number of lines in a file using context managers.
    
    Args:
        filename: Path to the file
        
    Returns:
        Number of lines in the file, or error message if file can't be read
    """
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            logger.info(f"Read {len(lines)} lines from {filename}")
            return len(lines)
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return f"Error: File {filename} not found"
    except PermissionError:
        logger.error(f"Permission denied: {filename}")
        return f"Error: No permission to read {filename}"
    except Exception as e:
        logger.error(f"Error reading {filename}: {e}")
        return f"Error: {str(e)}"

def update_json_file(filename: str, key: str, value: Any) -> bool:
    """
    Update a JSON file by modifying or adding a key-value pair using context managers.
    
    Args:
        filename: Path to the JSON file
        key: Key to update or add
        value: New value
        
    Returns:
        True if successful, False otherwise
    """
    # Initialize data with an empty dict
    data = {}
    
    # Try to read existing data if file exists
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                try:
                    data = json.load(file)
                    logger.info(f"Loaded existing JSON from {filename}")
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in {filename}, starting with empty data")
                    # Keep the empty dict
        else:
            logger.info(f"File {filename} does not exist, will create new file")
    except Exception as e:
        logger.error(f"Error reading {filename}: {e}")
        return False
    
    # Update data
    data[key] = value
    
    # Write updated data back to file
    try:
        # Ensure directory exists
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
            logger.info(f"Updated {filename} with key {key}")
        return True
    except Exception as e:
        logger.error(f"Error writing to {filename}: {e}")
        return False

# =====================================================================
# PART 4: Type Hinting for Better Code
# =====================================================================

T = TypeVar('T')  # Define a type variable for generic functions

def filter_data(items: List[T], condition: Callable[[T], bool]) -> List[T]:
    """
    Filter a list based on a condition function.
    
    Args:
        items: A list of items of any type
        condition: A function that takes an item and returns a boolean
        
    Returns:
        A new list containing only items that satisfy the condition
    """
    # Defensive check
    if not callable(condition):
        logger.error("condition must be callable")
        return []
    
    result = []
    for item in items:
        try:
            if condition(item):
                result.append(item)
        except Exception as e:
            logger.warning(f"Error applying condition to {item}: {e}")
    
    return result

def merge_dictionaries(dict1: Dict[str, Any], 
                       dict2: Dict[str, Any], 
                       override: bool = False) -> Dict[str, Any]:
    """
    Merge two dictionaries with type hints.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        override: If True, dict2 values override dict1 values for the same keys
        
    Returns:
        A new dictionary containing merged key-value pairs
    """
    # Defensive checks
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        logger.error(f"Both arguments must be dictionaries: {type(dict1)}, {type(dict2)}")
        return {}
    
    result = dict1.copy()
    
    for key, value in dict2.items():
        if override or key not in result:
            result[key] = value
    
    return result

def process_mixed_data(data: Union[str, List[Union[int, float]], Dict[str, Any]]) -> Union[int, float, None]:
    """
    Process data that could be a string, list, or dict.
    
    Args:
        data: Either a string, list of numbers, or dictionary
        
    Returns:
        - For strings: the length of the string
        - For lists: the sum of elements (if all are numeric)
        - For dicts: the number of key-value pairs
    """
    if isinstance(data, str):
        return len(data)
    elif isinstance(data, list):
        # Check if all elements are numeric
        if all(isinstance(item, (int, float)) for item in data):
            return sum(data)
        else:
            logger.warning("List contains non-numeric elements")
            return None
    elif isinstance(data, dict):
        return len(data)
    else:
        logger.error(f"Unsupported data type: {type(data)}")
        raise TypeError(f"Unsupported data type: {type(data)}")

# =====================================================================
# PART 5: Putting It All Together
# =====================================================================

class DataProcessor:
    """
    A class to process data from multiple sources with robust error handling.
    """
    
    def __init__(self, config_file: str):
        """
        Initialize the DataProcessor with a configuration file.
        
        Args:
            config_file: Path to the JSON configuration file
        
        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file contains invalid JSON
            KeyError: If required keys are missing from the config
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.data_dir: str = ""
        self.processed_data: List[Dict[str, Any]] = []
        
        # Load configuration
        logger.info(f"Initializing DataProcessor with config: {config_file}")
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from the config file."""
        try:
            # Check if config file exists
            if not os.path.exists(self.config_file):
                logger.error(f"Config file not found: {self.config_file}")
                raise FileNotFoundError(f"Config file not found: {self.config_file}")
                
            # Open and parse the config file
            with open(self.config_file, 'r') as file:
                self.config = json.load(file)
                
            # Validate required configuration
            if 'data_directory' not in self.config:
                logger.error("Missing 'data_directory' in config")
                raise KeyError("Missing 'data_directory' in config")
                
            if 'files' not in self.config or not isinstance(self.config['files'], list):
                logger.error("Missing 'files' list in config")
                raise KeyError("Missing 'files' list in config")
                
            self.data_dir = self.config['data_directory']
            
            # Ensure data directory exists
            if not os.path.exists(self.data_dir):
                logger.warning(f"Creating data directory: {self.data_dir}")
                os.makedirs(self.data_dir, exist_ok=True)
                
            logger.info(f"Configuration loaded successfully")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def load_data_from_file(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load data from a JSON file.
        
        Args:
            filename: Name of the JSON file (relative to data_dir)
            
        Returns:
            List of dictionaries containing the data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        file_path = os.path.join(self.data_dir, filename)
        logger.info(f"Loading data from: {file_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")
                
            # Load data from file
            with open(file_path, 'r') as file:
                data = json.load(file)
                
            # Validate that data is a list
            if not isinstance(data, list):
                logger.error(f"Expected list in {filename}, got {type(data)}")
                raise ValueError(f"Expected list in {filename}, got {type(data)}")
                
            logger.info(f"Loaded {len(data)} items from {filename}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filename}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading data from {filename}: {e}")
            raise
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str) -> None:
        """
        Save results to a JSON file.
        
        Args:
            results: List of results to save
            output_file: Name of the output file (relative to data_dir)
            
        Raises:
            ValueError: If results is not a list
            IOError: If there's an error writing to the file
        """
        if not isinstance(results, list):
            logger.error(f"Expected list for results, got {type(results)}")
            raise ValueError(f"Expected list for results, got {type(results)}")
            
        file_path = os.path.join(self.data_dir, output_file)
        logger.info(f"Saving {len(results)} results to: {file_path}")
        
        try:
            with open(file_path, 'w') as file:
                json.dump(results, file, indent=2)
                
            logger.info(f"Results saved successfully to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving results to {output_file}: {e}")
            raise IOError(f"Error saving results to {output_file}: {e}")
    
    def process_file(self, input_file: str, output_file: str) -> int:
        """
        Process a single file and save results.
        
        Args:
            input_file: Name of the input file
            output_file: Name of the output file
            
        Returns:
            Number of processed items
            
        Raises:
            Various exceptions that might occur during processing
        """
        logger.info(f"Processing file: {input_file} -> {output_file}")
        
        try:
            # Load data
            data = self.load_data_from_file(input_file)
            
            # Process the data
            results = []
            for item in data:
                try:
                    # Validate item is a dictionary
                    if not isinstance(item, dict):
                        logger.warning(f"Skipping non-dict item: {item}")
                        continue
                        
                    # Get id (required)
                    if 'id' not in item:
                        logger.warning(f"Skipping item without id: {item}")
                        continue
                        
                    processed_item = {
                        'id': item['id'],
                        'value': item.get('value', 0) * 2,
                        'name': item.get('name', 'UNKNOWN').upper(),
                        'valid': 'value' in item and 'name' in item,
                        'processed_at': datetime.now().isoformat()
                    }
                    results.append(processed_item)
                    
                except Exception as e:
                    logger.error(f"Error processing item {item}: {e}")
                    # Continue processing other items
            
            # Save the results
            self.save_results(results, output_file)
            self.processed_data.extend(results)
            
            logger.info(f"Processed {len(results)} items from {input_file}")
            return len(results)
            
        except FileNotFoundError:
            logger.error(f"Input file not found: {input_file}")
            # Re-raise to be handled by caller
            raise
        except Exception as e:
            logger.error(f"Error processing file {input_file}: {e}")
            raise
    
    def process_all_files(self) -> int:
        """
        Process all files specified in the configuration.
        
        Returns:
            Total number of processed items
            
        Raises:
            Exception: If there's an unrecoverable error
        """
        logger.info("Processing all files")
        total_processed = 0
        errors = []
        
        for file_info in self.config['files']:
            try:
                # Validate file_info
                if not isinstance(file_info, dict):
                    logger.error(f"Invalid file info: {file_info}")
                    errors.append(f"Invalid file info: {file_info}")
                    continue
                    
                # Get input and output filenames
                input_file = file_info.get('input')
                output_file = file_info.get('output')
                
                if not input_file or not output_file:
                    logger.error(f"Missing input or output in file info: {file_info}")
                    errors.append(f"Missing input or output in file info: {file_info}")
                    continue
                
                # Process the file
                count = self.process_file(input_file, output_file)
                total_processed += count
                
            except FileNotFoundError as e:
                logger.error(f"File not found: {e}")
                errors.append(str(e))
                # Continue with other files
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                errors.append(str(e))
                # Continue with other files
        
        # Report results
        logger.info(f"Completed processing {total_processed} items from all files")
        if errors:
            logger.warning(f"Encountered {len(errors)} errors during processing")
            
        return total_processed


# =====================================================================
# Test Code and Example Files
# =====================================================================

def create_test_files():
    """Create test files for the exercise."""
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Create a config file
    config = {
        "data_directory": "data",
        "files": [
            {"input": "input1.json", "output": "output1.json"},
            {"input": "input2.json", "output": "output2.json"},
            {"input": "input3.json", "output": "output3.json"}
        ]
    }
    
    with open("data/config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Create input files
    input1 = [
        {"id": 1, "name": "Item 1", "value": 10},
        {"id": 2, "name": "Item 2", "value": 20},
        {"id": 3, "name": "Item 3", "value": 30}
    ]
    
    with open("data/input1.json", "w") as f:
        json.dump(input1, f, indent=2)
    
    input2 = [
        {"id": 4, "name": "Item 4", "value": 40},
        {"id": 5, "name": "Item 5"},  # Missing value
        {"id": 6, "value": 60}  # Missing name
    ]
    
    with open("data/input2.json", "w") as f:
        json.dump(input2, f, indent=2)
    
    # Third file is intentionally missing to test error handling
    
    print("Test files created in the 'data' directory")


def test_functions():
    """Test the functions after they've been improved."""
    print("\n===== Testing Basic Exception Handling =====")
    
    print("\nTesting divide_numbers:")
    print(f"10 / 2 = {divide_numbers(10, 2)}")
    print(f"10 / 0 = {divide_numbers(10, 0)}")
    
    print("\nTesting parse_json_data:")
    print(f"Valid JSON: {parse_json_data('{\"key\": \"value\"}')}")
    print(f"Invalid JSON: {parse_json_data('{key: value}')}")
    
    print("\nTesting get_element_safely:")
    print(f"Get index 1 from [1, 2, 3]: {get_element_safely([1, 2, 3], 1)}")
    print(f"Get index 5 from [1, 2, 3]: {get_element_safely([1, 2, 3], 5)}")
    
    print("\n===== Testing Defensive Programming =====")
    
    print("\nTesting calculate_average:")
    print(f"Average of [1, 2, 3, 4, 5]: {calculate_average([1, 2, 3, 4, 5])}")
    print(f"Average of []: {calculate_average([])}")
    print(f"Average of [1, 2, 'three', 4, 5]: {calculate_average([1, 2, 'three', 4, 5])}")
    print(f"Average of None: {calculate_average(None)}")
    
    print("\nTesting process_user_data:")
    valid_user = {"name": "John Doe", "age": 30, "email": "john@example.com"}
    invalid_user = {"name": "Jane Doe", "age": -5, "email": "invalid-email"}
    missing_fields_user = {"name": "Bob Smith"}
    print(f"Valid user: {process_user_data(valid_user)}")
    print(f"Invalid user: {process_user_data(invalid_user)}")
    print(f"Missing fields: {process_user_data(missing_fields_user)}")
    
    print("\nTesting normalize_and_sort:")
    print(f"Normal list: {normalize_and_sort(['B', 'a', 'C'])}")
    print(f"List with non-strings: {normalize_and_sort(['B', 1, 'C'])}")
    print(f"Empty list: {normalize_and_sort([])}")
    print(f"None input: {normalize_and_sort(None)}")
    
    print("\n===== Testing Resource Management =====")
    
    print("\nTesting count_lines_in_file:")
    with open("test_file.txt", "w") as f:
        f.write("Line 1\nLine 2\nLine 3\n")
    print(f"Line count in test_file.txt: {count_lines_in_file('test_file.txt')}")
    print(f"Non-existent file: {count_lines_in_file('non_existent_file.txt')}")
    
    print("\nTesting update_json_file:")
    print(f"Update JSON file: {update_json_file('test_data.json', 'new_key', 'new_value')}")
    with open("test_data.json", "r") as f:
        print(f"Updated content: {f.read()}")
    
    print("\n===== Testing Type Hinted Functions =====")
    
    print("\nTesting filter_data:")
    numbers = [1, 2, 3, 4, 5, 6]
    is_even = lambda x: x % 2 == 0
    print(f"Even numbers from {numbers}: {filter_data(numbers, is_even)}")
    
    print("\nTesting merge_dictionaries:")
    dict1 = {"a": 1, "b": 2}
    dict2 = {"b": 3, "c": 4}
    print(f"Merge with override=False: {merge_dictionaries(dict1, dict2)}")
    print(f"Merge with override=True: {merge_dictionaries(dict1, dict2, True)}")
    
    print("\nTesting process_mixed_data:")
    print(f"String 'hello': {process_mixed_data('hello')}")
    print(f"List [1, 2, 3]: {process_mixed_data([1, 2, 3])}")
    print(f"Dict {{'a': 1, 'b': 2}}: {process_mixed_data({'a': 1, 'b': 2})}")
    try:
        print(f"Set {{1, 2, 3}}: {process_mixed_data({1, 2, 3})}")
    except TypeError as e:
        print(f"Set error: {e}")
    
    print("\n===== Testing DataProcessor Class =====")
    
    create_test_files()
    try:
        processor = DataProcessor("data/config.json")
        print(f"Processing all files: {processor.process_all_files()} items processed")
        print(f"Processed data count: {len(processor.processed_data)}")
    except Exception as e:
        print(f"Error in DataProcessor: {e}")


if __name__ == "__main__":
    test_functions()

"""
Solution Notes:

This solution demonstrates best practices for error handling and prevention in Python:

1. Basic Exception Handling:
   - Used specific exception classes (ZeroDivisionError, TypeError, etc.)
   - Added logging for errors to aid debugging
   - Provided appropriate fallback values or behavior

2. Defensive Programming:
   - Added input validation to check types, ranges, and required fields
   - Handled special cases like None values and empty collections
   - Filtered out invalid data rather than failing
   - Added appropriate logging at different severity levels

3. Resource Management:
   - Used context managers (with statements) for all file operations
   - Properly handled file-related exceptions
   - Created missing directories as needed
   - Added proper cleanup and error handling

4. Type Hinting:
   - Used Python's typing module for clear type annotations
   - Employed generics (TypeVar) for flexible but type-safe functions
   - Used Union types to handle multiple possible input types
   - Added Optional for values that might be None

5. Complete Implementation (DataProcessor class):
   - Combined all techniques in a robust implementation
   - Used proper OOP principles with private helper methods
   - Implemented comprehensive error handling and logging
   - Made the class resilient to various failure modes

Key Error Prevention Strategies Demonstrated:

1. Anticipate failures and handle them gracefully
2. Validate inputs before processing
3. Use appropriate data structures and type checking
4. Handle resources properly with context managers
5. Add clear type hints to document expected types
6. Keep error handling specific and targeted
7. Log errors and important operations
8. Use defensive programming to handle edge cases
9. Always clean up resources even when errors occur

These techniques collectively create more robust, maintainable code
that can handle real-world scenarios gracefully.
"""
