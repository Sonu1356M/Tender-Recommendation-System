import pymysql
import os
import json

class DatabaseOperation:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '')
        self.database = os.getenv('MYSQL_DATABASE', 'tender_db')
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.Cursor
            )
            self.cursor = self.connection.cursor()
            return True
        except pymysql.MySQLError as err:
            print(f"Error connecting to MySQL: {err}")
            return False

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def store_feedback(self, query_id, search_query, feedback_list):
        """Store customer feedback in the database"""
        try:
            if not self.connect():
                raise Exception("Failed to connect to database")

            # Insert query information
            query = """
            INSERT INTO search_queries (query_id, search_query) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE search_query = %s
            """
            self.cursor.execute(query, (query_id, search_query, search_query))

            # Insert feedback items
            for feedback in feedback_list:
                tender_id = feedback['ID']
                feedback_value = feedback['feedback']

                query = """
                INSERT INTO feedback (query_id, tender_id, feedback_value) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE feedback_value = %s
                """
                self.cursor.execute(query, (query_id, tender_id, feedback_value, feedback_value))

            self.connection.commit()
            return True

        except Exception as e:
            if self.connection:
                self.connection.rollback()
            raise e
        finally:
            self.disconnect()

    def get_feedback_by_query_id(self, query_id):
        """Get positive and negative feedback for a query"""
        try:
            if not self.connect():
                raise Exception("Failed to connect to database")

            positive_embeddings = []
            negative_embeddings = []

            # Get positive feedback
            query = """
            SELECT t.tender_embedding 
            FROM feedback f
            JOIN tenders t ON f.tender_id = t.id
            WHERE f.query_id = %s AND f.feedback_value = 'positive'
            """
            self.cursor.execute(query, (query_id,))
            for row in self.cursor.fetchall():
                embedding = json.loads(row[0]) if row[0] else []
                if embedding:
                    positive_embeddings.append(embedding)

            # Get negative feedback
            query = """
            SELECT t.tender_embedding 
            FROM feedback f
            JOIN tenders t ON f.tender_id = t.id
            WHERE f.query_id = %s AND f.feedback_value = 'negative'
            """
            self.cursor.execute(query, (query_id,))
            for row in self.cursor.fetchall():
                embedding = json.loads(row[0]) if row[0] else []
                if embedding:
                    negative_embeddings.append(embedding)

            return positive_embeddings, negative_embeddings

        except Exception as e:
            raise e
        finally:
            self.disconnect()

    def get_feedback_by_client_id(self, client_id):
        """Get positive and negative feedback for a client"""
        try:
            if not self.connect():
                raise Exception("Failed to connect to database")

            positive_embeddings = []
            negative_embeddings = []

            # Get positive feedback
            query = """
            SELECT t.tender_embedding 
            FROM feedback f
            JOIN tenders t ON f.tender_id = t.id
            JOIN search_queries sq ON f.query_id = sq.query_id
            WHERE sq.client_id = %s AND f.feedback_value = 'positive'
            """
            self.cursor.execute(query, (client_id,))
            for row in self.cursor.fetchall():
                embedding = json.loads(row[0]) if row[0] else []
                if embedding:
                    positive_embeddings.append(embedding)

            # Get negative feedback
            query = """
            SELECT t.tender_embedding 
            FROM feedback f
            JOIN tenders t ON f.tender_id = t.id
            JOIN search_queries sq ON f.query_id = sq.query_id
            WHERE sq.client_id = %s AND f.feedback_value = 'negative'
            """
            self.cursor.execute(query, (client_id,))
            for row in self.cursor.fetchall():
                embedding = json.loads(row[0]) if row[0] else []
                if embedding:
                    negative_embeddings.append(embedding)

            return positive_embeddings, negative_embeddings

        except Exception as e:
            raise e
        finally:
            self.disconnect()

    def initialize_database(self):
        """Initialize database tables if they don't exist"""
        try:
            if not self.connect():
                raise Exception("Failed to connect to database")

            # Create search_queries table
            query = """
            CREATE TABLE IF NOT EXISTS search_queries (
                query_id VARCHAR(36) PRIMARY KEY,
                client_id VARCHAR(36),
                search_query TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(query)

            # Create feedback table
            query = """
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                query_id VARCHAR(36),
                tender_id VARCHAR(36),
                feedback_value ENUM('positive', 'negative'),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_feedback (query_id, tender_id)
            )
            """
            self.cursor.execute(query)

            # Create tenders table
            query = """
            CREATE TABLE IF NOT EXISTS tenders (
                id VARCHAR(36) PRIMARY KEY,
                tender_title TEXT,
                tender_description TEXT,
                tender_embedding JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(query)

            self.connection.commit()
            return True

        except Exception as e:
            if self.connection:
                self.connection.rollback()
            raise e
        finally:
            self.disconnect()
