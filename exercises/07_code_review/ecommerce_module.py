"""
Exercise 1: Practicing Code Reviews

In this exercise, you'll practice conducting code reviews by examining this
Python module which contains several issues. Your task is to identify problems, 
categorize them by severity, and provide constructive feedback.

The module implements a simple e-commerce order processing system.
"""

import datetime
import random
import json
import sqlite3
from typing import Dict, List, Optional, Union, Any

# Global variables for database connection
conn = None
cursor = None

# Database initialization
def initalize_database():
    """Initialize the SQLite database with the required tables."""
    global conn, cursor
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        inventory_count INTEGER DEFAULT 0,
        active BOOLEAN DEFAULT 1
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        total_amount REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price_per_unit REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')
    
    conn.commit()

# Customer operations
def create_customer(name, email, address=None):
    """Create a new customer in the database."""
    if not email or '@' not in email:
        print("Invalid email address")
        return None
    
    try:
        cursor.execute(
            "INSERT INTO customers (name, email, address) VALUES (?, ?, ?)",
            (name, email, address)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"Customer with email {email} already exists")
        return None
    except Exception as e:
        print(f"Error creating customer: {str(e)}")
        return None

def get_customer(customer_id):
    """Retrieve a customer by ID."""
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = cursor.fetchone()
    if customer:
        return {
            'id': customer[0],
            'name': customer[1],
            'email': customer[2],
            'address': customer[3],
            'created_at': customer[4]
        }
    return None

