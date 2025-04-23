"""
Exercise 3: Debugging a Real Application with pdb

In this exercise, you'll debug a more complex application - a simple data analysis
pipeline that processes CSV files, performs calculations, and generates reports.
You'll use pdb to track down and fix several bugs in the application.

Objectives:
- Debug a multi-file application
- Use pdb to trace through complex data processing
- Fix bugs in error handling and calculations
- Use pdb.pm() for post-mortem debugging
- Practice setting breakpoints in different files
"""

import csv
import os
import datetime
import statistics
from pathlib import Path


class DataProcessor:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.data_files = []
        self.processed_data = {}
        self.analysis_results = {}
    
    def scan_data_directory(self):
        """Scan the data directory for CSV files."""
        try:
            # Get all CSV files in the data directory
            path = Path(self.data_dir)
            self.data_files = list(path.glob("*.csv"))
            
            if not self.data_files:
                print(f"No CSV files found in {self.data_dir}")
            else:
                print(f"Found {len(self.data_files)} CSV files")
                
            return len(self.data_files)
        except Exception as e:
            print(f"Error scanning directory: {e}")
            return 0
    
    def read_data_file(self, file_path):
        """Read and parse a CSV data file."""
        try:
            data = []
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Convert string values to appropriate types
                    processed_row = {}
                    for key, value in row.items():
                        # Try to convert to float if it's numeric
                        try:
                            processed_row[key] = float(value)
                        except ValueError:
                            # If not numeric, keep as string
                            processed_row[key] = value
                    
                    data.append(processed_row)
            
            return data
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []
    
    def process_all_files(self):
        """Process all data files."""
        if not self.data_files:
            self.scan_data_directory()
        
        for file_path in self.data_files:
            print(f"Processing {file_path}...")
            data = self.read_data_file(file_path)
            
            if data:
                # Use the filename (without extension) as the key
                key = file_path.stem
                self.processed_data[key] = data
                print(f"Successfully processed {len(data)} records from {key}")
            else:
                print(f"No data processed from {file_path}")
        
        return len(self.processed_data)
    
    def analyze_data(self):
        """Perform analysis on the processed data."""
        if not self.processed_data:
            print("No data to analyze. Run process_all_files() first.")
            return False
        
        print("Analyzing data...")
        
        for dataset_name, data in self.processed_data.items():
            # Initialize analysis results for this dataset
            self.analysis_results[dataset_name] = {
                "record_count": len(data),
                "fields": {},
                "timestamp": datetime.datetime.now()
            }
            
            # Skip empty datasets
            if not data:
                continue
            
            # Get all numeric fields from the first record
            numeric_fields = []
            for field, value in data[0].items():
                if isinstance(value, (int, float)):
                    numeric_fields.append(field)
            
            # Calculate statistics for each numeric field
            for field in numeric_fields:
                values = [record[field] for record in data if field in record]
                
                if not values:
                    continue
                
                # Calculate basic statistics
                try:
                    stats = {
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values),
                        "median": statistics.median(values),
                        "sum": sum(values),
                        "count": len(values)
                    }
                    
                    # Calculate standard deviation if there are enough values
                    if len(values) > 1:
                        stats["std_dev"] = statistics.stdev(values)
                    
                    self.analysis_results[dataset_name]["fields"][field] = stats
                except Exception as e:
                    print(f"Error calculating statistics for {field}: {e}")
        
        return True
    
    def generate_report(self, output_file="report.txt"):
        """Generate a report from the analysis results."""
        if not self.analysis_results:
            print("No analysis results. Run analyze_data() first.")
            return False
        
        try:
            with open(output_file, 'w') as f:
                f.write("DATA ANALYSIS REPORT\n")
                f.write("===================\n\n")
                f.write(f"Generated: {datetime.datetime.now()}\n")
                f.write(f"Datasets analyzed: {len(self.analysis_results)}\n\n")
                
                for dataset_name, results in self.analysis_results.items():
                    f.write(f"Dataset: {dataset_name}\n")
                    f.write(f"Records: {results['record_count']}\n")
                    f.write(f"Analysis timestamp: {results['timestamp']}\n\n")
                    
                    if "fields" in results and results["fields"]:
                        f.write("Field statistics:\n")
                        f.write("-----------------\n")
                        
                        for field_name, stats in results["fields"].items():
                            f.write(f"Field: {field_name}\n")
                            for stat_name, value in stats.items():
                                f.write(f"  {stat_name}: {value}\n")
                            f.write("\n")
                    else:
                        f.write("No field statistics available.\n\n")
                    
                    f.write("="*50 + "\n\n")
                
                print(f"Report generated: {output_file}")
                return True
                
        except Exception as e:
            print(f"Error generating report: {e}")
            return False


