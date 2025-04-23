"""
Exercise 2 Solution: Advanced VS Code Debugging

This solution demonstrates how to debug a multi-file budget tracking application
using VS Code's advanced debugging features. The main file imports and coordinates
functionality from transaction.py and budget_report.py.

The bugs in this multi-file application were identified and fixed by using VS Code's
debugger to step through code execution, examine variables, and analyze dependencies
between files.
"""

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
                    
                    # BUG FIX 1: Properly handle string conversion to float
                    # Using VS Code debugger's Variables panel and Watch expressions
                    # helped identify potential issues with string-to-number conversion
                    try:
                        amount = float(row['amount'])
                    except ValueError:
                        print(f"Warning: Invalid amount '{row['amount']}' - skipping row")
                        continue
                        
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
        # BUG FIX 2: Validate input parameters
        # VS Code's debugger helped trace issues with transaction creation
        if not isinstance(date, datetime.date):
            if isinstance(date, str):
                try:
                    date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                except ValueError:
                    print(f"Error: Invalid date format '{date}' - use YYYY-MM-DD")
                    return None
            else:
                print("Error: Date must be a datetime.date object or a YYYY-MM-DD string")
                return None
                
        try:
            amount = float(amount)
        except ValueError:
            print(f"Error: Invalid amount '{amount}'")
            return None
            
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
    # For demonstration purposes, we would use VS Code's debugger here
    main()

"""
VS Code Debugging Solution Notes for Multi-file Application:

This solution demonstrates how to use VS Code's advanced debugging features to debug
a multi-file Python application. The debugging process involved:

1. Setting breakpoints across all three files:
   - budget_tracker.py: In the main function and report generation methods
   - transaction.py: In the process_transactions function
   - budget_report.py: In the report generation functions

2. Stepping through execution:
   - Using F10 (Step Over) to execute one line at a time
   - Using F11 (Step Into) to dig into function calls across files
   - Using Shift+F11 (Step Out) to return from function calls

3. Using the Call Stack panel:
   - To understand how functions in different files call each other
   - To navigate between stack frames and examine variables at different levels

4. Setting conditional breakpoints:
   - For example, breaking only when processing specific months or categories
   - This helped focus debugging on problematic areas of the code

5. Using logpoints instead of print statements:
   - To track values without modifying the code or stopping execution

Main bugs identified and fixed in this file:

1. Error handling in load_transactions:
   - Added proper validation and error handling for loading transaction data
   - Used VS Code's Variables panel to inspect the CSV data as it was being processed

2. Input validation in add_transaction:
   - Added robust validation for date and amount values
   - Used VS Code's Call Stack to understand where invalid values might be introduced

The most valuable VS Code debugging features for this file were:
- The Variables panel for inspecting complex data structures
- Step Into/Out for navigating between files
- Watch expressions for monitoring key values across function calls
"""
