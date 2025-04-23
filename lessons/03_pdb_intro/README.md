# Python Debugger (pdb)

Welcome to the third module of the Python Debugging & Code Review Masterclass! In this module, we'll explore Python's built-in debugger (pdb) - a powerful interactive tool for understanding and fixing issues in your code.

## Learning Objectives

By the end of this module, you will be able to:
- Use the Python debugger (pdb) to inspect and control program execution
- Set breakpoints and navigate through code execution
- Examine and modify variables during debugging
- Use post-mortem debugging to analyze crashes
- Understand when to use pdb versus print debugging

## Introduction to pdb

While print debugging is useful, it has limitations. The Python debugger (pdb) offers a more interactive approach:

- **Step through code** line by line
- **Inspect variables** at any point during execution
- **Modify values** on the fly
- **Set conditional breakpoints** that trigger only under specific conditions
- **Continue execution** until the next breakpoint

Pdb is part of the Python standard library, so you don't need to install anything extra to use it.

## Getting Started with pdb

### Method 1: Programmatic Breakpoints

You can insert a breakpoint directly in your code:

```python
import pdb

def calculate_total(items):
    subtotal = sum(item.price for item in items)
    pdb.set_trace()  # The debugger will stop here when reached
    tax = subtotal * 0.1
    total = subtotal + tax
    return total
```

In Python 3.7+, you can use the built-in `breakpoint()` function instead:

```python
def calculate_total(items):
    subtotal = sum(item.price for item in items)
    breakpoint()  # Equivalent to pdb.set_trace()
    tax = subtotal * 0.1
    total = subtotal + tax
    return total
```

### Method 2: Running a Script with pdb

You can run an entire script under the debugger:

```bash
python -m pdb myscript.py
```

This will start the debugger and stop at the first line of the script.

### Method 3: Post-Mortem Debugging

If your program crashes, you can analyze the state at the time of the crash:

```python
try:
    # Some code that might raise an exception
    result = complicated_function()
except Exception:
    import pdb
    pdb.post_mortem()  # Start the debugger at the point of the exception
```

## Basic pdb Commands

Once the debugger is active, you'll see a prompt `(Pdb)` where you can enter commands:

| Command | Description |
|---------|-------------|
| `h` or `help` | Show help |
| `l` or `list` | Show the current line and context |
| `n` or `next` | Execute the current line and move to the next one (step over) |
| `s` or `step` | Step into a function call |
| `c` or `continue` | Continue execution until a breakpoint is hit |
| `q` or `quit` | Quit the debugger |
| `p expression` | Print the value of an expression |
| `pp expression` | Pretty-print the value of an expression |
| `w` or `where` | Show the call stack |
| `b` or `break` | Set a breakpoint |
| `r` or `return` | Continue execution until the current function returns |

## Advanced pdb Usage

### Setting Breakpoints

```
(Pdb) b 42                  # Set breakpoint at line 42
(Pdb) b module.py:42        # Set breakpoint in module.py, line 42
(Pdb) b function_name       # Break when entering function_name
(Pdb) b module.py:function  # Break when entering function in module.py
```

### Conditional Breakpoints

You can set breakpoints that only trigger when a condition is met:

```
(Pdb) b 42, total > 1000    # Break at line 42 only if total > 1000
```

### Examining Variables

```
(Pdb) p variable_name       # Print a variable's value
(Pdb) pp complex_object     # Pretty-print a complex object
(Pdb) locals()              # Show all local variables
```

### Modifying Variables

You can change variables while debugging:

```
(Pdb) !variable_name = new_value  # Change a variable's value
```

### Navigating the Call Stack

```
(Pdb) w                     # Show the call stack
(Pdb) u                     # Move up one level in the call stack
(Pdb) d                     # Move down one level in the call stack
```

## Using pdb Effectively

### Debugging Workflow with pdb

1. **Set a breakpoint** near where you suspect the problem is
2. **Run the program** until it hits your breakpoint
3. **Step through the code** line by line, examining variables
4. **Identify the issue** by finding unexpected values or behavior
5. **Modify variables** if needed to test hypotheses
6. **Continue execution** to see if your changes fix the issue

### Best Practices

- Start with breakpoints close to where you suspect the problem
- Use `next` (step over) most of the time, and `step` (step into) when you need to investigate a function
- Use `continue` to skip ahead to interesting parts of the code
- Remember that you can run any Python expression in the debugger
- Use `where` to understand how you got to the current point in execution

### When to Use pdb vs. Print Debugging

Use **pdb** when:
- You need to explore code execution interactively
- You want to examine multiple variables at specific points
- You need to modify variables during execution
- The bug is complex or hard to track with print statements

Use **print debugging** when:
- You just need a quick view of a few values
- You're debugging remote code or production systems
- You need to log values over time or across multiple runs
- You want to leave lightweight debugging in place

## Common Debugging Scenarios with pdb

### Scenario 1: Finding a Logic Error

```python
def calculate_discount(order_total, customer_type):
    if customer_type == "regular":
        if order_total >= 100:
            return order_total * 0.1
        else:
            return 0
    elif customer_type == "premium":
        if order_total >= 50:
            return order_total * 0.15
        else:
            return order_total * 0.05
    else:
        return 0

# Debug by setting a breakpoint and checking the discount calculation
breakpoint()
discount = calculate_discount(75, "premium")
final_price = 75 - discount
```

### Scenario 2: Debugging a Exception

```python
data = [{"name": "Item 1", "price": 10.0}, {"name": "Item 2"}]

def calculate_total(items):
    total = 0
    for item in items:
        total += item["price"]  # Will raise KeyError for Item 2
    return total

try:
    result = calculate_total(data)
except Exception:
    import pdb
    pdb.post_mortem()  # Examine the state at the time of the error
```

## Conclusion

The Python debugger is a powerful tool that allows you to interactively explore your code's execution. By mastering pdb, you'll be able to solve complex issues more efficiently than with print debugging alone.

In the next module, we'll explore VS Code's integrated debugger, which provides a graphical interface for many of the same debugging capabilities.

## Further Reading

- [Python pdb Documentation](https://docs.python.org/3/library/pdb.html)
- ["Python Debugging With Pdb" tutorial on Real Python](https://realpython.com/python-debugging-pdb/)
- [PDB Commands Reference](https://docs.python.org/3/library/pdb.html#debugger-commands)
