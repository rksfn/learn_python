# Advanced Debugging Techniques

Welcome to the eighth and final module of the Python Debugging & Code Review Masterclass! In this module, we'll explore advanced debugging techniques and tools that can help you tackle the most complex and challenging debugging scenarios in your Python applications.

## Learning Objectives

By the end of this module, you will be able to:
- Implement logging effectively as a debugging strategy
- Use profiling tools to identify performance bottlenecks
- Debug memory leaks and other resource management issues
- Troubleshoot multithreading and concurrency problems
- Debug network and API-related issues
- Create and use custom debugging tools and decorators
- Implement automated testing strategies that prevent bugs

## Effective Logging for Debugging

Logging is one of the most powerful debugging tools available, especially for production environments where traditional debuggers cannot be used.

### Key Logging Concepts

1. **Logging Levels**: Understanding when to use each level
   - DEBUG: Detailed information for diagnosing problems
   - INFO: Confirmation that things are working as expected
   - WARNING: Indication that something unexpected happened
   - ERROR: Error that prevented something from working
   - CRITICAL: Serious error that might cause program termination

2. **Structured Logging**: Creating logs that are machine-readable and searchable
   - Including contextual information (request IDs, user IDs, etc.)
   - Using consistent formats (JSON, etc.)
   - Adding timestamps and correlation IDs

3. **Log Rotation and Retention**: Managing log file growth
   - Setting appropriate retention periods
   - Configuring size-based rotation
   - Archiving and compression strategies

### Python's Logging Module

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='application.log'
)

# Create a logger
logger = logging.getLogger('my_application')

# Log at different levels
logger.debug('Detailed information for debugging')
logger.info('Confirmation that things are working')
logger.warning('Something unexpected happened')
logger.error('Error that prevented something from working')
logger.critical('Serious error that might cause program termination')

# Log with exception information
try:
    result = 10 / 0
except Exception as e:
    logger.error('Failed to perform division', exc_info=True)
