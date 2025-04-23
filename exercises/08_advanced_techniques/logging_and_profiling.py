"""
Exercise 1: Advanced Logging and Memory Profiling

In this exercise, you'll work with a data processing application that has
performance and memory issues. You'll implement advanced logging and use
profiling tools to identify and fix the problems.
"""

import os
import sys
import time
import random
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Generator


class DataProcessor:
    """
    A class for processing large datasets with various transformations.
    This class has performance and memory issues that need to be identified and fixed.
    """
    
    def __init__(self, data_dir: str = 'data'):
        """Initialize the data processor."""
        self.data_dir = data_dir
        self.cache = {}
        
        # BUG #1: Inefficient logging configuration
        # Missing proper logging configuration with levels, formatting, etc.
        print("DataProcessor initialized.")
    
    def load_dataset(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load a dataset from a JSON file.
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            The dataset as a list of dictionaries
        """
        filepath = os.path.join(self.data_dir, filename)
        
        # BUG #2: Inefficient file handling
        # The entire file is loaded into memory at once, which could be problematic
        # for very large files
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # BUG #3: Unnecessary data duplication
            # Creates a copy of the data unnecessarily
            print(f"Loaded {filename} with {len(data)} records.")
            return list(data)
        except Exception as e:
            print(f"Error loading {filename}: {str(e)}")
            return []
    
    def filter_dataset(self, dataset: List[Dict[str, Any]], 
                      field: str, value: Any) -> List[Dict[str, Any]]:
        """
        Filter a dataset to include only records where field matches value.
        
        Args:
            dataset: The dataset to filter
            field: The field to filter on
            value: The value to filter for
            
        Returns:
            Filtered dataset
        """
        # BUG #4: Inefficient filtering
        # Creates a new list and checks every item even after finding a match
        result = []
        record_count = 0
        
        for record in dataset:
            record_count += 1
            if field in record and record[field] == value:
                # BUG #5: Unnecessary data duplication
                # Makes a copy of each matching record
                result.append(record.copy())
        
        print(f"Filtered dataset: {len(result)} records match {field}={value}")
        return result
    
    def transform_dataset(self, dataset: List[Dict[str, Any]], 
                         transformations: Dict[str, callable]) -> List[Dict[str, Any]]:
        """
        Apply transformations to a dataset.
        
        Args:
            dataset: The dataset to transform
            transformations: A dictionary mapping field names to transformation functions
            
        Returns:
            Transformed dataset
        """
        # BUG #6: Inefficient transformation
        # Creates multiple copies of the data
        print(f"Transforming dataset with {len(transformations)} transformations...")
        
        result = []
        for record in dataset:
            # Make a copy of the record to avoid modifying the original
            transformed_record = record.copy()
            
            for field, transform_func in transformations.items():
                if field in transformed_record:
                    # Apply the transformation
                    transformed_record[field] = transform_func(transformed_record[field])
            
            result.append(transformed_record)
        
        print(f"Transformed {len(dataset)} records.")
        return result
    
    def aggregate_dataset(self, dataset: List[Dict[str, Any]], 
                         group_by: str, aggregate_field: str, 
                         aggregate_func: callable) -> Dict[Any, Any]:
        """
        Aggregate a dataset by a field.
        
        Args:
            dataset: The dataset to aggregate
            group_by: The field to group by
            aggregate_field: The field to aggregate
            aggregate_func: The aggregation function
            
        Returns:
            Aggregated results as a dictionary
        """
        # BUG #7: Inefficient aggregation
        # Creates multiple intermediate data structures
        print(f"Aggregating dataset by {group_by}...")
        
        # Group the data
        grouped_data = {}
        for record in dataset:
            if group_by not in record or aggregate_field not in record:
                continue
            
            group_value = record[group_by]
            if group_value not in grouped_data:
                grouped_data[group_value] = []
            
            # BUG #8: Unnecessary data duplication
            # Only the aggregate_field is needed, but the entire record is stored
            grouped_data[group_value].append(record)
        
        # Aggregate each group
        result = {}
        for group_value, group_records in grouped_data.items():
            # Extract the values to aggregate
            values = [record[aggregate_field] for record in group_records]
            # Apply the aggregation function
            result[group_value] = aggregate_func(values)
        
        print(f"Aggregated into {len(result)} groups.")
        return result
    
    def cache_result(self, key: str, data: Any) -> None:
        """
        Cache a result for later retrieval.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        # BUG #9: Memory leak in cache
        # The cache grows unbounded without any size limits or cleanup
        self.cache[key] = data
        print(f"Cached result with key: {key}")
    
    def get_cached_result(self, key: str) -> Optional[Any]:
        """
        Get a cached result.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found
        """
        if key in self.cache:
            print(f"Cache hit for key: {key}")
            return self.cache[key]
        
        print(f"Cache miss for key: {key}")
        return None
    
    def process_large_dataset(self, filename: str, batch_size: int = 1000) -> Generator[Dict[str, Any], None, None]:
        """
        Process a large dataset in batches to avoid loading it all into memory.
        
        Args:
            filename: The JSON file to process
            batch_size: Number of records to process in each batch
            
        Yields:
            Processed records one at a time
        """
        # BUG #10: Inefficient batch processing
        # Claims to process in batches but actually loads the entire dataset at once
        dataset = self.load_dataset(filename)
        
        # Process in batches
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1} with {len(batch)} records...")
            
            # Process each record in the batch
            for record in batch:
                # Simulate some processing time
                time.sleep(0.001)
                
                # BUG #11: Unnecessary data duplication
                # Returns a copy of each record
                yield record.copy()


