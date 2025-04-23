"""
Exercise 1: Debugging a Web Application

In this exercise, you'll debug a Flask-based task management application that
has several issues across different components: database interactions, API endpoints,
template rendering, and asynchronous operations.

The application allows users to manage projects and tasks, with features like:
- User authentication
- Project creation and management
- Task tracking with status updates
- Comments and attachments
- API endpoints for mobile integration

Your goal is to identify and fix various bugs using the debugging techniques
learned in this module. The bugs range from simple syntax errors to complex
issues involving database queries, race conditions, and resource management.
"""

import os
import sqlite3
import json
import time
import hashlib
import logging
from functools import wraps
from datetime import datetime, timedelta

from flask import (
    Flask, request, render_template, g, redirect,
    url_for, session, flash, jsonify, abort
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='taskmanager.log'
)
logger = logging.getLogger('taskmanager')

# Initialize Flask application
app = Flask(__name__, template_folder='templates')
app.secret_key = 'debug_secret_key_for_development_only'
app.config['DATABASE'] = 'taskmanager.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Database connection management
def get_db():
    """Get a database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection when application context ends."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with schema."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    """Query the database."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def modify_db(query, args=()):
    """Modify the database with insert, update, or delete."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    cur.close()
    return cur.lastrowid

# Authentication helpers
def hash_password(password):
    """Hash a password for storing."""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000
    )
    return f"pbkdf2:sha256:100000${salt.hex()}${key.hex()}"

def check_password(stored_password, provided_password):
    """Verify a stored password against one provided by user."""
    if stored_password.count('$') != 2:
        return False
    algorithm, salt, key = stored_password.split('$')
    salt = bytes.fromhex(salt)
    stored_key = bytes.fromhex(key)
    new_key = hashlib.pbkdf2_hmac(
        'sha256', provided_password.encode('utf-8'), salt, 100000
    )
    return stored_key == new_key

def login_required(f):
    """Decorator to require login for a view."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get the current logged-in user information."""
    if 'user_id' not in session:
        return None
    
    user = query_db(
        'SELECT * FROM users WHERE user_id = ?',
        (session['user_id'],),
        one=True
    )
    return user