def update_customer(customer_id, name=None, email=None, address=None):
    """Update a customer's information."""
    # Build update query based on provided fields
    update_fields = []
    update_values = []
    
    if name:
        update_fields.append("name = ?")
        update_values.append(name)
    
    if email:
        update_fields.append("email = ?")
        update_values.append(email)
    
    if address:
        update_fields.append("address = ?")
        update_values.append(address)
    
    if not update_fields:
        print("No fields to update")
        return False
    
    update_values.append(customer_id)
    
    try:
        cursor.execute(
            f"UPDATE customers SET {', '.join(update_fields)} WHERE id = ?",
            tuple(update_values)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating customer: {str(e)}")
        return False

# Product operations
def create_product(name, price, description=None, inventory_count=0):
    """Create a new product in the database."""
    if price <= 0:
        print("Price must be greater than zero")
        return None
    
    try:
        cursor.execute(
            "INSERT INTO products (name, description, price, inventory_count) VALUES (?, ?, ?, ?)",
            (name, description, price, inventory_count)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error creating product: {str(e)}")
        return None

def get_product(product_id):
    """Retrieve a product by ID."""
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    if product:
        return {
            'id': product[0],
            'name': product[1],
            'description': product[2],
            'price': product[3],
            'inventory_count': product[4],
            'active': bool(product[5])
        }
    return None

def update_product_inventory(product_id, count_change):
    """Update a product's inventory count."""
    try:
        # Get current inventory
        cursor.execute("SELECT inventory_count FROM products WHERE id = ?", (product_id,))
        current_count = cursor.fetchone()
        
        if current_count is None:
            print(f"Product with ID {product_id} not found")
            return False
        
        current_count = current_count[0]
        new_count = current_count + count_change
        
        # Don't allow negative inventory
        if new_count < 0:
            print(f"Cannot reduce inventory below zero (current: {current_count}, change: {count_change})")
            return False
        
        cursor.execute(
            "UPDATE products SET inventory_count = ? WHERE id = ?",
            (new_count, product_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating product inventory: {str(e)}")
        return False

def search_products(query, active_only=True):
    """Search for products by name or description."""
    try:
        search_term = f"%{query}%"
        if active_only:
            cursor.execute(
                "SELECT * FROM products WHERE (name LIKE ? OR description LIKE ?) AND active = 1",
                (search_term, search_term)
            )
        else:
            cursor.execute(
                "SELECT * FROM products WHERE name LIKE ? OR description LIKE ?",
                (search_term, search_term)
            )
        
        products = []
        for product in cursor.fetchall():
            products.append({
                'id': product[0],
                'name': product[1],
                'description': product[2],
                'price': product[3],
                'inventory_count': product[4],
                'active': bool(product[5])
            })
        return products
    except Exception as e:
        print(f"Error searching products: {str(e)}")
        return []

# Order operations
def create_order(customer_id, items):
    """
    Create a new order with the given items.
    
    Args:
        customer_id: The ID of the customer placing the order
        items: List of dictionaries with product_id and quantity keys
    
    Returns:
        The order ID if successful, None otherwise
    """
    # Validate customer exists
    customer = get_customer(customer_id)
    if not customer:
        print(f"Customer with ID {customer_id} not found")
        return None
    
    # Validate items
    if not items:
        print("No items provided for the order")
        return None
    
    # Start transaction
    conn.execute("BEGIN TRANSACTION")
    
    try:
        # Calculate total and check inventory
        total_amount = 0
        order_items = []
        
        for item in items:
            product_id = item['product_id']
            quantity = item['quantity']
            
            if quantity <= 0:
                raise ValueError(f"Invalid quantity for product {product_id}: {quantity}")
            
            # Get product info
            product = get_product(product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found")
            
            if not product['active']:
                raise ValueError(f"Product {product['name']} is not active")
            
            if product['inventory_count'] < quantity:
                raise ValueError(f"Insufficient inventory for {product['name']}")
            
            # Calculate item total
            item_total = product['price'] * quantity
            total_amount += item_total
            
            # Store item details for later
            order_items.append({
                'product_id': product_id,
                'quantity': quantity,
                'price_per_unit': product['price']
            })
            
            # Update inventory - we'll reduce it now
            if not update_product_inventory(product_id, -quantity):
                raise ValueError(f"Failed to update inventory for product {product_id}")
        
        # Create the order
        cursor.execute(
            "INSERT INTO orders (customer_id, total_amount) VALUES (?, ?)",
            (customer_id, total_amount)
        )
        order_id = cursor.lastrowid
        
        # Add order items
        for item in order_items:
            cursor.execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity, price_per_unit)
                VALUES (?, ?, ?, ?)
                """,
                (order_id, item['product_id'], item['quantity'], item['price_per_unit'])
            )
        
        # Commit the transaction
        conn.commit()
        print(f"Order #{order_id} created successfully with total ${total_amount:.2f}")
        return order_id
    
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"Error creating order: {str(e)}")
        return None

def get_order(order_id):
    """Get order details by ID, including all items."""
    try:
        # Get order header
        cursor.execute("""
            SELECT o.id, o.customer_id, c.name as customer_name, o.status, 
                   o.total_amount, o.created_at
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE o.id = ?
        """, (order_id,))
        
        order_data = cursor.fetchone()
        if not order_data:
            return None
        
        # Build order dict
        order = {
            'id': order_data[0],
            'customer_id': order_data[1],
            'customer_name': order_data[2],
            'status': order_data[3],
            'total_amount': order_data[4],
            'created_at': order_data[5],
            'items': []
        }
        
        # Get order items
        cursor.execute("""
            SELECT oi.product_id, p.name as product_name, oi.quantity, 
                   oi.price_per_unit, (oi.quantity * oi.price_per_unit) as item_total
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        """, (order_id,))
        
        for item in cursor.fetchall():
            order['items'].append({
                'product_id': item[0],
                'product_name': item[1],
                'quantity': item[2],
                'price_per_unit': item[3],
                'item_total': item[4]
            })
        
        return order
    
    except Exception as e:
        print(f"Error retrieving order: {str(e)}")
        return None

def update_order_status(order_id, new_status):
    """Update the status of an order."""
    valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    
    if new_status not in valid_statuses:
        print(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return False
    
    try:
        cursor.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (new_status, order_id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            print(f"Order with ID {order_id} not found")
            return False
        
        print(f"Order #{order_id} status updated to: {new_status}")
        return True
    
    except Exception as e:
        print(f"Error updating order status: {str(e)}")
        return False

def cancel_order(order_id):
    """
    Cancel an order and restore inventory.
    Only pending or processing orders can be cancelled.
    """
    try:
        # Get current order status
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        status_result = cursor.fetchone()
        
        if not status_result:
            print(f"Order with ID {order_id} not found")
            return False
        
        current_status = status_result[0]
        if current_status not in ['pending', 'processing']:
            print(f"Cannot cancel order with status: {current_status}")
            return False
        
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Get order items to restore inventory
        cursor.execute(
            "SELECT product_id, quantity FROM order_items WHERE order_id = ?",
            (order_id,)
        )
        
        for item in cursor.fetchall():
            product_id, quantity = item
            # Restore inventory
            update_product_inventory(product_id, quantity)
        
        # Update order status
        cursor.execute(
            "UPDATE orders SET status = 'cancelled' WHERE id = ?",
            (order_id,)
        )
        
        # Commit transaction
        conn.commit()
        print(f"Order #{order_id} has been cancelled and inventory restored")
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error cancelling order: {str(e)}")
        return False

# Reporting functions
def generate_sales_report(start_date, end_date):
    """
    Generate a sales report for a given date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Dictionary with sales report data
    """
    try:
        # Query to get order totals by date
        cursor.execute("""
            SELECT 
                DATE(created_at) as order_date,
                COUNT(*) as order_count,
                SUM(total_amount) as total_sales
            FROM orders
            WHERE status != 'cancelled'
              AND DATE(created_at) BETWEEN ? AND ?
            GROUP BY DATE(created_at)
            ORDER BY order_date
        """, (start_date, end_date))
        
        daily_sales = []
        for row in cursor.fetchall():
            daily_sales.append({
                'date': row[0],
                'order_count': row[1],
                'total_sales': row[2]
            })
        
        # Get top selling products
        cursor.execute("""
            SELECT 
                p.id,
                p.name,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.quantity * oi.price_per_unit) as total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status != 'cancelled'
              AND DATE(o.created_at) BETWEEN ? AND ?
            GROUP BY p.id, p.name
            ORDER BY total_revenue DESC
            LIMIT 5
        """, (start_date, end_date))
        
        top_products = []
        for row in cursor.fetchall():
            top_products.append({
                'id': row[0],
                'name': row[1],
                'total_quantity': row[2],
                'total_revenue': row[3]
            })
        
        # Calculate overall totals
        total_orders = sum(day['order_count'] for day in daily_sales)
        total_revenue = sum(day['total_sales'] for day in daily_sales)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Build and return the report
        report = {
            'start_date': start_date,
            'end_date': end_date,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_order_value': avg_order_value,
            'daily_sales': daily_sales,
            'top_products': top_products,
            'generated_at': datetime.datetime.now().isoformat()
        }
        
        return report
    
    except Exception as e:
        print(f"Error generating sales report: {str(e)}")
        return None

def export_report_to_json(report_data, filename):
    """Export a report to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"Report exported to {filename}")
        return True
    except Exception as e:
        print(f"Error exporting report: {str(e)}")
        return False

# Utility functions
def close_db_connection():
    """Close the database connection."""
    if conn:
        conn.close()
        print("Database connection closed")

def check_connection():
    """Check if database connection is active and reconnect if needed."""
    global conn, cursor
    try:
        # Try a simple query to check connection
        cursor.execute("SELECT 1")
        return True
    except (sqlite3.ProgrammingError, sqlite3.OperationalError, AttributeError):
        # Connection is closed or cursor is invalid, try to reconnect
        try:
            conn = sqlite3.connect('orders.db')
            cursor = conn.cursor()
            return True
        except Exception as e:
            print(f"Failed to reconnect to database: {str(e)}")
            return False

def generate_order_id():
    """Generate a unique order ID."""
    # Simple implementation for the exercise
    timestamp = int(datetime.datetime.now().timestamp())
    random_part = random.randint(1000, 9999)
    return f"{timestamp}-{random_part}"

# Demo function to show the module in action
def run_demo():
    """Run a demo to show the e-commerce system in action."""
    initalize_database()
    
    print("Creating test customers...")
    customer1_id = create_customer("John Doe", "john@example.com", "123 Main St")
    customer2_id = create_customer("Jane Smith", "jane@example.com", "456 Elm St")
    
    print("\nCreating test products...")
    product1_id = create_product("Laptop", 999.99, "High-performance laptop", 10)
    product2_id = create_product("Headphones", 149.99, "Noise-cancelling headphones", 20)
    product3_id = create_product("Mouse", 29.99, "Wireless mouse", 50)
    
    print("\nCreating a test order...")
    order_items = [
        {'product_id': product1_id, 'quantity': 1},
        {'product_id': product3_id, 'quantity': 2}
    ]
    order_id = create_order(customer1_id, order_items)
    
    print("\nGetting order details...")
    order = get_order(order_id)
    print(json.dumps(order, indent=2))
    
    print("\nUpdating order status...")
    update_order_status(order_id, "processing")
    
    print("\nGenerating sales report...")
    today = datetime.datetime.now().date()
    week_ago = today - datetime.timedelta(days=7)
    report = generate_sales_report(week_ago.isoformat(), today.isoformat())
    if report:
        print(f"Total orders in period: {report['total_orders']}")
        print(f"Total revenue in period: ${report['total_revenue']:.2f}")
    
    print("\nDemo completed!")
    close_db_connection()

if __name__ == "__main__":
    run_demo()
