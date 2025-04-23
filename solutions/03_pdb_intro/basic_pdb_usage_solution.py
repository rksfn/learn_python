"""
Exercise 1 Solution: Getting Started with pdb

This solution demonstrates how to use Python's built-in debugger (pdb) to find
and fix bugs in the receipt generator program.
"""

def calculate_discounted_price(prices, discount_percentage):
    """
    Calculate the discounted price for each item in the prices list.
    
    Args:
        prices: List of original prices
        discount_percentage: Percentage discount to apply (e.g., 10 for 10%)
        
    Returns:
        List of discounted prices
    """
    # BUG FIX 1: Convert string discount percentage to float
    # Adding type checking and conversion
    if isinstance(discount_percentage, str):
        try:
            discount_percentage = float(discount_percentage)
        except ValueError:
            raise ValueError("Discount percentage must be a number")
    
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError("Discount percentage must be between 0 and 100")
    
    discounted_prices = []
    
    for price in prices:
        # Calculate discount amount
        discount_amount = price * discount_percentage / 100
        
        # Apply discount
        discounted_price = price - discount_amount
        
        # Round to 2 decimal places
        discounted_price = round(discounted_price, 2)
        
        discounted_prices.append(discounted_price)
    
    return discounted_prices


def calculate_total(prices):
    """
    Calculate the total price of all items.
    
    Args:
        prices: List of prices
        
    Returns:
        Total price
    """
    total = 0
    
    for price in prices:
        total += price
    
    return total


def generate_receipt(items, prices, discount_percentage=0):
    """
    Generate a receipt with item details and totals.
    
    Args:
        items: List of item names
        prices: List of original prices
        discount_percentage: Percentage discount to apply (default: 0)
        
    Returns:
        A formatted receipt as a string
    """
    if len(items) != len(prices):
        raise ValueError("Items and prices must have the same length")
    
    # BUG FIX 2: Handle empty lists
    if not items:
        return "RECEIPT\n----------------------------------------\nNo items\n----------------------------------------\nTotal: $0.00"
    
    # Calculate discounted prices
    discounted_prices = calculate_discounted_price(prices, discount_percentage)
    
    # Calculate totals
    original_total = calculate_total(prices)
    discounted_total = calculate_total(discounted_prices)
    
    # Build receipt
    receipt = []
    receipt.append("RECEIPT")
    receipt.append("-" * 40)
    
    # Add items
    for i in range(len(items)):
        item = items[i]
        original_price = prices[i]
        discounted_price = discounted_prices[i]
        
        if discount_percentage > 0:
            receipt.append(f"{item}: ${original_price:.2f} -> ${discounted_price:.2f}")
        else:
            receipt.append(f"{item}: ${original_price:.2f}")
    
    receipt.append("-" * 40)
    
    # Add totals
    if discount_percentage > 0:
        savings = original_total - discounted_total
        receipt.append(f"Original Total: ${original_total:.2f}")
        receipt.append(f"Discount: {discount_percentage}%")
        receipt.append(f"You Save: ${savings:.2f}")
        receipt.append(f"Final Total: ${discounted_total:.2f}")
    else:
        receipt.append(f"Total: ${original_total:.2f}")
    
    return "\n".join(receipt)


# Test Cases with pdb debugging comments

# Test Case 1: No discount
def test_case_1():
    # No issues with this test case
    items1 = ["Apple", "Banana", "Orange"]
    prices1 = [1.20, 0.50, 0.75]
    print(generate_receipt(items1, prices1))

# Test Case 2: With discount
def test_case_2():
    # This test case runs correctly
    items2 = ["Laptop", "Mouse", "Keyboard"]
    prices2 = [1000, 25.50, 45.99]
    print("\n" + generate_receipt(items2, prices2, 15))  # 15% discount

# Test Case 3: Empty list
def test_case_3():
    # BUG: Original code didn't handle empty lists well
    # Using pdb, we would step through and see the issue when checking
    # the result of calculate_discounted_price with an empty list
    items3 = []
    prices3 = []
    discount3 = 20  # 20% discount
    
    # With pdb:
    # import pdb; pdb.set_trace()
    # Or in Python 3.7+: breakpoint()
    
    # Step through with 'n' to see that empty lists are handled properly
    print("\n" + generate_receipt(items3, prices3, discount3))

# Test Case 4: String discount
def test_case_4():
    # BUG: Original code didn't handle string discount
    # Using pdb to debug this:
    # - Set breakpoint before this call
    # - Step into calculate_discounted_price with 's'
    # - Observe the discount_percentage type is str
    # - Step through the error
    
    items4 = ["Chair", "Table", "Lamp"]
    prices4 = [49.99, 149.99, 29.99]
    discount4 = "25"  # String instead of number!
    
    # With pdb debugging:
    # breakpoint()
    
    try:
        print("\n" + generate_receipt(items4, prices4, discount4))
    except Exception as e:
        print(f"Error: {e}")


"""
Debugging Process and Bug Fixes:

1. Bug #1: String Discount Percentage
   - When running Test Case 4 with the debugger, stepping into calculate_discounted_price,
     we could see that discount_percentage was a string "25" instead of a number.
   - Observed behavior: TypeError when trying to use string in calculation
   - Fix: Added type checking and conversion at the beginning of calculate_discounted_price

   Debugging commands used:
   - breakpoint() before the test case
   - n (next) to step through the code
   - s (step) to step into the calculate_discounted_price function
   - p type(discount_percentage) to check the variable type
   - p discount_percentage to inspect the value

2. Bug #2: Empty List Handling
   - When examining Test Case 3 with the debugger, we noticed calculate_total was 
     correctly handling empty lists, but the receipt formatting wasn't optimal.
   - Fix: Added a special case for empty receipts at the beginning of generate_receipt

   Debugging commands used:
   - breakpoint() before the test case
   - n (next) to step through the code
   - s (step) to step into functions
   - p len(items) to check list length
   - r (return) to see function return values

3. Additional improvements:
   - Added better error handling for invalid discount percentages
   - Improved type checking and conversion
   - Added docstrings for better code understanding

Using pdb effectively:
1. Start by adding a breakpoint before the suspected problem area
2. Use 'n' to step through code execution line by line
3. Use 's' to step into functions when you need to investigate deeper
4. Use 'p' to examine variable values at any point
5. Use 'r' to continue until the current function returns
6. Use 'c' to continue to the next breakpoint or until completion
"""

# Run all test cases
if __name__ == "__main__":
    print("Running Test Case 1: No discount")
    test_case_1()
    
    print("\nRunning Test Case 2: 15% discount")
    test_case_2()
    
    print("\nRunning Test Case 3: Empty list")
    test_case_3()
    
    print("\nRunning Test Case 4: String discount (fixed)")
    test_case_4()
    
    # Verification: New test case to ensure all fixes work together
    print("\nVerification Test: Mixed types")
    items5 = ["Product A", "Product B"]
    prices5 = [10.99, 24.50]
    discount5 = "10"  # String that should get converted
    
    print("\n" + generate_receipt(items5, prices5, discount5))
