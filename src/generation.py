import nest_asyncio
from openai import OpenAI
import os

nest_asyncio.apply()
from dotenv import load_dotenv
load_dotenv()  

openai_api_key= os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

system_prompt = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know - I am an Insurance Query Assistant. Use five sentences when you have enough content else give three sentences and keep the answer concise.
Provide the answer and References!
"""

class Generator:
    def __init__(self, data_indexer, community_summarizer):
        self.indexer = data_indexer
        self.summarizer = community_summarizer

    def get_entities(self, query):
        """
        Retrieve relevant entities from the knowledge graph based on the query.
        
        Args:
            query: The user's question/query
            
        Returns:
            list: List of entity objects from the Neo4j database that are relevant to the query
        """
        entities = self.indexer.retrieve(query)  #Uses DataIndexer to get relevant nodes from Neo4j
        return entities

    def get_community_summaries(self, query):
        """
        Get summaries for all related entities and their communities.
        
        Args:
            query: The user's query
            
        Process:
        1. Get relevant entities for the query
        2. For each entity, get summaries from its community
        3. Combine all summaries into a set to remove duplicates
        
        Returns:
            set: A set of unique summaries related to the query
        """
        #Get entities related to the query
        entities = self.get_entities(query)
        #print(entities) 
        
        all_summaries = set()
        
        # For each entity, get its community summaries
        for entity in entities:
            # Get summaries for this entity from the community summarizer
            summaries = self.summarizer.get_summaries_for_entity(entity.name)
            # Add these summaries to our set (duplicates automatically removed)
            all_summaries.update(summaries)

        return all_summaries
    
    def generate(self, query):
        """
        Generate a response to the query using retrieved context and GPT-4.
        
        Args:
            query (str): The user's query
            
        Process:
        1. Get community summaries for context
        2. Combine summaries into a single context string
        3. Use GPT-4 to generate a response based on the context
        
        Returns:
            str: The generated response from GPT-4
        """
        # Get relevant summaries for context
        summaries = self.get_community_summaries(query)
        
        context = "\n\n".join(summaries)

        # Generate response using GPT-4
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4 mini model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"CONTEXT: {context}\n\nQUERY: {query}"},
            ],
        )

        return response.choices[0].message.content


if __name__ == '__main__':
    
    from graph_communities import CommunitySummarizer
    from data_index import DataIndexer

    # Initialize components
    summarizer = CommunitySummarizer()  
    indexer = DataIndexer()             
    summarizer.load()                   

    # Create generator 
    generator = Generator(indexer, summarizer)

    response = generator.generate('different types of Insurance coverages?')
    print(response)