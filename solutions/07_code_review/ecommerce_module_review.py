"""
Solution: Code Review of E-commerce Module

This file contains a detailed code review of the e-commerce_module.py file,
identifying issues of different types and severity levels, along with suggested solutions.
"""

# ========================================================================
# REVIEW SUMMARY
# ========================================================================
"""
Overall Assessment:
-------------------
The e-commerce module provides a solid foundation for a basic order processing system
with customer, product, and order management capabilities. However, there are several
issues that should be addressed to improve security, maintainability, and reliability.

Key Issues Identified:
---------------------
1. Global state management and database connection issues
2. SQL injection vulnerabilities
3. Lack of proper error handling and transaction management
4. Input validation gaps
5. Potential security issues
6. Code organization and structure problems
7. Missing documentation
8. Performance concerns

Recommendations:
---------------
1. Refactor the module into a class-based design
2. Implement consistent connection management with context managers
3. Use parameterized queries throughout to prevent SQL injection
4. Add comprehensive input validation
5. Improve error handling and logging
6. Add proper documentation including type hints
7. Implement unit tests
"""

# ========================================================================
# DETAILED CODE REVIEW
# ========================================================================

"""
Issue #1: Global State and Database Connection Management
Severity: High
Location: Throughout the file, starting at line 15

Description:
The code uses global variables (conn and cursor) for database connections,
which creates several problems:
- It makes testing difficult
- It makes the code harder to reason about
- It can lead to resource leaks if connections aren't properly closed
- It's not thread-safe

Recommendation:
Refactor the code to use a class-based design with proper connection management.
Use context managers to ensure connections are properly opened and closed.

Example solution:
```python
class ECommerceSystem:
    def __init__(self, db_path='orders.db'):
        self.db_path = db_path
        
    @contextmanager
    def get_connection(self):
        # Create a new connection
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()
            
    def create_customer(self, name, email, address=None):
        if not email or '@' not in email:
            return None
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO customers (name, email, address) VALUES (?, ?, ?)",
                    (name, email, address)
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None
```
"""

"""
Issue #2: SQL Injection Vulnerability
Severity: Critical
Location: Lines 89-90 (update_customer function)

Description:
The function uses string formatting to build a SQL query, which creates
a serious SQL injection vulnerability. An attacker could exploit this to
execute arbitrary SQL commands.

Code:
```python
cursor.execute(
    f"UPDATE customers SET {', '.join(update_fields)} WHERE id = ?",
    tuple(update_values)
)
```

Recommendation:
Use parameterized queries exclusively. Restructure the function to build
a safe query or use ORM libraries like SQLAlchemy.

Example solution:
```python
def update_customer(customer_id, name=None, email=None, address=None):
    updates = {}
    if name is not None:
        updates['name'] = name
    if email is not None:
        updates['email'] = email
    if address is not None:
        updates['address'] = address
    
    if not updates:
        return False
    
    # Build safe parameterized query
    set_clause = ', '.join(f"{field} = ?" for field in updates)
    values = list(updates.values()) + [customer_id]
    
    try:
        cursor.execute(
            f"UPDATE customers SET {set_clause} WHERE id = ?",
            tuple(values)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating customer: {str(e)}")
        return False
```
"""

"""
Issue #3: Lack of Input Validation
Severity: High
Location: Throughout the code, especially in functions like create_order (line 287)

Description:
Many functions lack comprehensive input validation. For example, create_order
doesn't validate that items is a list or that each item has the required keys.

Recommendation:
Add comprehensive input validation to all functions that accept user input.
Validate types, ranges, and required fields.

Example solution for create_order:
```python
def create_order(customer_id, items):
    # Validate customer exists
    customer = get_customer(customer_id)
    if not customer:
        print(f"Customer with ID {customer_id} not found")
        return None
    
    # Validate items
    if not items or not isinstance(items, list):
        print("Items must be a non-empty list")
        return None
    
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            print(f"Item {i} must be a dictionary")
            return None
        if 'product_id' not in item:
            print(f"Item {i} missing product_id")
            return None
        if 'quantity' not in item:
            print(f"Item {i} missing quantity")
            return None
            
        if not isinstance(item['product_id'], int):
            print(f"Item {i} product_id must be an integer")
            return None
        if not isinstance(item['quantity'], int):
            print(f"Item {i} quantity must be an integer")
            return None
```
"""

