# Print Debugging in Python

Welcome to the second module of the Python Debugging & Code Review Masterclass! In this module, we'll explore print debugging - a simple yet powerful technique for understanding program flow and diagnosing issues.

## Learning Objectives

By the end of this module, you will be able to:
- Apply print debugging effectively in your code
- Use formatted print statements for clearer output
- Know when print debugging is appropriate (and when it's not)
- Implement advanced print debugging techniques
- Avoid common print debugging pitfalls

## What is Print Debugging?

Print debugging (sometimes called "printf debugging" after the C function) is the practice of adding print statements to your code to inspect variable values, control flow, and program state during execution.

While it may seem primitive compared to interactive debuggers, print debugging remains one of the most widely used techniques because:
- It requires no special tools or setup
- It works in any environment
- It's easy to understand and implement
- It can be surprisingly effective for many bugs

## Basic Print Debugging Techniques

### 1. Tracing Program Flow

Print statements can help you understand the execution path your program is taking:

```python
def process_user(user_id):
    print("Starting to process user:", user_id)
    
    user = get_user(user_id)
    print("Retrieved user:", user)
    
    if user.is_active:
        print("User is active, processing...")
        process_active_user(user)
    else:
        print("User is inactive, skipping...")
    
    print("Finished processing user:", user_id)
```

### 2. Inspecting Variable Values

Print statements help you see the actual values of variables at runtime:

```python
def calculate_total(items, discount):
    print(f"Items: {items}, Discount: {discount}")
    
    subtotal = sum(item.price for item in items)
    print(f"Subtotal: {subtotal}")
    
    tax = subtotal * 0.1
    print(f"Tax: {tax}")
    
    total = subtotal + tax - discount
    print(f"Final total: {total}")
    
    return total
```

### 3. Debugging Conditional Logic

Print statements can help you understand why certain conditions are (or aren't) being met:

```python
def check_eligibility(user, product):
    print(f"Checking eligibility for {user.name} to purchase {product.name}")
    
    if user.age < product.minimum_age:
        print(f"User age ({user.age}) below minimum age ({product.minimum_age})")
        return False
    
    if user.balance < product.price:
        print(f"Insufficient balance: {user.balance} < {product.price}")
        return False
    
    print("User is eligible")
    return True
```

## Advanced Print Debugging Techniques

### 1. Using Formatted Strings (f-strings)

Python 3.6+ f-strings make print debugging much more readable:

```python
# Instead of this:
print("User:", user, "Age:", user.age, "Balance:", user.balance)

# Use this:
print(f"User: {user.name}, Age: {user.age}, Balance: {user.balance:.2f}")
```

### 2. Creating Distinguishable Output

Make your debug prints stand out:

```python
def debug_print(message, variable=None):
    if variable is not None:
        print(f"[DEBUG] {message}: {variable}")
    else:
        print(f"[DEBUG] {message}")

# Usage
debug_print("Processing item", item.id)
```

### 3. Selective Debugging

Turn debugging on/off without removing prints:

```python
DEBUG = True  # Set to False in production

def debug_print(message):
    if DEBUG:
        print(f"[DEBUG] {message}")

# Usage
debug_print(f"Current value: {value}")
```

### 4. Printing Data Structures

For complex data structures, use better formatting:

```python
import pprint

complex_data = {"users": [...], "products": [...], "stats": {...}}

# Instead of print(complex_data)
pprint.pprint(complex_data)
```

### 5. Print Statements with Context

Include function names, line numbers, or timestamps:

```python
import time
import inspect

def debug_print(message):
    timestamp = time.strftime("%H:%M:%S")
    caller = inspect.currentframe().f_back.f_code.co_name
    line_no = inspect.currentframe().f_back.f_lineno
    print(f"[{timestamp}] {caller}:{line_no} - {message}")
```

## When to Use Print Debugging

Print debugging is most effective when:
- You need a quick understanding of program flow
- You're working in an environment where other debugging tools aren't available
- You're tracking a specific variable's value across function calls
- You're debugging remote systems where interactive debuggers won't work

## When Not to Use Print Debugging

Consider other debugging techniques when:
- The code is complex with many execution paths
- You need to inspect many variables simultaneously
- You want to modify variables during execution
- You need to step through code line by line
- You're working with multi-threaded code
- There's too much output to analyze manually

## Common Pitfalls

1. **Forgetting to remove debug prints**: Always clean up before committing code
2. **Print statement overhead**: Too many prints can affect performance
3. **Buffering issues**: Output might not appear when expected due to buffering
4. **Thread safety**: Print statements aren't thread-safe and can produce interleaved output
5. **Altering program behavior**: The act of printing can sometimes change timing-sensitive code

## Best Practices

1. Use a consistent format for debug messages
2. Create a debug_print function you can easily disable
3. Be specific about what you're printing
4. Don't leave print statements in production code
5. Consider logging as a more robust alternative

## Moving Beyond Print Debugging

While print debugging is valuable, this course will introduce more powerful tools in subsequent modules:
- Python's built-in debugger (pdb)
- VS Code's integrated debugger
- Logging modules
- Assertions and unit tests

## Conclusion

Print debugging remains one of the most accessible and widely used debugging techniques. Mastering it will give you a quick way to gain insight into your code's behavior. In the next module, we'll explore Python's built-in debugger (pdb), which offers more interactive debugging capabilities.

## Further Reading

- [Python's f-strings documentation](https://docs.python.org/3/reference/lexical_analysis.html#f-strings)
- [pprint module documentation](https://docs.python.org/3/library/pprint.html)
- [Python's logging module](https://docs.python.org/3/library/logging.html) for a more robust alternative
