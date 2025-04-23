"""
Exercise 1 Solution: Identifying and Fixing Common Python Errors

This file contains solutions to various common Python errors, showing how to properly
identify and fix them. For each bug, I've included the error type, explanation of
the issue, and the corrected code.
"""

# =====================================================================
# PART 1: Syntax Errors
# =====================================================================
# Syntax errors prevent your code from running at all. Python will show
# an error message pointing to where the syntax is invalid.

def syntax_error_example1():
    """Fix the syntax error in this function."""
    # Error Type: SyntaxError
    # Issue: Missing closing parenthesis
    # Fix: Add the missing closing parenthesis
    print("Hello, world")  # Added closing parenthesis
    
    return "Function completed"

def syntax_error_example2():
    """Fix the syntax error in this function."""
    # Error Type: SyntaxError
    # Issue: Missing colon after if statement
    # Fix: Add the required colon
    x = 10
    if x > 5:  # Added the colon
        print("x is greater than 5")
    
    return "Function completed"

def syntax_error_example3():
    """Fix the indentation error in this function."""
    # Error Type: IndentationError
    # Issue: Inconsistent indentation
    # Fix: Properly indent the nested function code
    def nested_function():
        print("Inside nested function")
        print("This line should be indented")  # Fixed indentation
    
    return nested_function()

# =====================================================================
# PART 2: Name Errors
# =====================================================================
# Name errors occur when you try to use a variable or function that
# doesn't exist in the current scope.

def name_error_example1():
    """Fix the name error in this function."""
    # Error Type: NameError
    # Issue: Variable used before assignment
    # Fix: Define the variable before using it
    initial_value = 5  # Moved this line to before it's used
    result = initial_value + 10
    
    return result

def name_error_example2():
    """Fix the name error in this function."""
    # Error Type: NameError
    # Issue: Misspelled variable name
    # Fix: Correct the spelling of the variable
    message = "Hello, world"
    print(message)  # Fixed spelling from 'mesage' to 'message'
    
    return "Function completed"

def name_error_example3(data):
    """Fix the name error in this function."""
    # Error Type: NameError
    # Issue: Using an undefined global variable
    # Fix: Define the variable or provide a default value directly
    if data is None:
        # Define a default_data value instead of using undefined global
        default_data = []  # Added default data definition
        data = default_data
    
    return data

# =====================================================================
# PART 3: Type Errors
# =====================================================================
# Type errors occur when an operation is applied to an object of an
# inappropriate type.

def type_error_example1():
    """Fix the type error in this function."""
    # Error Type: TypeError
    # Issue: Adding string and integer
    # Fix: Convert the integer to string before concatenation
    num = 5
    result = "The number is " + str(num)  # Added str() conversion
    
    return result

def type_error_example2(items):
    """Fix the type error in this function."""
    # Error Type: TypeError/AttributeError
    # Issue: Calling a list method on a potential None value
    # Fix: Check if items is None first
    if items is None:
        items = []
    
    items.append("new item")
    return items

def type_error_example3():
    """Fix the type error in this function."""
    # Error Type: TypeError
    # Issue: Calling a non-callable object
    # Fix: Either make the value callable or don't call it
    data = {"process": "data processing function"}
    # Instead of trying to call the string, just return it
    result = data["process"]  # Removed the () to not call it
    
    # Alternative fix (if we want to make it callable):
    # data = {"process": lambda x: f"Processed: {x}"}
    # result = data["process"]("some data")
    
    return result

# =====================================================================
# PART 4: Index and Key Errors
# =====================================================================
# Index errors occur when you try to access an index that doesn't exist.
# Key errors occur when you try to access a key that doesn't exist in a dict.

def index_error_example1():
    """Fix the index error in this function."""
    # Error Type: IndexError
    # Issue: Accessing an index that doesn't exist
    # Fix: Use a valid index or handle the error
    list_data = [1, 2, 3]
    # Lists are 0-indexed, so the valid indices are 0, 1, and 2
    value = list_data[2]  # Changed from 3 to 2 to get the last item
    
    return value

def index_error_example2(items):
    """Fix the index error in this function to get the last item safely."""
    # Error Type: IndexError
    # Issue: This will fail on an empty list
    # Fix: Check if the list is empty before accessing
    if items:  # Check if the list is not empty
        last_item = items[-1]
        return last_item
    else:
        return None  # Return None if the list is empty

def key_error_example(user_data):
    """Fix the key error in this function."""
    # Error Type: KeyError
    # Issue: Accessing a key that might not exist
    # Fix: Use .get() method or check if key exists
    # Using get() with a default value
    user_name = user_data.get("name", "Unknown")
    user_email = user_data.get("email", "No email provided")
    
    return f"User: {user_name}, Email: {user_email}"