"""
Issue #4: Inconsistent Error Handling
Severity: Medium
Location: Throughout the code

Description:
Error handling is inconsistent throughout the codebase. Some functions log errors,
others print them, and some simply return None or False without any explanation.

Recommendation:
Implement a consistent error handling strategy. Consider using proper
exceptions for errors and a logging system instead of print statements.

Example improvement:
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ecommerce.log'
)
logger = logging.getLogger('ecommerce')

def create_customer(name, email, address=None):
    if not email or '@' not in email:
        logger.error(f"Invalid email address: {email}")
        raise ValueError("Invalid email address")
    
    try:
        cursor.execute(
            "INSERT INTO customers (name, email, address) VALUES (?, ?, ?)",
            (name, email, address)
        )
        conn.commit()
        customer_id = cursor.lastrowid
        logger.info(f"Created customer #{customer_id}: {name}")
        return customer_id
    except sqlite3.IntegrityError:
        logger.warning(f"Customer with email {email} already exists")
        raise ValueError(f"Customer with email {email} already exists")
    except Exception as e:
        logger.error(f"Error creating customer: {str(e)}")
        raise
```
"""

"""
Issue #5: Resource Leaks
Severity: High
Location: initalize_database function (line 21) and other places

Description:
The code doesn't properly manage database connections and can lead to resource leaks.
For example, the initalize_database function doesn't close the connection if an error occurs.

Additionally, the function name has a typo: "initalize" instead of "initialize".

Recommendation:
Use context managers consistently for resource management.
Correct function name spelling.

Example solution:
```python
def initialize_database():
    with sqlite3.connect('orders.db') as conn:
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Other table creations...
        
        conn.commit()
```
"""

"""
Issue #6: Unhandled Transaction Management
Severity: High
Location: create_order function (line 287)

Description:
The create_order function starts a transaction with "BEGIN TRANSACTION"
but doesn't ensure it's properly committed or rolled back if errors occur
in all code paths.

Recommendation:
Use a try/except/finally block to ensure proper transaction management.

Example solution:
```python
def create_order(customer_id, items):
    # Validation...
    
    # Start transaction
    conn.execute("BEGIN TRANSACTION")
    
    try:
        # Calculate total and check inventory
        total_amount = 0
        order_items = []
        
        for item in items:
            # Process items...
            
        # Create order and items...
        
        # Commit only if everything succeeds
        conn.commit()
        return order_id
    
    except Exception as e:
        # Rollback transaction on any error
        conn.rollback()
        print(f"Error creating order: {str(e)}")
        return None
```
"""

"""
Issue #7: Logging Using Print Statements
Severity: Low
Location: Throughout the code

Description:
The code uses print statements for logging, which is not suitable for a production system.

Recommendation:
Replace print statements with proper logging.

Example:
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ecommerce.log'
)
logger = logging.getLogger('ecommerce')

# Then replace print statements:
# Before:
print(f"Order #{order_id} created successfully with total ${total_amount:.2f}")

# After:
logger.info(f"Order #{order_id} created successfully with total ${total_amount:.2f}")
```
"""

"""
Issue #8: Missing Type Hints
Severity: Low
Location: Throughout the code

Description:
The code doesn't use type hints, which would make it more self-documenting
and enable static type checking.

Recommendation:
Add type hints to all function parameters and return values.

Example:
```python
from typing import Optional, List, Dict, Any, Union

def create_customer(name: str, email: str, address: Optional[str] = None) -> Optional[int]:
    # Function implementation...

def get_customer(customer_id: int) -> Optional[Dict[str, Any]]:
    # Function implementation...
```
"""

"""
Issue #9: Hard-coded Database Path
Severity: Medium
Location: Multiple functions

Description:
The database path is hard-coded in several places, making it difficult to
change or configure for different environments.

Recommendation:
Make the database path configurable, ideally through a settings mechanism
or at least a constant at the top of the file.

Example:
```python
# At the top of the file
DATABASE_PATH = os.environ.get('ECOMMERCE_DB_PATH', 'orders.db')

# When connecting
conn = sqlite3.connect(DATABASE_PATH)
```
"""

"""
Issue #10: Missing Security for Order Cancellation
Severity: Medium
Location: cancel_order function (line 439)

Description:
The cancel_order function doesn't verify that the user has permission
to cancel the order. Anyone with the order ID could cancel any order.

Recommendation:
Add authorization checks to ensure only authorized users can cancel orders.

Example improvement:
```python
def cancel_order(order_id, user_id):
    \"\"\"
    Cancel an order and restore inventory.
    Only pending or processing orders can be cancelled.
    Only the customer who placed the order or an admin can cancel it.
    \"\"\"
    try:
        # Get current order and check permission
        cursor.execute("""
            SELECT status, customer_id FROM orders WHERE id = ?
        """, (order_id,))
        
        result = cursor.fetchone()
        if not result:
            logger.warning(f"Order with ID {order_id} not found")
            return False
            
        current_status, customer_id = result
        
        # Check if user has permission (customer who placed order or admin)
        if user_id != customer_id and not is_admin(user_id):
            logger.warning(f"User {user_id} not authorized to cancel order {order_id}")
            return False
        
        # Rest of the function...
```
"""

