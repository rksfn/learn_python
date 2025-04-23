"""
Exercise 1: Bug Identification and Classification

In this exercise, you'll analyze a collection of buggy code snippets.
For each snippet:
1. Identify the bug(s)
2. Classify the bug type (syntax, runtime, logical, performance)
3. Explain what's wrong
4. Fix the code

This will help you recognize common patterns of bugs and develop your debugging intuition.
"""

# Bug 1: What's wrong with this function that calculates the average of a list?
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# Test Bug 1
try:
    print("Average test 1:", calculate_average([1, 2, 3, 4, 5]))
    print("Average test 2:", calculate_average([]))  # This will cause a problem
except Exception as e:
    print(f"Error in calculate_average: {e}")


# Bug 2: This function is supposed to remove duplicates from a list
def remove_duplicates(items):
    unique_items = []
    for item in items:
        if not item in unique_items:
            unique_items.append(item)
    return unique_items

# Test Bug 2
print("\nRemove duplicates test:", remove_duplicates([1, 2, 2, 3, 4, 4, 5]))


# Bug 3: This function should return True if a string is a palindrome
def is_palindrome(text):
    text = text.lower()
    return text == text.reverse()

# Test Bug 3
try:
    print("\nPalindrome test 1:", is_palindrome("radar"))
    print("Palindrome test 2:", is_palindrome("hello"))
except Exception as e:
    print(f"Error in is_palindrome: {e}")


# Bug 4: This function should count words in a string
def count_words(sentence):
    return len(sentence.split())

# Test Bug 4
print("\nWord count test:", count_words("This is a    test with   multiple spaces"))


# Bug 5: This function is supposed to find the largest number divisible by 3 in a list
def largest_divisible_by_3(numbers):
    largest = 0
    for num in numbers:
        if num % 3 == 0 and num > largest:
            largest = num
    return largest

# Test Bug 5
print("\nLargest divisible by 3:", largest_divisible_by_3([1, 2, 3, 6, 9, 4, 15, 12]))
print("Largest divisible by 3:", largest_divisible_by_3([1, 2, 4, 5, 7, 8]))


# --------------------------------
# Your task:
# 1. Run this script and observe the bugs
# 2. For each bug, determine what type it is (syntax, runtime, logical, performance)
# 3. Fix each bug and explain your solution
# 4. Consider: Are there any edge cases still not handled?
# --------------------------------

# After fixing, use this code to verify your solutions:
def verify_solutions():
    print("\n--- Verification Tests ---")
    
    # Bug 1 verification
    try:
        assert calculate_average([1, 2, 3, 4, 5]) == 3
        assert calculate_average([10]) == 10
        calculate_average([])  # Should handle empty lists
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
    print("Bug 5 fixed correctly!")

# Uncomment to verify your solutions
# verify_solutions()