def generate_sample_data(num_records: int = 10000) -> None:
    """
    Generate sample data for testing.
    
    Args:
        num_records: Number of records to generate
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate random user data
    users = []
    for i in range(num_records):
        user = {
            'id': i,
            'name': f"User {i}",
            'email': f"user{i}@example.com",
            'age': random.randint(18, 80),
            'active': random.choice([True, False]),
            'registration_date': (datetime.now().replace(
                day=random.randint(1, 28),
                month=random.randint(1, 12),
                year=random.randint(2015, 2023)
            )).isoformat(),
            'last_login': (datetime.now().replace(
                day=random.randint(1, 28),
                month=random.randint(1, 12),
                year=2023
            )).isoformat() if random.random() > 0.2 else None,
            'purchases': random.randint(0, 50),
            'total_spent': round(random.uniform(0, 10000), 2),
            'preferences': {
                'theme': random.choice(['light', 'dark', 'system']),
                'notifications': random.choice([True, False]),
                'language': random.choice(['en', 'fr', 'es', 'de', 'ja'])
            }
        }
        users.append(user)
    
    # Save to JSON file
    with open('data/users.json', 'w') as f:
        json.dump(users, f)
    
    print(f"Generated {num_records} user records in data/users.json")
    
    # Generate random product data
    products = []
    categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Food', 'Sports']
    
    for i in range(num_records // 10):  # Fewer products than users
        product = {
            'id': i,
            'name': f"Product {i}",
            'category': random.choice(categories),
            'price': round(random.uniform(5, 500), 2),
            'stock': random.randint(0, 100),
            'rating': round(random.uniform(1, 5), 1),
            'reviews_count': random.randint(0, 1000),
            'attributes': {
                'color': random.choice(['red', 'blue', 'green', 'black', 'white']),
                'size': random.choice(['S', 'M', 'L', 'XL']),
                'weight': round(random.uniform(0.1, 10), 2)
            }
        }
        products.append(product)
    
    # Save to JSON file
    with open('data/products.json', 'w') as f:
        json.dump(products, f)
    
    print(f"Generated {len(products)} product records in data/products.json")
    
    # Generate random order data
    orders = []
    
    for i in range(num_records * 2):  # More orders than users
        user_id = random.randint(0, num_records - 1)
        product_count = random.randint(1, 5)
        product_ids = random.sample(range(len(products)), product_count)
        order_products = []
        total = 0
        
        for product_id in product_ids:
            quantity = random.randint(1, 3)
            price = products[product_id]['price']
            subtotal = quantity * price
            total += subtotal
            
            order_products.append({
                'product_id': product_id,
                'quantity': quantity,
                'price': price,
                'subtotal': subtotal
            })
        
        order = {
            'id': i,
            'user_id': user_id,
            'date': (datetime.now().replace(
                day=random.randint(1, 28),
                month=random.randint(1, 12),
                year=random.randint(2020, 2023)
            )).isoformat(),
            'status': random.choice(['pending', 'shipped', 'delivered', 'cancelled']),
            'products': order_products,
            'total': round(total, 2),
            'shipping': round(random.uniform(5, 20), 2),
            'tax': round(total * 0.1, 2),
            'grand_total': round(total + (total * 0.1) + random.uniform(5, 20), 2)
        }
        orders.append(order)
    
    # Save to JSON file
    with open('data/orders.json', 'w') as f:
        json.dump(orders, f)
    
    print(f"Generated {len(orders)} order records in data/orders.json")


def demo_data_processor():
    """Run a demonstration of the DataProcessor class."""
    # Create a processor
    processor = DataProcessor()
    
    # Load datasets
    users = processor.load_dataset('users.json')
    products = processor.load_dataset('products.json')
    orders = processor.load_dataset('orders.json')
    
    # Filter active users
    active_users = processor.filter_dataset(users, 'active', True)
    
    # Define transformations
    transformations = {
        'age': lambda x: x + 1,  # Increment age by 1
        'total_spent': lambda x: round(x * 1.1, 2),  # Increase total spent by 10%
    }
    
    # Transform users
    transformed_users = processor.transform_dataset(active_users, transformations)
    
    # Aggregate orders by user_id, summing the grand_total
    user_totals = processor.aggregate_dataset(
        orders, 'user_id', 'grand_total', sum
    )
    
    # Cache some results
    processor.cache_result('active_users', active_users)
    processor.cache_result('user_totals', user_totals)
    
    # Process orders in batches
    processed_count = 0
    for processed_order in processor.process_large_dataset('orders.json'):
        processed_count += 1
        # Just count them
    
    print(f"Processed {processed_count} orders.")
    
    # Get a cached result
    cached_user_totals = processor.get_cached_result('user_totals')
    print(f"Retrieved cached user totals with {len(cached_user_totals)} entries.")


if __name__ == '__main__':
    # Generate sample data if it doesn't exist
    if not os.path.exists('data/users.json'):
        generate_sample_data()
    
    # Run the demonstration
    demo_data_processor()

"""
Exercise Instructions:

