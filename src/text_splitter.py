from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  

# Get Environment variables
openai_api_key= os.getenv('OPENAI_API_KEY')

class TextSplitter:
    def load_data(self, directory="./book"):
        """
        Load and split documents into semantic chunks using LlamaIndex.
        
        Args:
            directory (str): Path to directory containing documents, defaults to "./book"
        
        Process:
        1. Loads all documents from the specified directory
        2. Initialize OpenAI embedding model for semantic analysis
        3. Creates semantic splitter with specific thresholds
        4. Splits documents into semantic chunks
        
        Returns:
            list: List of text nodes containing document chunks
        """
        #Load all documents from the specified folder
        docs = SimpleDirectoryReader(directory).load_data()
        
        # Initialize OpenAI embedding model for semantic analysis
        embed_model = OpenAIEmbedding(api_key=openai_api_key)
        
        # Initialize semantic splitter with:
        #       buffer_size=1: Minimum chunk size
        #       breakpoint_percentile_threshold=95: Split at major semantic changes
        splitter = SemanticSplitterNodeParser(
                     buffer_size=1, 
                     breakpoint_percentile_threshold=95, 
                     embed_model=embed_model
                    )
        
        # Process documents and split into nodes
        nodes = splitter.get_nodes_from_documents(docs)
        
        return nodes