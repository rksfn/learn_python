"""
Exercise 2: Error Handling and Prevention Strategies

In this exercise, you'll practice implementing effective error handling and prevention 
strategies in Python. You'll work with code that's prone to errors and improve it by:

1. Adding proper exception handling
2. Implementing defensive programming techniques
3. Adding input validation
4. Using context managers for resource management
5. Applying Python's type hinting system

The goal is to make the code more robust and less prone to runtime errors.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Union, TypeVar, Callable
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

def divide_numbers(a, b):
    """
    Divide a by b.
    
    TODO: Implement proper exception handling to deal with division by zero.
    Return None if division is not possible.
    """
    result = a / b
    return result

def parse_json_data(json_string):
    """
    Parse a JSON string into a Python dictionary.
    
    TODO: Add exception handling to deal with invalid JSON.
    Return an empty dict if the JSON is invalid.
    """
    data = json.loads(json_string)
    return data

def get_element_safely(items, index):
    """
    Get an element from a list at the specified index.
    
    TODO: Implement exception handling to prevent IndexError.
    Return None if the index is out of bounds.
    """
    return items[index]

# =====================================================================
# PART 2: Defensive Programming
# =====================================================================

def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.
    
    TODO: Implement defensive programming techniques to handle:
      - Empty lists
      - Lists with non-numeric elements
      - None input
    Return 0 for empty lists and None for invalid inputs.
    """
    total = sum(numbers)
    average = total / len(numbers)
    return average

def process_user_data(user_dict):
    """
    Process user data to create a user profile.
    
    TODO: Add validation to ensure the dictionary contains required fields:
      - 'name' (string)
      - 'age' (positive integer)
      - 'email' (string containing '@')
    Return None and log an error for invalid data.
    """
    profile = {
        'name': user_dict['name'],
        'age': user_dict['age'],
        'email': user_dict['email'],
        'is_adult': user_dict['age'] >= 18,
        'processed_at': datetime.now().isoformat()
    }
    return profile

def normalize_and_sort(text_list):
    """
    Normalize (convert to lowercase) and sort a list of strings.
    
    TODO: Add defensive programming to handle:
      - None input
      - Lists with non-string elements
      - Empty lists
    Return empty list for invalid inputs and log appropriate warnings.
    """
    normalized = [item.lower() for item in text_list]
    return sorted(normalized)

# =====================================================================
# PART 3: Resource Management with Context Managers
# =====================================================================

def count_lines_in_file(filename):
    """
    Count the number of lines in a file.
    
    TODO: Rewrite using a context manager (with statement) to ensure
    the file is properly closed even if an exception occurs.
    Handle FileNotFoundError and PermissionError separately.
    """
    file = open(filename, 'r')
    lines = file.readlines()
    file.close()
    return len(lines)

def update_json_file(filename, key, value):
    """
    Update a JSON file by modifying or adding a key-value pair.
    
    TODO: Implement with proper resource management using context managers.
    Create the file with an empty dict if it doesn't exist.
    Handle file access errors and JSON parsing errors.
    """
    # Read existing data
    file = open(filename, 'r')
    data = json.load(file)
    file.close()
    
    # Update data
    data[key] = value
    
    # Write back to file
    file = open(filename, 'w')
    json.dump(data, file, indent=2)
    file.close()
    
    return True

# =====================================================================
# PART 4: Type Hinting for Better Code
# =====================================================================

def filter_data(items, condition):
    """
    Filter a list based on a condition function.
    
    TODO: Add type hints to this function using the typing module.
    The function should work with any list type and a condition function
    that takes an item and returns a boolean.
    """
    result = []
    for item in items:
        if condition(item):
            result.append(item)
    return result

def merge_dictionaries(dict1, dict2, override=False):
    """
    Merge two dictionaries.
    
    TODO: Add type hints to parameters and return value.
    If override is True, dict2 values override dict1 values for the same keys.
    If override is False, dict1 values are kept when keys clash.
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if override or key not in result:
            result[key] = value
    return result

def process_mixed_data(data):
    """
    Process data that could be a string, list, or dict.
    
    TODO: Add type hints using Union to specify the function
    accepts either a string, list, or dict.
    
    Returns:
    - For strings: the length of the string
    - For lists: the sum of elements (if all are numeric)
    - For dicts: the number of key-value pairs
    """
    if isinstance(data, str):
        return len(data)
    elif isinstance(data, list):
        return sum(data)
    elif isinstance(data, dict):
        return len(data)
    else:
        raise TypeError("Unsupported data type")

# =====================================================================
# PART 5: Putting It All Together
# =====================================================================

class DataProcessor:
    """
    A class to process data from multiple sources.
    
    TODO: Improve this class by:
    1. Adding proper type hints
    2. Implementing exception handling
    3. Adding input validation
    4. Using context managers for file operations
    5. Adding logging for errors and operations
    """
    
    def __init__(self, config_file):
        # Load configuration
        file = open(config_file, 'r')
        self.config = json.load(file)
        file.close()
        
        self.data_dir = self.config['data_directory']
        self.processed_data = []
    
    def load_data_from_file(self, filename):
        """Load data from a JSON file."""
        file_path = os.path.join(self.data_dir, filename)
        file = open(file_path, 'r')
        data = json.load(file)
        file.close()
        return data
    
    def save_results(self, results, output_file):
        """Save results to a JSON file."""
        file_path = os.path.join(self.data_dir, output_file)
        file = open(file_path, 'w')
        json.dump(results, file, indent=2)
        file.close()
    
    def process_file(self, input_file, output_file):
        """Process a single file and save results."""
        data = self.load_data_from_file(input_file)
        
        # Process the data
        results = []
        for item in data:
            processed_item = {
                'id': item['id'],
                'value': item['value'] * 2 if 'value' in item else 0,
                'name': item['name'].upper() if 'name' in item else 'UNKNOWN',
                'valid': 'value' in item and 'name' in item
            }
            results.append(processed_item)
        
        # Save the results
        self.save_results(results, output_file)
        self.processed_data.extend(results)
        
        return len(results)
    
    def process_all_files(self):
        """Process all files specified in the configuration."""
        total_processed = 0
        for file_info in self.config['files']:
            input_file = file_info['input']
            output_file = file_info['output']
            
            count = self.process_file(input_file, output_file)
            total_processed += count
            
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
Exercise Instructions:

1. For each function in the exercise, implement the requested improvements:
   - Add proper exception handling
   - Implement defensive programming techniques
   - Add input validation
   - Use context managers for resource management
   - Apply type hints

2. Test each function after making your improvements
   - Run the test_functions() to see if your implementations work
   - Fix any issues that arise during testing

3. For the DataProcessor class, implement all best practices together to create
   a robust, error-resistant class.

4. As you work, consider and document:
   - What errors might occur in each function?
   - How can you make your code resilient to unexpected inputs?
   - What's the appropriate way to handle different types of errors?
   - How can you make the code self-documenting with type hints?

5. After completing all improvements, review your code and consider:
   - Are there any other vulnerabilities you should address?
   - Did you handle all edge cases?
   - Is your error handling specific enough (not catching all exceptions generically)?
   - Does your error handling provide useful information for debugging?

Bonus Challenges:
1. Implement custom exception classes for domain-specific errors
2. Add retry logic for operations that might temporarily fail
3. Implement a more sophisticated logging system that traces function calls
4. Add unit tests that specifically test your error handling code
"""