# =====================================================================
# PART 5: Value Errors
# =====================================================================
# Value errors occur when a function receives an argument of the right type
# but an inappropriate value.

def value_error_example1():
    """Fix the value error in this function."""
    # Error Type: ValueError
    # Issue: Converting an invalid string to an integer
    # Fix: Handle the error or extract the numeric part
    user_input = "abc123"
    try:
        value = int(user_input)
    except ValueError:
        # Extract just the numeric part (if possible)
        numeric_part = ''.join(c for c in user_input if c.isdigit())
        if numeric_part:
            value = int(numeric_part)  # Convert to integer
        else:
            value = 0  # Default value if no digits found
    
    return value

def value_error_example2():
    """Fix the value error in this function."""
    # Error Type: ValueError
    # Issue: Trying to create a list with a negative size
    # Fix: Use a positive size or handle the negative case
    size = -5
    # Ensure size is positive
    if size < 0:
        size = abs(size)  # Convert to positive
    data = [0] * size
    
    return data

# =====================================================================
# PART 6: Attribute Errors
# =====================================================================
# Attribute errors occur when you try to access an attribute or method
# that doesn't exist for an object.

def attribute_error_example1():
    """Fix the attribute error in this function."""
    # Error Type: AttributeError
    # Issue: Calling a method that doesn't exist on the string type
    # Fix: Use a method that is valid for strings or convert to the right type
    text = "Hello, world"
    # Strings don't have append, but they can be concatenated
    text = text + "!"  # Changed to proper string concatenation
    
    return text

def attribute_error_example2(data):
    """Fix the attribute error in this function."""
    # Error Type: AttributeError
    # Issue: Trying to access attributes on a potential None value
    # Fix: Check if data is None before using its methods
    if data is not None and hasattr(data, 'process'):
        result = data.process()
        return result
    else:
        return None  # Return None if data is None or doesn't have the method

# =====================================================================
# PART 7: Import Errors
# =====================================================================
# Import errors occur when you try to import a module that doesn't exist.

# Error Type: ImportError/ModuleNotFoundError
# Issue: Importing a module that doesn't exist or isn't installed
# Fix: Use a try-except block for the import or use an alternative module
try:
    from missing_module import process_data
except ImportError:
    # Define our own process_data function as a fallback
    def process_data(data):
        """Fallback function when the module can't be imported."""
        return [item * 2 for item in data]

def import_error_example():
    """Fix the import error in this function."""
    data = [1, 2, 3, 4, 5]
    result = process_data(data)
    
    return result

# =====================================================================
# PART 8: Logic Errors
# =====================================================================
# Logic errors don't raise exceptions but produce incorrect results.

def logic_error_example1(numbers):
    """Fix the logic error in this function.
    It should return the average of the numbers."""
    # Error Type: Logic Error
    # Issue: Returning the total instead of the average
    # Fix: Return the average instead of the total
    total = sum(numbers)
    average = total / len(numbers) if numbers else 0
    
    return average  # Fixed to return average instead of total

def logic_error_example2(numbers):
    """Fix the logic error in this function.
    It should return only the even numbers from the list."""
    # Error Type: Logic Error
    # Issue: Logic error in filtering even numbers
    # Fix: Correct the condition to check for even numbers
    even_numbers = []
    for num in numbers:
        if num % 2 == 0:  # Changed from 1 to 0 to check for even numbers
            even_numbers.append(num)
    
    return even_numbers

def logic_error_example3(start, end):
    """Fix the logic error in this function.
    It should return a list of numbers from start to end (inclusive)."""
    # Error Type: Logic Error
    # Issue: Off-by-one error
    # Fix: Use range(start, end+1) to include the end value
    result = []
    for i in range(start, end + 1):  # Added +1 to include 'end'
        result.append(i)
    
    return result

# =====================================================================
# PART 9: Exception Handling
# =====================================================================
# This section focuses on properly handling exceptions.

def exception_handling_example1(data):
    """Fix the exception handling in this function.
    It should handle the case where data is not iterable."""
    # Error Type: Too Broad Exception Handling
    # Issue: Catching all exceptions indiscriminately
    # Fix: Catch specific exceptions
    try:
        result = sum(data)
        return result
    except TypeError:  # Catch specific exception (TypeError for non-iterable)
        return 0
    except ValueError:  # Catch another specific possible error
        return 0

def exception_handling_example2(filename):
    """Fix the exception handling in this function.
    It should handle file not found and permission errors differently."""
    # Error Type: Insufficient Exception Handling
    # Issue: Not handling specific exceptions appropriately
    # Fix: Catch specific exceptions with appropriate responses
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except PermissionError:
        return f"Error: No permission to read '{filename}'."
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"

# =====================================================================
# PART 10: Circular References and Resource Management
# =====================================================================
# This section deals with more complex issues.

