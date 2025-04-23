"""
Exercise 1: Basic Print Debugging

In this exercise, you'll practice using print statements to debug a function 
that's supposed to calculate the Fibonacci sequence but has a logical error.

Your tasks:
1. Run the code and observe the incorrect output
2. Add print statements to trace the execution and identify the issue
3. Fix the bug
4. Refactor your debugging prints into a reusable debug_print() function
"""

def fibonacci(n):
    """Calculate the first n numbers in the Fibonacci sequence."""
    result = []
    for i in range(n):
        if i <= 1:
            result.append(i)
        else:
            # Calculate next Fibonacci number
            next_fib = result[i-1] + result[i-2]
            result.append(next_fib)
    return result

# Test the function
print("First 10 Fibonacci numbers:", fibonacci(10))
# Expected: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

"""
Questions to consider:
1. What variable values would be most helpful to print?
2. At what points in the code should you add print statements?
3. How can you format your debug output to make it more readable?
4. How would you create a debug_print() function that can be easily disabled?
"""
