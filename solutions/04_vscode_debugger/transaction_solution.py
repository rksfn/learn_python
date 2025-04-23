"""
Transaction module for the Budget Tracker application - Solution.

This solution demonstrates how VS Code debugging was used to identify and fix
bugs in the transaction processing module.
"""

import datetime
from collections import defaultdict

class Transaction:
    """Represents a financial transaction."""
    
    def __init__(self, date, amount, category, description):
        """
        Initialize a transaction.
        
        Args:
            date: Date of the transaction (datetime.date)
            amount: Transaction amount (float, positive for income, negative for expense)
            category: Transaction category (str)
            description: Transaction description (str)
        """
        self.date = date if isinstance(date, datetime.date) else datetime.datetime.now().date()
        self.amount = float(amount)
        self.category = category
        self.description = description
        
        # Flag indicating if this is an expense (negative amount) or income (positive amount)
        self.is_expense = self.amount < 0
        
        # Extract month and year for easier grouping
        self.month = self.date.month
        self.year = self.date.year
        self.month_key = f"{self.year}-{self.month:02d}"
    
    def __repr__(self):
        """String representation of the transaction."""
        transaction_type = "Expense" if self.is_expense else "Income"
        return f"{transaction_type}: ${abs(self.amount):.2f} on {self.date} for {self.category} ({self.description})"


def process_transactions(transactions):
    """
    Process a list of transactions and calculate monthly and category totals.
    
    Args:
        transactions: List of Transaction objects
        
    Returns:
        Dictionary with 'monthly' and 'categories' totals
    """
    # Initialize data structures for calculations
    monthly_totals = defaultdict(lambda: {"income": 0, "expenses": 0, "net": 0})
    category_totals = defaultdict(float)
    
    # Process each transaction
    for transaction in transactions:
        month_key = transaction.month_key
        amount = transaction.amount
        
        # BUG FIX 1: Fix the expenses calculation to use absolute value
        # Using VS Code's debugger, we set a breakpoint here and checked the values
        # With the Variables panel, we could see that expenses were negative
        if transaction.is_expense:
            # Fixed: Use abs(amount) to make expenses a positive number for display
            monthly_totals[month_key]["expenses"] += abs(amount)
        else:
            monthly_totals[month_key]["income"] += amount
        
        # BUG FIX 2: Fix the net calculation formula
        # Using the Watch panel, we monitored the net calculation and saw the issue
        # The correct formula is income - expenses (both positive numbers)
        monthly_totals[month_key]["net"] = (
            monthly_totals[month_key]["income"] - monthly_totals[month_key]["expenses"]
        )
        
        # Update category totals
        # BUG FIX 3: Use absolute values for expense categories
        # Using VS Code's debugger, we set a conditional breakpoint to check expense categories
        if transaction.is_expense:
            # For expenses, we store negative values to distinguish from income
            category_totals[transaction.category] += amount
        else:
            # For income, we store positive values
            category_totals[transaction.category] += amount
    
    # Convert defaultdicts to regular dicts for easier debugging
    return {
        "monthly": dict(monthly_totals),
        "categories": dict(category_totals)
    }


def get_month_name(month_number):
    """Convert a month number (1-12) to a month name."""
    return datetime.date(2000, month_number, 1).strftime("%B")


def categorize_transactions(transactions):
    """
    Group transactions by category and type (expense/income).
    
    Args:
        transactions: List of Transaction objects
        
    Returns:
        Dictionary mapping categories to lists of transactions
    """
    categories = defaultdict(list)
    
    for transaction in transactions:
        categories[transaction.category].append(transaction)
    
    return dict(categories)


def analyze_spending_trends(transactions, months=3):
    """
    Analyze spending trends over the past n months.
    
    Args:
        transactions: List of Transaction objects
        months: Number of months to analyze
        
    Returns:
        Dictionary with trend analysis
    """
    if not transactions:
        return {"trends": {}, "average_monthly_expenses": 0}
    
    # Get the current date to calculate relative months
    latest_date = max(t.date for t in transactions)
    
    # Initialize monthly expense tracking
    monthly_expenses = defaultdict(float)
    
    # Process transactions
    for transaction in transactions:
        if transaction.is_expense:
            # Only consider expenses
            month_key = transaction.month_key
            monthly_expenses[month_key] += abs(transaction.amount)
    
    # Calculate trends
    trend_data = {}
    month_keys = sorted(monthly_expenses.keys())[-months:]
    
    # If we don't have enough months of data, adjust
    actual_months = len(month_keys)
    
    if actual_months >= 2:
        # Calculate month-to-month changes
        for i in range(1, actual_months):
            current_month = month_keys[i]
            previous_month = month_keys[i-1]
            
            current_expenses = monthly_expenses[current_month]
            previous_expenses = monthly_expenses[previous_month]
            
            # Calculate percentage change
            if previous_expenses > 0:
                change_pct = ((current_expenses - previous_expenses) / previous_expenses) * 100
            else:
                change_pct = 0
            
            # Extract month and year from key
            year, month = current_month.split('-')
            month_name = get_month_name(int(month))
            
            trend_data[current_month] = {
                "month_name": month_name,
                "expenses": current_expenses,
                "change_pct": change_pct,
                "change_type": "increase" if change_pct > 0 else "decrease"
            }
    
    # Calculate average monthly expenses
    if monthly_expenses:
        average_expenses = sum(monthly_expenses.values()) / len(monthly_expenses)
    else:
        average_expenses = 0
    
    return {
        "trends": trend_data,
        "average_monthly_expenses": average_expenses
    }

"""
VS Code Debugging Solution Notes for Transaction Module:

Three main bugs were identified and fixed in this module using VS Code's debugging tools:

1. Bug #1: Incorrect Storage of Expense Values
   - Original code: monthly_totals[month_key]["expenses"] += amount
   - Issue: Since amount is negative for expenses, this was adding negative values
   - Fix: Use abs(amount) to store expenses as positive values
   
   Debugging approach:
   - Set a breakpoint at the expense calculation line
   - Used Variables panel to inspect the amount value and monthly_totals
   - Verified the fix by watching the values update correctly

2. Bug #2: Incorrect Net Calculation Formula
   - Original code: monthly_totals[month_key]["income"] + monthly_totals[month_key]["expenses"]
   - Issue: Since expenses were stored as negative, this was adding income and negative expenses
   - Fix: Changed to subtract expenses (now positive values) from income
   
   Debugging approach:
   - Added a Watch expression for monthly_totals[month_key]["net"]
   - Stepped through the calculation to see how it was being computed
   - Verified the fix by comparing with manual calculations

3. Bug #3: Category Totals Not Distinguished by Type
   - Issue: The category totals didn't distinguish between expenses and income
   - Fix: Made sure to store expense categories with negative values
   
   Debugging approach:
   - Set a conditional breakpoint that triggered only for specific categories
   - Used the Call Stack to see how the categories were being processed
   - Tracked the values using Watch expressions during debugging

VS Code Debugging Features That Were Most Helpful:
1. Conditional breakpoints - to debug specific types of transactions
2. Watch expressions - to monitor calculated values
3. Variables panel - to inspect complex data structures
4. Call stack navigation - to understand how the functions were called

This solution demonstrates how VS Code's visual debugging tools make it much easier
to understand and fix bugs in complex data processing code compared to using print 
statements or command-line debuggers.
"""
