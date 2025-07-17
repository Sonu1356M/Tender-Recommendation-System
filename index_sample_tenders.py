import os
import json
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.utils.elastic_handler import ElasticHandler
from app.utils.openai_embedding import OpenAIEmbedding
from app.utils.prompt import Prompt

# Load environment variables
load_dotenv()

def generate_sample_tenders():
    """Generate sample tender data for testing"""
    
    sample_tenders = [
        {
            "ID": str(uuid.uuid4()),
            "eTitle": "Supply of Construction Equipment for Highway Project",
            "eDescription": "Procurement of heavy machinery including excavators, bulldozers, and asphalt pavers for the national highway construction project.",
            "eMainCategoryName1": "Construction Equipment",
            "eMainCategoryName2": "Heavy Machinery",
            "eMainCategoryName3": "Transportation Infrastructure",
            "ePublisherCountryName": "US",
            "ePublicationDate": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "eDeadlineDate": (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d")
        },
        {
            "ID": str(uuid.uuid4()),
            "eTitle": "IT Services for Government Healthcare System",
            "eDescription": "Provision of comprehensive IT services including software development, maintenance, and technical support for the national healthcare management system.",
            "eMainCategoryName1": "Information Technology",
            "eMainCategoryName2": "Healthcare IT",
            "eMainCategoryName3": "Software Development",
            "ePublisherCountryName": "GB",
            "ePublicationDate": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
            "eDeadlineDate": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
        },
        {
            "ID": str(uuid.uuid4()),
            "eTitle": "Educational Materials for Public Schools",
            "eDescription": "Supply of textbooks, teaching aids, and educational software for primary and secondary public schools nationwide.",
            "eMainCategoryName1": "Education",
            "eMainCategoryName2": "Teaching Materials",
            "eMainCategoryName3": "Educational Technology",
            "ePublisherCountryName": "CA",
            "ePublicationDate": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
            "eDeadlineDate": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        },
        {
            "ID": str(uuid.uuid4()),
            "eTitle": "Medical Equipment for New Hospital",
            "eDescription": "Procurement of advanced medical equipment including MRI machines, CT scanners, and laboratory equipment for the newly constructed regional hospital.",
            "eMainCategoryName1": "Healthcare",
            "eMainCategoryName2": "Medical Equipment",
            "eMainCategoryName3": "Diagnostic Imaging",
            "ePublisherCountryName": "DE",
            "ePublicationDate": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "eDeadlineDate": (datetime.now() + timedelta(days=23)).strftime("%Y-%m-%d")
        },
        {
            "ID": str(uuid.uuid4()),
            "eTitle": "Renewable Energy Solutions for Government Buildings",
            "eDescription": "Installation of solar panels, wind turbines, and energy storage systems for government buildings to reduce carbon footprint and energy costs.",
            "eMainCategoryName1": "Energy",
            "eMainCategoryName2": "Renewable Energy",
            "eMainCategoryName3": "Green Building",
            "ePublisherCountryName": "FR",
            "ePublicationDate": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "eDeadlineDate": (datetime.now() + timedelta(days=27)).strftime("%Y-%m-%d")
        }
    ]
    
    return sample_tenders

def generate_embeddings_for_tenders(tenders):
    """Generate embeddings for the tender categories"""
    
    openai_embedding = OpenAIEmbedding()
    prompt_generator = Prompt()
    
    for tender in tenders:
        # Create category prompts
        if tender.get("eMainCategoryName1"):
            category1_prompt = prompt_generator.generate_tender_embedding_prompt({
                "eTitle": tender["eTitle"],
                "eDescription": tender["eDescription"],
                "eMainCategoryName1": tender["eMainCategoryName1"]
            })
            tender["eMainCategoryName1_vector"] = openai_embedding.generate_embedding(category1_prompt)
        
        if tender.get("eMainCategoryName2"):
            category2_prompt = prompt_generator.generate_tender_embedding_prompt({
                "eTitle": tender["eTitle"],
                "eDescription": tender["eDescription"],
                "eMainCategoryName2": tender["eMainCategoryName2"]
            })
            tender["eMainCategoryName2_vector"] = openai_embedding.generate_embedding(category2_prompt)
        
        if tender.get("eMainCategoryName3"):
            category3_prompt = prompt_generator.generate_tender_embedding_prompt({
                "eTitle": tender["eTitle"],
                "eDescription": tender["eDescription"],
                "eMainCategoryName3": tender["eMainCategoryName3"]
            })
            tender["eMainCategoryName3_vector"] = openai_embedding.generate_embedding(category3_prompt)
    
    return tenders

def index_tenders():
    """Index sample tender data in Elasticsearch"""
    try:
        # Generate sample tenders
        tenders = generate_sample_tenders()
        
        # Generate embeddings for the tenders
        tenders_with_embeddings = generate_embeddings_for_tenders(tenders)
        
        # Create ElasticHandler instance
        elastic_handler = ElasticHandler()
        
        # Create the index if it doesn't exist
        elastic_handler.create_index()
        
        # Bulk index the tenders
        success = elastic_handler.bulk_index_tenders(tenders_with_embeddings)
        
        if success:
            print(f"Successfully indexed {len(tenders)} sample tenders.")
        else:
            print("Failed to index sample tenders.")
            
    except Exception as e:
        print(f"Error indexing sample tenders: {e}")

if __name__ == "__main__":
    index_tenders() 