"""
Issue #11: Inconsistent Function Return Values
Severity: Low
Location: Throughout the code

Description:
Functions have inconsistent return values. Some return None on error,
others return False, making it difficult to use the API consistently.

Recommendation:
Standardize function return values. Consider using exceptions for errors
and consistent return types.

Example approach:
- Functions that create/retrieve entities return the entity or None if not found
- Functions that perform operations return True/False for success/failure
- All errors raise appropriate exceptions with descriptive messages
"""

"""
Issue #12: Missing Unit Tests
Severity: Medium
Location: Overall project

Description:
The code doesn't include any unit tests, making it difficult to verify
functionality and prevent regressions.

Recommendation:
Add unit tests for all functions, especially critical paths like order creation
and processing.

Example test:
```python
import unittest
from unittest.mock import patch, MagicMock

class TestEcommerceModule(unittest.TestCase):
    def setUp(self):
        # Set up test database
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        # Create schema...
        
    def test_create_customer_valid_data(self):
        with patch('ecommerce_module.conn', self.conn), \
             patch('ecommerce_module.cursor', self.cursor):
            
            customer_id = create_customer('Test User', 'test@example.com', '123 Test St')
            self.assertIsNotNone(customer_id)
            
            # Verify customer was created
            self.cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            customer = self.cursor.fetchone()
            self.assertIsNotNone(customer)
            self.assertEqual(customer[1], 'Test User')
            self.assertEqual(customer[2], 'test@example.com')
    
    def test_create_customer_invalid_email(self):
        result = create_customer('Test User', 'invalid-email', '123 Test St')
        self.assertIsNone(result)
```
"""

"""
Issue #13: Potential Race Conditions
Severity: Medium
Location: update_product_inventory function (line 153)

Description:
The update_product_inventory function has a race condition vulnerability.
It reads the current inventory, modifies it, and then writes it back.
If two concurrent operations modify the same product, one change could be lost.

Recommendation:
Use atomic database operations that don't depend on reading the current state.

Example solution:
```python
def update_product_inventory(product_id, count_change):
    \"\"\"Update a product's inventory count atomically.\"\"\"
    try:
        if count_change < 0:
            # For decreases, check if we have enough inventory
            cursor.execute("""
                UPDATE products 
                SET inventory_count = inventory_count + ? 
                WHERE id = ? AND inventory_count >= ?
            """, (count_change, product_id, abs(count_change)))
        else:
            # For increases, just add to inventory
            cursor.execute("""
                UPDATE products 
                SET inventory_count = inventory_count + ? 
                WHERE id = ?
            """, (count_change, product_id))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating product inventory: {str(e)}")
        return False
```
"""

# ========================================================================
# SUMMARY OF RECOMMENDATIONS
# ========================================================================
"""
Prioritized Recommendations:

Critical (Should be fixed immediately):
1. Fix SQL injection vulnerability in update_customer function
2. Implement proper transaction management in create_order and other functions
3. Fix resource leak issues with database connections

High Priority:
4. Refactor to use a class-based design with proper connection management
5. Add comprehensive input validation, especially for order creation
6. Implement consistent error handling and logging

Medium Priority:
7. Add authorization checks to sensitive operations like order cancellation
8. Fix the race condition in inventory updates
9. Make database path configurable
10. Add unit tests

Low Priority:
11. Add type hints
12. Standardize function return values
13. Improve documentation
"""