class Node:
    """A node in a linked list."""
    def __init__(self, value):
        self.value = value
        self.next = None
    
    def __del__(self):
        print(f"Node {self.value} deleted")

def circular_reference_example():
    """Fix the circular reference in this function."""
    # Error Type: Memory Leak due to Circular References
    # Issue: Creating nodes that refer to each other, causing memory leaks
    # Fix: Break the circular reference before the function ends
    node1 = Node(1)
    node2 = Node(2)
    
    # Create a reference but avoid the circular reference
    node1.next = node2
    # Don't create a circular reference
    # node2.next = node1  # This line was the problem
    
    # Alternatively, break the circular reference at the end
    # node1.next = node2
    # node2.next = node1
    # node2.next = None  # Break the circular reference
    
    return "Function completed"

def resource_management_example(filename):
    """Fix the resource management in this function.
    It should properly close the file even if an exception occurs."""
    # Error Type: Resource leak
    # Issue: Not using a context manager for file handling
    # Fix: Use a context manager (with statement)
    try:
        with open(filename, 'r') as file:  # Use context manager
            content = file.read()
            return content
    except FileNotFoundError:
        return f"Error: File {filename} not found."
    except Exception as e:
        return f"Error: {e}"

# =====================================================================
# TEST CODE
# =====================================================================

if __name__ == "__main__":
    print("Testing fixed functions...")
    
    # Test syntax error examples
    print("\nTesting syntax error examples:")
    print(syntax_error_example1())
    print(syntax_error_example2())
    print(syntax_error_example3())
    
    # Test name error examples
    print("\nTesting name error examples:")
    print(name_error_example1())
    print(name_error_example2())
    print(name_error_example3(None))
    
    # Test type error examples
    print("\nTesting type error examples:")
    print(type_error_example1())
    print(type_error_example2(None))
    print(type_error_example3())
    
    # Test index and key error examples
    print("\nTesting index and key error examples:")
    print(index_error_example1())
    print(index_error_example2([]))
    print(index_error_example2([1, 2, 3]))
    print(key_error_example({"name": "John"}))
    
    # Test value error examples
    print("\nTesting value error examples:")
    print(value_error_example1())
    print(value_error_example2())
    
    # Test attribute error examples
    print("\nTesting attribute error examples:")
    print(attribute_error_example1())
    print(attribute_error_example2(None))
    
    # Test import error example
    print("\nTesting import error example:")
    print(import_error_example())
    
    # Test logic error examples
    print("\nTesting logic error examples:")
    print(logic_error_example1([1, 2, 3, 4, 5]))
    print(logic_error_example2([1, 2, 3, 4, 5]))
    print(logic_error_example3(1, 5))
    
    # Test exception handling examples
    print("\nTesting exception handling examples:")
    print(exception_handling_example1(None))
    print(exception_handling_example2("nonexistent_file.txt"))
    
    # Test circular reference and resource management examples
    print("\nTesting circular reference and resource management examples:")
    print(circular_reference_example())
    print(resource_management_example("example.txt"))
    
    print("\nAll tests completed!")

"""
Solution Notes:

This solution demonstrates how to fix various common Python errors:

1. Syntax Errors:
   - Fixed by correcting missing syntax elements like parentheses, colons, and indentation
   - These errors prevent code from running at all and must be fixed first

2. Name Errors:
   - Fixed by ensuring variables are defined before they're used
   - Corrected misspelled variable names
   - Provided default values for missing variables

3. Type Errors:
   - Fixed by performing appropriate type conversions
   - Added checks to handle None values
   - Corrected improper method calls

4. Index and Key Errors:
   - Added bounds checking for list indexing
   - Used .get() method with defaults for dictionary access
   - Added empty collection handling

5. Value Errors:
   - Added validation and error handling for invalid values
   - Implemented fallback strategies when values are inappropriate

6. Attribute Errors:
   - Used proper methods for each data type
   - Added checks for None values before attribute access
   - Used hasattr() to verify attribute existence

7. Import Errors:
   - Added try/except to handle missing modules
   - Provided fallback implementations when imports fail

8. Logic Errors:
   - Corrected algorithmic mistakes
   - Fixed off-by-one errors
   - Corrected improper boolean conditions

9. Exception Handling:
   - Replaced broad except clauses with specific exception handling
   - Added appropriate error messages for different error types
   - Used more structured exception hierarchies

10. Resource Management:
    - Used context managers (with statements) for file operations
    - Fixed circular references to prevent memory leaks
    - Added proper cleanup of resources

Key Debugging Principles Demonstrated:
1. Read error messages carefully to identify the exact issue
2. Understand the different error types and their common causes
3. Add appropriate validation before operations that might fail
4. Use defensive programming techniques to handle edge cases
5. Always manage resources properly with context managers
"""
