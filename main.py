from deadline_manager import DocumentDeadlineManager
from pathlib import Path

def read_document(file_path):
    """Read document content from file"""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None

def main():
    print("Document Deadline Analyzer")
    print("-" * 30)
    
    # Initialize deadline manager
    manager = DocumentDeadlineManager()
    
    while True:
        print("\nOptions:")
        print("1. Analyze a document")
        print("2. View all deadlines")
        print("3. View upcoming deadlines")
        print("4. View expired deadlines")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            # Get document path from user
            file_path = input("\nEnter the path to your document: ")
            
            # Validate path
            if not Path(file_path).exists():
                print(f"Error: File {file_path} does not exist")
                continue
            
            # Read and process document
            print(f"\nAnalyzing document: {Path(file_path).name}")
            content = read_document(file_path)
            if content:
                manager.process_new_document(content, Path(file_path).name)
                
        elif choice == "2":
            deadlines = manager.get_all_deadlines()
            if deadlines.empty:
                print("\nNo deadlines stored yet")
            else:
                print("\nAll Deadlines:")
                print(deadlines)
                
        elif choice == "3":
            days = input("\nEnter number of days to look ahead (default 30): ")
            days = int(days) if days.isdigit() else 30
            
            deadlines = manager.get_upcoming_deadlines(days)
            if deadlines.empty:
                print(f"\nNo upcoming deadlines in the next {days} days")
            else:
                print(f"\nUpcoming Deadlines (next {days} days):")
                print(deadlines)
                
        elif choice == "4":
            deadlines = manager.get_expired_deadlines()
            if deadlines.empty:
                print("\nNo expired deadlines")
            else:
                print("\nExpired Deadlines:")
                print(deadlines)
                
        elif choice == "5":
            print("\nExiting program...")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()
