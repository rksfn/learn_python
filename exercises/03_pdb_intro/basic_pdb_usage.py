"""
Exercise 1: Getting Started with pdb

In this exercise, you'll learn the basics of using Python's built-in debugger (pdb)
by debugging a simple function with logical errors.

Objectives:
- Use pdb.set_trace() and breakpoint() to pause execution
- Navigate through code using basic pdb commands
- Inspect variable values during execution
- Find and fix logical errors using the debugger
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


# Test Case 1: No discount
items1 = ["Apple", "Banana", "Orange"]
prices1 = [1.20, 0.50, 0.75]
print(generate_receipt(items1, prices1))

# Test Case 2: With discount
items2 = ["Laptop", "Mouse", "Keyboard"]
prices2 = [1000, 25.50, 45.99]
print("\n" + generate_receipt(items2, prices2, 15))  # 15% discount

# Test Case 3: This will cause a bug! Can you find it using pdb?
items3 = ["Book", "Notebook", "Pen"]
prices3 = [15.99, 4.99, 1.29]
discount3 = 20  # 20% discount

# Try running the code with a breakpoint before this line
# Insert either: 
# import pdb; pdb.set_trace()
# or
# breakpoint()

print("\n" + generate_receipt(items3, prices3, discount3))

# Test Case 4: Another bug! Use pdb to investigate
items4 = ["Chair", "Table", "Lamp"]
prices4 = [49.99, 149.99, 29.99]
discount4 = "25"  # Note: This is a string, not a number!

# Add another breakpoint here to debug the issue
# Run in pdb to find out what happens

try:
    print("\n" + generate_receipt(items4, prices4, discount4))
except Exception as e:
    print(f"Error: {e}")


"""
Exercise Instructions:

1. Run this script as-is and observe its behavior.

2. Add a breakpoint before Test Case 3 (using either `import pdb; pdb.set_trace()` or `breakpoint()`)
   and run the script again.

3. When the debugger starts, use the following commands to explore:
   - `n` (next): Execute the current line and move to the next one
   - `s` (step): Step into function calls
   - `p variable_name`: Print a variable's value
   - `l` (list): Show current line and context
   - `c` (continue): Continue execution until next breakpoint or end

4. Step through the code for Test Case 3 and identify any issues.

5. For Test Case 4, predict what will happen, then add another breakpoint and use the debugger
   to confirm your prediction.

6. Fix any bugs you find in the code.

Questions to consider while debugging:
1. What values do the variables have at each step?
2. How do the values change as you step through the code?
3. What happens when you step into the functions?
4. How can you use the debugger to fix these issues efficiently?
"""
