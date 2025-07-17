import os
from dotenv import load_dotenv
from app.utils.database_operation import DatabaseOperation

# Load environment variables
load_dotenv()

def init_database():
    """Initialize the database with required tables"""
    try:
        # Create an instance of DatabaseOperation
        db_op = DatabaseOperation()
        
        # Initialize database tables
        success = db_op.initialize_database()
        
        if success:
            print("Database initialized successfully!")
        else:
            print("Failed to initialize database.")
            
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_database() 