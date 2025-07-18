# Tender-Recommendation-System
# Tender On Time

A Flask-based web application for tender searching with feedback-based relevance improvement.

## Overview

Tender On Time is an AI-powered tender search platform developed by xAI that enables efficient searching of tender opportunities with:

- Text-based semantic search using OpenAI embeddings
- Country and date range filtering
- Feedback incorporation for improved relevance
- Secure API access with token authentication

## Features

- **Vector-based Search**: Uses Elasticsearch with dense vectors for high-quality similarity matching
- **Natural Language Processing**: Leverages OpenAI's gpt-4o-mini-2024-07-18 model for query categorization
- **User Feedback**: Incorporates positive and negative feedback to refine search results
- **Responsive UI**: Clean, modern interface with pagination and filtering

## System Architecture

- **Frontend**: HTML/CSS/JavaScript with Bootstrap 5
- **Backend**: Flask (Python)
- **Database**: MySQL for persistent storage
- **Search Engine**: Elasticsearch with vector search capabilities
- **AI/ML**: OpenAI for embeddings and natural language processing

## Prerequisites
- HTML,CSS,JAVASCRIPT,BOOSTRAP
- Python 3.8+
- MySQL 8.0+
- Elasticsearch 8.0+
- OpenAI API key

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd tender-on-time
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the variables in `.env` with your settings

5. Initialize the database:
   ```
   # First create the MySQL database
   mysql -u root -p
   CREATE DATABASE tender_db;
   exit;
   
   # Then initialize tables
   python -c "from app.utils.database_operation import DatabaseOperation; DatabaseOperation().initialize_database()"
   ```

6. Start Elasticsearch:
   Make sure Elasticsearch is running on your system or in a Docker container.

7. Run the application:
   ```
   flask run --host=0.0.0.0
   ```

## API Endpoints

### 1. Tender Search
- **URL**: `/tenders_search`
- **Method**: `POST`
- **Auth**: Bearer token
- **Body**:
  ```json
  {
    "query": "construction equipment for highways",
    "result_columns": ["ID", "eTitle", "eDescription"],
    "country_code": "US",
    "date_from": "2023-01-01",
    "date_to": "2023-12-31",
    "page": 1,
    "page_size": 10
  }
  ```

### 2. Customer Feedback
- **URL**: `/customer_feedback`
- **Method**: `POST`
- **Auth**: Bearer token
- **Body**:
  ```json
  {
    "query_id": "550e8400-e29b-41d4-a716-446655440000",
    "search_query": "construction equipment",
    "feedback_list": [
      {"ID": "tender123", "feedback": "positive"},
      {"ID": "tender456", "feedback": "negative"}
    ]
  }
  ```

### 3. Search with Feedback
- **URL**: `/tenders_search_with_feedback`
- **Method**: `POST`
- **Auth**: Bearer token
- **Body**:
  ```json
  {
    "query_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "construction equipment",
    "result_columns": ["ID", "eTitle", "eDescription"]
  }
  ```

### 4. Search by Feedback Only
- **URL**: `/tenders_search_by_feedback`
- **Method**: `POST`
- **Auth**: Bearer token
- **Body**:
  ```json
  {
    "client_id": "client123",
    "result_columns": ["ID", "eTitle", "eDescription"]
  }
  ```

## Security

All API endpoints are protected with token-based authentication. Include the following header in all requests:
```
Authorization: Bearer T#nde0o43kl^4opkSD
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Proprietary - All rights reserved

## Contact

xAI - support@xai-company.com 
