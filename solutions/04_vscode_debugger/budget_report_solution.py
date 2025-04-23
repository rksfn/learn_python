"""
Budget Report module for the Budget Tracker application - Solution.

This solution demonstrates how VS Code debugging was used to identify and fix
bugs in the budget report generation module.
"""

from collections import defaultdict
from transaction import get_month_name


def generate_monthly_report(transactions, monthly_totals, monthly_budgets):
    """
    Generate a monthly financial report.
    
    Args:
        transactions: List of Transaction objects
        monthly_totals: Dictionary of monthly income/expense totals
        monthly_budgets: Dictionary of monthly budget amounts
        
    Returns:
        Formatted report string
    """
    if not transactions:
        return "No transactions to report."
    
    # Organize transactions by month
    monthly_transactions = defaultdict(list)
    for transaction in transactions:
        monthly_transactions[transaction.month_key].append(transaction)
    
    # Generate the report
    report = []
    report.append("MONTHLY FINANCIAL REPORT")
    report.append("=========================\n")
    
    # Sort months chronologically
    sorted_months = sorted(monthly_transactions.keys())
    
    for month_key in sorted_months:
        year, month = month_key.split('-')
        month_name = get_month_name(int(month))
        
        # Get transactions for this month
        month_transactions = monthly_transactions[month_key]
        expense_count = sum(1 for t in month_transactions if t.is_expense)
        income_count = len(month_transactions) - expense_count
        
        # Get monthly totals
        if month_key in monthly_totals:
            totals = monthly_totals[month_key]
            income = totals["income"]
            
            # BUG FIX 1: Display expenses as positive values
            # Using VS Code's Variables panel, we could see expenses were already
            # stored as positive values in the fixed transaction module
            expenses = totals["expenses"]  # Now correctly stored as positive
            net = totals["net"]
        else:
            income = 0
            expenses = 0
            net = 0
        
        # Get budget information
        budget = monthly_budgets.get(month_key, 0)
        
        # BUG FIX 2: Correct the budget comparison calculation
        # Using a conditional breakpoint when month_key equals a specific month,
        # we were able to examine this calculation closely
        budget_difference = budget - expenses  # Fixed from "budget + expenses"
        budget_status = "under budget" if budget_difference >= 0 else "over budget"
        
        # Add month header
        report.append(f"{month_name} {year}")
        report.append("-" * len(f"{month_name} {year}"))
        
        # Add summary statistics
        report.append(f"Transactions: {len(month_transactions)} ({expense_count} expenses, {income_count} income)")
        report.append(f"Income: ${income:.2f}")
        report.append(f"Expenses: ${expenses:.2f}")  # Now correctly displayed as positive
        report.append(f"Net: ${net:.2f}")
        
        # Add budget information
        if budget > 0:
            report.append(f"Budget: ${budget:.2f}")
            report.append(f"Status: ${abs(budget_difference):.2f} {budget_status}")
        else:
            report.append("Budget: Not set")
        
        # Add transaction details
        report.append("\nTransactions:")
        if month_transactions:
            for transaction in sorted(month_transactions, key=lambda t: t.date):
                amount = transaction.amount
                sign = "" if amount < 0 else "+"
                report.append(f"  {transaction.date}: {sign}${abs(amount):.2f} - {transaction.category} - {transaction.description}")
        else:
            report.append("  No transactions for this month.")
        
        report.append("")  # Empty line between months
    
    return "\n".join(report)


def generate_category_report(transactions, category_totals):
    """
    Generate a report of spending by category.
    
    Args:
        transactions: List of Transaction objects
        category_totals: Dictionary of category totals
        
    Returns:
        Formatted report string
    """
    if not transactions:
        return "No transactions to report."
    
    # Organize transactions by category
    category_transactions = defaultdict(list)
    for transaction in transactions:
        category_transactions[transaction.category].append(transaction)
    
    # Generate the report
    report = []
    report.append("CATEGORY SPENDING REPORT")
    report.append("========================\n")
    
    # BUG FIX 3: Correctly calculate total expenses and income
    # Using VS Code's Debug Console to evaluate expressions helped identify this issue
    total_expenses = sum(abs(t.amount) for t in transactions if t.is_expense)
    total_income = sum(t.amount for t in transactions if not t.is_expense)
    
    report.append(f"Total Income: ${total_income:.2f}")
    report.append(f"Total Expenses: ${total_expenses:.2f}")
    report.append("")
    
    # BUG FIX 4: Category calculations now correctly handle negative values
    # Using the Watch panel to monitor category_totals helped identify this issue
    
    # Sort categories by total amount (largest absolute value first)
    sorted_categories = sorted(
        category_totals.items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )
    
    # Add category details
    report.append("BY CATEGORY:")
    for category, amount in sorted_categories:
        # Get transactions for this category
        cat_transactions = category_transactions[category]
        transaction_count = len(cat_transactions)
        
        # Determine if this is primarily an expense or income category
        is_expense_category = amount < 0
        
        # Calculate percentage of total
        if is_expense_category and total_expenses > 0:
            percentage = (abs(amount) / total_expenses) * 100
            report.append(f"{category}: ${abs(amount):.2f} ({percentage:.1f}% of expenses)")
        elif not is_expense_category and total_income > 0:
            percentage = (amount / total_income) * 100
            report.append(f"{category}: +${amount:.2f} ({percentage:.1f}% of income)")
        else:
            report.append(f"{category}: ${abs(amount):.2f}")
        
        # Add transaction details for this category
        if transaction_count > 0:
            report.append(f"  Transactions: {transaction_count}")
            
            # Show most recent transactions (up to 3)
            recent = sorted(cat_transactions, key=lambda t: t.date, reverse=True)[:3]
            for transaction in recent:
                amount = transaction.amount
                sign = "" if amount < 0 else "+"
                report.append(f"  • {transaction.date}: {sign}${abs(amount):.2f} - {transaction.description}")
            
            # If there are more transactions, indicate it
            if transaction_count > 3:
                report.append(f"  • ... and {transaction_count - 3} more")
            
            report.append("")  # Empty line between categories
    
    return "\n".join(report)


