"""
Exercise 1 Solution: Bug Identification and Classification

This file contains solutions and explanations for the five bugs in bug_identification.py.
"""

# Bug 1: Division by Zero Error (Runtime Error)
# Problem: The function tries to divide by the length of the list, which causes a ZeroDivisionError 
# when the list is empty.
# Solution: Add a check for empty lists

def calculate_average(numbers):
    if not numbers:  # Check if the list is empty
        return 0  # Or return None, or raise a custom exception
    
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# Test Bug 1 Fix
print("Average test 1:", calculate_average([1, 2, 3, 4, 5]))
print("Average test 2 (empty list):", calculate_average([]))


# Bug 2: No Bug, But Inefficient (Performance Issue)
# Problem: The code works correctly but is inefficient for larger lists
# because 'in' operation on lists has O(n) time complexity.
# Solution: Use a set for faster lookups

def remove_duplicates(items):
    # One-liner using a set (much more efficient)
    # return list(set(items))  # This works but doesn't preserve order
    
    # If order matters:
    unique_items = []
    seen = set()  # Using a set for O(1) lookups
    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)
    return unique_items

# Test Bug 2 Fix
print("\nRemove duplicates test:", remove_duplicates([1, 2, 2, 3, 4, 4, 5]))


# Bug 3: AttributeError (Runtime Error)
# Problem: Strings don't have a 'reverse' method; we need to use slicing
# Solution: Use string slicing with [::-1] to reverse

def is_palindrome(text):
    text = text.lower()
    return text == text[::-1]  # Use slicing to reverse the string

# Test Bug 3 Fix
print("\nPalindrome test 1:", is_palindrome("radar"))
print("Palindrome test 2:", is_palindrome("hello"))


# Bug 4: Logical Error
# Problem: Multiple spaces between words are not handled correctly
# Solution: Use a more robust word counting approach

def count_words(sentence):
    # Split by any number of whitespace characters and filter out empty strings
    words = [word for word in sentence.split() if word]
    return len(words)

# Test Bug 4 Fix
print("\nWord count test:", count_words("This is a    test with   multiple spaces"))


# Bug 5: Logical Error
# Problem: If there are negative numbers divisible by 3, they won't be found
# because we initialize largest to 0. Also, if no number is divisible by 3,
# it incorrectly returns 0 (which might not be in the list).
# Solution: Initialize largest to None and handle this special case

def largest_divisible_by_3(numbers):
    largest = None
    for num in numbers:
        if num % 3 == 0 and (largest is None or num > largest):
            largest = num
    # Return 0 or another default value if no number is divisible by 3
    return largest if largest is not None else 0

# Test Bug 5 Fix
print("\nLargest divisible by 3:", largest_divisible_by_3([1, 2, 3, 6, 9, 4, 15, 12]))
print("Largest divisible by 3:", largest_divisible_by_3([1, 2, 4, 5, 7, 8]))
print("Largest divisible by 3 (with negatives):", largest_divisible_by_3([-3, -6, 1, 2]))


# Verification
def verify_solutions():
    print("\n--- Verification Tests ---")
    
    # Bug 1 verification
    try:
        assert calculate_average([1, 2, 3, 4, 5]) == 3
        assert calculate_average([10]) == 10
        assert calculate_average([]) == 0  # Should handle empty lists
        print("Bug 1 fixed correctly!")
    except Exception as e:
        print(f"Bug 1 still has issues: {e}")
    
    # Bug 2 verification
    assert remove_duplicates([1, 2, 2, 3, 4, 4, 5]) == [1, 2, 3, 4, 5]
    assert remove_duplicates([]) == []
    print("Bug 2 fixed correctly!")
    
    # Bug 3 verification
    assert is_palindrome("radar") == True
    assert is_palindrome("Radar") == True  # Case insensitivity
    assert is_palindrome("hello") == False
    print("Bug 3 fixed correctly!")
    
    # Bug 4 verification
    assert count_words("This is a test") == 4
    assert count_words("This is a    test with   multiple spaces") == 6
    print("Bug 4 fixed correctly!")
    
    # Bug 5 verification
    assert largest_divisible_by_3([1, 2, 3, 6, 9, 4, 15, 12]) == 15
    assert largest_divisible_by_3([1, 2, 4, 5, 7, 8]) == 0  # No numbers divisible by 3
    assert largest_divisible_by_3([-3, -6, 1, 2]) == -3  # Test with negative numbers
    print("Bug 5 fixed correctly!")

# Run verification
verify_solutions()

"""
Summary of Bug Types Found:

1. Bug 1: Runtime Error (Division by Zero)
   - Failing to check for edge cases (empty list)
   
2. Bug 2: Performance Issue
   - Not a bug in terms of functionality, but inefficient for large datasets
   - Using O(n) operations when O(1) operations would work
   
3. Bug 3: Runtime Error (AttributeError)
   - Using a non-existent method (common when confusing different data types)
   
4. Bug 4: Logical Error
   - Produces incorrect results for certain inputs
   - Doesn't properly handle multiple spaces
   
5. Bug 5: Logical Error with Edge Cases
   - Incorrect initialization leading to edge case failures
   - Negative numbers weren't handled correctly
   
Debugging lessons learned:
1. Always consider edge cases
2. Be aware of the methods available for different data types
3. Test with diverse inputs
4. Consider performance implications
5. Initialize variables carefully
"""