```

### Advanced Logging Techniques

1. **Context Managers for Temporary Logging Configuration**:
   ```python
   @contextmanager
   def temporary_debug_level():
       logger = logging.getLogger()
       original_level = logger.level
       logger.setLevel(logging.DEBUG)
       try:
           yield
       finally:
           logger.setLevel(original_level)
   
   # Usage
   with temporary_debug_level():
       # Code that needs detailed debug logging
   ```

2. **Logging Decorators**:
   ```python
   def log_function_call(func):
       @wraps(func)
       def wrapper(*args, **kwargs):
           logger = logging.getLogger(func.__module__)
           logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
           try:
               result = func(*args, **kwargs)
               logger.debug(f"{func.__name__} returned {result}")
               return result
           except Exception as e:
               logger.error(f"{func.__name__} raised {e.__class__.__name__}: {e}")
               raise
       return wrapper
   
   # Usage
   @log_function_call
   def calculate_total(items):
       return sum(item.price for item in items)
   ```

## Performance Profiling

Profiling helps identify bottlenecks in your code, showing you where optimization efforts will have the greatest impact.

### Python's Built-in Profilers

1. **cProfile**: Time profiling (measures execution time)
   ```python
   import cProfile
   
   # Profile a function call
   cProfile.run('my_function()')
   
   # Profile and save results to a file
   cProfile.run('my_function()', 'profile_results')
   
   # Analyze results
   import pstats
   p = pstats.Stats('profile_results')
   p.strip_dirs().sort_stats('cumulative').print_stats(10)  # Print top 10 time-consuming functions
   ```

2. **Tracemalloc**: Memory profiling (tracks memory allocations)
   ```python
   import tracemalloc
   
   # Start tracking memory allocations
   tracemalloc.start()
   
   # Run your code
   result = my_function()
   
   # Get memory snapshot
   snapshot = tracemalloc.take_snapshot()
   
   # Get top 10 lines where memory is allocated
   top_stats = snapshot.statistics('lineno')
   for stat in top_stats[:10]:
       print(stat)
   ```

### Popular Third-Party Profiling Tools

1. **line_profiler**: Line-by-line profiling
2. **memory_profiler**: Detailed memory usage tracking
3. **py-spy**: Sampling profiler that can attach to running processes
4. **pyflame**: Low-overhead profiler that generates flame graphs

### Visualizing Profiling Results

1. **SnakeViz**: Visualizes cProfile output as an interactive sunburst chart
2. **Flamegraph**: Visualizes profiling data as a flame graph
3. **KCachegrind**: Powerful visualization tool for callgrind format data

## Debugging Memory Issues

Memory issues can be challenging to diagnose and fix, but Python provides several tools to help.

### Common Memory Issues

1. **Memory Leaks**: When objects are not properly garbage collected
2. **Excessive Memory Usage**: When code uses more memory than necessary
3. **Memory Fragmentation**: When memory becomes fragmented, reducing performance

### Memory Debugging Tools

1. **Using `sys.getsizeof()` for Basic Memory Usage**:
   ```python
   import sys
   
   data = [1, 2, 3, 4, 5]
   print(f"Size of data: {sys.getsizeof(data)} bytes")
   ```

2. **Using `objgraph` for Tracking Object References**:
   ```python
   import objgraph
   
   # Find the objects consuming the most memory
   objgraph.show_most_common_types()
   
   # Track what's keeping an object alive
   objgraph.show_backrefs([problem_object], filename='backrefs.png')
   ```

3. **Using `gc` Module for Garbage Collection Control**:
   ```python
   import gc
   
   # Force garbage collection
   gc.collect()
   
   # Get objects that couldn't be collected
   unreachable = gc.collect()
   print(f"Unreachable objects: {unreachable}")
   
   # Disable automatic garbage collection
   gc.disable()
   
   # Custom work...
   
   # Manual collection when ready
   gc.collect()
   
   # Enable automatic garbage collection again
   gc.enable()
   ```

### Best Practices for Memory Management

1. **Use context managers for resource cleanup**
2. **Be careful with circular references**
3. **Use weakref for breaking reference cycles**
4. **Prefer generators and iterators for large datasets**
5. **Implement `__slots__` for classes with many instances**
6. **Use appropriate data structures (e.g., `collections.Counter` instead of custom dictionaries)**

## Debugging Concurrency Issues

Concurrency bugs are notoriously difficult to diagnose and fix because they often appear inconsistently and can be hard to reproduce.

### Common Concurrency Issues

1. **Race Conditions**: When the outcome depends on the order of operations
2. **Deadlocks**: When two or more threads are waiting for each other
3. **Starvation**: When a thread is perpetually denied resources
4. **Livelocks**: When threads are actively performing operations but not making progress

### Threading Debugging Techniques

1. **Using `threading.enumerate()` to List All Threads**:
   ```python
   import threading
   
   # List all active threads
   for thread in threading.enumerate():
       print(f"Thread name: {thread.name}, is alive: {thread.is_alive()}")
   ```

2. **Using Thread Names and IDs for Identification**:
   ```python
   import threading
   
   def worker():
       thread = threading.current_thread()
       print(f"Worker running in {thread.name} (ID: {thread.ident})")
   
   # Create a named thread
   thread = threading.Thread(name="WorkerThread", target=worker)
   thread.start()
   ```

3. **Using Thread-Local Storage for Isolation**:
   ```python
   import threading
   
   # Create thread-local storage
   local_data = threading.local()
   
   def worker():
       # Each thread has its own 'value'
       local_data.value = threading.current_thread().name
       print(f"Thread {threading.current_thread().name} has value: {local_data.value}")
   
   threads = [threading.Thread(name=f"Thread-{i}", target=worker) for i in range(3)]
   for thread in threads:
       thread.start()
   ```

### Multprocessing Debugging Techniques

1. **Using Process Names and PIDs**:
   ```python
   import multiprocessing
   import os
   
   def worker():
       process = multiprocessing.current_process()
       print(f"Worker running in {process.name} (PID: {os.getpid()})")
   
   process = multiprocessing.Process(name="WorkerProcess", target=worker)
   process.start()
   ```

2. **Using Locks for Synchronization**:
   ```python
   import multiprocessing
   
   def worker(lock, shared_resource):
       with lock:
           # Critical section - only one process at a time
           shared_resource.value += 1
   
   # Create a shared resource and lock
   shared_resource = multiprocessing.Value('i', 0)
   lock = multiprocessing.Lock()
   
   processes = [
       multiprocessing.Process(target=worker, args=(lock, shared_resource))
       for _ in range(10)
   ]
   
   for process in processes:
       process.start()
   ```

### Debugging Tools for Concurrency

1. **`faulthandler` for Diagnosing Crashes**:
   ```python
   import faulthandler
   
   # Enable faulthandler to get tracebacks on crashes
   faulthandler.enable()
   ```

2. **Deadlock Detection with Custom Monitoring**:
   ```python
   import threading
   import time
   
   def monitor_threads():
       while True:
           time.sleep(10)  # Check every 10 seconds
           for thread in threading.enumerate():
               if thread.name != threading.current_thread().name:
                   print(f"Thread {thread.name} is {'alive' if thread.is_alive() else 'dead'}")
                   # You could add stack trace printing here with traceback module
   
   # Start the monitor
   monitor = threading.Thread(name="ThreadMonitor", target=monitor_threads, daemon=True)
   monitor.start()
   ```

## Network and API Debugging

Debugging network interactions and API calls requires specialized approaches.

### Debugging HTTP Requests

1. **Using `requests` Session with Logging**:
   ```python
   import requests
   from requests.adapters import HTTPAdapter
   
   class LoggingAdapter(HTTPAdapter):
       def send(self, request, **kwargs):
           print(f"Sending request: {request.method} {request.url}")
           print(f"Headers: {request.headers}")
           if request.body:
               print(f"Body: {request.body}")
           response = super().send(request, **kwargs)
           print(f"Response status: {response.status_code}")
           print(f"Response headers: {response.headers}")
           return response
   
   session = requests.Session()
   session.mount('https://', LoggingAdapter())
   session.mount('http://', LoggingAdapter())
   
   # Now all requests will be logged
   response = session.get('https://api.example.com/data')
   ```

2. **Using `curl` for HTTP Testing**:
   ```python
   import subprocess
   
   def curl_request(url, method='GET', headers=None, data=None):
       cmd = ['curl', '-X', method, '-v']
       
       if headers:
           for key, value in headers.items():
               cmd.extend(['-H', f'{key}: {value}'])
       
       if data:
           cmd.extend(['-d', data])
       
       cmd.append(url)
       
       result = subprocess.run(cmd, capture_output=True, text=True)
       print(result.stderr)  # Verbose output goes to stderr
       return result.stdout
   
   # Example usage
   response = curl_request('https://api.example.com/data',
                          headers={'Content-Type': 'application/json'},
                          method='POST',
                          data='{"key": "value"}')
   ```

### Network Traffic Analysis

1. **Using `mitmproxy` for HTTP/HTTPS Inspection**:
   - Configure your application to use the mitmproxy as a proxy
   - Inspect all traffic in the mitmproxy console

2. **Using `tcpdump` for Raw Packet Capture**:
   ```bash
   # Capture packets on port 80 (HTTP)
   sudo tcpdump -A -s 0 'tcp port 80'
   ```

3. **Wireshark** for detailed packet analysis

### Mocking and Stubbing for Isolation

1. **Using `responses` to Mock HTTP Requests**:
   ```python
   import responses
   import requests
   
   @responses.activate
   def test_api_call():
       responses.add(
           responses.GET,
           'https://api.example.com/data',
           json={'key': 'value'},
           status=200
       )
       
       # This will use the mock response, not the real API
       response = requests.get('https://api.example.com/data')
       assert response.json() == {'key': 'value'}
   ```

2. **Using `unittest.mock` for General Mocking**:
   ```python
   from unittest.mock import patch
   import requests
   
   def get_user_data(user_id):
       response = requests.get(f'https://api.example.com/users/{user_id}')
       return response.json()
   
   # Test with a mock
   @patch('requests.get')
   def test_get_user_data(mock_get):
       # Configure the mock
       mock_get.return_value.json.return_value = {'id': 123, 'name': 'Test User'}
       
       # Call the function
       result = get_user_data(123)
       
       # Assert the results
       assert result == {'id': 123, 'name': 'Test User'}
       mock_get.assert_called_once_with('https://api.example.com/users/123')
   ```

## Custom Debugging Tools

Creating your own debugging tools can help with specific challenges in your applications.

### Custom Decorators for Debugging

1. **Function Tracing Decorator**:
   ```python
   import functools
   import inspect
   import logging
   
   logger = logging.getLogger(__name__)
   
   def trace(func):
       @functools.wraps(func)
       def wrapper(*args, **kwargs):
           arg_values = [repr(arg) for arg in args]
           kwarg_values = [f"{k}={repr(v)}" for k, v in kwargs.items()]
           all_args = ', '.join(arg_values + kwarg_values)
           
           logger.debug(f"Calling: {func.__name__}({all_args})")
           
           # Get the source code line numbers
           source_lines, start_line = inspect.getsourcelines(func)
           logger.debug(f"  defined at line {start_line} in {inspect.getfile(func)}")
           
           result = func(*args, **kwargs)
           
           logger.debug(f"{func.__name__} returned: {repr(result)}")
           return result
       return wrapper
   
   # Usage
   @trace
   def calculate_total(x, y, multiply=False):
       if multiply:
           return x * y
       return x + y
   ```

2. **Performance Monitoring Decorator**:
   ```python
   import time
   import functools
   import logging
   
   logger = logging.getLogger(__name__)
   
   def timing(threshold=None):
       def decorator(func):
           @functools.wraps(func)
           def wrapper(*args, **kwargs):
               start_time = time.time()
               result = func(*args, **kwargs)
               end_time = time.time()
               
               execution_time = end_time - start_time
               
               # Only log if execution time exceeds threshold (if provided)
               if threshold is None or execution_time > threshold:
                   logger.info(f"{func.__name__} took {execution_time:.4f} seconds to execute")
               
               return result
           return wrapper
       return decorator
   
   # Usage
   @timing(threshold=0.5)  # Only log if function takes more than 0.5 seconds
   def slow_function():
       time.sleep(1)
       return "Done"
   ```

### Custom Context Managers

1. **Timer Context Manager**:
   ```python
   import time
   import logging
   from contextlib import contextmanager
   
   logger = logging.getLogger(__name__)
   
   @contextmanager
   def timer(operation_name):
       start_time = time.time()
       try:
           yield
       finally:
           end_time = time.time()
           execution_time = end_time - start_time
           logger.info(f"{operation_name} took {execution_time:.4f} seconds")
   
   # Usage
   with timer("Data processing"):
       # Code to time
       process_large_dataset()
   ```

2. **Temporary Debug Logging Context Manager**:
   ```python
   import logging
   from contextlib import contextmanager
   
   @contextmanager
   def debug_logging(logger_name):
       logger = logging.getLogger(logger_name)
       original_level = logger.level
       logger.setLevel(logging.DEBUG)
       try:
           yield logger
       finally:
           logger.setLevel(original_level)
   
   # Usage
   with debug_logging("my_module") as logger:
       logger.debug("This will be logged at DEBUG level")
   ```

## Preventive Debugging with Testing

The best way to debug is to prevent bugs in the first place. Comprehensive testing helps catch issues before they reach production.

### Effective Testing Strategies

1. **Unit Testing**:
   ```python
   import unittest
   
   class TestCalculator(unittest.TestCase):
       def test_addition(self):
           self.assertEqual(Calculator.add(2, 3), 5)
       
       def test_division(self):
           self.assertEqual(Calculator.divide(10, 2), 5)
           
       def test_division_by_zero(self):
           with self.assertRaises(ValueError):
               Calculator.divide(10, 0)
   ```

2. **Property-Based Testing with Hypothesis**:
   ```python
   from hypothesis import given
   from hypothesis import strategies as st
   
   @given(st.integers(), st.integers().filter(lambda x: x != 0))
   def test_division_property(a, b):
       result = Calculator.divide(a, b)
       assert Calculator.multiply(result, b) == a
   ```

3. **Mutation Testing**:
   - Use tools like mutmut or cosmic-ray to verify test quality
   - These tools make small modifications to your code and check if tests catch them

### Continuous Integration Practices

1. **Automated Testing on Every Commit**
2. **Code Coverage Reports**
3. **Static Analysis with Tools Like `pylint`, `flake8`, and `mypy`**
4. **Security Vulnerability Scanning**

## Conclusion

Advanced debugging is as much art as science. The techniques in this module give you a powerful toolkit for solving the most difficult bugs in your Python applications.

Remember these key principles:
1. **Use the right tool for the job**: Different problems require different approaches
2. **Be systematic**: Work methodically rather than randomly trying solutions
3. **Isolate the issue**: Reproduce the problem in the simplest possible context
4. **Focus on prevention**: Good practices prevent bugs from occurring in the first place

In the exercises for this module, you'll practice these advanced techniques on realistic scenarios, giving you hands-on experience with these powerful debugging tools.
