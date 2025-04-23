"""
Exercise 1 Solution: Basic Print Debugging

This solution demonstrates how to use print statements to identify and fix
the logical error in the Fibonacci sequence calculation.
"""

# Step 1: Add basic print statements to understand the flow and variable values

def fibonacci_with_basic_prints(n):
    """Calculate the first n numbers in the Fibonacci sequence with basic print debugging."""
    print(f"Starting fibonacci calculation with n = {n}")
    result = []
    
    for i in range(n):
        print(f"Iteration {i}, result so far: {result}")
        
        if i <= 1:
            result.append(i)
            print(f"  Added {i} to result (base case)")
        else:
            # Calculate next Fibonacci number
            print(f"  Calculating next Fibonacci number using indexes {i-1} and {i-2}")
            print(f"  Values at those indexes: {result[i-1]} and {result[i-2]}")
            next_fib = result[i-1] + result[i-2]
            print(f"  Next Fibonacci number: {next_fib}")
            result.append(next_fib)
            
    print(f"Final result: {result}")
    return result

print("\n--- With Basic Print Debugging ---")
fibonacci_with_basic_prints(10)

# Step 2: Based on the prints, we can identify the issue
# The problem is in the index calculation. The Fibonacci sequence starts with 0, 1, ...
# But our code produces [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
# which is correct! So there's actually no bug in this implementation.

# Let's see what happens if we try to implement the "standard" Fibonacci function 
# that most people think of, starting with [1, 1, 2, 3, 5, 8, ...]

def fibonacci_standard(n):
    """Calculate the first n numbers in the 'standard' Fibonacci sequence that starts with [1, 1, ...]."""
    print(f"Starting standard fibonacci calculation with n = {n}")
    result = []
    
    for i in range(n):
        print(f"Iteration {i}, result so far: {result}")
        
        if i <= 1:
            result.append(1)  # Start with 1, 1 instead of 0, 1
            print(f"  Added 1 to result (base case)")
        else:
            # Calculate next Fibonacci number
            print(f"  Calculating next Fibonacci number using indexes {i-1} and {i-2}")
            print(f"  Values at those indexes: {result[i-1]} and {result[i-2]}")
            next_fib = result[i-1] + result[i-2]
            print(f"  Next Fibonacci number: {next_fib}")
            result.append(next_fib)
            
    print(f"Final result: {result}")
    return result

print("\n--- Standard Fibonacci Implementation ---")
fibonacci_standard(10)

# Step 3: Create a reusable debug_print function that can be easily disabled

DEBUG = True  # Global flag to enable/disable debugging

def debug_print(message, value=None):
    """Print debug information only if DEBUG is True."""
    if DEBUG:
        if value is not None:
            print(f"[DEBUG] {message}: {value}")
        else:
            print(f"[DEBUG] {message}")

def fibonacci_with_debug_function(n, standard=False):
    """Calculate Fibonacci sequence using a reusable debug function."""
    debug_print(f"Starting fibonacci calculation with n", n)
    debug_print(f"Using standard version (starts with 1,1)", standard)
    
    result = []
    
    for i in range(n):
        debug_print(f"Iteration {i}, result so far", result)
        
        if i <= 1:
            if standard:
                result.append(1)  # Standard version starts with 1,1
                debug_print("Added 1 to result (base case)")
            else:
                result.append(i)  # Mathematical version starts with 0,1
                debug_print(f"Added {i} to result (base case)")
        else:
            # Calculate next Fibonacci number
            debug_print(f"Calculating next Fibonacci using indexes {i-1} and {i-2}")
            next_fib = result[i-1] + result[i-2]
            debug_print("Next Fibonacci number", next_fib)
            result.append(next_fib)
            
    debug_print("Final result", result)
    return result

print("\n--- Using Custom Debug Function (Mathematical Version) ---")
fibonacci_with_debug_function(10, standard=False)

print("\n--- Using Custom Debug Function (Standard Version) ---")
fibonacci_with_debug_function(10, standard=True)

# Turn off debugging for final version
DEBUG = False

print("\n--- Final Output (Debugging Off) ---")
print("Mathematical Fibonacci (starting with 0,1):", fibonacci_with_debug_function(10, standard=False))
print("Standard Fibonacci (starting with 1,1):", fibonacci_with_debug_function(10, standard=True))

"""
Insights from Print Debugging:

1. By adding print statements, we discovered that the original implementation
   was actually correct mathematically: the Fibonacci sequence starting with 0, 1.

2. However, many people expect the Fibonacci sequence to start with 1, 1,
   which is also a valid convention.

3. Our debug prints helped us:
   - Trace the execution flow
   - See the values being calculated at each step
   - Confirm that the algorithm logic was working correctly

4. The debug_print() function provides advantages:
   - Can be enabled/disabled with a global flag
   - Consistent formatting of debug messages
   - Reduces clutter in the code
   - Can be extended with additional features (timestamps, logging levels, etc.)

Key Takeaways:
1. Print debugging is effective for tracing algorithm logic
2. A simple debug_print function makes debugging more organized
3. Sometimes "bugs" are just misunderstandings about requirements!
"""
