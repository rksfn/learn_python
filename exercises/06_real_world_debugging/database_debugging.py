"""
Exercise 2: Database Interaction Debugging

In this exercise, you'll debug database interaction issues in a Python application.
You'll identify and fix problems related to connection management, query performance,
transaction handling, and data integrity.

The application performs various operations on the Task Management database you've
already seen in Exercise 1, but focuses exclusively on the data layer.
"""

import sqlite3
import time
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple, Generator

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

# Connection pool (simple implementation)
connection_pool = []

def get_connection() -> sqlite3.Connection:
    """Get a database connection from the pool or create a new one."""
    # BUG #1: Improper connection pooling
    # This implementation doesn't properly manage the pool size
    # or handle connection problems
    
    if connection_pool:
        return connection_pool.pop()
    else:
        connection = sqlite3.connect(
            DATABASE_PATH,
            timeout=DEFAULT_TIMEOUT,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        connection.row_factory = sqlite3.Row
        return connection

def release_connection(connection: sqlite3.Connection) -> None:
    """Return a connection to the pool."""
    # BUG #2: No connection validation
    # This doesn't check if the connection is still valid
    # before returning it to the pool
    
    connection_pool.append(connection)

@contextmanager
def db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections."""
    connection = get_connection()
    try:
        yield connection
    finally:
        release_connection(connection)

def execute_query(query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
    """Execute a query and return the results as a list of dictionaries."""
    # BUG #3: Doesn't close the connection if an exception occurs
    # This can lead to connection leaks
    
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    release_connection(connection)
    return results

def execute_write(query: str, params: Tuple = ()) -> int:
    """Execute a write operation (INSERT, UPDATE, DELETE) and return affected rows."""
    # BUG #4: No error handling or transaction management
    # If an error occurs after the execute but before the commit,
    # the transaction is left open
    
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    affected_rows = cursor.rowcount
    cursor.close()
    release_connection(connection)
    return affected_rows

def execute_many(query: str, params_list: List[Tuple]) -> int:
    """Execute a query with multiple parameter sets."""
    # BUG #5: No batch size limit
    # If params_list is very large, this could cause memory issues
    
    connection = get_connection()
    cursor = connection.cursor()
    cursor.executemany(query, params_list)
    connection.commit()
    affected_rows = cursor.rowcount
    cursor.close()
    release_connection(connection)
    return affected_rows

def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user by ID."""
    # BUG #6: Uses string formatting for SQL, potential SQL injection
    # Should use parameterized queries
    
    query = f"SELECT * FROM users WHERE user_id = {user_id}"
    results = execute_query(query)
    return results[0] if results else None

def get_project_tasks(project_id: int) -> List[Dict[str, Any]]:
    """Get all tasks for a project."""
    # This function is correct - using parameterized queries properly
    
    query = """
        SELECT t.*, u.username as assigned_username
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.user_id
        WHERE t.project_id = ?
        ORDER BY t.due_date
    """
    return execute_query(query, (project_id,))

def search_tasks(search_term: str) -> List[Dict[str, Any]]:
    """Search for tasks matching the search term."""
    # BUG #7: Inefficient query - doesn't use LIKE with parameters correctly
    # This implements the search term concatenation incorrectly
    
    search_pattern = "%" + search_term + "%"
    query = f"""
        SELECT t.*, p.title as project_title, u.username as assigned_username
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        LEFT JOIN users u ON t.assigned_to = u.user_id
        WHERE t.title LIKE '{search_pattern}' OR t.description LIKE '{search_pattern}'
        ORDER BY t.due_date
    """
    return execute_query(query)

def get_task_with_relations(task_id: int) -> Dict[str, Any]:
    """Get a task with all its related data (comments, attachments, etc.)."""
    # BUG #8: N+1 query problem
    # This function makes multiple database calls for related data
    # instead of using JOINs
    
    # Get the task
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
    
    # Get comments - separate query (N+1 problem)
    comments_query = """
        SELECT c.*, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.user_id
        WHERE c.task_id = ?
        ORDER BY c.created_at DESC
    """
    task['comments'] = execute_query(comments_query, (task_id,))
    
    # Get attachments - separate query (N+1 problem)
    attachments_query = """
        SELECT a.*, u.username
        FROM attachments a
        JOIN users u ON a.uploaded_by = u.user_id
        WHERE a.task_id = ?
        ORDER BY a.uploaded_at DESC
    """
    task['attachments'] = execute_query(attachments_query, (task_id,))
    
    # Get tags - separate query (N+1 problem)
    tags_query = """
        SELECT t.*
        FROM tags t
        JOIN task_tags tt ON t.tag_id = tt.tag_id
        WHERE tt.task_id = ?
    """
    task['tags'] = execute_query(tags_query, (task_id,))
    
    return task

def create_task(data: Dict[str, Any]) -> int:
    """Create a new task."""
    # BUG #9: Incorrect parameter handling
    # This doesn't check if all required fields are present
    # and doesn't handle NULL values correctly
    
    query = """
        INSERT INTO tasks 
        (title, description, project_id, assigned_to, created_by, status, priority, due_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        data['title'],
        data['description'],
        data['project_id'],
        data['assigned_to'],
        data['created_by'],
        data['status'],
        data['priority'],
        data['due_date']
    )
    
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    task_id = cursor.lastrowid
    
    # Record task creation activity
    activity_query = """
        INSERT INTO task_activities 
        (task_id, user_id, action, details)
        VALUES (?, ?, ?, ?)
    """
    activity_params = (task_id, data['created_by'], 'created', 'Task created')
    cursor.execute(activity_query, activity_params)
    
    connection.commit()
    cursor.close()
    release_connection(connection)
    
    return task_id

def assign_tags_to_task(task_id: int, tag_ids: List[int]) -> bool:
    """Assign multiple tags to a task."""
    # BUG #10: Transaction not handling rollback correctly
    # If an error occurs during one of the inserts,
    # previous successful inserts are not rolled back
    
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        for tag_id in tag_ids:
            query = "INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)"
            cursor.execute(query, (task_id, tag_id))
        
        connection.commit()
        cursor.close()
        release_connection(connection)
        return True
    except sqlite3.Error as e:
        logger.error(f"Error assigning tags: {e}")
        cursor.close()
        release_connection(connection)
        return False

def get_project_statistics(project_id: int) -> Dict[str, Any]:
    """Get statistics about a project's tasks."""
    # BUG #11: Inefficient query - calculates statistics in Python
    # instead of using SQL aggregation functions
    
    # Get all tasks for the project
    tasks = get_project_tasks(project_id)
    
    # Calculate statistics
    stats = {
        'total_tasks': len(tasks),
        'pending_tasks': 0,
        'in_progress_tasks': 0,
        'completed_tasks': 0,
        'cancelled_tasks': 0,
        'high_priority_tasks': 0,
        'overdue_tasks': 0
    }
    
    # Count tasks in each category
    for task in tasks:
        if task['status'] == 'pending':
            stats['pending_tasks'] += 1
        elif task['status'] == 'in_progress':
            stats['in_progress_tasks'] += 1
        elif task['status'] == 'completed':
            stats['completed_tasks'] += 1
        elif task['status'] == 'cancelled':
            stats['cancelled_tasks'] += 1
        
        if task['priority'] >= 4:
            stats['high_priority_tasks'] += 1
        
        # Check if task is overdue
        if task['due_date'] and task['due_date'] < time.strftime('%Y-%m-%d') and task['status'] not in ['completed', 'cancelled']:
            stats['overdue_tasks'] += 1
    
    return stats

def perform_database_cleanup() -> None:
    """Perform database cleanup operations."""
    # BUG #12: Dangerous operations without proper safeguards
    # This could potentially delete important data without confirmation
    
    # Delete old activities (older than 90 days)
    cleanup_activities_query = """
        DELETE FROM task_activities
        WHERE created_at < date('now', '-90 days')
    """
    
    # Archive completed tasks older than 30 days
    archive_tasks_query = """
        UPDATE tasks
        SET status = 'archived'
        WHERE status = 'completed' AND updated_at < date('now', '-30 days')
    """
    
    # Dangerous: This would delete all attachments for archived tasks
    delete_attachments_query = """
        DELETE FROM attachments
        WHERE task_id IN (SELECT task_id FROM tasks WHERE status = 'archived')
    """
    
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(cleanup_activities_query)
    cursor.execute(archive_tasks_query)
    cursor.execute(delete_attachments_query)
    
    connection.commit()
    cursor.close()
    release_connection(connection)

def find_duplicate_tasks() -> List[Dict[str, Any]]:
    """Find potential duplicate tasks based on title similarity."""
    # BUG #13: Memory-intensive operation
    # This loads all tasks into memory and does an O(n²) comparison
    
    # Get all tasks
    all_tasks_query = "SELECT * FROM tasks"
    all_tasks = execute_query(all_tasks_query)
    
    duplicates = []
    
    # Compare each task with every other task (O(n²) complexity)
    for i, task1 in enumerate(all_tasks):
        for task2 in all_tasks[i+1:]:
            # Check if titles are similar (simple check for demonstration)
            if task1['title'].lower() == task2['title'].lower():
                duplicates.append({
                    'task1_id': task1['task_id'],
                    'task1_title': task1['title'],
                    'task2_id': task2['task_id'],
                    'task2_title': task2['title']
                })
    
    return duplicates

# Demo functions to run the database operations

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
    print(f"\nRemaining connections in pool: {len(connection_pool)}")
    for conn in connection_pool:
        conn.close()

"""
Exercise Instructions:

This exercise focuses on database interaction bugs that are common in real-world
applications. Your task is to identify and fix 13 bugs related to:

1. Connection Pooling and Resource Management
2. SQL Injection Vulnerabilities
3. Query Performance Problems (N+1 queries)
4. Transaction Handling
5. Parameter Validation and Type Safety
6. Memory Efficiency

Before you start:
1. Make sure the schema.sql file has been executed to create the database
2. Review the code to understand the functionality

Steps to complete the exercise:
1. Run the code and observe any errors or performance issues
2. Use debugging tools and logging to identify the bugs
3. Fix each bug and document your solution
4. Improve the code's overall performance and security

Tips:
1. Use proper connection pooling practices
2. Always use parameterized queries
3. Minimize the number of database calls
4. Ensure proper transaction handling
5. Validate input data before queries
6. Use SQL's aggregate functions for statistics

Bonus Challenge:
1. Implement proper connection pooling with connection validation
2. Rewrite the N+1 query functions to use JOINs
3. Add comprehensive error handling
4. Add performance measurement to track query execution time
"""
