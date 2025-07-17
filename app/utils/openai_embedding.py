import os
import openai
import numpy as np

class OpenAIEmbedding:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4o-mini-2024-07-18"
        openai.api_key = self.api_key
    
    def get_categorized_response(self, prompt):
        """Get a categorized response from OpenAI based on the prompt"""
        try:
            # Create a chat completion
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that categorizes tender queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            # Return the content of the response
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error getting categorized response: {e}")
            return ""
    
    def generate_embedding(self, text):
        """Generate a 1536-dimensional embedding for the given text"""
        try:
            # Create an embedding
            response = openai.embeddings.create(
                input=[text],
                model="text-embedding-ada-002"  # This model outputs 1536-dimensional vectors
            )
            
            # Return the embedding vector
            return response.data[0].embedding
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0] * 1536  # Return a zero vector in case of error
    
    def combine_with_feedback(self, query_embedding, positive_embeddings, negative_embeddings, alpha=1.0, beta=0.5):
        """Combine query embedding with feedback embeddings using weighted sum"""
        try:
            # If no query embedding, start with a zero vector
            if query_embedding is None:
                query_embedding = [0] * 1536
            
            # Convert to numpy arrays for easier math
            query_embedding = np.array(query_embedding)
            
            # Process positive feedback
            positive_vector = np.zeros(1536)
            if positive_embeddings:
                for embedding in positive_embeddings:
                    positive_vector += np.array(embedding)
                positive_vector = positive_vector / len(positive_embeddings)
            
            # Process negative feedback
            negative_vector = np.zeros(1536)
            if negative_embeddings:
                for embedding in negative_embeddings:
                    negative_vector += np.array(embedding)
                negative_vector = negative_vector / len(negative_embeddings)
            
            # Combine embeddings: query * alpha + positive - negative * beta
            combined_embedding = (query_embedding * alpha) + positive_vector - (negative_vector * beta)
            
            # Normalize the combined embedding
            norm = np.linalg.norm(combined_embedding)
            if norm > 0:
                combined_embedding = combined_embedding / norm
            
            return combined_embedding.tolist()
            
        except Exception as e:
            print(f"Error combining embeddings: {e}")
            return query_embedding.tolist() if query_embedding is not None else [0] * 1536
    
    def combine_feedback_only(self, positive_embeddings, negative_embeddings, beta=0.5):
        """Combine only feedback embeddings (no query)"""
        try:
            # Process positive feedback
            positive_vector = np.zeros(1536)
            if positive_embeddings:
                for embedding in positive_embeddings:
                    positive_vector += np.array(embedding)
                positive_vector = positive_vector / len(positive_embeddings)
            
            # Process negative feedback
            negative_vector = np.zeros(1536)
            if negative_embeddings:
                for embedding in negative_embeddings:
                    negative_vector += np.array(embedding)
                negative_vector = negative_vector / len(negative_embeddings)
            
            # Combine embeddings: positive - negative * beta
            combined_embedding = positive_vector - (negative_vector * beta)
            
            # Normalize the combined embedding
            norm = np.linalg.norm(combined_embedding)
            if norm > 0:
                combined_embedding = combined_embedding / norm
            
            return combined_embedding.tolist()
            
        except Exception as e:
            print(f"Error combining feedback embeddings: {e}")
            return [0] * 1536 