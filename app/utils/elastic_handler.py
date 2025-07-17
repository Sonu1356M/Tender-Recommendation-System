from elasticsearch import Elasticsearch
import os
import json
import math

class ElasticHandler:
    def __init__(self):
        self.es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
        self.es_port = os.getenv('ELASTICSEARCH_PORT', '9200')
        self.es_user = os.getenv('ELASTICSEARCH_USER', '')
        self.es_password = os.getenv('ELASTICSEARCH_PASSWORD', '')
        self.index_name = os.getenv('ELASTICSEARCH_INDEX', 'tenders')
        
        # Initialize Elasticsearch client
        if self.es_user and self.es_password:
            self.es = Elasticsearch(
                [f"http://{self.es_host}:{self.es_port}"],
                basic_auth=(self.es_user, self.es_password)
            )
        else:
            self.es = Elasticsearch([f"http://{self.es_host}:{self.es_port}"])
    
    def create_index(self):
        """Create the Elasticsearch index with mappings if it doesn't exist"""
        try:
            if not self.es.indices.exists(index=self.index_name):
                # Define index mappings
                mappings = {
                    "mappings": {
                        "properties": {
                            "ID": {"type": "keyword"},
                            "eMainCategoryName1": {"type": "text"},
                            "eMainCategoryName2": {"type": "text"},
                            "eMainCategoryName3": {"type": "text"},
                            "ePublisherCountryName": {"type": "keyword"},
                            "ePublicationDate": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"},
                            "eTitle": {"type": "text"},
                            "eDescription": {"type": "text"},
                            "eDeadlineDate": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"},
                            # Dense vectors for embeddings
                            "eMainCategoryName1_vector": {
                                "type": "dense_vector",
                                "dims": 1536,
                                "index": True,
                                "similarity": "cosine"
                            },
                            "eMainCategoryName2_vector": {
                                "type": "dense_vector",
                                "dims": 1536,
                                "index": True,
                                "similarity": "cosine"
                            },
                            "eMainCategoryName3_vector": {
                                "type": "dense_vector",
                                "dims": 1536,
                                "index": True,
                                "similarity": "cosine"
                            }
                        }
                    },
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                    }
                }
                
                # Create the index
                self.es.indices.create(index=self.index_name, body=mappings)
                return True
            return False
            
        except Exception as e:
            print(f"Error creating index: {e}")
            return False
    
    def index_tender(self, tender_data):
        """Index a tender document with its embeddings"""
        try:
            # Make sure the index exists
            self.create_index()
            
            # Index the document
            self.es.index(
                index=self.index_name,
                id=tender_data['ID'],
                document=tender_data
            )
            return True
            
        except Exception as e:
            print(f"Error indexing tender: {e}")
            return False
    
    def search_tenders(self, query_embedding, result_columns=None, country_code=None, date_from=None, date_to=None, page=1, page_size=10):
        """Search for tenders using vector similarity and filters"""
        try:
            # Default result columns if none provided
            if not result_columns:
                result_columns = ["ID", "eTitle", "eDescription", "ePublisherCountryName", "ePublicationDate", "eDeadlineDate"]
            
            # Build the query
            query = {
                "size": page_size,
                "from": (page - 1) * page_size,
                "query": {
                    "function_score": {
                        "query": {
                            "bool": {
                                "must": [],
                                "filter": []
                            }
                        },
                        "functions": [
                            {
                                "script_score": {
                                    "script": {
                                        "source": """
                                        double max_score = 0;
                                        if (doc.containsKey('eMainCategoryName1_vector') && !doc['eMainCategoryName1_vector'].empty) {
                                            double score = cosineSimilarity(params.query_vector, 'eMainCategoryName1_vector');
                                            max_score = Math.max(max_score, score);
                                        }
                                        if (doc.containsKey('eMainCategoryName2_vector') && !doc['eMainCategoryName2_vector'].empty) {
                                            double score = cosineSimilarity(params.query_vector, 'eMainCategoryName2_vector');
                                            max_score = Math.max(max_score, score);
                                        }
                                        if (doc.containsKey('eMainCategoryName3_vector') && !doc['eMainCategoryName3_vector'].empty) {
                                            double score = cosineSimilarity(params.query_vector, 'eMainCategoryName3_vector');
                                            max_score = Math.max(max_score, score);
                                        }
                                        return max_score;
                                        """,
                                        "params": {
                                            "query_vector": query_embedding
                                        }
                                    }
                                }
                            }
                        ],
                        "boost_mode": "replace"
                    }
                },
                "_source": result_columns
            }
            
            # Add country filter if provided
            if country_code:
                query["query"]["function_score"]["query"]["bool"]["filter"].append({
                    "term": {"ePublisherCountryName": country_code}
                })
            
            # Add date range filter if provided
            if date_from or date_to:
                date_filter = {"range": {"ePublicationDate": {}}}
                if date_from:
                    date_filter["range"]["ePublicationDate"]["gte"] = date_from
                if date_to:
                    date_filter["range"]["ePublicationDate"]["lte"] = date_to
                
                query["query"]["function_score"]["query"]["bool"]["filter"].append(date_filter)
            
            # Execute the search
            response = self.es.search(index=self.index_name, body=query)
            
            # Format the results
            hits = response["hits"]["hits"]
            total_results = response["hits"]["total"]["value"]
            total_pages = math.ceil(total_results / page_size)
            
            results = []
            for hit in hits:
                result = hit["_source"]
                result["_score"] = hit["_score"]
                results.append(result)
            
            # Return results with pagination metadata
            return {
                "tenders": results,
                "pagination": {
                    "total_results": total_results,
                    "total_pages": total_pages,
                    "current_page": page,
                    "page_size": page_size
                }
            }
            
        except Exception as e:
            print(f"Error searching tenders: {e}")
            return {"tenders": [], "pagination": {"total_results": 0, "total_pages": 0, "current_page": page, "page_size": page_size}}
    
    def delete_tender(self, tender_id):
        """Delete a tender document from the index"""
        try:
            self.es.delete(index=self.index_name, id=tender_id)
            return True
            
        except Exception as e:
            print(f"Error deleting tender: {e}")
            return False
    
    def bulk_index_tenders(self, tenders_data):
        """Bulk index multiple tender documents"""
        try:
            # Make sure the index exists
            self.create_index()
            
            # Prepare bulk request
            bulk_data = []
            for tender in tenders_data:
                bulk_data.append({"index": {"_index": self.index_name, "_id": tender["ID"]}})
                bulk_data.append(tender)
            
            # Execute bulk request
            if bulk_data:
                self.es.bulk(body=bulk_data, refresh=True)
            
            return True
            
        except Exception as e:
            print(f"Error bulk indexing tenders: {e}")
            return False 