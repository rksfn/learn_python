"""
Exercise 2 Solution: Advanced Print Debugging

This solution demonstrates how to use advanced print debugging techniques to identify
issues in a multi-function application processing student data.
"""

import random
from datetime import datetime
import inspect
import time

# Global debug flag - set to True to enable debug prints
DEBUG = True

# Step 1: Implement a proper debug_print function with timestamps and function context
def debug_print(message, value=None, level="INFO"):
    """
    Advanced debug print function with timestamps, calling function name, and log levels.
    
    Args:
        message (str): The debug message to print
        value (any, optional): A value to print after the message
        level (str, optional): Log level (INFO, WARNING, ERROR)
    """
    if not DEBUG:
        return
        
    # Get timestamp
    timestamp = time.strftime("%H:%M:%S")
    
    # Get caller information
    caller_frame = inspect.currentframe().f_back
    caller_name = caller_frame.f_code.co_name
    line_no = caller_frame.f_lineno
    
    # Format the log level
    level_str = f"[{level}]".ljust(9)
    
    # Format the base message
    base_msg = f"{timestamp} {level_str} {caller_name}:{line_no} - {message}"
    
    # Print with or without a value
    if value is not None:
        # Format different types of values appropriately
        if isinstance(value, float):
            print(f"{base_msg}: {value:.2f}")
        elif isinstance(value, dict) or isinstance(value, list):
            print(f"{base_msg}:")
            import pprint
            pprint.pprint(value, indent=2, width=100)
        else:
            print(f"{base_msg}: {value}")
    else:
        print(base_msg)


class Student:
    def __init__(self, id, name, scores):
        self.id = id
        self.name = name
        self.scores = scores  # List of exam scores
    
    def __repr__(self):
        return f"Student({self.id}, {self.name}, {self.scores})"


def generate_sample_data():
    """Generate sample student data for testing."""
    names = ["Alice", "Bob", "Charlie", "Dana", "Elijah", "Fiona", "George", "Hannah"]
    students = []
    
    debug_print("Generating sample student data")
    
    for i in range(8):
        # Generate 5 random scores between 50 and 100
        scores = [random.randint(50, 100) for _ in range(5)]
        students.append(Student(i+1, names[i], scores))
        debug_print(f"Created student {i+1}", students[i])
    
    debug_print("Sample data generation complete", len(students))
    return students


def calculate_statistics(students):
    """Calculate average scores and identify struggling students."""
    debug_print("Starting statistics calculation", len(students))
    
    class_averages = []
    struggling_students = []
    
    for student in students:
        debug_print(f"Processing student {student.id}", student.name)
        debug_print("Scores", student.scores)
        
        # Calculate student's average score
        avg_score = sum(student.scores) / len(student.scores)
        debug_print("Average score", avg_score)
        
        # If average is below 70, student needs help
        if avg_score < 70:
            debug_print("Student is struggling", avg_score)
            struggling_students.append(student)
        
        # Add to class averages
        class_averages.append(avg_score)
    
    # Calculate overall class average
    overall_average = sum(class_averages) / len(class_averages)
    debug_print("Overall class average", overall_average)
    
    # BUG FOUND: The code doesn't save student average scores with the student objects
    # Let's fix that by attaching the average to each student object
    for i, student in enumerate(students):
        student.average_score = class_averages[i]
        debug_print(f"Attached average to {student.name}", student.average_score)
    
    result = {
        'overall_average': overall_average,
        'student_averages': class_averages,
        'struggling_students': struggling_students
    }
    
    debug_print("Statistics calculation complete")
    debug_print("Struggling students count", len(struggling_students))
    return result


def generate_report(stats):
    """Generate a human-readable report from the statistics."""
    debug_print("Generating report")
    debug_print("Stats input", stats)
    
    report = []
    report.append("STUDENT PERFORMANCE REPORT")
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"Class Average: {stats['overall_average']:.2f}")
    report.append("\nStruggling Students (Average < 70):")
    
    # Check if there are any struggling students
    debug_print("Struggling students count", len(stats['struggling_students']))
    
    if stats['struggling_students']:
        for student in stats['struggling_students']:
            # BUG FOUND: The report is calculating student average again 
            # instead of using the one we already calculated
            
            # Original bug:
            # avg = sum(student.scores) / len(student.scores)
            
            # Fixed version - using the attached average property:
            avg = student.average_score
            debug_print(f"Student {student.name} struggling with average", avg)
            report.append(f"- {student.name} (ID: {student.id}): {avg:.2f}")
    else:
        report.append("None")
    
    debug_print("Report generation complete")
    return "\n".join(report)


def main():
    """Main function to run the program."""
    debug_print("Program started")
    
    # Generate sample data
    students = generate_sample_data()
    
    # Set specific scores for one student to ensure they're struggling
    debug_print("Setting specific scores for Charlie")
    students[2].scores = [65, 62, 68, 70, 69]
    
    # Calculate statistics
    debug_print("Calculating statistics")
    stats = calculate_statistics(students)
    
    # Generate report
    debug_print("Generating final report")
    report = generate_report(stats)
    
    # Display report
    print("\n" + "="*50 + "\n")
    print(report)
    
    debug_print("Program completed")


if __name__ == "__main__":
    main()

"""
Explanation of Bugs Found:

1. Missing Student Averages:
   The original code calculates student averages but doesn't store them with 
   the student objects. When the report generation function runs, it recalculates
   the averages again, which is inefficient and potentially inconsistent.
   
   Solution: Store the calculated average with each student object.

2. Redundant Calculation:
   The generate_report function unnecessarily recalculates each student's average
   instead of using the already calculated values.
   
   Solution: Use the stored average instead of recalculating.

Using print debugging techniques helped identify these issues by:

1. Showing the flow of data between functions
2. Highlighting redundant calculations
3. Making it clear that student averages weren't preserved between functions
4. Providing visibility into how the struggling students were identified

The advanced debug_print function we implemented provides several benefits:

1. Timestamps help track execution time
2. Function names and line numbers pinpoint where debug prints are coming from
3. Value formatting makes output more readable
4. The ability to disable all debug output with a single flag
5. Different log levels (INFO, WARNING, ERROR) help categorize messages

This approach is much more maintainable than using raw print statements throughout
the code. It's also a step towards using a proper logging system, which would be
the next evolution of this debugging technique.
"""
