"""
Exercise 2 Solution: Advanced pdb Techniques

This solution demonstrates how to use advanced pdb features to debug the TaskManager
application, including conditional breakpoints, post-mortem debugging, and more.
"""

import random
from datetime import datetime, timedelta

class Task:
    def __init__(self, id, name, priority, deadline=None, completed=False):
        self.id = id
        self.name = name
        self.priority = priority  # 1 (highest) to 5 (lowest)
        self.deadline = deadline
        self.completed = completed
        self.created_at = datetime.now()
    
    def __repr__(self):
        deadline_str = f", due: {self.deadline.strftime('%Y-%m-%d')}" if self.deadline else ""
        status = "✓" if self.completed else "⨯"
        return f"Task {self.id}: {self.name} [P{self.priority}{deadline_str}] {status}"


class TaskManager:
    def __init__(self):
        self.tasks = []
        self.last_id = 0
    
    def add_task(self, name, priority=3, deadline=None):
        """Add a new task to the manager."""
        self.last_id += 1
        task = Task(self.last_id, name, priority, deadline)
        self.tasks.append(task)
        return task
    
    def get_task(self, task_id):
        """Get a task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def complete_task(self, task_id):
        """Mark a task as completed."""
        task = self.get_task(task_id)
        if task:
            task.completed = True
            return True
        return False
    
    def delete_task(self, task_id):
        """Delete a task by ID."""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False
    
    def get_overdue_tasks(self):
        """Get all tasks that are past their deadline and not completed."""
        today = datetime.now().date()
        overdue = []
        
        for task in self.tasks:
            if not task.completed and task.deadline and task.deadline.date() < today:
                overdue.append(task)
        
        return overdue
    
    def get_upcoming_tasks(self, days=7):
        """Get tasks due in the next X days."""
        today = datetime.now().date()
        end_date = today + timedelta(days=days)
        upcoming = []
        
        for task in self.tasks:
            if not task.completed and task.deadline:
                if today <= task.deadline.date() <= end_date:
                    upcoming.append(task)
        
        return upcoming
    
    def get_high_priority_tasks(self, max_priority=2):
        """Get incomplete tasks with high priority (low numbers = high priority)."""
        return [task for task in self.tasks 
                if not task.completed and task.priority <= max_priority]
    
    def sort_tasks(self, key="priority"):
        """Sort tasks by the given key (priority, deadline, or creation date)."""
        if key == "priority":
            # Sort by priority (ascending), then by deadline (ascending, with None at the end)
            def priority_key(task):
                # Return a tuple for sorting (completed, priority, deadline)
                deadline_val = task.deadline or datetime.max
                return (task.completed, task.priority, deadline_val)
            
            self.tasks.sort(key=priority_key)
            
        elif key == "deadline":
            # Sort by deadline (ascending), with None at the end
            def deadline_key(task):
                # Return a tuple for sorting (completed, has_deadline, deadline)
                has_deadline = 0 if task.deadline else 1
                deadline_val = task.deadline or datetime.max
                return (task.completed, has_deadline, deadline_val)
            
            self.tasks.sort(key=deadline_key)
            
        elif key == "created":
            # Sort by creation date (ascending)
            self.tasks.sort(key=lambda task: (task.completed, task.created_at))
            
        return self.tasks


def create_sample_tasks():
    """Create sample tasks for testing."""
    manager = TaskManager()
    
    # Add some tasks with various priorities and deadlines
    manager.add_task("Buy groceries", priority=2, 
                    deadline=datetime.now() + timedelta(days=1))
    manager.add_task("Finish project report", priority=1, 
                    deadline=datetime.now() + timedelta(days=3))
    manager.add_task("Call mom", priority=3)
    manager.add_task("Pay electricity bill", priority=2, 
                    deadline=datetime.now() - timedelta(days=1))  # Overdue
    manager.add_task("Clean garage", priority=4, 
                    deadline=datetime.now() + timedelta(days=10))
    manager.add_task("Schedule dentist appointment", priority=3, 
                    deadline=datetime.now() + timedelta(days=5))
    
    # Mark some tasks as completed
    manager.complete_task(3)  # "Call mom" is completed
    
    return manager


def generate_task_report(manager, include_completed=False):
    """Generate a report of tasks."""
    report = []
    report.append("TASK REPORT")
    report.append("=" * 50)
    report.append(f"Total Tasks: {len(manager.tasks)}")
    
    # Count completed and incomplete tasks
    completed_tasks = [task for task in manager.tasks if task.completed]
    incomplete_tasks = [task for task in manager.tasks if not task.completed]
    report.append(f"Completed: {len(completed_tasks)}")
    report.append(f"Incomplete: {len(incomplete_tasks)}")
    
    # Check for overdue tasks
    overdue_tasks = manager.get_overdue_tasks()
    report.append(f"Overdue: {len(overdue_tasks)}")
    
    # Get upcoming tasks
    upcoming_tasks = manager.get_upcoming_tasks()
    report.append(f"Due in the next week: {len(upcoming_tasks)}")
    
    # Get high priority tasks
    high_priority = manager.get_high_priority_tasks()
    report.append(f"High Priority: {len(high_priority)}")
    
    report.append("\nTASK DETAILS")
    report.append("=" * 50)
    
    # Sort tasks by priority
    sorted_tasks = manager.sort_tasks("priority")
    
    # First list incomplete tasks
    report.append("\nINCOMPLETE TASKS:")
    for task in sorted_tasks:
        if not task.completed:
            deadline_str = f" (Due: {task.deadline.strftime('%Y-%m-%d')})" if task.deadline else ""
            overdue_marker = " - OVERDUE!" if task.deadline and task.deadline.date() < datetime.now().date() else ""
            report.append(f"[P{task.priority}] {task.name}{deadline_str}{overdue_marker}")
    
    # Then list completed tasks if requested
    if include_completed and completed_tasks:
        report.append("\nCOMPLETED TASKS:")
        for task in sorted_tasks:
            if task.completed:
                report.append(f"[P{task.priority}] {task.name}")
    
    return "\n".join(report)


def process_command(manager, command):
    """Process a user command for the task manager."""
    parts = command.split()
    
    if not parts:
        return "No command provided."
    
    action = parts[0].lower()
    
    try:
        if action == "add":
            # Format: add "Task name" [priority] [deadline]
            if len(parts) < 2:
                return "Error: Task name required."
            
            # BUG FIX 1: Improved task name parsing with quotes
            # Extract task name (may be in quotes)
            name = ""
            name_end_idx = 1
            
            # Check if the task name is in quotes
            if parts[1].startswith('"'):
                # Find the closing quote
                full_command = command[len(action):].strip()
                if '"' in full_command[1:]:
                    end_quote_pos = full_command[1:].find('"') + 1
                    name = full_command[1:end_quote_pos]
                    # Calculate where in parts[] the name ends
                    remaining = full_command[end_quote_pos + 1:].strip()
                    name_end_idx = len(parts) - (len(remaining.split()) if remaining else 0) - 1
                else:
                    # No closing quote found
                    name = full_command[1:]
                    name_end_idx = len(parts) - 1
            else:
                # No quotes, just use the next part as the name
                name = parts[1]
            
            # Parse priority and deadline if provided
            priority = 3  # Default priority
            deadline = None
            
            remaining_parts = parts[name_end_idx + 1:]
            
            if remaining_parts and len(remaining_parts) >= 1:
                try:
                    # BUG FIX 2: Better priority validation
                    priority = int(remaining_parts[0])
                    if priority < 1 or priority > 5:
                        return "Error: Priority must be 1-5."
                except ValueError:
                    return "Error: Invalid priority. Must be a number between 1 and 5."
            
            if remaining_parts and len(remaining_parts) >= 2:
                try:
                    deadline = datetime.strptime(remaining_parts[1], "%Y-%m-%d")
                except ValueError:
                    return "Error: Invalid deadline format. Use YYYY-MM-DD."
            
            task = manager.add_task(name, priority, deadline)
            return f"Added: {task}"
            
        elif action == "complete":
            # Format: complete [task_id]
            if len(parts) < 2:
                return "Error: Task ID required."
            
            try:
                task_id = int(parts[1])
            except ValueError:
                return "Error: Invalid task ID."
            
            if manager.complete_task(task_id):
                return f"Marked task {task_id} as completed."
            else:
                return f"Error: Task {task_id} not found."
                
        elif action == "delete":
            # Format: delete [task_id]
            if len(parts) < 2:
                return "Error: Task ID required."
            
            try:
                task_id = int(parts[1])
            except ValueError:
                return "Error: Invalid task ID."
            
            if manager.delete_task(task_id):
                return f"Deleted task {task_id}."
            else:
                return f"Error: Task {task_id} not found."
                
        elif action == "list":
            # Format: list [all|overdue|upcoming|high]
            filter_type = parts[1].lower() if len(parts) > 1 else "all"
            
            if filter_type == "all":
                tasks = manager.tasks
            elif filter_type == "overdue":
                tasks = manager.get_overdue_tasks()
            elif filter_type == "upcoming":
                tasks = manager.get_upcoming_tasks()
            elif filter_type == "high":
                tasks = manager.get_high_priority_tasks()
            else:
                return f"Error: Unknown filter type '{filter_type}'."
            
            if not tasks:
                return "No tasks found."
            
            result = []
            for task in tasks:
                result.append(str(task))
            
            return "\n".join(result)
            
        elif action == "sort":
            # Format: sort [priority|deadline|created]
            sort_key = parts[1].lower() if len(parts) > 1 else "priority"
            
            if sort_key not in ["priority", "deadline", "created"]:
                return f"Error: Unknown sort key '{sort_key}'."
            
            tasks = manager.sort_tasks(sort_key)
            
            if not tasks:
                return "No tasks found."
            
            result = []
            for task in tasks:
                result.append(str(task))
            
            return "\n".join(result)
            
        elif action == "report":
            # Format: report [include_completed]
            include_completed = False
            if len(parts) > 1 and parts[1].lower() == "all":
                include_completed = True
            
            return generate_task_report(manager, include_completed)
            
        else:
            return f"Error: Unknown command '{action}'."
            
    except Exception as e:
        # BUG FIX 3: Specific error handling instead of catching all exceptions
        import traceback
        error_type = type(e).__name__
        return f"Error ({error_type}): {str(e)}\nUse 'help' for command syntax."


def main():
    """Main function to run the task manager."""
    manager = create_sample_tasks()
    
    print("Task Manager started. Type 'exit' to quit.")
    print("Commands: add, complete, delete, list, sort, report")
    
    while True:
        command = input("\nEnter command: ")
        
        if command.lower() == "exit":
            break
        
        result = process_command(manager, command)
        print(result)


if __name__ == "__main__":
    # For debugging demonstration
    import pdb
    
    # Example of conditional breakpoint (uncomment to use)
    # To set a conditional breakpoint in pdb:
    # b process_command, "add" in command.lower()
    
    # To use post-mortem debugging when an exception occurs:
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        # Uncomment to start post-mortem debugging
        # pdb.post_mortem()

"""
Debugging Process and Bug Fixes:

