from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from app.utils.database_operation import DatabaseOperation
from app.utils.elastic_handler import ElasticHandler
from app.utils.openai_embedding import OpenAIEmbedding
from app.utils.prompt import Prompt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            static_folder='app/static',
            template_folder='app/templates')
CORS(app)

# Initialize components
db_operation = DatabaseOperation()
elastic_handler = ElasticHandler()
openai_embedding = OpenAIEmbedding()
prompt_generator = Prompt()

# Authentication middleware
def authenticate(request):
    auth_token = request.headers.get('Authorization')
    expected_token = "Bearer T#nde0o43kl^4opkSD"
    
    if not auth_token or auth_token != expected_token:
        return False
    return True

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/tenders_search', methods=['POST'])
def tenders_search():
    # Authenticate request
    if not authenticate(request):
        return jsonify({"error": "Unauthorized access"}), 401
    
    try:
        data = request.json
        query = data.get('query', '')
        result_columns = data.get('result_columns', [])
        country_code = data.get('country_code')
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        page = data.get('page', 1)
        page_size = data.get('page_size', 10)
        
        # Generate categorization prompt
        categorization_prompt = prompt_generator.generate_categorization_prompt(query)
        
        # Get categorized response from OpenAI
        categorized_response = openai_embedding.get_categorized_response(categorization_prompt)
        
        # Generate embedding for the query
        query_embedding = openai_embedding.generate_embedding(categorized_response)
        
        # Search in Elasticsearch
        search_results = elastic_handler.search_tenders(
            query_embedding, 
            result_columns, 
            country_code, 
            date_from, 
            date_to, 
            page, 
            page_size
        )
        
        return jsonify(search_results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/customer_feedback', methods=['POST'])
def customer_feedback():
    # Authenticate request
    if not authenticate(request):
        return jsonify({"error": "Unauthorized access"}), 401
    
    try:
        data = request.json
        query_id = data.get('query_id')
        search_query = data.get('search_query')
        feedback_list = data.get('feedback_list', [])
        
        # Validate required fields
        if not query_id or not search_query or not feedback_list:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Validate feedback list format
        for feedback in feedback_list:
            if 'ID' not in feedback or 'feedback' not in feedback:
                return jsonify({"error": "Invalid feedback format"}), 400
        
        # Store feedback in database
        db_operation.store_feedback(query_id, search_query, feedback_list)
        
        return jsonify({"success": True, "message": "Feedback submitted successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tenders_search_with_feedback', methods=['POST'])
def tenders_search_with_feedback():
    # Authenticate request
    if not authenticate(request):
        return jsonify({"error": "Unauthorized access"}), 401
    
    try:
        data = request.json
        query_id = data.get('query_id')
        query = data.get('query', '')
        result_columns = data.get('result_columns', [])
        
        # Fetch feedback from database
        positive_feedback, negative_feedback = db_operation.get_feedback_by_query_id(query_id)
        
        # Generate embeddings for query and feedback
        final_embedding = None
        
        if query:
            # Generate categorization prompt
            categorization_prompt = prompt_generator.generate_categorization_prompt(query)
            
            # Get categorized response from OpenAI
            categorized_response = openai_embedding.get_categorized_response(categorization_prompt)
            
            # Generate embedding for the query
            query_embedding = openai_embedding.generate_embedding(categorized_response)
            final_embedding = query_embedding
        
        # Combine with feedback embeddings (alpha=1.0, beta=0.5)
        final_embedding = openai_embedding.combine_with_feedback(
            final_embedding, 
            positive_feedback, 
            negative_feedback, 
            alpha=1.0, 
            beta=0.5
        )
        
        # Search with combined embedding
        search_results = elastic_handler.search_tenders(
            final_embedding, 
            result_columns
        )
        
        return jsonify(search_results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tenders_search_by_feedback', methods=['POST'])
def tenders_search_by_feedback():
    # Authenticate request
    if not authenticate(request):
        return jsonify({"error": "Unauthorized access"}), 401
    
    try:
        data = request.json
        client_id = data.get('client_id')
        result_columns = data.get('result_columns', [])
        
        # Fetch feedback from database based on client ID
        positive_feedback, negative_feedback = db_operation.get_feedback_by_client_id(client_id)
        
        # Generate final embedding from feedback
        final_embedding = openai_embedding.combine_feedback_only(
            positive_feedback, 
            negative_feedback, 
            beta=0.5
        )
        
        # Search with feedback embedding
        search_results = elastic_handler.search_tenders(
            final_embedding, 
            result_columns
        )
        
        return jsonify(search_results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 