"""
Solution to Exercise 2: Database Interaction Debugging

This solution addresses the 13 bugs in the database interaction module,
demonstrating fixes for common database-related issues:
- Connection pooling problems
- SQL injection vulnerabilities
- Query performance issues (N+1 queries)
- Transaction handling errors
- Parameter validation failures
- Memory inefficiency problems
- Resource leaks

Each fix is documented with a detailed explanation.
"""

import sqlite3
import time
import logging
import os
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple, Generator, Union
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='db_debugging.log'
)
logger = logging.getLogger('db_debugging')

# Database configuration
DATABASE_PATH = 'taskmanager.db'
DEFAULT_TIMEOUT = 5.0  # seconds
MAX_CONNECTIONS = 5
MAX_BATCH_SIZE = 1000  # Maximum number of items to process in a batch

# FIX #1: Improved connection pooling
class ConnectionPool:
    """A simple database connection pool that properly manages connections."""
    
    def __init__(self, db_path: str, max_connections: int = 5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = []
        
    def get_connection(self) -> sqlite3.Connection:
        """Get a connection from the pool or create a new one if the pool is empty."""
        if self.connections:
            connection = self.connections.pop()
            
            # Validate the connection before returning it
            try:
                # Execute a simple query to test the connection
                connection.execute("SELECT 1")
                return connection
            except sqlite3.Error as e:
                # Connection is not valid, close it and create a new one
                logger.warning(f"Invalid connection from pool: {e}")
                try:
                    connection.close()
                except:
                    pass
        
        # Create a new connection
        try:
            connection = sqlite3.connect(
                self.db_path,
                timeout=DEFAULT_TIMEOUT,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            connection.row_factory = sqlite3.Row
            return connection
        except sqlite3.Error as e:
            logger.error(f"Error creating database connection: {e}")
            raise
    
    def release_connection(self, connection: sqlite3.Connection) -> None:
        """Return a connection to the pool if it's valid and the pool isn't full."""
        # FIX #2: Connection validation
        # Validate the connection before returning it to the pool
        try:
            # Check if the connection is still valid
            connection.execute("SELECT 1")
            
            # Check if we already have max connections in the pool
            if len(self.connections) < self.max_connections:
                self.connections.append(connection)
            else:
                # Pool is full, close this connection
                connection.close()
        except sqlite3.Error:
            # Connection is no longer valid, close it
            try:
                connection.close()
            except:
                pass
    
    def close_all(self) -> None:
        """Close all connections in the pool."""
        for connection in self.connections:
            try:
                connection.close()
            except:
                pass
        self.connections.clear()

# Create a global connection pool
connection_pool = ConnectionPool(DATABASE_PATH, MAX_CONNECTIONS)

@contextmanager
def db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections."""
    connection = connection_pool.get_connection()
    try:
        yield connection
    finally:
        connection_pool.release_connection(connection)

# FIX #3: Fixed resource leaks in execute_query
def execute_query(query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
    """Execute a query and return the results as a list of dictionaries."""
    # Use context manager to ensure connection is properly released
    with db_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except sqlite3.Error as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            cursor.close()

# FIX #4: Added proper transaction management
def execute_write(query: str, params: Tuple = ()) -> int:
    """Execute a write operation (INSERT, UPDATE, DELETE) and return affected rows."""
    with db_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
            affected_rows = cursor.rowcount
            return affected_rows
        except sqlite3.Error as e:
            # Roll back the transaction on error
            connection.rollback()
            logger.error(f"Error executing write operation: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            cursor.close()

# FIX #5: Added batch size limit to executemany
def execute_many(query: str, params_list: List[Tuple]) -> int:
    """Execute a query with multiple parameter sets, with batch size limits."""
    if not params_list:
        return 0
    
    total_affected = 0
    
    with db_connection() as connection:
        cursor = connection.cursor()
        try:
            # Process in batches to avoid memory issues
            for i in range(0, len(params_list), MAX_BATCH_SIZE):
                batch = params_list[i:i + MAX_BATCH_SIZE]
                cursor.executemany(query, batch)
                total_affected += cursor.rowcount
            
            connection.commit()
            return total_affected
        except sqlite3.Error as e:
            # Roll back the transaction on error
            connection.rollback()
            logger.error(f"Error executing batch operation: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Batch size: {len(params_list)}")
            raise
        finally:
            cursor.close()

# FIX #6: Fixed SQL injection vulnerability
def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user by ID."""
    # Use parameterized query instead of string formatting
    query = "SELECT * FROM users WHERE user_id = ?"
    results = execute_query(query, (user_id,))
    return results[0] if results else None

def get_project_tasks(project_id: int) -> List[Dict[str, Any]]:
    """Get all tasks for a project."""
    query = """
        SELECT t.*, u.username as assigned_username
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.user_id
        WHERE t.project_id = ?
        ORDER BY t.due_date
    """
    return execute_query(query, (project_id,))

# FIX #7: Fixed LIKE with parameters
def search_tasks(search_term: str) -> List[Dict[str, Any]]:
    """Search for tasks matching the search term."""
    # Use parameterized query with proper LIKE parameters
    search_pattern = f"%{search_term}%"
    query = """
        SELECT t.*, p.title as project_title, u.username as assigned_username
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        LEFT JOIN users u ON t.assigned_to = u.user_id
        WHERE t.title LIKE ? OR t.description LIKE ?
        ORDER BY t.due_date
    """
    return execute_query(query, (search_pattern, search_pattern))

# FIX #8: Solved N+1 query problem
def get_task_with_relations(task_id: int) -> Dict[str, Any]:
    """Get a task with all its related data (comments, attachments, etc.)."""
    # Get the task with its direct relations in a single query
    task_query = """
        SELECT t.*, p.title as project_title, 
               u1.username as created_username,
               u2.username as assigned_username
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        JOIN users u1 ON t.created_by = u1.user_id
        LEFT JOIN users u2 ON t.assigned_to = u2.user_id
        WHERE t.task_id = ?
    """
    task_results = execute_query(task_query, (task_id,))
    if not task_results:
        return {}
    
    task = task_results[0]
    
    # Get all related data in a single query each instead of in a loop
    
    # Get comments
    comments_query = """
        SELECT c.*, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.user_id
        WHERE c.task_id = ?
        ORDER BY c.created_at DESC
    """
    task['comments'] = execute_query(comments_query, (task_id,))
    
    # Get attachments
    attachments_query = """
        SELECT a.*, u.username
        FROM attachments a
        JOIN users u ON a.uploaded_by = u.user_id
        WHERE a.task_id = ?
        ORDER BY a.uploaded_at DESC
    """
    task['attachments'] = execute_query(attachments_query, (task_id,))
    
    # Get tags
    tags_query = """
        SELECT t.*
        FROM tags t
        JOIN task_tags tt ON t.tag_id = tt.tag_id
        WHERE tt.task_id = ?
    """
    task['tags'] = execute_query(tags_query, (task_id,))
    
    return task

# FIX #9: Added parameter validation for create_task
def create_task(data: Dict[str, Any]) -> int:
    """Create a new task with proper validation."""
    # Validate required fields
    required_fields = ['title', 'project_id', 'created_by']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Required field '{field}' is missing")
    
    # Prepare fields with proper NULL handling
    title = data['title']
    description = data.get('description', '')
    project_id = data['project_id']
    assigned_to = data.get('assigned_to')  # Can be None
    created_by = data['created_by']
    status = data.get('status', 'pending')
    priority = data.get('priority', 1)
    due_date = data.get('due_date')  # Can be None
    
    # Use context manager to handle the transaction
    with db_connection() as connection:
        cursor = connection.cursor()
        try:
            # Insert the task
            query = """
                INSERT INTO tasks 
                (title, description, project_id, assigned_to, created_by, status, priority, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (title, description, project_id, assigned_to, created_by, status, priority, due_date)
            cursor.execute(query, params)
            task_id = cursor.lastrowid
            
            # Record task creation activity
            activity_query = """
                INSERT INTO task_activities 
                (task_id, user_id, action, details)
                VALUES (?, ?, ?, ?)
            """
            activity_params = (task_id, created_by, 'created', 'Task created')
            cursor.execute(activity_query, activity_params)
            
            # Commit the transaction
            connection.commit()
            return task_id
        except sqlite3.Error as e:
            # Roll back the transaction on error
            connection.rollback()
            logger.error(f"Error creating task: {e}")
            raise
        finally:
            cursor.close()

# FIX #10: Added proper transaction handling for assign_tags_to_task
def assign_tags_to_task(task_id: int, tag_ids: List[int]) -> bool:
    """Assign multiple tags to a task within a single transaction."""
    if not tag_ids:
        return True  # Nothing to do
    
    # Use a single transaction for all inserts
    with db_connection() as connection:
        cursor = connection.cursor()
        try:
            # First, delete any existing tag assignments
            cursor.execute("DELETE FROM task_tags WHERE task_id = ?", (task_id,))
            
            # Create parameter tuples for batch insert
            params = [(task_id, tag_id) for tag_id in tag_ids]
            
            # Insert all tag assignments at once
            query = "INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)"
            cursor.executemany(query, params)
            
            # Commit the transaction
            connection.commit()
            return True
        except sqlite3.Error as e:
            # Roll back the transaction on error
            connection.rollback()
            logger.error(f"Error assigning tags to task {task_id}: {e}")
            return False
        finally:
            cursor.close()

# FIX #11: Used SQL aggregation for project statistics
def get_project_statistics(project_id: int) -> Dict[str, Any]:
    """Get statistics about a project's tasks using SQL aggregation."""
    # Use SQL to calculate statistics directly in the database
    query = """
        SELECT 
            COUNT(*) as total_tasks,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_tasks,
            SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_tasks,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
            SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_tasks,
            SUM(CASE WHEN priority >= 4 THEN 1 ELSE 0 END) as high_priority_tasks,
            SUM(CASE WHEN due_date < date('now') AND status NOT IN ('completed', 'cancelled') THEN 1 ELSE 0 END) as overdue_tasks
        FROM tasks
        WHERE project_id = ?
    """
    
    results = execute_query(query, (project_id,))
    return results[0] if results else {
        'total_tasks': 0,
        'pending_tasks': 0,
        'in_progress_tasks': 0,
        'completed_tasks': 0,
        'cancelled_tasks': 0,
        'high_priority_tasks': 0,
        'overdue_tasks': 0
    }

# FIX #12: Added safeguards for dangerous operations
def perform_database_cleanup(confirm: bool = False) -> Dict[str, int]:
    """Perform database cleanup operations with safeguards and tracking."""
    if not confirm:
        # Require explicit confirmation for potentially destructive operations
        logger.warning("Database cleanup was attempted without confirmation")
        return {
            'status': 'cancelled',
            'reason': 'Confirmation required for cleanup operations'
        }
    
    # Use a single transaction for all operations
    with db_connection() as connection:
        cursor = connection.cursor()
        try:
            # Get counts before deletion for reporting
            cursor.execute("SELECT COUNT(*) FROM task_activities WHERE created_at < date('now', '-90 days')")
            old_activities_count = cursor.fetchone()[0]
            
            # Delete old activities (older than 90 days)
            cursor.execute(
                "DELETE FROM task_activities WHERE created_at < date('now', '-90 days')"
            )
            
            # Archive completed tasks older than 30 days
            cursor.execute(
                "SELECT COUNT(*) FROM tasks WHERE status = 'completed' AND updated_at < date('now', '-30 days')"
            )
            archived_tasks_count = cursor.fetchone()[0]
            
            cursor.execute(
                "UPDATE tasks SET status = 'archived' WHERE status = 'completed' AND updated_at < date('now', '-30 days')"
            )
            
            # Instead of deleting attachments, just get a count of what would be deleted
            # This is a safer approach - actual deletion should be a separate, deliberate operation
            cursor.execute(
                "SELECT COUNT(*) FROM attachments WHERE task_id IN (SELECT task_id FROM tasks WHERE status = 'archived')"
            )
            attachments_count = cursor.fetchone()[0]
            
            # Commit the transaction
            connection.commit()
            
            return {
                'status': 'success',
                'activities_deleted': old_activities_count,
                'tasks_archived': archived_tasks_count,
                'attachments_to_review': attachments_count  # We don't delete them automatically
            }
        except sqlite3.Error as e:
            # Roll back the transaction on error
            connection.rollback()
            logger.error(f"Error during database cleanup: {e}")
            return {
                'status': 'error',
                'reason': str(e)
            }
        finally:
            cursor.close()

# FIX #13: Optimized duplicate task detection
def find_duplicate_tasks() -> List[Dict[str, Any]]:
    """Find potential duplicate tasks based on title similarity using SQL."""
    # Use a SQL query to find potential duplicates
    # This avoids loading all tasks into memory and doing O(n²) comparisons
    query = """
        SELECT t1.task_id as task1_id, t1.title as task1_title,
               t2.task_id as task2_id, t2.title as task2_title
        FROM tasks t1
        JOIN tasks t2 ON t1.task_id < t2.task_id  -- Ensure we only get each pair once
        WHERE lower(t1.title) = lower(t2.title)   -- Case-insensitive comparison
        ORDER BY t1.task_id
        LIMIT 100  -- Limit results to prevent excessive data
    """
    
    return execute_query(query)

# Performance measurement decorator
def measure_performance(f):
    """Decorator to measure and log function execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        logger.info(f"Function {f.__name__} took {end_time - start_time:.4f} seconds to execute")
        return result
    return wrapper

# Demo functions to run the database operations

@measure_performance
def demo_basic_operations():
    """Demonstrate basic database operations."""
    # Users
    user = get_user(1)
    print(f"User: {user['username'] if user else 'Not found'}")
    
    # Projects with their tasks
    tasks = get_project_tasks(1)
    print(f"Project 1 has {len(tasks)} tasks")
    
    # Search
    search_results = search_tasks("database")
    print(f"Search found {len(search_results)} tasks")
    
    # Task with relations
    task = get_task_with_relations(1)
    if task:
        print(f"Task: {task['title']}")
        print(f"Comments: {len(task.get('comments', []))}")
        print(f"Attachments: {len(task.get('attachments', []))}")
        print(f"Tags: {len(task.get('tags', []))}")
    
    # Project statistics
    stats = get_project_statistics(1)
    print(f"Project statistics: {stats}")

@measure_performance
def demo_write_operations():
    """Demonstrate write operations (only run this on a test database)."""
    # Create a task
    new_task_data = {
        'title': 'Test Task',
        'description': 'This is a test task created for the exercise',
        'project_id': 1,
        'assigned_to': 2,
        'created_by': 1,
        'status': 'pending',
        'priority': 3,
        'due_date': time.strftime('%Y-%m-%d')
    }
    
    task_id = create_task(new_task_data)
    print(f"Created task with ID: {task_id}")
    
    # Assign tags
    assign_tags_to_task(task_id, [1, 2, 3])
    print(f"Assigned tags to task {task_id}")

def init_db():
    """Initialize the database with schema."""
    if os.path.exists(DATABASE_PATH):
        print(f"Database already exists at {DATABASE_PATH}")
        return
    
    with open('schema.sql', 'r') as f:
        schema_sql = f.read()
    
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        conn.executescript(schema_sql)
        conn.commit()
        print(f"Database initialized at {DATABASE_PATH}")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Initialize the database if needed (uncomment to initialize)
    # init_db()
    
    # Run the demos
    print("\n=== Basic Operations ===")
    demo_basic_operations()
    
    # Uncomment to test write operations
    # print("\n=== Write Operations ===")
    # demo_write_operations()
    
    # Cleanup connections
    print(f"\nClosing remaining connections in pool")
    connection_pool.close_all()

"""
Solution Explanations:

1. Improper Connection Pooling (Bug #1)
   - Problem: The connection pool implementation didn't properly manage pool size or validate connections.
   - Fix: Created a ConnectionPool class with proper initialization, validation, and connection management.
   - Why it matters: Proper connection pooling is essential for database performance and resource management.

2. No Connection Validation (Bug #2)
   - Problem: Connections weren't validated before reuse, potentially leading to errors when using stale connections.
   - Fix: Added validation checks for connections before returning them to the pool or reusing them.
   - Why it matters: Invalid connections can cause application errors and resource leaks.

3. Resource Leak in execute_query (Bug #3)
   - Problem: Connections weren't properly closed if exceptions occurred.
   - Fix: Used a context manager to ensure connections are properly released even during exceptions.
   - Why it matters: Resource leaks can deplete database connection limits and impact performance.

4. Missing Transaction Management (Bug #4)
   - Problem: Transactions weren't properly handled with commits and rollbacks.
   - Fix: Added explicit transaction handling with proper commits and rollbacks.
   - Why it matters: Proper transaction management ensures data consistency and integrity.

5. No Batch Size Limit (Bug #5)
   - Problem: The executemany function had no limit on batch size, potentially causing memory issues with large inputs.
   - Fix: Added batch processing to limit memory usage when dealing with large datasets.
   - Why it matters: Without limits, large operations can exhaust memory and cause application crashes.

6. SQL Injection Vulnerability (Bug #6)
   - Problem: String formatting was used to build queries, creating a SQL injection vulnerability.
   - Fix: Used parameterized queries with proper parameter binding.
   - Why it matters: SQL injection is a critical security vulnerability that can lead to data breaches.

7. Improper LIKE Parameter Handling (Bug #7)
   - Problem: Using string concatenation for LIKE queries, creating a SQL injection vulnerability.
   - Fix: Used parameterized queries with properly formatted LIKE patterns.
   - Why it matters: Improper LIKE handling is a common source of SQL injection vulnerabilities.

8. N+1 Query Problem (Bug #8)
   - Problem: Fetching related data with separate queries for each item, causing performance issues.
   - Fix: Used more efficient querying with JOINs and reduced the number of database calls.
   - Why it matters: N+1 queries dramatically reduce application performance as data volume grows.

9. Incorrect Parameter Handling (Bug #9)
   - Problem: No validation for required fields and improper NULL handling.
   - Fix: Added validation for required fields and proper handling of NULL values.
   - Why it matters: Missing required fields can cause runtime errors or data integrity issues.

10. Transaction Not Handling Rollback Correctly (Bug #10)
    - Problem: If an error occurred during tag assignment, previous successful inserts weren't rolled back.
    - Fix: Wrapped the entire operation in a single transaction with proper error handling.
    - Why it matters: Partial updates can leave the database in an inconsistent state.

11. Inefficient Query (Bug #11)
    - Problem: Calculating statistics in Python instead of using SQL aggregation.
    - Fix: Used SQL's aggregation functions (COUNT, SUM) to perform calculations in the database.
    - Why it matters: Pushing calculations to the database is more efficient and reduces data transfer.

12. Dangerous Operations Without Safeguards (Bug #12)
    - Problem: Performing potentially destructive operations without confirmation or proper tracking.
    - Fix: Added a confirmation parameter and tracking of affected records.
    - Why it matters: Accidental data deletion can cause significant problems in a production environment.

13. Memory-Intensive Operation (Bug #13)
    - Problem: Loading all tasks into memory and performing O(n²) comparisons.
    - Fix: Used a SQL-based approach to find duplicates directly in the database.
    - Why it matters: Memory-intensive operations can cause application crashes with large datasets.

Additional Improvements:
1. Added a performance measurement decorator to track function execution time
2. Improved error logging throughout the code
3. Enhanced transaction management with proper commits and rollbacks
4. Added better error messages and diagnostic information
5. Implemented proper resource cleanup
"""