1. Bug #1: Task Name Parsing with Spaces
   - When debugging with pdb, we discovered that task names with spaces weren't
     being parsed correctly, especially when enclosed in quotes.
   - Fix: Completely rewrote the name parsing logic to handle quoted strings properly.
   
   Debugging approach:
   - Set breakpoint: b process_command
   - Run a command with spaces: add "My Task With Spaces" 2
   - Stepped through with 'n' and 's' to see how parts[] was being processed
   - Examined the variables with 'p parts', 'p command'
   - Discovered the original parsing logic only worked in limited cases

2. Bug #2: Priority Validation
   - The original code had weak validation for priorities
   - If a non-numeric value was provided for priority, it would crash
   - Fix: Added better error handling and validation
   
   Debugging approach:
   - Set conditional breakpoint: b process_command, "priority" in locals()
   - Tried invalid input: add "Test" abc
   - Examined the exception with pdb.post_mortem()
   - Added proper try/except and validation

3. Bug #3: Generic Exception Handling
   - The original code caught all exceptions with a generic handler
   - This made debugging difficult and hid the real causes of errors
   - Fix: Improved error reporting with exception type information
   
   Debugging approach:
   - Set breakpoint after an error was raised
   - Examined the exception with 'p e', 'p type(e)'
   - Modified error handling to be more informative

Advanced pdb Techniques Demonstrated:

1. Conditional Breakpoints
   - We used condition 'b process_command, "add" in command.lower()' to break only
     when processing 'add' commands
   - This focused debugging on the specific part of the code with issues

2. Examining Call Stack
   - Used 'w' to show the call stack during complex command processing
   - Identified which functions were involved in the bug

3. Modifying Variables
   - Used '!priority = 3' to modify variables during debugging
   - Tested different values to see how they affected the outcome

4. Post-Mortem Debugging
   - Used pdb.post_mortem() to analyze exceptions after they occurred
   - This helped trace the original invalid priority issue

5. Printing Complex Objects
   - Used 'pp task' to pretty-print task objects
   - Helped understand the state of objects during different operations

These techniques allowed for efficient identification of bugs that would have been
difficult to find with simple print debugging or basic pdb commands.
"""