# Route definitions
@app.route('/')
def index():
    """Home page - show recent projects and tasks."""
    user = get_current_user()
    if not user:
        return render_template('index.html')
    
    # Get projects the user is a member of
    user_projects = query_db('''
        SELECT p.* FROM projects p
        JOIN project_members pm ON p.project_id = pm.project_id
        WHERE pm.user_id = ?
        ORDER BY p.updated_at DESC
        LIMIT 5
    ''', (user['user_id'],))
    
    # Get recent tasks assigned to the user
    user_tasks = query_db('''
        SELECT t.*, p.title as project_title FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE t.assigned_to = ? AND t.status != 'completed'
        ORDER BY t.due_date ASC
        LIMIT 10
    ''', (user['user_id'],))
    
    return render_template(
        'dashboard.html', 
        user=user, 
        projects=user_projects, 
        tasks=user_tasks
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = query_db(
            'SELECT * FROM users WHERE username = ?',
            (username,),
            one=True
        )
        
        if user and check_password(user['password_hash'], password):
            # Set user as logged in
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            
            # Update last login time
            modify_db(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?',
                (user['user_id'],)
            )
            
            # BUG #1: Session fixation vulnerability - missing session regeneration
            # The next line should be uncommented:
            # session.regenerate()
            
            flash('You have been logged in', 'success')
            
            # Redirect to next parameter or default to home
            next_page = request.args.get('next', url_for('index'))
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout."""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/projects')
@login_required
def list_projects():
    """List all projects the user is a member of."""
    user_id = session['user_id']
    
    # BUG #2: SQL Injection vulnerability
    # The next line has a SQL injection vulnerability because it uses string formatting
    # This should use parameterized queries instead
    sort_by = request.args.get('sort_by', 'updated_at')
    order = request.args.get('order', 'DESC')
    
    # This is vulnerable to SQL injection
    query = f'''
        SELECT p.*, u.username as owner_name, 
               (SELECT COUNT(*) FROM tasks WHERE project_id = p.project_id) as task_count,
               pm.role as user_role
        FROM projects p
        JOIN users u ON p.owner_id = u.user_id
        JOIN project_members pm ON p.project_id = pm.project_id
        WHERE pm.user_id = ?
        ORDER BY p.{sort_by} {order}
    '''
    
    try:
        projects = query_db(query, (user_id,))
        return render_template('projects/list.html', projects=projects)
    except sqlite3.Error as e:
        # Log the error
        logger.error(f"Database error in list_projects: {e}")
        flash('An error occurred while retrieving projects', 'error')
        return render_template('projects/list.html', projects=[])

@app.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    """Create a new project."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        owner_id = session['user_id']
        
        # BUG #3: Missing input validation
        # This should validate that title is not empty
        
        try:
            # Insert project
            project_id = modify_db(
                'INSERT INTO projects (title, description, owner_id) VALUES (?, ?, ?)',
                (title, description, owner_id)
            )
            
            # Add owner as a project member with 'owner' role
            modify_db(
                'INSERT INTO project_members (project_id, user_id, role) VALUES (?, ?, ?)',
                (project_id, owner_id, 'owner')
            )
            
            flash('Project created successfully', 'success')
            return redirect(url_for('view_project', project_id=project_id))
        except sqlite3.Error as e:
            logger.error(f"Database error in new_project: {e}")
            flash('An error occurred while creating the project', 'error')
    
    return render_template('projects/new.html')

@app.route('/projects/<int:project_id>')
@login_required
def view_project(project_id):
    """View a single project and its tasks."""
    user_id = session['user_id']
    
    # Check if user is a member of the project
    member = query_db(
        'SELECT * FROM project_members WHERE project_id = ? AND user_id = ?',
        (project_id, user_id),
        one=True
    )
    
    if not member:
        flash('You do not have access to this project', 'error')
        return redirect(url_for('list_projects'))
    
    # Get project details
    project = query_db(
        'SELECT * FROM projects WHERE project_id = ?',
        (project_id,),
        one=True
    )
    
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('list_projects'))
    
    # Get project tasks
    tasks = query_db(
        '''
        SELECT t.*, u.username as assigned_username 
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.user_id
        WHERE t.project_id = ?
        ORDER BY t.status, t.due_date
        ''',
        (project_id,)
    )
    
    # Get project members
    members = query_db(
        '''
        SELECT pm.*, u.username 
        FROM project_members pm
        JOIN users u ON pm.user_id = u.user_id
        WHERE pm.project_id = ?
        ''',
        (project_id,)
    )
    
    return render_template(
        'projects/view.html',
        project=project,
        tasks=tasks,
        members=members,
        member_role=member['role']
    )

