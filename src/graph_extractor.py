from openai import OpenAI
from llama_index.core.schema import TextNode
from data_models import KnowledgeModel
from llama_index.core.graph_stores.types import (
    EntityNode,
    KG_NODES_KEY,
    KG_RELATIONS_KEY,
    Relation,
)
from multiprocessing import Pool, cpu_count
import os
from dotenv import load_dotenv
load_dotenv()  

openai_api_key= os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

system_prompt = """
    -Goal-
    Given a text document, identify all entities and their entity types from the text and all relationships among the identified entities.

    -Steps-
    1. Identify all entities. For each identified entity, extract the following information:
    - entity_name: Name of the entity, capitalized
    - entity_type: Type of the entity
    - entity_description: Comprehensive description of the entity's attributes and activities

    2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
    For each pair of related entities, extract the following information:
    - source_entity: name of the source entity, as identified in step 1
    - target_entity: name of the target entity, as identified in step 1
    - relation: relationship between source_entity and target_entity
    - relationship_description: explanation as to why you think the source entity and the target entity are related to each other
"""

class GraphExtractor:
    def extract_from_node(self, node: TextNode):
        """
        Extract knowledge graph elements from a text node using GPT-4.
        
        Args:
            node (TextNode): A text node containing content to analyze
            
        Process:
        1. Send text to GPT-4 for entity and relationship extraction.
        2. Convert the response into LlamaIndex format.
        3. Add extracted information to node metadata
        
        Returns:
            TextNode: The input node with updated metadata containing graph elements
        """
        # Use GPT-4 to extract knowledge graph elements
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"text: {node}"}
            ],
            #Expect response in KnowledgeModel format
            response_format=KnowledgeModel,
        )

        #Get the parsed knowledge model from response
        knowledge_model = completion.choices[0].message.parsed
        
        entities, relationships = self.convert_to_llamaindex(knowledge_model)
        
        node.metadata[KG_NODES_KEY] = entities          # Store entities
        node.metadata[KG_RELATIONS_KEY] = relationships # Store relationships
        
        return node

    def convert_to_llamaindex(self, knowledge_model: KnowledgeModel):
        """
        Convert extracted knowledge into LlamaIndex format.
        Args:
            knowledge_model (KnowledgeModel): The extracted knowledge structure
            
        Returns:
            tuple: (list of entities, list of relationships)
        """
        entities = []
        relationships = []

        # Convert each entity to LlamaIndex EntityNode format
        for entity_model in knowledge_model.entities:
            entity = EntityNode(
                name=entity_model.name,       
                label=entity_model.type,      
                properties={
                    "entity_description": entity_model.description  
                }
            )
            entities.append(entity)

        # Keep track of valid entity names for relationship validation
        valid_entities = {entity.name for entity in entities}

        #Convert each relationship to LlamaIndex Relation format
        for relationship_model in knowledge_model.relationships:
            #Skip relationships if either entity doesn't exist
            if not (relationship_model.source_entity.name in valid_entities and 
                   relationship_model.target_entity.name in valid_entities):
                continue
            
            # Create relationship
            relationship = Relation(
                label=relationship_model.relation,  # Relationship type
                source_id=relationship_model.source_entity.name, 
                target_id=relationship_model.target_entity.name,  
                properties={
                    "relationship_description": relationship_model.description  
                }
            )
            relationships.append(relationship)
        
        return entities, relationships

    def extract(self, nodes):
        """
        Process multiple nodes in parallel using multiprocessing.
        
        Args:
            nodes (list): List of TextNodes to process
            
        Process:
        1. Create a process pool using available CPU cores
        2. Process nodes in parallel using extract_from_node
        
        Returns:
            list: Processed nodes with extracted graph information
        """
        #Use multiprocessing to process nodes in parallel
        with Pool(cpu_count()) as pool:
            nodes = pool.map(self.extract_from_node, nodes)
        return nodes