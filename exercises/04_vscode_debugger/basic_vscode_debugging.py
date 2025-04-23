"""
Exercise 1: Getting Started with VS Code Debugging

In this exercise, you'll learn the basics of debugging Python code using Visual
Studio Code's integrated debugger. You'll practice setting breakpoints, stepping
through code, examining variables, and fixing bugs.

Objectives:
- Configure VS Code's debugging environment
- Set and use breakpoints
- Navigate code execution with debugging controls
- Use the Variables panel to inspect data
- Fix bugs using the VS Code debugging interface
"""

def calculate_statistics(numbers):
    """
    Calculate several statistics for a list of numbers.
    
    Args:
        numbers: A list of numbers
        
    Returns:
        A dictionary containing various statistics
    """
    if not numbers:
        return {
            "count": 0,
            "sum": 0,
            "min": None,
            "max": None,
            "range": None,
            "mean": None,
            "median": None
        }
    
    # Sort the numbers for easier calculations
    sorted_numbers = sorted(numbers)
    
    # Calculate basic statistics
    count = len(sorted_numbers)
    total = sum(sorted_numbers)
    minimum = sorted_numbers[0]
    maximum = sorted_numbers[-1]
    value_range = maximum - minimum
    mean = total / count
    
    # Calculate median
    if count % 2 == 0:
        # Even number of elements
        middle1 = sorted_numbers[count // 2 - 1]
        middle2 = sorted_numbers[count // 2]
        median = (middle1 + middle2) / 2
    else:
        # Odd number of elements
        median = sorted_numbers[count // 2]
    
    return {
        "count": count,
        "sum": total,
        "min": minimum,
        "max": maximum,
        "range": value_range,
        "mean": mean,
        "median": median
    }


def analyze_student_scores(student_data):
    """
    Analyze student test scores and identify students who need help.
    
    Args:
        student_data: A list of dictionaries, each containing:
                     - name: Student name
                     - scores: List of test scores
                     
    Returns:
        A tuple containing:
        1. Class statistics (from calculate_statistics)
        2. List of students needing help (average below 70)
        3. Dictionary mapping each student to their average score
    """
    # Collect all scores for overall class statistics
    all_scores = []
    student_averages = {}
    students_needing_help = []
    
    for student in student_data:
        name = student["name"]
        scores = student["scores"]
        
        # Add to all scores collection
        all_scores.extend(scores)
        
        # Calculate student's average
        if scores:
            average = sum(scores) / len(scores)
            student_averages[name] = average
            
            # Check if student needs help (average below 70)
            if average < 70:
                students_needing_help.append(name)
        else:
            student_averages[name] = 0
    
    # Calculate overall class statistics
    class_stats = calculate_statistics(all_scores)
    
    return class_stats, students_needing_help, student_averages


def generate_report(student_data):
    """
    Generate a report on student performance.
    
    Args:
        student_data: A list of dictionaries with student names and scores
        
    Returns:
        A formatted report string
    """
    class_stats, students_needing_help, student_averages = analyze_student_scores(student_data)
    
    # Format the report
    report = []
    report.append("STUDENT PERFORMANCE REPORT")
    report.append("=" * 30)
    report.append(f"Total students: {len(student_data)}")
    report.append(f"Total scores analyzed: {class_stats['count']}")
    report.append(f"Class average: {class_stats['mean']:.2f}")
    report.append(f"Highest score: {class_stats['max']}")
    report.append(f"Lowest score: {class_stats['min']}")
    report.append(f"Score range: {class_stats['range']}")
    report.append("")
    
    # Add student averages section
    report.append("STUDENT AVERAGES")
    report.append("-" * 30)
    
    # Sort students by average score (highest to lowest)
    sorted_students = sorted(student_averages.items(), key=lambda x: x[1], reverse=True)
    
    for student, average in sorted_students:
        report.append(f"{student}: {average:.2f}")
    
    # Add section for students needing help
    report.append("")
    report.append("STUDENTS NEEDING HELP")
    report.append("-" * 30)
    
    if students_needing_help:
        for student in students_needing_help:
            report.append(f"{student} (Average: {student_averages[student]:.2f})")
    else:
        report.append("No students identified as needing help.")
    
    return "\n".join(report)


# Test data
student_data = [
    {"name": "Alice", "scores": [92, 88, 95, 91]},
    {"name": "Bob", "scores": [78, 65, 72, 81]},
    {"name": "Charlie", "scores": [65, 62, 68, 70]},
    {"name": "David", "scores": [55, 60, 65, 62]},
    {"name": "Eve", "scores": [98, 96, 99, 95]},
    {"name": "Frank", "scores": [81, 75, 79, 82]},
    {"name": "Grace", "scores": [68, 71, 73, 69]},
    {"name": "Helen", "scores": [85, 88, 90, 87]}
]

# Generate and print the report
print(generate_report(student_data))

# Test with an empty list
print("\nEmpty data test:")
print(generate_report([]))

# Test with some edge cases
print("\nEdge case test:")
edge_case_data = [
    {"name": "NoScores", "scores": []},
    {"name": "OneScore", "scores": [75]},
    {"name": "ExtremeScores", "scores": [0, 100]}
]
print(generate_report(edge_case_data))

"""
VS Code Debugging Exercise Instructions:

1. Configure VS Code Debugger:
   - Make sure you have the Python extension installed in VS Code
   - Click the "Run and Debug" tab in the sidebar (or press Ctrl+Shift+D)
   - Click "create a launch.json file" if needed
   - Select "Python File" configuration

2. Start Basic Debugging:
   - Set a breakpoint on line 90 (where analyze_student_scores is called in generate_report)
     by clicking in the margin next to the line number
   - Press F5 to start debugging
   - When execution pauses at the breakpoint, examine the student_data variable in the Variables panel
   - Press F10 to step over the function call
   - Examine the returned values (class_stats, students_needing_help, student_averages)

3. Find and Fix Bug #1:
   - Set a breakpoint in the calculate_statistics function
   - Restart the debugger
   - When it hits the breakpoint in calculate_statistics, step through the function
   - Look for potential issues with handling empty lists or calculating statistics
   - Fix any bugs you find

4. Find and Fix Bug #2:
   - Set a breakpoint in the generate_report function
   - Restart the debugger
   - Examine how the student data is processed and formatted
   - Fix any issues in the report generation

5. Use the Watch Panel:
   - Add expressions to the Watch panel to monitor key values
   - Try watching: `student_averages.get("David", 0)` and `len(students_needing_help)`

6. Try Conditional Breakpoints:
   - Right-click on a breakpoint and add a condition
   - For example, in the loop processing student data, break only when `name == "David"`

7. Use Debug Console:
   - While stopped at a breakpoint, open the Debug Console
   - Try evaluating expressions like `sum(student_averages.values()) / len(student_averages)`

Questions to consider:
1. How does watching variables in the Variables panel compare to print debugging?
2. What advantages do you see in using VS Code's visual debugger?
3. How might conditional breakpoints help with more complex debugging scenarios?
4. What was easier to find with the VS Code debugger compared to using pdb?
"""
