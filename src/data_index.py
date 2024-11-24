from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core.vector_stores.types import VectorStoreQuery
from openai import OpenAI
from data_models import EntityModel
import os
from dotenv import load_dotenv
import logging
from typing import List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# System prompt
system_prompt = """
Given some initial query, generate synonyms or related keywords up to 10 in total, considering possible cases of pluralization, common expressions, etc.
The resulting list should be a list of entity names used to index a graph database.
"""

class DataIndexer:
    def __init__(self):
        # Get credentials from environment variables
        self.neo4j_uri = os.getenv('NEO4J_URI')
        self.neo4j_username = os.getenv('NEO4J_USERNAME', 'neo4j')
        self.neo4j_password = os.getenv('NEO4J_PASSWORD')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

        # Initialize OpenAI client
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found")
        self.client = OpenAI(api_key=self.openai_api_key)

        # Initialize Neo4j connection
        try:
            self.graph_store = Neo4jPropertyGraphStore(
                username=self.neo4j_username,
                password=self.neo4j_password,
                url=self.neo4j_uri,
            )
            logger.info("Successfully connected to Neo4j Aura")
            self._verify_connection()
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def _verify_connection(self):
        """
           Verify Neo4j connection and log database state
        """
        try:
            # Use graph store to verify connection
            schema = self.graph_store.get_schema()
            logger.info(f"Connected to Neo4j Aura - Schema: {schema}")
        except Exception as e:
            logger.error(f"Connection verification failed: {e}")
            raise

    def get_embeddings(self, texts: List[str]):
        """  
           Get embeddings from OpenAI
        """
        try:
            data = self.client.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            ).data
            embeddings = [d.embedding for d in data]
            
            return embeddings
        except Exception as e:
            raise

    def vector_search(self, query: str, similarity_top_k=10):
        """ 
           Perform vector similarity search 
        """

        try:
            logger.info(f"Performing vector search for: {query}")
            # Get query embedding
            embedding = self.get_embeddings([query])[0]
            
            # Create vector store query
            vector_query = VectorStoreQuery(
                query_embedding=embedding,
                similarity_top_k=similarity_top_k
            )
            
            # Execute search
            results = self.graph_store.vector_query(vector_query)
            nodes = results[0] if results else []
            
            return nodes
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []

    def get_synonyms(self, query: str):
        """
           Generate synonyms using GPT-4
        """

        try:
            
            completion = self.client.chat.completions.create(
                model="gpt-4",  
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"QUERY: {query}"}
                ]
            )
            
            # Extract keywords from response
            response_text = completion.choices[0].message.content
            keywords = [k.strip().capitalize() for k in response_text.split(',')]
            
            return keywords
        except Exception as e:
            logger.error(f"Error generating synonyms: {e}")
            return []

    def keyword_search(self, query: str):
        """ 
           Perform keyword-based search 
        """

        try:
            keywords = self.get_synonyms(query)
            if not keywords:
                return []
            
            nodes = self.graph_store.get(ids=keywords)
            return nodes
        except Exception as e:
            logger.error(f"Keyword search error: {e}")
            return []

    def get_related_nodes(self, nodes):
        """ 
           Get related nodes from the graph 
        """
        try:
            if not nodes:
                return []
                
            triplets = self.graph_store.get_rel_map(nodes)
            related_nodes = []
            
            for triplet in triplets:
                related_nodes.extend([triplet[0], triplet[-1]])
            return related_nodes
        except Exception as e:
            logger.error(f"Error getting related nodes: {e}")
            return []

    def retrieve(self, query: str):
        """
           Retrieve nodes using both vector and keyword search
        """
        try:
            logger.info(f"Starting retrieval for query: {query}")
            
            # Get nodes from both methods
            nodes_from_vector = self.vector_search(query)
            nodes_from_keywords = self.keyword_search(query)
            
            # Get related nodes
            all_nodes = nodes_from_vector + nodes_from_keywords
            nodes = self.get_related_nodes(all_nodes)
            
            # Remove duplicates
            nodes_dict = {n.name: n for n in nodes}
            final_nodes = list(nodes_dict.values())
            return final_nodes
        except Exception as e:
            logger.error(f"Error in retrieve: {e}")
            return []

    def insert_data(self, entities, relationships):
        """
           Insert data into Neo4j Aura
        """

        try:
            # Generate embeddings
            texts_index = [str(entity) for entity in entities]
            embeddings = self.get_embeddings(texts_index)
            
            # Add embeddings to entities
            for entity, embedding in zip(entities, embeddings):
                entity.embedding = embedding
            
            # Insert into graph store
            self.graph_store.upsert_nodes(entities)
            self.graph_store.upsert_relations(relationships)
            
            # Refresh schema if needed
            if self.graph_store.supports_structured_queries:
                self.graph_store.get_schema(refresh=True)
                
            logger.info("Successfully inserted data")
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            raise