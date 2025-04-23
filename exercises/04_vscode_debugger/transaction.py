"""
Transaction module for the Budget Tracker application.

This module defines the Transaction class and functions for processing transaction data.
It contains intentional bugs for the VS Code debugging exercise.
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
        
        # BUG: The monthly calculation uses the wrong sign for expenses
        # This bug will be found and fixed during the debugging exercise
        if transaction.is_expense:
            monthly_totals[month_key]["expenses"] += amount  # Bug: should be += abs(amount)
        else:
            monthly_totals[month_key]["income"] += amount
        
        # Calculate monthly net (income - expenses)
        # BUG: The net calculation is affected by the expense bug
        monthly_totals[month_key]["net"] = (
            monthly_totals[month_key]["income"] + monthly_totals[month_key]["expenses"]
        )
        
        # Update category totals
        # BUG: Category calculations don't check for expenses vs income
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
