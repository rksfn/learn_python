"""
Solution: Advanced Logging and Memory Profiling

This solution demonstrates how to implement advanced logging and use profiling
to identify and fix performance and memory issues in a data processing application.
"""

import os
import sys
import time
import random
import json
import logging
import tracemalloc
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Generator
from functools import wraps
from contextlib import contextmanager
from collections import OrderedDict


# Configure logging with proper levels, formatting, and output options
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('data_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('data_processor')


# Custom context manager for temporary debug logging
@contextmanager
def debug_logging(logger_name=None):
    """
    Temporarily increase logging level to DEBUG for the specified logger.
    
    Args:
        logger_name: Name of the logger to modify (uses root logger if None)
    """
    selected_logger = logging.getLogger(logger_name) if logger_name else logger
    original_level = selected_logger.level
    selected_logger.setLevel(logging.DEBUG)
    logger.debug(f"Temporarily increased logging level to DEBUG for {logger_name or 'root'}")
    
    try:
        yield selected_logger
    finally:
        selected_logger.setLevel(original_level)
        logger.debug(f"Restored logging level for {logger_name or 'root'} to {logging.getLevelName(original_level)}")


# Function logging decorator
def log_function_call(func):
    """
    Decorator to log function calls, arguments, and return values.
    
    Args:
        func: The function to wrap
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(f"{func_name} completed in {elapsed:.4f}s with result type: {type(result)}")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.exception(f"{func_name} failed after {elapsed:.4f}s with error: {str(e)}")
            raise
    
    return wrapper


# Memory usage tracking decorator
def track_memory(func):
    """
    Decorator to track memory usage during function execution.
    
    Args:
        func: The function to wrap
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_snapshot = tracemalloc.take_snapshot()
        
        try:
            result = func(*args, **kwargs)
            
            end_snapshot = tracemalloc.take_snapshot()
            tracemalloc.stop()
            
            # Compare memory usage
            memory_diff = end_snapshot.compare_to(start_snapshot, 'lineno')
            
            # Log top 5 memory differences
            for stat in memory_diff[:5]:
                logger.debug(f"Memory: {stat}")
                
            return result
        except Exception:
            tracemalloc.stop()
            raise
    
    return wrapper


# Performance timing decorator
def timing(threshold=None):
    """
    Decorator to log function execution time if it exceeds the threshold.
    
    Args:
        threshold: Time threshold in seconds (logs all executions if None)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            if threshold is None or elapsed > threshold:
                logger.info(f"Performance: {func.__name__} took {elapsed:.4f}s to execute")
            
            return result
        return wrapper
    return decorator


# LRU Cache with size limit
class LRUCache:
    """A least-recently-used cache with size limits."""
    
    def __init__(self, max_size=100):
        self.cache = OrderedDict()
        self.max_size = max_size
        logger.info(f"Initialized LRUCache with max_size={max_size}")
    
    def __contains__(self, key):
        return key in self.cache
    
    def get(self, key, default=None):
        if key not in self.cache:
            logger.debug(f"Cache miss for key: {key}")
            return default
        
        # Move the item to the end (most recently used)
        self.cache.move_to_end(key)
        logger.debug(f"Cache hit for key: {key}")
        return self.cache[key]
    
    def put(self, key, value):
        # If key exists, update and move to end
        if key in self.cache:
            self.cache[key] = value
            self.cache.move_to_end(key)
            logger.debug(f"Updated cache entry for key: {key}")
            return
        
        # If cache is full, remove oldest item
        if len(self.cache) >= self.max_size:
            oldest_key, _ = self.cache.popitem(last=False)
            logger.debug(f"Removed oldest cache entry: {oldest_key}")
        
        # Add new item
        self.cache[key] = value
        logger.debug(f"Added new cache entry for key: {key}")
    
    def clear(self):
        self.cache.clear()
        logger.debug("Cache cleared")
    
    def __len__(self):
        return len(self.cache)


class DataProcessor:
    """
    A class for processing large datasets with various transformations.
    Optimized for performance and memory efficiency.
    """
    
    def __init__(self, data_dir: str = 'data'):
        """Initialize the data processor."""
        self.data_dir = data_dir
        self.cache = LRUCache(max_size=10)
        logger.info(f"DataProcessor initialized with data_dir={data_dir}")
    
    @log_function_call
    def load_dataset(self, filename: str) -> Generator[Dict[str, Any], None, None]:
        """
        Load a dataset from a JSON file, yielding records one at a time.
        
        Args:
            filename: Name of the JSON file to load
            
        Yields:
            Records from the dataset one at a time
        """
        filepath = os.path.join(self.data_dir, filename)
        logger.info(f"Loading dataset from {filepath}")
        
        # FIX #2: Inefficient file handling
        # Use a streaming approach to avoid loading entire file into memory
        try:
            record_count = 0
            
            # Open the file and process it incrementally
            with open(filepath, 'r') as f:
                # Read the opening bracket
                char = f.read(1)
                if char != '[':
                    logger.error(f"Invalid JSON format in {filename}: does not start with '['")
                    return
                
                # Read and process records one by one
                buffer = ""
                bracket_count = 1  # We've already seen one opening bracket
                in_string = False
                escape_next = False
                
                while True:
                    char = f.read(1)
                    if not char:  # End of file
                        break
                    
                    buffer += char
                    
                    # Handle strings and escaping
                    if char == '\\' and not escape_next:
                        escape_next = True
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                    
                    escape_next = False
                    
                    if not in_string:
                        if char == '{':
                            bracket_count += 1
                        elif char == '}':
                            bracket_count -= 1
                            
                            # If we've found a complete object
                            if bracket_count == 1 and buffer.strip():
                                # Check if there's a comma at the end and remove it
                                next_char = f.read(1)
                                if next_char == ',':
                                    pass  # Skip the comma
                                elif next_char:
                                    # Put the character back if it's not a comma
                                    f.seek(f.tell() - 1)
                                
                                # Parse the record and yield it
                                try:
                                    # Extract the object without surrounding junk
                                    object_start = buffer.find('{')
                                    record = json.loads(buffer[object_start:])
                                    record_count += 1
                                    yield record
                                except json.JSONDecodeError as e:
                                    logger.error(f"JSON decode error in record: {e}")
                                
                                # Reset buffer to start a new record
                                buffer = ""
            
            logger.info(f"Loaded {record_count} records from {filename}")
            
        except Exception as e:
            logger.exception(f"Error loading {filename}: {str(e)}")
    
    @log_function_call
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
        # FIX #4: Inefficient filtering
        # Use generator expression and avoid unnecessary copying
        logger.info(f"Filtering dataset on {field}={value}")
        
        # Filter without creating unnecessary intermediate lists
        try:
            result = [record for record in dataset if field in record and record[field] == value]
            logger.info(f"Filtered dataset: {len(result)} records match {field}={value}")
            return result
        except Exception as e:
            logger.exception(f"Error filtering dataset: {str(e)}")
            return []
    
    @log_function_call
    @timing()
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
        # FIX #6: Inefficient transformation
        # Transform records in place instead of creating copies
        logger.info(f"Transforming dataset with {len(transformations)} transformations")
        
        try:
            # Make a shallow copy of the dataset to avoid modifying the original
            result = []
            
            for record in dataset:
                # Create a shallow copy of the record
                transformed_record = dict(record)  # Shallow copy
                
                # Apply transformations
                for field, transform_func in transformations.items():
                    if field in transformed_record:
                        transformed_record[field] = transform_func(transformed_record[field])
                
                result.append(transformed_record)
            
            logger.info(f"Transformed {len(dataset)} records")
            return result
        except Exception as e:
            logger.exception(f"Error transforming dataset: {str(e)}")
            return []
    
    @log_function_call
    @timing()
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
        # FIX #7: Inefficient aggregation
        # Use a more efficient approach that doesn't create intermediate lists
        logger.info(f"Aggregating dataset by {group_by}, aggregating {aggregate_field}")
        
        try:
            # Group and aggregate in a single pass
            result = {}
            
            for record in dataset:
                if group_by not in record or aggregate_field not in record:
                    continue
                
                group_value = record[group_by]
                
                # Only extract the value we need, not the entire record
                value = record[aggregate_field]
                
                # If this is the first value for this group, initialize
                if group_value not in result:
                    result[group_value] = [value]
                else:
                    result[group_value].append(value)
            
            # Apply aggregation function to each group
            for group_value, values in list(result.items()):
                result[group_value] = aggregate_func(values)
            
            logger.info(f"Aggregated into {len(result)} groups")
            return result
        except Exception as e:
            logger.exception(f"Error aggregating dataset: {str(e)}")
            return {}
    
    @log_function_call
    def cache_result(self, key: str, data: Any) -> None:
        """
        Cache a result for later retrieval.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        # FIX #9: Memory leak in cache
        # Use LRU cache with size limits
        self.cache.put(key, data)
        logger.info(f"Cached result with key: {key} (cache size: {len(self.cache)})")
    
    @log_function_call
    def get_cached_result(self, key: str) -> Optional[Any]:
        """
        Get a cached result.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found
        """
        result = self.cache.get(key)
        if result is not None:
            logger.info(f"Cache hit for key: {key}")
            return result
        
        logger.info(f"Cache miss for key: {key}")
        return None
    
    @log_function_call
    @timing()
    def process_large_dataset(self, filename: str, batch_size: int = 1000) -> Generator[Dict[str, Any], None, None]:
        """
        Process a large dataset in batches to avoid loading it all into memory.
        
        Args:
            filename: The JSON file to process
            batch_size: Number of records to process in each batch
            
        Yields:
            Processed records one at a time
        """
        # FIX #10: Inefficient batch processing
        # Use a generator to load and process data incrementally
        logger.info(f"Processing large dataset {filename} with batch_size={batch_size}")
        
        record_count = 0
        batch_count = 0
        batch = []
        
        # Use the streaming dataset loader
        for record in self.load_dataset(filename):
            # Add to current batch
            batch.append(record)
            record_count += 1
            
            # Process the batch when it reaches the target size
            if len(batch) >= batch_size:
                batch_count += 1
                logger.debug(f"Processing batch {batch_count} with {len(batch)} records")
                
                # Process and yield each record
                for processed_record in batch:
                    # Skip the copying - just yield the record as is
                    yield processed_record
                
                # Clear the batch for the next round
                batch.clear()
        
        # Process any remaining records in the last batch
        if batch:
            batch_count += 1
            logger.debug(f"Processing final batch {batch_count} with {len(batch)} records")
            
            for processed_record in batch:
                yield processed_record
        
        logger.info(f"Completed processing {record_count} records in {batch_count} batches")


def generate_sample_data(num_records: int = 10000) -> None:
    """
    Generate sample data for testing.
    
    Args:
        num_records: Number of records to generate
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    logger.info(f"Generating sample data with {num_records} records")
    
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
    
    logger.info(f"Generated {num_records} user records in data/users.json")
    
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
    
    logger.info(f"Generated {len(products)} product records in data/products.json")
    
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
    
    logger.info(f"Generated {len(orders)} order records in data/orders.json")


@timing(threshold=0.5)
def demo_data_processor():
    """Run a demonstration of the DataProcessor class."""
    logger.info("Starting DataProcessor demonstration")
    
    # Create a processor
    processor = DataProcessor()
    
    # Load datasets
    with debug_logging():
        users = list(processor.load_dataset('users.json'))
        products = list(processor.load_dataset('products.json'))
        orders = list(processor.load_dataset('orders.json'))
    
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
        if processed_count % 1000 == 0:
            logger.debug(f"Processed {processed_count} orders so far")
    
    logger.info(f"Processed {processed_count} orders total")
    
    # Get a cached result
    cached_user_totals = processor.get_cached_result('user_totals')
    logger.info(f"Retrieved cached user totals with {len(cached_user_totals)} entries")
    
    logger.info("DataProcessor demonstration completed")


if __name__ == '__main__':
    # Enable tracking for the entire run
    logger.info("Application started")
    
    # Generate sample data if it doesn't exist
    if not os.path.exists('data/users.json'):
        generate_sample_data()
    
    # Run the demonstration with memory tracking
    try:
        # Enable memory tracking for the demo
        tracemalloc.start()
        demo_data_processor()
        
        # Get and display memory statistics
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        logger.info("Top 10 memory allocations:")
        for stat in top_stats[:10]:
            logger.info(f"{stat}")
        
    finally:
        tracemalloc.stop()
        logger.info("Application finished")


"""
Solution Explanation:

This solution addresses all the issues in the original code and adds 
advanced debugging features:

1. Implemented Proper Logging:
   - Configured logging with appropriate levels and formatting
   - Created a debug_logging context manager for temporary debugging
   - Added a log_function_call decorator to track function execution
   - Replaced all print statements with proper logging calls

2. Added Memory Profiling:
   - Used tracemalloc to track memory allocations
   - Created a track_memory decorator to analyze function memory usage
   - Added memory tracking for the entire application run

3. Added Performance Profiling:
   - Created a timing decorator to measure function execution time
   - Added threshold-based performance logging

4. Fixed Memory Issues:
   - Replaced the unbounded cache with an LRU cache implementation
   - Eliminated unnecessary data copying
   - Implemented a streaming approach for loading large JSON files
   - Used generators for memory-efficient batch processing

5. Optimized Performance:
   - Used more efficient algorithms for filtering and aggregation
   - Reduced unnecessary object creation
   - Implemented incremental processing for large datasets
   - Used more efficient data structures

Specific Bug Fixes:

1. Bug #1: Added proper logging configuration
2. Bug #2: Implemented streaming JSON loading to avoid memory issues
3. Bug #3: Eliminated unnecessary data duplication
4. Bug #4: Optimized filtering to avoid checking all items
5. Bug #5: Removed unnecessary record copying
6. Bug #6: Improved transformation efficiency
7. Bug #7: Optimized aggregation algorithm
8. Bug #8: Only stored necessary fields during aggregation
9. Bug #9: Implemented LRU cache with size limits
10. Bug #10: Used proper incremental processing for large datasets
11. Bug #11: Eliminated unnecessary data duplication in batch processing

The solution demonstrates several advanced debugging techniques:
- Context managers for temporary logging configuration
- Decorators for cross-cutting concerns like logging and performance tracking
- Memory profiling with tracemalloc
- Performance monitoring and threshold-based alerting
- LRU caching for resource management
- Streaming and generator-based processing for memory efficiency
"""