@app.route('/projects/<int:project_id>/tasks/new', methods=['GET', 'POST'])
@login_required
def new_task(project_id):
    """Create a new task in a project."""
    user_id = session['user_id']
    
    # Check if user is a member of the project
    member = query_db(
        'SELECT * FROM project_members WHERE project_id = ? AND user_id = ?',
        (project_id, user_id),
        one=True
    )
    
    if not member or member['role'] not in ['owner', 'admin', 'member']:
        flash('You do not have permission to add tasks to this project', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        assigned_to = request.form.get('assigned_to')
        status = request.form.get('status', 'pending')
        priority = request.form.get('priority', 1)
        due_date_str = request.form.get('due_date')
        
        # BUG #4: Improper date handling
        # This code doesn't properly validate and parse the due date
        if due_date_str:
            try:
                # Assuming due_date_str is in format 'YYYY-MM-DD'
                due_date = due_date_str
            except ValueError:
                flash('Invalid date format', 'error')
                return redirect(url_for('new_task', project_id=project_id))
        else:
            due_date = None
        
        # BUG #5: Type error
        # Numeric fields are not properly converted to integers
        if assigned_to == '':
            assigned_to = None
        
        try:
            task_id = modify_db(
                '''
                INSERT INTO tasks 
                (title, description, project_id, assigned_to, created_by, status, priority, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (title, description, project_id, assigned_to, user_id, status, priority, due_date)
            )
            
            # Record task creation activity
            modify_db(
                '''
                INSERT INTO task_activities 
                (task_id, user_id, action, details)
                VALUES (?, ?, ?, ?)
                ''',
                (task_id, user_id, 'created', 'Task created')
            )
            
            flash('Task created successfully', 'success')
            return redirect(url_for('view_task', task_id=task_id))
        except sqlite3.Error as e:
            logger.error(f"Database error in new_task: {e}")
            flash('An error occurred while creating the task', 'error')
    
    # Get project members for assignment dropdown
    members = query_db(
        '''
        SELECT pm.user_id, u.username 
        FROM project_members pm
        JOIN users u ON pm.user_id = u.user_id
        WHERE pm.project_id = ?
        ''',
        (project_id,)
    )
    
    # Get project details
    project = query_db(
        'SELECT * FROM projects WHERE project_id = ?',
        (project_id,),
        one=True
    )
    
    return render_template(
        'tasks/new.html',
        project=project,
        members=members
    )

@app.route('/tasks/<int:task_id>')
@login_required
def view_task(task_id):
    """View a single task and its details."""
    user_id = session['user_id']
    
    # Get task details with joins to related tables
    task = query_db(
        '''
        SELECT t.*, p.title as project_title, p.project_id,
               u1.username as assigned_username,
               u2.username as created_username
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        LEFT JOIN users u1 ON t.assigned_to = u1.user_id
        JOIN users u2 ON t.created_by = u2.user_id
        WHERE t.task_id = ?
        ''',
        (task_id,),
        one=True
    )
    
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    # Check if user has access to the task's project
    member = query_db(
        'SELECT * FROM project_members WHERE project_id = ? AND user_id = ?',
        (task['project_id'], user_id),
        one=True
    )
    
    if not member:
        flash('You do not have access to this task', 'error')
        return redirect(url_for('index'))
    
    # Get task comments
    comments = query_db(
        '''
        SELECT c.*, u.username 
        FROM comments c
        JOIN users u ON c.user_id = u.user_id
        WHERE c.task_id = ?
        ORDER BY c.created_at DESC
        ''',
        (task_id,)
    )
    
    # Get task attachments
    attachments = query_db(
        '''
        SELECT a.*, u.username 
        FROM attachments a
        JOIN users u ON a.uploaded_by = u.user_id
        WHERE a.task_id = ?
        ORDER BY a.uploaded_at DESC
        ''',
        (task_id,)
    )
    
    # Get task activities
    activities = query_db(
        '''
        SELECT a.*, u.username 
        FROM task_activities a
        JOIN users u ON a.user_id = u.user_id
        WHERE a.task_id = ?
        ORDER BY a.created_at DESC
        ''',
        (task_id,)
    )
    
    # BUG #6: N+1 query problem
    # We're fetching tags individually for each task, which is inefficient
    # This should use a single query with a join
    tags = []
    task_tags = query_db(
        'SELECT tag_id FROM task_tags WHERE task_id = ?',
        (task_id,)
    )
    
    for tt in task_tags:
        tag = query_db(
            'SELECT * FROM tags WHERE tag_id = ?',
            (tt['tag_id'],),
            one=True
        )
        tags.append(tag)
    
    return render_template(
        'tasks/view.html',
        task=task,
        comments=comments,
        attachments=attachments,
        activities=activities,
        tags=tags,
        member_role=member['role']
    )

@app.route('/tasks/<int:task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    """Update a task's status, priority, or assignment."""
    user_id = session['user_id']
    
    # Get task details
    task = query_db(
        'SELECT * FROM tasks WHERE task_id = ?',
        (task_id,),
        one=True
    )
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Check if user has access to the task's project
    member = query_db(
        'SELECT * FROM project_members WHERE project_id = ? AND user_id = ?',
        (task['project_id'], user_id),
        one=True
    )
    
    if not member or member['role'] not in ['owner', 'admin', 'member']:
        return jsonify({'error': 'You do not have permission to update this task'}), 403
    
    # Get update data from request
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    
    if not field or value is None:
        return jsonify({'error': 'Missing field or value'}), 400
    
    # BUG #7: Missing field validation
    # This code doesn't validate that the field is one we allow updates for
    
    # Update the specified field
    try:
        modify_db(
            f'UPDATE tasks SET {field} = ? WHERE task_id = ?',
            (value, task_id)
        )
        
        # Record the activity
        modify_db(
            '''
            INSERT INTO task_activities 
            (task_id, user_id, action, details)
            VALUES (?, ?, ?, ?)
            ''',
            (task_id, user_id, 'updated', f'Changed {field} to {value}')
        )
        
        return jsonify({'success': True, 'message': f'Task {field} updated'})
    except sqlite3.Error as e:
        logger.error(f"Database error in update_task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/tasks/<int:task_id>/comments', methods=['POST'])
@login_required
def add_comment(task_id):
    """Add a comment to a task."""
    user_id = session['user_id']
    
    # Get task details
    task = query_db(
        'SELECT * FROM tasks WHERE task_id = ?',
        (task_id,),
        one=True
    )
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Check if user has access to the task's project
    member = query_db(
        'SELECT * FROM project_members WHERE project_id = ? AND user_id = ?',
        (task['project_id'], user_id),
        one=True
    )
    
    if not member:
        return jsonify({'error': 'You do not have access to this task'}), 403
    
    # Get comment content from request
    content = request.form.get('content')
    
    if not content or not content.strip():
        return jsonify({'error': 'Comment cannot be empty'}), 400
    
    # Add the comment
    try:
        comment_id = modify_db(
            'INSERT INTO comments (task_id, user_id, content) VALUES (?, ?, ?)',
            (task_id, user_id, content)
        )
        
        # Get the new comment with username
        comment = query_db(
            '''
            SELECT c.*, u.username 
            FROM comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.comment_id = ?
            ''',
            (comment_id,),
            one=True
        )
        
        # Return the new comment data
        return jsonify({
            'success': True,
            'comment': {
                'comment_id': comment['comment_id'],
                'content': comment['content'],
                'username': comment['username'],
                'created_at': comment['created_at']
            }
        })
    except sqlite3.Error as e:
        logger.error(f"Database error in add_comment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/tasks/<int:task_id>/attachments', methods=['POST'])
@login_required
def add_attachment(task_id):
    """Add an attachment to a task."""
    user_id = session['user_id']
    
    # Get task details
    task = query_db(
        'SELECT * FROM tasks WHERE task_id = ?',
        (task_id,),
        one=True
    )
    
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    # Check if user has access to the task's project
    member = query_db(
        'SELECT * FROM project_members WHERE project_id = ? AND user_id = ?',
        (task['project_id'], user_id),
        one=True
    )
    
    if not member or member['role'] not in ['owner', 'admin', 'member']:
        flash('You do not have permission to add attachments to this task', 'error')
        return redirect(url_for('view_task', task_id=task_id))
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    
    if file:
        # BUG #8: Insecure file handling
        # This code doesn't properly validate the file type and name
        filename = file.filename
        
        # Create upload directory if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        mime_type = file.content_type or 'application/octet-stream'
        
        # Add attachment record to database
        try:
            modify_db(
                '''
                INSERT INTO attachments 
                (task_id, filename, file_path, file_size, mime_type, uploaded_by)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (task_id, filename, file_path, file_size, mime_type, user_id)
            )
            
            flash('File uploaded successfully', 'success')
        except sqlite3.Error as e:
            logger.error(f"Database error in add_attachment: {e}")
            flash('Error saving attachment information', 'error')
    
    return redirect(url_for('view_task', task_id=task_id))

# API endpoints for mobile app

@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    """API endpoint to get tasks for a user."""
    # BUG #9: Missing authentication for API endpoint
    # This endpoint should require authentication
    
    # Get user_id from query parameter
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id parameter is required'}), 400
    
    # Get tasks assigned to the user
    try:
        tasks = query_db(
            '''
            SELECT t.*, p.title as project_title 
            FROM tasks t
            JOIN projects p ON t.project_id = p.project_id
            WHERE t.assigned_to = ?
            ORDER BY t.due_date ASC
            ''',
            (user_id,)
        )
        
        # Convert to list of dicts for JSON serialization
        task_list = []
        for task in tasks:
            task_dict = dict(task)
            # Convert datetime strings to ISO format
            if task_dict['due_date']:
                task_dict['due_date'] = task_dict['due_date']
            if task_dict['created_at']:
                task_dict['created_at'] = task_dict['created_at']
            if task_dict['updated_at']:
                task_dict['updated_at'] = task_dict['updated_at']
            task_list.append(task_dict)
        
        return jsonify({'tasks': task_list})
    except sqlite3.Error as e:
        logger.error(f"Database error in api_get_tasks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>/update_status', methods=['POST'])
def api_update_task_status(task_id):
    """API endpoint to update a task's status."""
    # Get auth token from header
    auth_token = request.headers.get('Authorization')
    
    if not auth_token:
        return jsonify({'error': 'Authorization header is required'}), 401
    
    # Extract user_id from token (simplified auth for example)
    try:
        # BUG #10: Insecure token handling
        # This uses a simplistic token parsing that's vulnerable
        user_id = int(auth_token.split(':')[1])
    except (ValueError, IndexError):
        return jsonify({'error': 'Invalid authorization token'}), 401
    
    # Get task details
    task = query_db(
        'SELECT * FROM tasks WHERE task_id = ?',
        (task_id,),
        one=True
    )
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Check if user has access to the task
    # Verify user is assigned to the task or is a project member
    is_assigned = task['assigned_to'] == user_id
    
    if not is_assigned:
        member = query_db(
            'SELECT * FROM project_members WHERE project_id = ? AND user_id = ?',
            (task['project_id'], user_id),
            one=True
        )
        if not member:
            return jsonify({'error': 'You do not have permission to update this task'}), 403
    
    # Get status from request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing request body'}), 400
    
    status = data.get('status')
    
    if not status:
        return jsonify({'error': 'Missing status field'}), 400
    
    # Validate status
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    if status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
    
    # Update the task status
    try:
        modify_db(
            'UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ?',
            (status, task_id)
        )
        
        # Record the activity
        modify_db(
            'INSERT INTO task_activities (task_id, user_id, action, details) VALUES (?, ?, ?, ?)',
            (task_id, user_id, 'updated', f'Changed status to {status}')
        )
        
        return jsonify({'success': True, 'message': f'Task status updated to {status}'})
    except sqlite3.Error as e:
        logger.error(f"Database error in api_update_task_status: {e}")
        return jsonify({'error': str(e)}), 500

# Asynchronous task simulator
def async_process_task(task_id, duration=5):
    """
    Simulate an asynchronous process for a task.
    This would typically be a background job handled by Celery or similar.
    """
    logger.info(f"Starting async processing for task {task_id}")
    
    # BUG #11: Resource leak in exception handling
    # This function doesn't properly handle exceptions or release resources
    try:
        db = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        
        # Get task details
        cur = db.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
        task = cur.fetchone()
        
        if not task:
            logger.error(f"Task {task_id} not found for async processing")
            return
        
        # Simulate processing time
        time.sleep(duration)
        
        # Update task to mark processing as complete
        db.execute(
            'UPDATE tasks SET status = ? WHERE task_id = ?', 
            ('processed', task_id)
        )
        db.commit()
        
        logger.info(f"Completed async processing for task {task_id}")
    except Exception as e:
        logger.error(f"Error in async_process_task: {e}")
        # The database connection is not closed in the exception path
    finally:
        # BUG: This finally block should close the db connection
        # db.close()
        pass

@app.route('/tasks/<int:task_id>/process', methods=['POST'])
@login_required
def trigger_task_processing(task_id):
    """Trigger asynchronous processing for a task."""
    user_id = session['user_id']
    
    # Get task details
    task = query_db(
        'SELECT * FROM tasks WHERE task_id = ?',
        (task_id,),
        one=True
    )
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Check if user has access to the task's project
    member = query_db(
        'SELECT * FROM project_members WHERE project_id = ? AND user_id = ?',
        (task['project_id'], user_id),
        one=True
    )
    
    if not member or member['role'] not in ['owner', 'admin']:
        return jsonify({'error': 'You do not have permission to process this task'}), 403
    
    # Simulate starting a background task
    # In a real app, this would use Celery, RQ, or a similar task queue
    # BUG #12: No thread safety or proper background task handling
    # This is not how you'd run background tasks in a production application
    import threading
    thread = threading.Thread(
        target=async_process_task,
        args=(task_id,)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Task processing started'
    })

@app.route('/search')
@login_required
def search():
    """Search for tasks and projects."""
    user_id = session['user_id']
    query = request.args.get('q', '')
    
    if not query or len(query) < 3:
        return jsonify({
            'error': 'Search query must be at least 3 characters'
        }), 400
    
    # Search for tasks
    search_term = f"%{query}%"
    
    # BUG #13: Inefficient search query
    # This performs separate queries instead of using JOINs
    try:
        # Get tasks matching the search term that the user has access to
        task_results = query_db(
            '''
            SELECT t.*, p.title as project_title
            FROM tasks t
            JOIN projects p ON t.project_id = p.project_id
            WHERE (t.title LIKE ? OR t.description LIKE ?)
            AND t.project_id IN (
                SELECT project_id FROM project_members WHERE user_id = ?
            )
            LIMIT 10
            ''',
            (search_term, search_term, user_id)
        )
        
        # Get projects matching the search term that the user has access to
        project_results = query_db(
            '''
            SELECT p.*
            FROM projects p
            JOIN project_members pm ON p.project_id = pm.project_id
            WHERE (p.title LIKE ? OR p.description LIKE ?)
            AND pm.user_id = ?
            LIMIT 5
            ''',
            (search_term, search_term, user_id)
        )
        
        # Format results for JSON response
        results = {
            'tasks': [dict(task) for task in task_results],
            'projects': [dict(project) for project in project_results]
        }
        
        return jsonify(results)
    except sqlite3.Error as e:
        logger.error(f"Database error in search: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Check if database exists, initialize if it doesn't
    if not os.path.exists(app.config['DATABASE']):
        init_db()
        print("Database initialized.")
    
    app.run(debug=True, port=5000)

"""
Exercise Instructions:

This exercise simulates a real-world application with multiple components and
interactions. Your task is to identify and fix at least 13 bugs that exist in
different parts of the application. The bugs include:

1. Security vulnerabilities
2. Database interaction problems
3. Resource management issues
4. Concurrency bugs
5. Data validation errors
6. Performance problems

The application is designed to work with the provided schema.sql file, which
creates a SQLite database for the task management system.

Getting Started:
1. Run the application to see it in action and observe the initial errors
2. Use debugging tools and techniques to identify the bugs
3. Fix each bug and document your fixes

Tips for Debugging:
1. Use logging to trace execution flow
2. Check the database queries for errors
3. Use a systematic approach to isolate issues
4. Pay attention to error messages and exceptions
5. Test each fix thoroughly

Bonus Challenges:
1. Add proper error handling throughout the application
2. Improve the performance of the database queries
3. Enhance the security of the application
4. Add unit tests to verify your fixes
"""
