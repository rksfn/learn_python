"""
Exercise 2: Advanced Print Debugging

In this exercise, you'll debug a more complex application with multiple functions
and data transformations. You'll practice using formatted print statements and
selective debugging techniques.

Scenario: This program is supposed to analyze student exam scores, calculate statistics,
and identify students who need additional help. However, it's producing incorrect results.
"""

import random
from datetime import datetime

# Global debug flag - set to True to enable debug prints
DEBUG = True

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
    
    for i in range(8):
        # Generate 5 random scores between 50 and 100
        scores = [random.randint(50, 100) for _ in range(5)]
        students.append(Student(i+1, names[i], scores))
    
    return students


def calculate_statistics(students):
    """Calculate average scores and identify struggling students."""
    class_averages = []
    struggling_students = []
    
    for student in students:
        # Calculate student's average score
        avg_score = sum(student.scores) / len(student.scores)
        
        # If average is below 70, student needs help
        if avg_score < 70:
            struggling_students.append(student)
        
        # Add to class averages
        class_averages.append(avg_score)
    
    # Calculate overall class average
    overall_average = sum(class_averages) / len(class_averages)
    
    return {
        'overall_average': overall_average,
        'student_averages': class_averages,
        'struggling_students': struggling_students
    }


def generate_report(stats):
    """Generate a human-readable report from the statistics."""
    report = []
    report.append("STUDENT PERFORMANCE REPORT")
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"Class Average: {stats['overall_average']:.2f}")
    report.append("\nStruggling Students (Average < 70):")
    
    # Check if there are any struggling students
    if stats['struggling_students']:
        for student in stats['struggling_students']:
            # Calculate student average again for the report
            avg = sum(student.scores) / len(student.scores)
            report.append(f"- {student.name} (ID: {student.id}): {avg:.2f}")
    else:
        report.append("None")
    
    return "\n".join(report)


def main():
    """Main function to run the program."""
    # Generate sample data
    students = generate_sample_data()
    
    # Set specific scores for one student to ensure they're struggling
    students[2].scores = [65, 62, 68, 70, 69]
    
    # Calculate statistics
    stats = calculate_statistics(students)
    
    # Generate report
    report = generate_report(stats)
    
    # Display report
    print(report)


if __name__ == "__main__":
    main()


"""
Tasks:

1. Run the program and observe its output. Is the struggling students list correct?

2. Add print debugging statements to identify why some struggling students might 
   not be appearing in the report correctly.
   
3. Implement a proper debug_print() function that:
   - Respects the global DEBUG flag
   - Includes timestamps
   - Formats values nicely
   - Shows the function name where the debug print was called

4. Use your debug_print() function to trace the calculation of student averages
   and the identification of struggling students.
   
5. Find and fix any bugs in the code.

6. Explain how your print debugging approach helped identify the issue.

Bonus: Update your debug_print() function to support different debug levels
(e.g., INFO, WARNING, ERROR) and filter output based on level.
"""
