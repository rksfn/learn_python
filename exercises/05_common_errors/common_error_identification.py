"""
Exercise 1: Identifying and Fixing Common Python Errors

In this exercise, you'll practice identifying and fixing various types of common Python errors.
Each section contains code with bugs that represent real-world mistakes developers frequently make.
Your task is to:
1. Identify the type of error
2. Understand why it's occurring
3. Fix the code to make it work correctly

The exercise covers syntax errors, type errors, name errors, and more.
"""

# =====================================================================
# PART 1: Syntax Errors
# =====================================================================
# Syntax errors prevent your code from running at all. Python will show
# an error message pointing to where the syntax is invalid.

def syntax_error_example1():
    """Fix the syntax error in this function."""
    # Bug: Missing closing parenthesis
    print("Hello, world"
    
    return "Function completed"

def syntax_error_example2():
    """Fix the syntax error in this function."""
    # Bug: Invalid syntax in if statement (missing colon)
    x = 10
    if x > 5
        print("x is greater than 5")
    
    return "Function completed"

def syntax_error_example3():
    """Fix the indentation error in this function."""
    # Bug: Incorrect indentation
    def nested_function():
        print("Inside nested function")
    print("This line should be indented")
    
    return nested_function()

# =====================================================================
# PART 2: Name Errors
# =====================================================================
# Name errors occur when you try to use a variable or function that
# doesn't exist in the current scope.

def name_error_example1():
    """Fix the name error in this function."""
    # Bug: Variable used before assignment
    result = initial_value + 10
    initial_value = 5
    
    return result

def name_error_example2():
    """Fix the name error in this function."""
    # Bug: Misspelled variable name
    message = "Hello, world"
    print(mesage)
    
    return "Function completed"

def name_error_example3(data):
    """Fix the name error in this function."""
    # Bug: Using a global variable that doesn't exist
    if data is None:
        data = default_data
    
    return data

# =====================================================================
# PART 3: Type Errors
# =====================================================================
# Type errors occur when an operation is applied to an object of an
# inappropriate type.

def type_error_example1():
    """Fix the type error in this function."""
    # Bug: Adding string and integer
    num = 5
    result = "The number is " + num
    
    return result

def type_error_example2(items):
    """Fix the type error in this function."""
    # Bug: Calling a list method on a potential None value
    if items is None:
        items = []
    
    items.append("new item")
    return items

def type_error_example3():
    """Fix the type error in this function."""
    # Bug: Calling a non-callable object
    data = {"process": "data processing function"}
    result = data["process"]()
    
    return result

# =====================================================================
# PART 4: Index and Key Errors
# =====================================================================
# Index errors occur when you try to access an index that doesn't exist.
# Key errors occur when you try to access a key that doesn't exist in a dict.

def index_error_example1():
    """Fix the index error in this function."""
    # Bug: Accessing an index that doesn't exist
    list_data = [1, 2, 3]
    value = list_data[3]
    
    return value

def index_error_example2(items):
    """Fix the index error in this function to get the last item safely."""
    # Bug: This will fail on an empty list
    last_item = items[-1]
    
    return last_item

def key_error_example(user_data):
    """Fix the key error in this function."""
    # Bug: Accessing a key that might not exist
    user_name = user_data["name"]
    user_email = user_data["email"]
    
    return f"User: {user_name}, Email: {user_email}"

# =====================================================================
# PART 5: Value Errors
# =====================================================================
# Value errors occur when a function receives an argument of the right type
# but an inappropriate value.

def value_error_example1():
    """Fix the value error in this function."""
    # Bug: Converting an invalid string to an integer
    user_input = "abc123"
    value = int(user_input)
    
    return value

def value_error_example2():
    """Fix the value error in this function."""
    # Bug: Trying to create a list with a negative size
    size = -5
    data = [0] * size
    
    return data

# =====================================================================
# PART 6: Attribute Errors
# =====================================================================
# Attribute errors occur when you try to access an attribute or method
# that doesn't exist for an object.

def attribute_error_example1():
    """Fix the attribute error in this function."""
    # Bug: Calling a method that doesn't exist on the string type
    text = "Hello, world"
    text.append("!")
    
    return text

def attribute_error_example2(data):
    """Fix the attribute error in this function."""
    # Bug: Trying to access attributes on a potential None value
    result = data.process()
    
    return result

# =====================================================================
# PART 7: Import Errors
# =====================================================================
# Import errors occur when you try to import a module that doesn't exist.

# Bug: Importing a module that doesn't exist or isn't installed
from missing_module import process_data

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
    # Bug: Logic error in calculating average
    total = sum(numbers)
    average = total / len(numbers)
    
    return total  # Returning the wrong value

def logic_error_example2(numbers):
    """Fix the logic error in this function.
    It should return only the even numbers from the list."""
    # Bug: Logic error in filtering even numbers
    even_numbers = []
    for num in numbers:
        if num % 2 == 1:  # Wrong condition
            even_numbers.append(num)
    
    return even_numbers

def logic_error_example3(start, end):
    """Fix the logic error in this function.
    It should return a list of numbers from start to end (inclusive)."""
    # Bug: Off-by-one error
    result = []
    for i in range(start, end):  # Doesn't include 'end'
        result.append(i)
    
    return result

# =====================================================================
# PART 9: Exception Handling
# =====================================================================
# This section focuses on properly handling exceptions.

def exception_handling_example1(data):
    """Fix the exception handling in this function.
    It should handle the case where data is not iterable."""
    # Bug: Too broad exception clause
    try:
        result = sum(data)
        return result
    except:  # Catches all exceptions, including keyboard interrupts and system exits
        return 0

def exception_handling_example2(filename):
    """Fix the exception handling in this function.
    It should handle file not found and permission errors differently."""
    # Bug: Not handling specific exceptions appropriately
    try:
        with open(filename, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error: {e}"

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
    # Bug: Creating nodes that refer to each other, causing memory leaks
    node1 = Node(1)
    node2 = Node(2)
    node1.next = node2
    node2.next = node1  # Circular reference
    
    return "Function completed"

def resource_management_example(filename):
    """Fix the resource management in this function.
    It should properly close the file even if an exception occurs."""
    # Bug: Not using a context manager for file handling
    file = open(filename, 'r')
    content = file.read()
    # file might not be closed if an exception occurs before this line
    file.close()
    
    return content

# =====================================================================
# TEST CODE
# =====================================================================
# Uncomment the functions you want to test after fixing them

if __name__ == "__main__":
    print("Testing fixed functions...")
    
    # Test syntax error examples
    # print(syntax_error_example1())
    # print(syntax_error_example2())
    # print(syntax_error_example3())
    
    # Test name error examples
    # print(name_error_example1())
    # print(name_error_example2())
    # print(name_error_example3(None))
    
    # Test type error examples
    # print(type_error_example1())
    # print(type_error_example2(None))
    # print(type_error_example3())
    
    # Test index and key error examples
    # print(index_error_example1())
    # print(index_error_example2([]))
    # print(key_error_example({"name": "John"}))
    
    # Test value error examples
    # print(value_error_example1())
    # print(value_error_example2())
    
    # Test attribute error examples
    # print(attribute_error_example1())
    # print(attribute_error_example2(None))
    
    # Test import error example
    # print(import_error_example())
    
    # Test logic error examples
    # print(logic_error_example1([1, 2, 3, 4, 5]))
    # print(logic_error_example2([1, 2, 3, 4, 5]))
    # print(logic_error_example3(1, 5))
    
    # Test exception handling examples
    # print(exception_handling_example1(None))
    # print(exception_handling_example2("nonexistent_file.txt"))
    
    # Test circular reference and resource management examples
    # print(circular_reference_example())
    # print(resource_management_example("example.txt"))
    
    print("All tests completed!")

"""
Exercise Instructions:

1. Work through each part, one function at a time
2. For each function:
   a. Run it and observe the error
   b. Identify the error type and cause
   c. Fix the code to eliminate the error
   d. Test your solution by uncommenting the function call in the test section

3. For logic errors, verify that the function produces the correct results

4. Keep notes about:
   - The error types you encountered
   - How you identified the cause
   - What you learned from fixing each issue

5. After fixing all the bugs, consider how you might prevent similar errors in the future:
   - What coding practices could help?
   - What kinds of tests would catch these errors?
   - How could documentation have helped?

Bonus Challenge:
- Try to come up with additional examples of each error type from your own experience
- Create a "debugging cheat sheet" listing error types and common solutions
"""
