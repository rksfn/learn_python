"""
Exercise 3 Solution: Debugging Complex Data Structures

This solution demonstrates how to debug code that processes complex nested data structures
using effective print debugging techniques with pretty printing and structured output.
"""

import json
from pprint import pprint

# Step 1: Implement a debug helper for complex data structures
def debug_data(label, data, pretty=True, level=0):
    """
    Print a labeled data structure with appropriate formatting based on its type.
    
    Args:
        label (str): A descriptive label for the data
        data (any): The data structure to print
        pretty (bool): Whether to use pretty printing (default True)
        level (int): Indentation level for nested debug calls
    """
    indent = "  " * level
    separator = "=" * 40
    
    print(f"\n{indent}{separator}")
    print(f"{indent}DEBUG: {label}")
    print(f"{indent}{separator}")
    
    if data is None:
        print(f"{indent}None")
    elif isinstance(data, (dict, list)) and pretty:
        pprint(data, indent=2, width=100, depth=4)
    elif isinstance(data, dict) and not pretty:
        for key, value in data.items():
            print(f"{indent}{key}: ", end="")
            if isinstance(value, (dict, list)):
                print()
                debug_data(f"{key} contents", value, pretty, level + 1)
            else:
                print(value)
    elif isinstance(data, list) and not pretty:
        for i, item in enumerate(data):
            print(f"{indent}[{i}]: ", end="")
            if isinstance(item, (dict, list)):
                print()
                debug_data(f"Item {i} contents", item, pretty, level + 1)
            else:
                print(item)
    else:
        print(f"{indent}{data}")
    
    print(f"{indent}{separator}\n")

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
    # Step 2: Add debug prints to trace the JSON parsing
    try:
        data = json.loads(api_response)
        debug_data("Parsed JSON data", data)
        
        library = data['library']
        debug_data("Library object", library)
        
        result = {
            'library_name': library['name'],
            'total_books': len(library['books']),
            'available_books': [],
            'borrowed_books': {},
            'categories': set()
        }
        
        debug_data("Initial result structure", result)
        
        # Process each book
        for i, book in enumerate(library['books']):
            debug_data(f"Processing book {i+1}", book)
            
            # Add categories to our set
            for category in book['categories']:
                result['categories'].add(category)
            
            # Process book based on availability
            if book['available']:
                debug_data(f"Book {book['id']} is available", None)
                result['available_books'].append({
                    'id': book['id'],
                    'title': book['title'],
                    'author': f"{book['author']['first_name']} {book['author']['last_name']}"
                })
            else:
                debug_data(f"Book {book['id']} is borrowed", book['borrowers'])
                # Store borrower info by user ID
                for borrower in book['borrowers']:
                    if borrower['id'] not in result['borrowed_books']:
                        result['borrowed_books'][borrower['id']] = []
                    
                    # BUG FIX 1: Include borrower name in the book record
                    # (missing in original code)
                    result['borrowed_books'][borrower['id']].append({
                        'book_id': book['id'],
                        'title': book['title'],
                        'due_date': borrower['due_date'],
                        'borrower_name': borrower['name']  # Add borrower name
                    })
        
        # Convert categories set to sorted list for consistency
        result['categories'] = sorted(list(result['categories']))
        
        debug_data("Final processed data", result)
        return result
        
    except Exception as e:
        debug_data("Error parsing library data", str(e))
        raise

def generate_library_report(library_data):
    """Generate a report from the processed library data."""
    debug_data("Generating report from library data", library_data)
    
    report = []
    
    report.append(f"LIBRARY REPORT: {library_data['library_name']}")
    report.append(f"Total Books: {library_data['total_books']}")
    report.append(f"Available Books: {len(library_data['available_books'])}")
    
    # BUG FIX 2: The borrowed books count was incorrectly calculated
    # Calculate total borrowed books correctly
    borrowed_count = sum(len(books) for books in library_data['borrowed_books'].values())
    report.append(f"Books Currently Borrowed: {borrowed_count}")
    
    report.append(f"Categories: {', '.join(library_data['categories'])}")
    
    report.append("\nAVAILABLE BOOKS:")
    for book in library_data['available_books']:
        report.append(f"- {book['title']} by {book['author']} (ID: {book['id']})")
    
    report.append("\nBORROWED BOOKS BY USER:")
    for user_id, books in library_data['borrowed_books'].items():
        # BUG FIX 3: Access the borrower name correctly from the first book
        user_name = books[0]['borrower_name'] if books else "Unknown"
        report.append(f"User: {user_name} (ID: {user_id})")
        for book in books:
            report.append(f"  - {book['title']} (Due: {book['due_date']})")
    
    debug_data("Final report", "\n".join(report))
    return "\n".join(report)

def main():
    """Main function to process library data and generate report."""
    try:
        debug_data("Starting library data processing", None)
        
        # Parse the library data
        library_data = parse_library_data(API_RESPONSE)
        
        # Generate and print the report
        report = generate_library_report(library_data)
        
        print("\n\n" + "="*60 + "\n")
        print(report)
        print("\n" + "="*60)
        
        debug_data("Library processing completed successfully", None)
        
    except Exception as e:
        debug_data("Error in main function", str(e))

if __name__ == "__main__":
    main()

"""
Explanation of Bugs Found:

1. Missing Borrower Name:
   The original code didn't store the borrower's name with the borrowed book 
   information, causing the "Unknown" fallback to be used in the report.
   
   Solution: Add 'borrower_name': borrower['name'] to the book information
   in the borrowed_books dictionary.

2. Incorrect Borrowed Books Count:
   The calculation of total borrowed books was using a method (len(items))
   that wouldn't work correctly for nested dictionaries.
   
   Solution: Use sum(len(books) for books in library_data['borrowed_books'].values())
   to count all books across all borrowers.

3. Incorrect Borrower Name Access:
   The report generation code tried to access 'borrower_name' directly in the books
   dictionary, but it wasn't stored there in the original code.
   
   Solution: This is fixed by the first bug fix, storing the borrower name with each book.

Using print debugging with complex data structures:

1. The debug_data() function provides a consistent way to visualize complex
   nested structures, making the output easier to read and understand.

2. By including descriptive labels and separators, we can quickly identify different
   stages of data processing in the output.

3. Using pprint for complex structures makes the nested structure visible
   and easier to navigate.

4. Tracing the data transformations between functions helps identify where and
   how the data structure changes, making it easier to spot bugs.

5. Using conditional formatting based on data type makes the output even more
   helpful - simple values are shown directly, while complex structures are
   pretty-printed.

The debug_data() function is particularly valuable for APIs, JSON processing,
and other situations involving complex nested data structures, where standard
print statements would produce hard-to-read output.
"""
