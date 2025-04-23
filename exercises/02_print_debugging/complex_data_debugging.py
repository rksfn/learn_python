"""
Exercise 3: Debugging Complex Data Structures

In this exercise, you'll practice debugging code that processes and transforms 
complex nested data structures. You'll learn how to effectively visualize and
trace changes to dictionaries, lists, and custom objects.

Scenario: You're working with a program that processes a JSON response from an API
containing information about books in a library. The code attempts to transform this
data for use in a library management system but contains bugs.
"""

import json
from pprint import pprint

# Sample API response data
API_RESPONSE = '''
{
  "library": {
    "name": "City Central Library",
    "books": [
      {
        "id": "B001",
        "title": "Python Programming",
        "author": {"first_name": "John", "last_name": "Smith"},
        "categories": ["Programming", "Computer Science"],
        "available": true,
        "borrowers": []
      },
      {
        "id": "B002",
        "title": "Data Science Fundamentals",
        "author": {"first_name": "Jane", "last_name": "Doe"},
        "categories": ["Data Science", "Statistics", "Programming"],
        "available": false,
        "borrowers": [
          {"id": "U005", "name": "Mike Johnson", "due_date": "2023-05-15"}
        ]
      },
      {
        "id": "B003",
        "title": "Machine Learning Basics",
        "author": {"first_name": "Robert", "last_name": "Davis"},
        "categories": ["Machine Learning", "Artificial Intelligence"],
        "available": true,
        "borrowers": []
      },
      {
        "id": "B004",
        "title": "The Art of Fiction",
        "author": {"first_name": "Lisa", "last_name": "Wong"},
        "categories": ["Fiction", "Writing"],
        "available": false,
        "borrowers": [
          {"id": "U010", "name": "Sarah Miller", "due_date": "2023-05-20"}
        ]
      }
    ]
  }
}
'''

def parse_library_data(api_response):
    """Parse the API response and return structured library data."""
    data = json.loads(api_response)
    library = data['library']
    
    result = {
        'library_name': library['name'],
        'total_books': len(library['books']),
        'available_books': [],
        'borrowed_books': {},
        'categories': set()
    }
    
    # Process each book
    for book in library['books']:
        # Add categories to our set
        for category in book['categories']:
            result['categories'].add(category)
        
        # Process book based on availability
        if book['available']:
            result['available_books'].append({
                'id': book['id'],
                'title': book['title'],
                'author': f"{book['author']['first_name']} {book['author']['last_name']}"
            })
        else:
            # Store borrower info by user ID
            for borrower in book['borrowers']:
                if borrower['id'] not in result['borrowed_books']:
                    result['borrowed_books'][borrower['id']] = []
                
                result['borrowed_books'][borrower['id']].append({
                    'book_id': book['id'],
                    'title': book['title'],
                    'due_date': borrower['due_date']
                })
    
    # Convert categories set to sorted list for consistency
    result['categories'] = sorted(list(result['categories']))
    
    return result

def generate_library_report(library_data):
    """Generate a report from the processed library data."""
    report = []
    
    report.append(f"LIBRARY REPORT: {library_data['library_name']}")
    report.append(f"Total Books: {library_data['total_books']}")
    report.append(f"Available Books: {len(library_data['available_books'])}")
    report.append(f"Books Currently Borrowed: {sum(len(items) for items in library_data['borrowed_books'].values())}")
    report.append(f"Categories: {', '.join(library_data['categories'])}")
    
    report.append("\nAVAILABLE BOOKS:")
    for book in library_data['available_books']:
        report.append(f"- {book['title']} by {book['author']} (ID: {book['id']})")
    
    report.append("\nBORROWED BOOKS BY USER:")
    for user_id, books in library_data['borrowed_books'].items():
        user_name = books[0]['borrower_name'] if 'borrower_name' in books[0] else "Unknown"
        report.append(f"User: {user_name} (ID: {user_id})")
        for book in books:
            report.append(f"  - {book['title']} (Due: {book['due_date']})")
    
    return "\n".join(report)

def main():
    """Main function to process library data and generate report."""
    try:
        # Parse the library data
        library_data = parse_library_data(API_RESPONSE)
        
        # Generate and print the report
        report = generate_library_report(library_data)
        print(report)
        
    except Exception as e:
        print(f"Error processing library data: {e}")

if __name__ == "__main__":
    main()

"""
Tasks:

1. Run the program and identify the errors that occur.

2. Use print debugging techniques to visualize the complex data structures at 
   different stages of processing. Specifically:
   
   a. Use pprint to visualize the parsed JSON data
   b. Add debug prints to track the transformation of book data
   c. Print the final processed data structure before report generation
   
3. Find and fix all bugs in the code. There are at least three issues to identify.

4. Implement the following debug helper for complex data structures:

   def debug_data(label, data, pretty=True):
       '''Print a labeled data structure, optionally using pretty printing.'''
       # Your implementation here
       
5. Refactor the code to use your debug_data() function to trace the data transformations.

Bonus: Extend your debug_data() function to handle different types of data structures
appropriately (e.g., special formatting for dictionaries vs lists vs custom objects).
"""
