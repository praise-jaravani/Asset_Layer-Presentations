import argparse
from pathlib import Path
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import HuggingFaceHubEmbeddings

def setup_connections():
    """Setup connections to embedding service and database"""
    try:
        embeddings = HuggingFaceHubEmbeddings(
            model="http://localhost:9002",
            huggingfacehub_api_token="EMPTY"
        )
        
        store = PGVector(
            collection_name="documents",
            connection_string="postgresql+psycopg2://postgres:postgres@localhost:9003/postgres",
            embedding_function=embeddings,
            pre_delete_collection=True
        )
        print("Successfully connected to embedding service and database")
        return store
    except Exception as e:
        print(f"Error setting up connections: {str(e)}")
        return None

def load_file_to_db(file_path: str, store: PGVector):
    """Load a text file into the vector database"""
    try:
        # Check if file exists
        if not Path(file_path).exists():
            print(f"Error: File {file_path} does not exist")
            return
        
        # Check if file is a text file
        if not file_path.endswith('.txt'):
            print(f"Error: {file_path} is not a text file")
            return
            
        loader = TextLoader(file_path)
        document = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=0)
        for chunk in text_splitter.split_documents(document):
            store.add_documents([chunk])
        print(f"Successfully loaded {file_path} into the database")
    except Exception as e:
        print(f"Error loading file {file_path}: {str(e)}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Load documents into vector database',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Add arguments
    parser.add_argument(
        '--file', 
        help='Path to single text file'
    )
    parser.add_argument(
        '--directory', 
        help='Path to directory containing text files'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=512,
        help='Size of text chunks (default: 512)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Verify that at least one argument is provided
    if not args.file and not args.directory:
        parser.print_help()
        print("\nError: Please provide either --file or --directory argument")
        return
    
    # Setup connections
    store = setup_connections()
    if not store:
        return
    
    # Process files based on arguments
    if args.file:
        load_file_to_db(args.file, store)
    elif args.directory:
        directory = Path(args.directory)
        if not directory.exists():
            print(f"Error: Directory {args.directory} does not exist")
            return
            
        txt_files = list(directory.glob("*.txt"))
        if not txt_files:
            print(f"No text files found in {args.directory}")
            return
            
        print(f"Found {len(txt_files)} text files")
        for txt_file in txt_files:
            load_file_to_db(str(txt_file), store)

if __name__ == "__main__":
    main()
