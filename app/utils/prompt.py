class Prompt:
    def __init__(self):
        pass
    
    def generate_categorization_prompt(self, query):
        """Generate a prompt for categorizing a tender search query"""
        
        prompt = f"""
        You are tasked with analyzing the following tender search query and identifying relevant categories, industries, and technical terms. 
        
        Query: "{query}"
        
        Please provide a concise analysis of this query by:
        1. Identifying the main industry sector(s) this query relates to
        2. Listing any specific technical requirements mentioned
        3. Identifying geographical preferences if any
        4. Noting any timeframe requirements
        5. Highlighting any specific qualifications or certifications needed
        
        Format your response as a structured analysis without introducing new information not present in the query.
        """
        
        return prompt
    
    def generate_feedback_analysis_prompt(self, search_query, positive_feedback, negative_feedback):
        """Generate a prompt for analyzing user feedback on search results"""
        
        # Format positive feedback items
        positive_items = ""
        for item in positive_feedback:
            positive_items += f"- ID: {item['ID']}, Title: {item['eTitle']}\n"
        
        # Format negative feedback items
        negative_items = ""
        for item in negative_feedback:
            negative_items += f"- ID: {item['ID']}, Title: {item['eTitle']}\n"
        
        prompt = f"""
        You are analyzing feedback on tender search results to improve future search quality.
        
        Original Search Query: "{search_query}"
        
        Positive Feedback (items the user found relevant):
        {positive_items if positive_items else "None"}
        
        Negative Feedback (items the user found irrelevant):
        {negative_items if negative_items else "None"}
        
        Based on this feedback, please:
        1. Identify common themes among positively rated items
        2. Identify why negatively rated items might have been unsuitable
        3. Suggest how the original query could be modified to better match the user's actual intent
        
        Provide a concise analysis that could help improve the relevance of future search results.
        """
        
        return prompt
    
    def generate_tender_embedding_prompt(self, tender):
        """Generate a prompt for creating a rich embedding for a tender"""
        
        # Extract key fields from the tender
        title = tender.get('eTitle', '')
        description = tender.get('eDescription', '')
        category1 = tender.get('eMainCategoryName1', '')
        category2 = tender.get('eMainCategoryName2', '')
        category3 = tender.get('eMainCategoryName3', '')
        country = tender.get('ePublisherCountryName', '')
        
        prompt = f"""
        The following is a tender announcement that needs to be analyzed for embedding purposes.
        
        Title: {title}
        
        Description: {description}
        
        Primary Category: {category1}
        Secondary Category: {category2}
        Tertiary Category: {category3}
        
        Country: {country}
        
        Please provide a rich, detailed analysis of this tender, focusing on:
        1. The core industry sector(s) this relates to
        2. Specific technical elements or requirements
        3. Geographical considerations
        4. Any special qualifications or expertise needed
        5. Keywords that best represent this tender's focus
        
        Your analysis should be comprehensive and focus on the practical details that would help match this tender with relevant searches.
        """
        
        return prompt 