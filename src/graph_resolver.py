
from llama_index.core.graph_stores.types import (
    EntityNode,
    KG_NODES_KEY,
    KG_RELATIONS_KEY,
    Relation
)
from openai import OpenAI
from collections import defaultdict
import os
from dotenv import load_dotenv
load_dotenv()  

openai_api_key= os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)


system_prompt = """
    You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
    Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
    Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
    If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
    Make sure it is written in third person, and include the entity names so we have the full context.
"""


class GraphResolver:
    """
    A class to resolve and combine duplicate entities and relationships in the knowledge graph.
    Handles merging of descriptions and resolving conflicts.
    """

    def summarize_entity(self, descriptions, entity_name):
        """
        Generate a consolidated summary for an entity with multiple descriptions.
        
        Args:
            descriptions(str): Combined descriptions of the entity
            entity_name str): Name of the entity to summarize
            
        Returns:
            str: Consolidated description of the entity
            
        - Uses GPT-4 to create a coherent summary from multiple descriptions
        """

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"entity: {entity_name}\n\ndescriptions: {descriptions}"},]
        )
        return completion.choices[0].message.content
    
    def summarize_relation(self, descriptions, source_entity, target_entity, relation):
        """
        Generate a consolidated summary for a relationship with multiple descriptions.
        
        Args:
            descriptions(str): Combined descriptions of the relationship
            source_entity(str): Name of the source entity
            target_entity(str): Name of the target entity
            relation(str): Type of relationship
            
        Returns:
            str: Consolidated description of the relationship
        """
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": 
                    f"Source_entity: {source_entity}\n"
                    f"Target_entity: {target_entity}\n"
                    f"Relation: {relation}\n\n"
                    f"descriptions: {descriptions}"
                },
            ]
        )
        return completion.choices[0].message.content
    
    def resolve_entities(self, nodes):
        """
        Resolve and combine duplicate entities across nodes.
        
        Args:
            nodes(list): List of nodes containing entity information
            
        Process:
        1. Collect all entities from nodes
        2. Group entities by name
        3. Merge descriptions for duplicates
        4. Create final entity list
        
        Returns:
            list: List of unique EntityNode objects with merged descriptions
        """
        #Collect all entities from nodes
        entities = []
        for node in nodes:
            entities.extend(node.metadata[KG_NODES_KEY])

        #Group entities by name
        entities_dict = defaultdict(list)
        for entity in entities:
            entities_dict[entity.name].append(entity)

        final_entities = []

        #Process each group of entities
        for name, entities in entities_dict.items():
            if len(entities) == 1:
                #Single entity - use existing description
                description = entities[0].properties["entity_description"]
            else:
                #Multiple entities - combine and summarize descriptions
                descriptions = "\n\n".join(
                    [node.properties["entity_description"] for node in entities]
                )
                description = self.summarize_entity(descriptions, name)
            
            #Create final entity with merged description
            final_entity = EntityNode(
                name=name, 
                label=entities[0].label, 
                properties={"entity_description": description}
            )
            final_entities.append(final_entity)

        return final_entities
    
    def resolve_relationships(self, nodes):
        """
        Resolve and combine duplicate relationships across nodes.
        
        Args:
            nodes (list): List of nodes containing relationship information
            
        Process:
        1. Collect all relationships from nodes
        2. Group relationships by source, target, and type
        3. Merge descriptions for duplicates
        4. Create final relationship list
        
        Returns:
            list: List of unique Relation objects with merged descriptions
        """
        # Collect all relationships
        relationships = []
        for node in nodes:
            relationships.extend(node.metadata[KG_RELATIONS_KEY])

        # Group relationships by key components
        relationships_dict = defaultdict(list)
        for relationship in relationships:
            key = (relationship.source_id, relationship.target_id, relationship.label)
            relationships_dict[key].append(relationship)

        final_relationships = []

        # Process each group of relationships
        for (source_entity, target_entity, relation), relationships in relationships_dict.items():
            if len(relationships) == 1:
                # Single relationship - use existing description
                description = relationships[0].properties["relationship_description"]
            else:
                # Multiple relationships - combine and summarize descriptions
                descriptions = "\n\n".join(
                    [node.properties["relationship_description"] for node in relationships]
                )
                description = self.summarize_relation(
                    descriptions, source_entity, target_entity, relation
                )
            
            # Create final relationship with merged description
            final_relationship = Relation(
                label=relation,
                source_id=source_entity,
                target_id=target_entity,
                properties={"relationship_description": description}
            )
            final_relationships.append(final_relationship)

        return final_relationships
    
    def resolve(self, nodes):
        """
        Main method to resolve both entities and relationships.
        
        Args:
            nodes (list): List of nodes to process
            
        Returns:
            tuple: (resolved_entities, resolved_relationships)
        """
        entities = self.resolve_entities(nodes)
        relationships = self.resolve_relationships(nodes)
        return entities, relationships