# ========================================================================
# REFACTORED CODE EXAMPLE
# ========================================================================
"""
Below is an example of how the module could be refactored to address the major issues.
This is a partial implementation focusing on the core structure and key improvements.

```python
import os
import sqlite3
import json
import datetime
import logging
from contextlib import contextmanager
from typing import List, Dict, Optional, Union, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ecommerce.log'
)
logger = logging.getLogger('ecommerce')

class ECommerceSystem:
    def __init__(self, db_path: str = 'orders.db'):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        \"\"\"Get a database connection using a context manager.\"\"\"
        connection = None
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row
            yield connection
        finally:
            if connection:
                connection.close()
    
    def initialize_database(self) -> bool:
        \"\"\"Initialize the database with required tables.\"\"\"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create tables (same as original)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # Other table creations...
                
                conn.commit()
                logger.info("Database initialized successfully")
                return True
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            return False
    
    def create_customer(self, name: str, email: str, address: Optional[str] = None) -> Optional[int]:
        \"\"\"Create a new customer in the database.\"\"\"
        # Validate input
        if not name or not name.strip():
            logger.error("Customer name cannot be empty")
            return None
            
        if not email or '@' not in email:
            logger.error(f"Invalid email address: {email}")
            return None
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO customers (name, email, address) VALUES (?, ?, ?)",
                    (name, email, address)
                )
                conn.commit()
                customer_id = cursor.lastrowid
                logger.info(f"Created customer #{customer_id}: {name}")
                return customer_id
        except sqlite3.IntegrityError:
            logger.warning(f"Customer with email {email} already exists")
            return None
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            return None
    
    def update_customer(self, customer_id: int, 
                       name: Optional[str] = None, 
                       email: Optional[str] = None, 
                       address: Optional[str] = None) -> bool:
        \"\"\"Update a customer's information.\"\"\"
        # Build update data with proper validation
        updates = {}
        if name is not None:
            if not name.strip():
                logger.error("Customer name cannot be empty")
                return False
            updates['name'] = name
            
        if email is not None:
            if not email or '@' not in email:
                logger.error(f"Invalid email address: {email}")
                return False
            updates['email'] = email
            
        if address is not None:
            updates['address'] = address
        
        if not updates:
            logger.warning("No fields to update")
            return False
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build safe parameterized query
                set_clause = ', '.join(f"{field} = ?" for field in updates)
                values = list(updates.values()) + [customer_id]
                
                cursor.execute(
                    f"UPDATE customers SET {set_clause} WHERE id = ?",
                    tuple(values)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Updated customer #{customer_id}")
                    return True
                else:
                    logger.warning(f"Customer with ID {customer_id} not found")
                    return False
        except Exception as e:
            logger.error(f"Error updating customer: {str(e)}")
            return False
    
    # Similar refactoring for other methods...
    
    def create_order(self, customer_id: int, 
                    items: List[Dict[str, Union[int, float]]]) -> Optional[int]:
        \"\"\"Create a new order with the given items.\"\"\"
        # Validate customer exists
        customer = self.get_customer(customer_id)
        if not customer:
            logger.error(f"Customer with ID {customer_id} not found")
            return None
        
        # Validate items
        if not items or not isinstance(items, list):
            logger.error("Items must be a non-empty list")
            return None
            
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                logger.error(f"Item {i} must be a dictionary")
                return None
            if 'product_id' not in item:
                logger.error(f"Item {i} missing product_id")
                return None
            if 'quantity' not in item:
                logger.error(f"Item {i} missing quantity")
                return None
                
            if not isinstance(item['product_id'], int):
                logger.error(f"Item {i} product_id must be an integer")
                return None
            if not isinstance(item['quantity'], int) or item['quantity'] <= 0:
                logger.error(f"Item {i} quantity must be a positive integer")
                return None
        
        with self.get_connection() as conn:
            # Start transaction
            conn.execute("BEGIN TRANSACTION")
            cursor = conn.cursor()
            
            try:
                # Calculate total and check inventory
                total_amount = 0
                order_items = []
                
                for item in items:
                    product_id = item['product_id']
                    quantity = item['quantity']
                    
                    # Get product info
                    cursor.execute(
                        "SELECT * FROM products WHERE id = ?",
                        (product_id,)
                    )
                    product = cursor.fetchone()
                    
                    if not product:
                        raise ValueError(f"Product with ID {product_id} not found")
                    
                    if not product['active']:
                        raise ValueError(f"Product {product['name']} is not active")
                    
                    if product['inventory_count'] < quantity:
                        raise ValueError(
                            f"Insufficient inventory for {product['name']}: "
                            f"requested {quantity}, available {product['inventory_count']}"
                        )
                    
                    # Calculate item total
                    item_total = product['price'] * quantity
                    total_amount += item_total
                    
                    # Store item details for later
                    order_items.append({
                        'product_id': product_id,
                        'quantity': quantity,
                        'price_per_unit': product['price']
                    })
                    
                    # Update inventory - atomic update
                    cursor.execute(
                        \"\"\"
                        UPDATE products 
                        SET inventory_count = inventory_count - ?
                        WHERE id = ? AND inventory_count >= ?
                        \"\"\",
                        (quantity, product_id, quantity)
                    )
                    
                    if cursor.rowcount == 0:
                        # This should not happen if we checked inventory correctly
                        raise ValueError(
                            f"Failed to update inventory for product {product_id}"
                        )
                
                # Create the order
                cursor.execute(
                    "INSERT INTO orders (customer_id, total_amount) VALUES (?, ?)",
                    (customer_id, total_amount)
                )
                order_id = cursor.lastrowid
                
                # Add order items
                for item in order_items:
                    cursor.execute(
                        \"\"\"
                        INSERT INTO order_items 
                        (order_id, product_id, quantity, price_per_unit)
                        VALUES (?, ?, ?, ?)
                        \"\"\",
                        (order_id, item['product_id'], item['quantity'], 
                         item['price_per_unit'])
                    )
                
                # Commit the transaction
                conn.commit()
                logger.info(
                    f"Order #{order_id} created successfully "
                    f"with total ${total_amount:.2f}"
                )
                return order_id
            
            except Exception as e:
                # Rollback in case of error
                conn.rollback()
                logger.error(f"Error creating order: {str(e)}")
                return None
```
"""
