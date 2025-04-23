"""
Exercise 2: Advanced VS Code Debugging

In this exercise, you'll practice advanced VS Code debugging features with a multi-file
application. You'll debug a budget tracking system that imports data, processes transactions,
and generates reports. The application has several bugs that require advanced debugging
techniques to identify and fix.

Objectives:
- Debug across multiple Python files
- Use conditional breakpoints and logpoints
- Debug with the Watch and Call Stack panels
- Modify variables during debugging
- Debug a more complex application architecture
"""

# This file is the main entry point for the budget tracking system.
# It uses functionality from transaction.py and budget_report.py

import csv
import datetime
from pathlib import Path
from transaction import Transaction, process_transactions
from budget_report import generate_monthly_report, generate_category_report

class BudgetTracker:
    def __init__(self):
        self.transactions = []
        self.categories = set()
        self.monthly_budgets = {}
        self.monthly_totals = {}
    
    def load_transactions(self, file_path):
        """Load transactions from a CSV file."""
        if not Path(file_path).exists():
            print(f"Error: File not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # CSV fields: date, amount, category, description
                    date = datetime.datetime.strptime(row['date'], '%Y-%m-%d').date()
                    amount = float(row['amount'])
                    category = row['category']
                    description = row['description']
                    
                    transaction = Transaction(date, amount, category, description)
                    self.transactions.append(transaction)
                    self.categories.add(category)
            
            print(f"Loaded {len(self.transactions)} transactions")
            return True
        except Exception as e:
            print(f"Error loading transactions: {e}")
            return False
    
    def set_monthly_budget(self, month, year, amount):
        """Set a budget for a specific month."""
        key = f"{year}-{month:02d}"
        self.monthly_budgets[key] = amount
    
    def analyze_transactions(self):
        """Analyze transactions and calculate monthly totals and category breakdowns."""
        if not self.transactions:
            print("No transactions to analyze")
            return False
        
        # Process all transactions
        processed_data = process_transactions(self.transactions)
        
        # Store the results
        self.monthly_totals = processed_data['monthly']
        self.category_totals = processed_data['categories']
        
        return True
    
    def generate_reports(self, output_dir):
        """Generate budget reports."""
        if not self.transactions:
            print("No transactions to include in reports")
            return False
        
        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate monthly report
        monthly_report = generate_monthly_report(
            self.transactions,
            self.monthly_totals,
            self.monthly_budgets
        )
        
        with open(output_path / "monthly_report.txt", 'w') as f:
            f.write(monthly_report)
        
        # Generate category report
        category_report = generate_category_report(
            self.transactions, 
            self.category_totals
        )
        
        with open(output_path / "category_report.txt", 'w') as f:
            f.write(category_report)
        
        print(f"Reports generated in {output_dir}")
        return True
    
    def add_transaction(self, date, amount, category, description):
        """Add a new transaction."""
        transaction = Transaction(date, amount, category, description)
        self.transactions.append(transaction)
        self.categories.add(category)
        return transaction


def create_sample_data(file_path):
    """Create sample transaction data for testing."""
    transactions = [
        {"date": "2023-01-05", "amount": "-120.50", "category": "Groceries", "description": "Weekly shopping"},
        {"date": "2023-01-10", "amount": "-45.00", "category": "Dining", "description": "Restaurant dinner"},
        {"date": "2023-01-15", "amount": "-60.00", "category": "Transportation", "description": "Gas"},
        {"date": "2023-01-20", "amount": "1500.00", "category": "Income", "description": "Salary"},
        {"date": "2023-01-25", "amount": "-200.00", "category": "Utilities", "description": "Electricity bill"},
        {"date": "2023-01-30", "amount": "-15.99", "category": "Entertainment", "description": "Movie ticket"},
        {"date": "2023-02-05", "amount": "-135.20", "category": "Groceries", "description": "Weekly shopping"},
        {"date": "2023-02-12", "amount": "-22.50", "category": "Dining", "description": "Lunch"},
        {"date": "2023-02-18", "amount": "-70.00", "category": "Transportation", "description": "Gas"},
        {"date": "2023-02-20", "amount": "1500.00", "category": "Income", "description": "Salary"},
        {"date": "2023-02-22", "amount": "-180.00", "category": "Utilities", "description": "Internet and phone"},
        {"date": "2023-02-28", "amount": "-50.00", "category": "Entertainment", "description": "Concert ticket"},
        {"date": "2023-03-05", "amount": "-142.30", "category": "Groceries", "description": "Weekly shopping"},
        {"date": "2023-03-11", "amount": "-35.00", "category": "Dining", "description": "Dinner"},
        {"date": "2023-03-15", "amount": "-65.00", "category": "Transportation", "description": "Gas"},
        {"date": "2023-03-20", "amount": "1500.00", "category": "Income", "description": "Salary"},
        {"date": "2023-03-25", "amount": "-210.00", "category": "Utilities", "description": "Electricity bill"},
        {"date": "2023-03-28", "amount": "-60.00", "category": "Entertainment", "description": "Books"}
    ]
    
    Path(file_path).parent.mkdir(exist_ok=True)
    
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ["date", "amount", "category", "description"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)
    
    print(f"Sample data created in {file_path}")


def main():
    """Main function to run the budget tracker."""
    # Create sample data
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    transactions_file = data_dir / "transactions.csv"
    create_sample_data(transactions_file)
    
    # Initialize the budget tracker
    tracker = BudgetTracker()
    
    # Load transactions
    tracker.load_transactions(transactions_file)
    
    # Set monthly budgets
    tracker.set_monthly_budget(1, 2023, 1000.00)  # January 2023
    tracker.set_monthly_budget(2, 2023, 1000.00)  # February 2023
    tracker.set_monthly_budget(3, 2023, 1000.00)  # March 2023
    
    # Analyze transactions
    tracker.analyze_transactions()
    
    # Generate reports
    reports_dir = Path("reports")
    tracker.generate_reports(reports_dir)


if __name__ == "__main__":
    main()

"""
This exercise requires two additional files: transaction.py and budget_report.py.
Make sure to create these files in the same directory before running this exercise.

VS Code Debugging Exercise Instructions:

1. Multi-file Debugging:
   - Set breakpoints in each of the three files (this file, transaction.py, and budget_report.py)
   - Press F5 to start debugging
   - Observe how VS Code navigates between files as execution progresses
   - Use the Call Stack panel to understand the relationships between files

2. Find and Fix Bug #1: Transaction Processing
   - The transaction processing has a bug in calculating monthly totals
   - Set breakpoints in the process_transactions function in transaction.py
   - Use the Variables panel to inspect the data structures
   - Find and fix the issue in the monthly calculations

3. Find and Fix Bug #2: Budget Report Generation
   - There's a bug in the budget report generation that causes incorrect under/over budget amounts
   - Use conditional breakpoints in the generate_monthly_report function that trigger only when
     processing certain months
   - Identify and fix the issue

4. Find and Fix Bug #3: Category Handling
   - Certain categories are not being properly tallied in the category report
   - Use the Watch panel to monitor category totals
   - Find and fix the issue in how categories are processed

5. Advanced VS Code Features to Try:
   - Add a logpoint that logs transaction details without stopping execution
   - Use "Run to Cursor" to skip to a specific line
   - Try the "Restart Frame" option in the Call Stack to re-run a function
   - Use the Debug Console to modify transaction amounts during execution

Key VS Code Debugging Features to Practice:
1. Navigating between files during debugging
2. Using the Call Stack to understand program flow
3. Setting conditional breakpoints and logpoints
4. Adding watch expressions for complex objects
5. Using the Debug Console to investigate and modify data

Questions to Consider:
1. How does debugging across multiple files in VS Code compare to traditional print debugging?
2. What challenges arise when debugging a multi-file application?
3. How do advanced features like conditional breakpoints and logpoints help with complex debugging?
4. How could you use the VS Code debugger to test different scenarios without changing your code?
"""