In this exercise, you'll improve a data processing application by implementing 
advanced logging and using profiling tools to identify and fix performance and 
memory issues.

The DataProcessor class has several inefficiencies and memory leaks that need to be addressed.

Part 1: Implement Advanced Logging
---------------------------------
1. Replace all print statements with proper logging using Python's logging module
2. Configure logging with appropriate levels, formatting, and output options
3. Add context information to log messages (function names, line numbers, etc.)
4. Create a log decorator to track function calls, arguments, and return values

Part 2: Profile and Optimize Memory Usage
----------------------------------------
1. Use memory_profiler or tracemalloc to identify memory leaks and inefficiencies
2. Fix the cache implementation to prevent unbounded growth
3. Eliminate unnecessary data duplication
4. Implement proper batch processing for large datasets

Part 3: Profile and Optimize Performance
---------------------------------------
1. Use cProfile to identify performance bottlenecks
2. Optimize the filtering, transformation, and aggregation methods
3. Use appropriate data structures for better performance
4. Implement generator-based processing for the load_dataset method

Bonus Challenges:
---------------
1. Implement a context manager for temporary debug logging
2. Add a custom memory tracking decorator
3. Create a performance monitoring system that logs slow operations
4. Implement a proper LRU cache with size limits and expiration

Notes:
-----
- The sample data is generated automatically in the data/ directory
- Each bug is marked with a comment (BUG #1, BUG #2, etc.) in the code
- Focus on both fixing the issues and adding proper instrumentation to detect them
"""
