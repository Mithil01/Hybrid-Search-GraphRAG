from text_splitter import TextSplitter
from graph_extractor import GraphExtractor
from graph_resolver import GraphResolver
from data_index import DataIndexer
from graph_communities import CommunitySummarizer

def run():
   """
    Main function to process documents and build the knowledge graph.
   
   Process Workflow:
   1. Initialize components:
      - TextSplitter: Splits documents into semantic chunks
      - GraphExtractor: Extracts entities and relationships from text
      - GraphResolver: Resolves duplicate entities and relationships
      - DataIndexer: Stores data in Neo4j database
      - CommunitySummarizer: Creates summaries for graph communities
      
   2. Pipeline Steps:
      a. Load and split documents into chunks
      b. Extract knowledge graph elements from chunks
      c. Resolve and merge duplicate elements
      d. Generate community summaries
      e. Store final graph in Neo4j
   """

   # Initialize components
   text_splitter = TextSplitter()          # For document splitting
   graph_extractor = GraphExtractor()      # For entity extraction
   graph_resolver = GraphResolver()         # For resolving duplicates
   data_indexer = DataIndexer()            # For Neo4j indexing
   summarizer = CommunitySummarizer()      # For community summarization

   #Step 1: Load and split documents into semantic chunks
   nodes = text_splitter.load_data()

   #Step 2: Extract entities and relationships from text chunks
   nodes = graph_extractor.extract(nodes)

   #Step 3: Resolve and merge duplicate entities/relationships
   entities, relationships = graph_resolver.resolve(nodes)

   #Step 4: Generate summaries for graph communities
   summarizer.run(entities, relationships)

   #Step 5: Store final knowledge graph in Neo4j
   data_indexer.insert_data(entities, relationships)


if __name__ == "__main__":
   run()