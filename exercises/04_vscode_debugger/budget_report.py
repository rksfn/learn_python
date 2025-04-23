"""
Budget Report module for the Budget Tracker application.

This module contains functions for generating various financial reports.
It contains intentional bugs for the VS Code debugging exercise.
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
            
            # BUG: Expense amount is negative but should be displayed as positive
            expenses = totals["expenses"]  # Bug: should be abs(totals["expenses"])
            net = totals["net"]
        else:
            income = 0
            expenses = 0
            net = 0
        
        # Get budget information
        budget = monthly_budgets.get(month_key, 0)
        
        # BUG: Budget comparison is incorrect due to expenses being negative
        # This is the bug for students to find
        budget_difference = budget + expenses  # Bug: should be budget - abs(expenses)
        budget_status = "under budget" if budget_difference >= 0 else "over budget"
        
        # Add month header
        report.append(f"{month_name} {year}")
        report.append("-" * len(f"{month_name} {year}"))
        
        # Add summary statistics
        report.append(f"Transactions: {len(month_transactions)} ({expense_count} expenses, {income_count} income)")
        report.append(f"Income: ${income:.2f}")
        report.append(f"Expenses: ${expenses:.2f}")  # Bug: should show positive amount
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
    
    # Get total expenses and income
    total_expenses = sum(abs(t.amount) for t in transactions if t.is_expense)
    total_income = sum(t.amount for t in transactions if not t.is_expense)
    
    report.append(f"Total Income: ${total_income:.2f}")
    report.append(f"Total Expenses: ${total_expenses:.2f}")
    report.append("")
    
    # BUG: Category calculations don't separate expenses and income
    # This bug is intentional for the debugging exercise
    
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
                sign = "" if transaction.amount < 0 else "+"
                report.append(f"  • {transaction.date}: {sign}${abs(transaction.amount):.2f} - {transaction.description}")
            
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