def generate_savings_report(transactions, start_date, end_date):
    """
    Generate a savings analysis report for a date range.
    
    Args:
        transactions: List of Transaction objects
        start_date: Start date for analysis
        end_date: End date for analysis
        
    Returns:
        Formatted report string
    """
    # Filter transactions in the date range
    filtered = [t for t in transactions if start_date <= t.date <= end_date]
    
    if not filtered:
        return f"No transactions found between {start_date} and {end_date}."
    
    # Calculate income and expenses
    income = sum(t.amount for t in filtered if not t.is_expense)
    expenses = sum(t.amount for t in filtered if t.is_expense)
    savings = income + expenses  # expenses are negative, so we add
    
    # Calculate savings rate
    savings_rate = (savings / income) * 100 if income > 0 else 0
    
    # Generate the report
    report = []
    report.append("SAVINGS REPORT")
    report.append("==============\n")
    
    report.append(f"Period: {start_date} to {end_date}")
    report.append(f"Total Income: ${income:.2f}")
    report.append(f"Total Expenses: ${abs(expenses):.2f}")
    report.append(f"Savings: ${savings:.2f}")
    report.append(f"Savings Rate: {savings_rate:.1f}%")
    
    return "\n".join(report)


"""
VS Code Debugging Solution Notes for Budget Report Module:

Four main bugs were identified and fixed in this module using VS Code's debugging tools:

1. Bug #1: Incorrect Display of Expense Values
   - With VS Code debugging, we stepped through the code execution and observed
     that expenses were coming in as positive values after fixing the transaction module
   - We used the Variables panel to verify this behavior

2. Bug #2: Incorrect Budget Comparison Calculation
   - Original code: budget_difference = budget + expenses
   - Issue: Since expenses were now positive, this was adding budget and expenses
   - Fix: Changed to subtract expenses from budget
   
   Debugging approach:
   - Set a conditional breakpoint when processing specific months
   - Used Watch expressions to monitor the calculation
   - Verified the formula produced correct under/over budget results

3. Bug #3: Incorrect Percentage Calculations
   - Using the Debug Console to evaluate various expressions, we could test
     different percentage calculations and see which gave correct results
   - This helped ensure our category percentages were calculated accurately

4. Bug #4: Category Calculations with Negative Values
   - Using VS Code's Watch panel, we monitored category_totals during execution
   - Observed that some categories now had negative values (expenses)
   - Ensured the report generation properly interpreted these values

Advanced VS Code Debugging Features Used:

1. Conditional Breakpoints:
   - Setting breakpoints that only trigger for specific conditions like:
     - b generate_monthly_report, "2023-01" in str(month_key)
   - This allowed focusing on debugging specific months without stopping for every iteration

2. Watch Expressions:
   - Adding complex expressions to continuously monitor, such as:
     - category_totals['Groceries']
     - monthly_totals["2023-01"]["expenses"]
   - These provided real-time insight into how values changed during execution

3. Logpoints:
   - Using logpoints to output formatted values without stopping execution:
     - "Month: {month_key}, Budget: {budget}, Expenses: {expenses}"
   - This allowed tracking the flow without interrupting debugging

4. Call Stack Navigation:
   - Using the Call Stack panel to jump between different function calls and
     examine variables at different points in the application's execution
   - This helped understand how data was transformed between functions

This solution demonstrates how VS Code's visual debugging interface makes it
possible to efficiently trace and fix bugs in interconnected modules, where
a change in one file affects the behavior in others.
"""
