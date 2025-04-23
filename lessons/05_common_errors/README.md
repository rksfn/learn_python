# Common Python Errors and Debugging Strategies

Welcome to the fifth module of the Python Debugging & Code Review Masterclass! In this module, we'll explore the most common Python errors, understand their causes, and develop strategies to fix them efficiently.

## Learning Objectives

By the end of this module, you will be able to:
- Identify and understand Python's main error types
- Interpret error messages and tracebacks effectively
- Apply targeted strategies to fix different categories of errors
- Anticipate and prevent common errors through defensive programming
- Resolve challenging errors such as circular imports and memory issues

## Understanding Python Error Messages

Python's error messages may seem cryptic at first, but they contain valuable information to help you diagnose problems:

### Anatomy of a Traceback

```
Traceback (most recent call last):
  File "script.py", line 10, in <module>
    result = calculate_average(data)
  File "script.py", line 5, in calculate_average
    total = sum(values)
TypeError: 'NoneType' object is not iterable
```

A traceback includes:
1. **The call stack**: Shows the sequence of function calls leading to the error
2. **File and line information**: Points to specific locations in the code
3. **Error type**: Identifies the category of the error (e.g., TypeError)
4. **Error message**: Provides specific details about what went wrong

Reading tracebacks from bottom to top helps identify the immediate cause of the error, while the stack trace shows how the program reached that point.

## Common Python Error Types

### 1. Syntax Errors

Syntax errors occur when your code violates Python's grammar rules.

```python
# Missing closing parenthesis
print("Hello, world"
```

**Key characteristics:**
- Prevents the program from running
- Often includes a caret (^) pointing to the approximate location of the issue
- Usually detected by the parser before execution

**Common causes:**
- Missing parentheses, brackets, or colons
- Incorrect indentation
- Mismatched quotes
- Invalid variable names

### 2. IndentationError

A special type of syntax error in Python related to improper indentation.

```python
def function():
print("This line is not indented")
```

**Common causes:**
- Missing indentation after function/class definitions or control flow statements
- Mixing tabs and spaces
- Inconsistent indentation levels

### 3. NameError

Occurs when trying to access a variable or function that doesn't exist in the current scope.

```python
# variable_name doesn't exist
print(variable_name)
```

**Common causes:**
- Misspelling variable/function names
- Using variables before they're defined
- Forgetting to import necessary modules
- Issues with variable scope

### 4. TypeError

Occurs when an operation is performed on an incompatible data type.

```python
# Cannot add a string and an integer
result = "5" + 5
```

**Common causes:**
- Mixing incompatible data types in operations
- Calling methods on incorrect types
- Passing wrong argument types to functions
- Using a non-callable object as a function

### 5. ValueError

Occurs when a function receives an argument of the correct type but with an inappropriate value.

```python
# Cannot convert "hello" to an integer
int("hello")
```

**Common causes:**
- Numeric conversion of non-numeric strings
- Out-of-range values for functions with restricted domains
- Invalid arguments to functions that expect specific values

### 6. IndexError and KeyError

- **IndexError**: Occurs when trying to access an index that doesn't exist in a sequence
- **KeyError**: Occurs when trying to access a non-existent key in a dictionary

```python
# List has only 3 elements, no index 3
my_list = [1, 2, 3]
print(my_list[3])

# Dictionary has no key "d"
my_dict = {"a": 1, "b": 2, "c": 3}
print(my_dict["d"])
```

**Common causes:**
- Off-by-one errors (forgetting that indices start at 0)
- Failing to check if an index/key exists before accessing it
- Typos in keys
- Misunderstanding the size/structure of the data

### 7. AttributeError

Occurs when trying to access an attribute or method that doesn't exist for an object.

```python
# Strings don't have an append method
"hello".append("world")
```

**Common causes:**
- Calling methods that don't exist for a particular type
- Misspelling attribute/method names
- Using methods from one class on objects of another class
- Attempting to use attributes of None

### 8. ImportError and ModuleNotFoundError

Occurs when there are problems importing modules.

```python
# Module doesn't exist or isn't in the Python path
import non_existent_module
```

**Common causes:**
- Misspelling module names
- Module not installed
- Module not in the Python path
- Circular imports

### 9. FileNotFoundError

Occurs when trying to open a file that doesn't exist.

```python
# File doesn't exist
with open("non_existent_file.txt", "r") as file:
    content = file.read()
```

**Common causes:**
- Incorrect file paths
- Misspelling file names
- File permissions issues
- Working with relative paths incorrectly

### 10. ZeroDivisionError

Occurs when dividing by zero.

```python
# Cannot divide by zero
result = 10 / 0
```