def create_sample_data():
    """Create sample CSV files for testing."""
    # Create data directory if it doesn't exist
    path = Path("data")
    path.mkdir(exist_ok=True)
    
    # Sample data for sales
    sales_data = [
        {"date": "2023-01-01", "product_id": "P001", "quantity": 5, "price": 10.99, "customer_id": "C001"},
        {"date": "2023-01-02", "product_id": "P002", "quantity": 3, "price": 24.95, "customer_id": "C002"},
        {"date": "2023-01-02", "product_id": "P001", "quantity": 2, "price": 10.99, "customer_id": "C003"},
        {"date": "2023-01-03", "product_id": "P003", "quantity": 1, "price": 99.99, "customer_id": "C001"},
        {"date": "2023-01-04", "product_id": "P002", "quantity": 4, "price": 24.95, "customer_id": "C004"},
        {"date": "2023-01-05", "product_id": "P001", "quantity": 10, "price": 9.99, "customer_id": "C005"}  # Note price changed
    ]
    
    # Sample data for inventory
    inventory_data = [
        {"product_id": "P001", "name": "Widget", "category": "A", "stock": 45, "reorder_level": 10},
        {"product_id": "P002", "name": "Gadget", "category": "B", "stock": 30, "reorder_level": 5},
        {"product_id": "P003", "name": "Doohickey", "category": "A", "stock": 10, "reorder_level": 2},
        {"product_id": "P004", "name": "Thingamajig", "category": "C", "stock": 25, "reorder_level": 5},
        {"product_id": "P005", "name": "Whatchamacallit", "category": "B", "stock": 0, "reorder_level": 10}
    ]
    
    # Sample data for customers
    customer_data = [
        {"customer_id": "C001", "name": "John Smith", "city": "New York", "segment": "Retail", "since": "2020-05-15"},
        {"customer_id": "C002", "name": "Jane Doe", "city": "Los Angeles", "segment": "Wholesale", "since": "2019-11-30"},
        {"customer_id": "C003", "name": "Bob Johnson", "city": "Chicago", "segment": "Retail", "since": "2021-02-10"},
        {"customer_id": "C004", "name": "Alice Brown", "city": "Houston", "segment": "Wholesale", "since": "2018-07-22"},
        {"customer_id": "C005", "name": "Charlie Davis", "city": "Phoenix", "segment": "Retail", "since": "2022-01-05"}
    ]
    
    # Write sales data to CSV
    with open(path / "sales.csv", 'w', newline='') as csvfile:
        fieldnames = ["date", "product_id", "quantity", "price", "customer_id"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in sales_data:
            writer.writerow(row)
    
    # Write inventory data to CSV
    with open(path / "inventory.csv", 'w', newline='') as csvfile:
        fieldnames = ["product_id", "name", "category", "stock", "reorder_level"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in inventory_data:
            writer.writerow(row)
    
    # Write customer data to CSV
    with open(path / "customers.csv", 'w', newline='') as csvfile:
        fieldnames = ["customer_id", "name", "city", "segment", "since"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in customer_data:
            writer.writerow(row)
    
    # Create a file with errors to test error handling
    with open(path / "bad_data.csv", 'w', newline='') as csvfile:
        csvfile.write("id,name,value\n")
        csvfile.write("1,Good,100\n")
        csvfile.write("2,Bad,not_a_number\n")  # This will cause conversion error
        csvfile.write("3,Missing\n")  # This line is missing a value
        csvfile.write("4,Good,200\n")
    
    print(f"Created sample data files in {path}")
    return path


def main():
    """Main function to run the data processor."""
    print("Data Processor Demo")
    print("===================")
    
    # Create sample data files
    data_dir = create_sample_data()
    
    # Initialize processor
    processor = DataProcessor(data_dir)
    
    # Process data files
    num_files = processor.scan_data_directory()
    print(f"Found {num_files} data files")
    
    num_datasets = processor.process_all_files()
    print(f"Processed {num_datasets} datasets")
    
    # Analyze data
    if processor.analyze_data():
        print("Data analysis complete")
    else:
        print("Data analysis failed")
    
    # Generate report
    if processor.generate_report("analysis_report.txt"):
        print("Report generated successfully")
    else:
        print("Report generation failed")


if __name__ == "__main__":
    main()


"""
Exercise Instructions:

This exercise simulates a real-world data processing application with several bugs.
Your task is to use pdb to find and fix these issues.

Setup:
1. This script will create sample CSV files in a 'data' directory for testing
2. The DataProcessor class reads these files, analyzes the data, and generates a report

Known Issues:
1. The application doesn't handle some types of errors correctly
2. The analysis results are sometimes incorrect
3. There may be logic errors in data processing

Debugging Tasks:

1. Use pdb to trace through the execution:
   - Add 'breakpoint()' at key points or run with 'python -m pdb'
   - Step through data processing and analysis

2. Find and fix Bug #1: Data Reading
   - The bad_data.csv file causes issues when processing
   - Use pdb to understand what's happening and modify the code to handle this properly

3. Find and fix Bug #2: Statistical Calculation
   - There's a bug in the data analysis when calculating statistics
   - Use pdb to check the values and calculations

4. Find and fix Bug #3: Report Generation
   - The report generation has an issue with formatting or data access
   - Step through the generate_report method to identify it

5. Post-Mortem Debugging:
   - If the program crashes, use pdb.post_mortem() to analyze the crash
   - Fix the issue to make the code more robust

Advanced Tasks:

1. Add a conditional breakpoint that activates only when processing the 'bad_data.csv' file
   - Hint: b DataProcessor.read_data_file, 'bad_data' in str(file_path)

2. Use the debugger to examine the processed data structures:
   - Examine raw data vs. processed data
   - Check the analysis results for each field

3. Practice using the 'w' (where) command to navigate the call stack when errors occur

Report:
- Document each bug you found
- Explain how pdb helped you identify it
- Describe your solution
"""
