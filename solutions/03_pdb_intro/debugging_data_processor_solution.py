"""
Exercise 3 Solution: Debugging a Real Application with pdb

This solution demonstrates how to debug a multi-file data processing application
using advanced pdb techniques to find and fix various issues.
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
            
            # BUG FIX 1: Create directory if it doesn't exist
            if not path.exists():
                print(f"Creating directory {self.data_dir}")
                path.mkdir(exist_ok=True)
                
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
                
                # BUG FIX 2: Track row number for better error reporting
                for row_num, row in enumerate(reader, start=1):
                    # Convert string values to appropriate types
                    processed_row = {}
                    for key, value in row.items():
                        if key is None:
                            continue  # Skip columns with no header
                            
                        # Try to convert to float if it's numeric
                        try:
                            processed_row[key] = float(value)
                        except (ValueError, TypeError):
                            # BUG FIX 3: Handle missing values
                            if value == '' or value is None:
                                processed_row[key] = None
                            else:
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
                # BUG FIX 4: Filter out None values before calculating stats
                values = [record[field] for record in data 
                         if field in record and record[field] is not None]
                
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
                    
                    # BUG FIX 5: Format timestamp properly
                    timestamp = results['timestamp']
                    f.write(f"Analysis timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    if "fields" in results and results["fields"]:
                        f.write("Field statistics:\n")
                        f.write("-----------------\n")
                        
                        for field_name, stats in results["fields"].items():
                            f.write(f"Field: {field_name}\n")
                            for stat_name, value in stats.items():
                                # BUG FIX 6: Format floating point values nicely
                                if isinstance(value, float):
                                    f.write(f"  {stat_name}: {value:.4f}\n")
                                else:
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
    # For debugging demonstration, we can show different ways to debug
    import pdb
    
    # Example 1: Setting a breakpoint before running the program
    # breakpoint()  # This would stop here before any code runs
    
    # Example 2: Conditional breakpoint (would be set within pdb)
    # In pdb you would type: b DataProcessor.read_data_file, 'bad_data' in str(file_path)
    
    # Example 3: Run the program and use post-mortem debugging if it crashes
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        
        # Uncomment to use post-mortem debugging
        # pdb.post_mortem()
        
        # Or to start interactive debugging at this point
        # pdb.set_trace()

"""
Debugging Process and Bug Fixes:

Using pdb, we identified and fixed six major bugs in the data processing application:

1. Bug #1: Missing Data Directory
   - When running the program, pdb showed that it failed if the data directory didn't exist
   - Used 'n' and 's' to step through the scan_data_directory method 
   - Fix: Added code to create the directory if it doesn't exist

   pdb commands used:
   - b DataProcessor.scan_data_directory
   - n (next) to step through function execution
   - p path.exists() to check if the directory exists

2. Bug #2: Poor Error Reporting in CSV Parsing
   - When processing bad data, pdb showed the exact line where parsing failed, but the
     original code didn't track row numbers
   - Fix: Added row number tracking for better error reporting

   pdb commands used:
   - b DataProcessor.read_data_file
   - c (continue) to get to the file reading
   - s (step) into the CSV reading loop
   - p row to examine the row content

3. Bug #3: Missing Values in CSV
   - Using pdb, we found that empty values caused calculation errors later
   - Fix: Added explicit handling for empty or missing values, converting them to None

   pdb commands used:
   - b DataProcessor.read_data_file, 'bad_data' in str(file_path)
   - p value to examine values during parsing
   - pp processed_row to see the resulting data structure

4. Bug #4: None Values in Statistical Calculations
   - Statistics calculations were failing because of None values mixed with numbers
   - Used pdb to watch values going into statistical calculations
   - Fix: Added filtering to remove None values before calculating statistics

   pdb commands used:
   - b DataProcessor.analyze_data
   - p values to examine the values array before calculations
   - pp [v for v in values if v is not None] to test the filter

5. Bug #5: Timestamp Formatting
   - Report generation was failing when trying to write the timestamp
   - Fix: Added proper formatting for the timestamp

   pdb commands used:
   - b DataProcessor.generate_report
   - p type(timestamp) to see it was a datetime object
   - p timestamp.strftime('%Y-%m-%d %H:%M:%S') to test formatting

6. Bug #6: Numeric Value Formatting
   - The report had long floating point values that were hard to read
   - Fix: Added formatting for floating point values to limit decimals

   pdb techniques used:
   - Navigating the call stack with 'w' (where)
   - Examining variables with 'p' and 'pp'
   - Moving up/down in the stack with 'u' and 'd'
   - Using 'b' to set conditional breakpoints when processing specific files

Valuable pdb Techniques Demonstrated:

1. Conditional Breakpoints
   - Setting breakpoints that only trigger for specific files:
     b DataProcessor.read_data_file, 'bad_data' in str(file_path)
   - This saved time by focusing only on problematic cases

2. Post-Mortem Debugging
   - Using pdb.post_mortem() to analyze exceptions after they occurred
   - Extremely valuable for dissecting crashes and exceptions

3. Call Stack Navigation
   - Using 'w' to see the full call stack
   - Moving up/down with 'u' and 'd' to examine variables at different levels

4. Variable Examination and Modification
   - Using 'p' to print variables, 'pp' for pretty printing
   - Using '!' to modify variables (like !values = [x for x in values if x is not None])
   - Evaluating complex expressions in the debugger

These techniques combined allowed for systematic identification and fixing of bugs
in the data processing pipeline, creating a much more robust application.
"""