**Common causes:**
- Division by zero or modulo by zero
- Not validating denominators before division
- Unexpected zero values in calculations

## Less Common But Challenging Errors

### 1. RecursionError

Occurs when a function calls itself too many times, exceeding Python's recursion limit.

```python
def recursive_function():
    # No base case to stop recursion
    return recursive_function()
```

### 2. MemoryError

Occurs when an operation runs out of memory.

```python
# Creates a huge list that may exhaust memory
huge_list = [0] * 10**10
```

### 3. RuntimeError

A generic error for situations that don't fit other categories.

### 4. UnboundLocalError

A special case of NameError that occurs when trying to use a local variable before it's assigned.

```python
def function():
    # Tries to modify x before defining it
    x += 1
    print(x)
```

## Debugging Strategies by Error Type

### For Syntax Errors and IndentationErrors

1. Look at the line indicated in the error message
2. Check for missing or extra punctuation 
3. Verify proper indentation (4 spaces per level by convention)
4. Make sure brackets, parentheses, and quotes are balanced
5. Use an editor with syntax highlighting to spot issues

### For NameErrors and AttributeErrors

1. Check for typos in variable/attribute names
2. Verify the variable is defined before use
3. Check import statements
4. Review variable scope (are you trying to access a local variable from outside its function?)
5. Print `dir(object)` to see all available attributes

### For TypeErrors and ValueErrors

1. Check the types of your variables with `print(type(var))`
2. Make sure you're converting types appropriately before operations
3. Review function documentation for expected argument types
4. Add explicit type conversions where needed
5. Use defensive programming with type checking

### For IndexErrors and KeyErrors

1. Check the length of lists/strings before accessing elements
2. Use `in` to test if a key exists in a dictionary
3. Use `get()` method for dictionaries to provide default values
4. Be mindful of zero-based indexing
5. For complex data structures, print the structure to verify its shape

### For ImportErrors

1. Verify the module is installed (use `pip list`)
2. Check for typos in the import statement
3. Make sure the module is in the Python path
4. Restructure code to avoid circular imports
5. Consider using relative imports in packages

### For FileNotFoundErrors

1. Print the full file path you're trying to access
2. Check file permissions
3. Use `os.path.exists()` before opening files
4. Use absolute paths instead of relative paths when possible
5. Understand how relative paths work from the execution context

## Prevention Techniques

### Defensive Programming

1. **Validate inputs**: Check arguments before processing them
2. **Use assertions**: Add assertions to verify assumptions
3. **Handle edge cases**: Consider empty collections, None values, and other edge cases
4. **Add type hints**: Use Python's type hinting to clarify expected types

```python
def calculate_average(values: list[float]) -> float:
    """Calculate the average of a list of numbers."""
    if not values:
        return 0.0
    return sum(values) / len(values)
```

### Using try-except Blocks Effectively

```python
try:
    value = int(user_input)
except ValueError:
    print("Please enter a valid number")
    value = 0
```

Best practices:
1. Only catch specific exceptions, not all exceptions
2. Keep try blocks as small as possible
3. Don't hide errors that indicate real bugs
4. Use the exception information to provide helpful error messages

### Using Logging Instead of Print

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_data(data):
    logger.info(f"Processing {len(data)} items")
    try:
        result = [item.process() for item in data]
        logger.info("Processing successful")
        return result
    except AttributeError as e:
        logger.error(f"Processing failed: {e}")
        return []
```

Logging advantages:
1. Can be enabled/disabled without code changes
2. Includes timestamps and contextual information
3. Can log to files, not just console
4. Has different severity levels

## Investigating Challenging Errors

### Dealing with Circular Imports

1. Restructure your modules
2. Move imports inside functions
3. Use import statements at the end of the module
4. Create a new module for shared functionality

### Memory Issues

1. Handle large files in chunks
2. Use generators for large data processing
3. Implement proper cleanup for resources
4. Profile memory usage with tools like `memory_profiler`

### Strange Behavior Without Errors

1. Add print statements to confirm values and flow
2. Check for logic errors
3. Look for side effects from functions
4. Consider threading/concurrency issues
5. Verify inputs from external sources

## Conclusion

Understanding Python's error types and messages is a powerful debugging skill. By recognizing common patterns and applying targeted strategies for each error type, you can resolve issues more quickly and write more robust code.

In the next module, we'll apply these concepts to real-world debugging scenarios, combining the tools and techniques from all previous modules.

## Further Reading

- [Python Exceptions Documentation](https://docs.python.org/3/library/exceptions.html)
- [The Python Standard Library - logging](https://docs.python.org/3/library/logging.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Effective Python: 90 Specific Ways to Write Better Python](https://effectivepython.com/)
