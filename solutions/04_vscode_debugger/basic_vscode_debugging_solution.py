"""
Exercise 1 Solution: Getting Started with VS Code Debugging

This solution demonstrates how to use VS Code's debugging features to find and fix
bugs in the student performance analysis program.
"""

def calculate_statistics(numbers):
    """
    Calculate several statistics for a list of numbers.
    
    Args:
        numbers: A list of numbers
        
    Returns:
        A dictionary containing various statistics
    """
    # BUG FIX 1: Handle empty lists properly
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
    # BUG FIX 2: Handle empty student_data properly
    if not student_data:
        return (
            {"count": 0, "sum": 0, "min": None, "max": None, "range": None, "mean": None, "median": None},
            [],
            {}
        )
    
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
            # BUG FIX 3: Properly handle students with no scores
            student_averages[name] = None
    
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
    # BUG FIX 4: Handle empty student_data gracefully
    if not student_data:
        return "STUDENT PERFORMANCE REPORT\n" + "=" * 30 + "\nNo student data available."
    
    class_stats, students_needing_help, student_averages = analyze_student_scores(student_data)
    
    # Format the report
    report = []
    report.append("STUDENT PERFORMANCE REPORT")
    report.append("=" * 30)
    report.append(f"Total students: {len(student_data)}")
    report.append(f"Total scores analyzed: {class_stats['count']}")
    
    # BUG FIX 5: Check if mean is None before formatting
    if class_stats['mean'] is not None:
        report.append(f"Class average: {class_stats['mean']:.2f}")
    else:
        report.append("Class average: N/A")
        
    # BUG FIX 6: Check if min/max/range are None before adding them
    if class_stats['max'] is not None:
        report.append(f"Highest score: {class_stats['max']}")
    else:
        report.append("Highest score: N/A")
        
    if class_stats['min'] is not None:
        report.append(f"Lowest score: {class_stats['min']}")
    else:
        report.append("Lowest score: N/A")
        
    if class_stats['range'] is not None:
        report.append(f"Score range: {class_stats['range']}")
    else:
        report.append("Score range: N/A")
        
    report.append("")
    
    # Add student averages section
    report.append("STUDENT AVERAGES")
    report.append("-" * 30)
    
    # Filter out None averages and sort students by average score (highest to lowest)
    valid_averages = {k: v for k, v in student_averages.items() if v is not None}
    sorted_students = sorted(valid_averages.items(), key=lambda x: x[1], reverse=True)
    
    if sorted_students:
        for student, average in sorted_students:
            report.append(f"{student}: {average:.2f}")
    else:
        report.append("No valid student averages available.")
    
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
VS Code Debugging Solution Notes:

During the debugging process, we identified and fixed several bugs:

1. Empty List Handling in calculate_statistics:
   - The original code didn't properly handle empty lists, which would cause errors
     when trying to calculate min, max, and other statistics.
   - Using VS Code's debugging, we stepped into the function execution and caught
     the issue before it became a runtime error.
   - Fix: Added proper handling for empty lists at the beginning of the function.

2. Empty Student Data:
   - When student_data was empty, the program would produce errors or confusing output.
   - Using the Watch panel to monitor the length of student_data throughout execution
     helped identify this issue.
   - Fix: Added checks for empty student_data in analyze_student_scores and generate_report.

3. Students with No Scores:
   - The original code set student_averages[name] = 0 when a student had no scores,
     which is misleading (0 is a valid score).
   - While stepping through the code in VS Code's debugger, we observed this in the
     Variables panel and identified it as problematic.
   - Fix: Changed to student_averages[name] = None to indicate no valid average.

4. Formatting Issues for None Values:
   - When statistics were None, the original code tried to format them with :.2f,
     causing errors.
   - VS Code's debugger allowed us to set watch expressions for class_stats and
     see exactly what values were causing issues.
   - Fix: Added checks before formatting to handle None values gracefully.

5. Sorting with None Values:
   - When sorting student averages that included None values, errors would occur.
   - Using a conditional breakpoint in VS Code (condition: sorted_students is not None),
     we could examine the data structure before the error.
   - Fix: Filter out None averages before sorting.

VS Code Debugging Features Used:

1. Breakpoints:
   - Set breakpoints at key locations like the beginning of functions
   - Used conditional breakpoints to stop only in specific scenarios

2. Step Execution:
   - Used Step Over (F10) to execute one line at a time
   - Used Step Into (F11) to dig into function calls
   - Used Step Out (Shift+F11) to complete functions and return to callers

3. Variable Inspection:
   - Examined variables in the Variables panel
   - Hovered over variables in the code to see current values
   - Used the Watch panel to monitor expressions like student_averages.values()

4. Debug Console:
   - Evaluated expressions during debugging to test fixes
   - Modified variables to simulate different scenarios

5. Call Stack:
   - Used the Call Stack panel to understand how functions were calling each other
   - Jumped between stack frames to examine variables at different levels

This exercise demonstrated how VS Code's visual debugging interface can make
finding and fixing bugs much more efficient than using print statements or pdb alone.
"""
