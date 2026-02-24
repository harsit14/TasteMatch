"""
Recipe CSV to Chroma Loader
Implements Structured Semantic Storage for recipe matching chatbot
Using Ollama for free local embeddings
"""

import os
import json
import pandas as pd
from typing import List, Dict, Optional
from langchain_community.document_loaders import CSVLoader
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
import chromadb
from chromadb.config import Settings


class RecipeChromaLoader:
    """
    Loads recipe data from CSV into Chroma with structured semantic storage
    """
    
    def __init__(
        self,
        csv_path: str,
        persist_directory: str = "./chroma_recipes_db",
        collection_name: str = "recipes",
        embedding_model: str = "nomic-embed-text",  # Ollama embedding model
        ollama_base_url: str = "http://localhost:11434"  # Ollama server URL
    ):
        """
        Initialize the Recipe Chroma Loader
        
        Args:
            csv_path: Path to the recipes CSV file
            persist_directory: Directory to persist Chroma database
            collection_name: Name of the Chroma collection
            embedding_model: Ollama model name for embeddings (nomic-embed-text, mxbai-embed-large, or all-minilm)
            ollama_base_url: URL of the Ollama server
        """
        self.csv_path = csv_path
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize Ollama embeddings
        # Popular embedding models for Ollama:
        # - nomic-embed-text (768 dimensions, very good quality)
        # - mxbai-embed-large (1024 dimensions, excellent quality)
        # - all-minilm (384 dimensions, fast and efficient)
        self.embeddings = OllamaEmbeddings(
            model=embedding_model,
            base_url=ollama_base_url
        )
        
        # Initialize Chroma client
        self.chroma_client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
    def clean_and_parse_value(self, value):
        """
        Clean and parse values from CSV, handling various data types
        """
        if pd.isna(value) or value == '' or value == 'NA':
            return None
        
        # Try to parse as JSON if it looks like a list/dict
        if isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
            try:
                return json.loads(value)
            except:
                # If JSON parsing fails, clean and return as string
                return value.strip()
        
        # Try to convert to appropriate numeric type
        if isinstance(value, str):
            # Check if it's a numeric value
            try:
                if '.' in value:
                    return float(value)
                else:
                    # Check if it's a time value (could be 'PT15M' format)
                    if value.startswith('PT'):
                        return self.parse_iso_duration(value)
                    return int(value)
            except:
                return value.strip()
        
        return value
    
    def parse_iso_duration(self, duration_str: str) -> int:
        """
        Parse ISO 8601 duration (PT15M) to minutes
        """
        if not duration_str or duration_str == 'NA':
            return 0
        
        try:
            # Remove PT prefix
            if duration_str.startswith('PT'):
                duration_str = duration_str[2:]
            
            minutes = 0
            # Check for hours
            if 'H' in duration_str:
                hours_part = duration_str.split('H')[0]
                minutes += int(hours_part) * 60
                duration_str = duration_str.split('H')[1] if 'H' in duration_str else ''
            
            # Check for minutes
            if 'M' in duration_str:
                minutes_part = duration_str.split('M')[0]
                if minutes_part:
                    minutes += int(minutes_part)
            
            return minutes
        except:
            return 0
    
    def create_structured_content(self, row: pd.Series) -> str:
        """
        Create structured document content from recipe data
        """
        content_parts = []
        
        # Add recipe name
        if pd.notna(row.get('Name')):
            content_parts.append(f"Recipe: {row['Name']}")
        
        # Add category
        if pd.notna(row.get('RecipeCategory')):
            content_parts.append(f"Category: {row['RecipeCategory']}")
        
        # Add ingredients
        if pd.notna(row.get('RecipeIngredientParts')):
            ingredients = row['RecipeIngredientParts']
            # Handle if it's a JSON string list
            if isinstance(ingredients, str) and ingredients.startswith('['):
                try:
                    ingredients = json.loads(ingredients)
                    ingredients = ', '.join(ingredients)
                except:
                    pass
            content_parts.append(f"Ingredients: {ingredients}")
        
        # Add description
        if pd.notna(row.get('Description')):
            content_parts.append(f"Description: {row['Description']}")
        
        # Add keywords
        if pd.notna(row.get('Keywords')):
            keywords = row['Keywords']
            # Handle if it's a JSON string list
            if isinstance(keywords, str) and keywords.startswith('['):
                try:
                    keywords = json.loads(keywords)
                    keywords = ', '.join(keywords)
                except:
                    pass
            content_parts.append(f"Keywords: {keywords}")
        
        return "\n".join(content_parts)
    
    def create_metadata(self, row: pd.Series) -> Dict:
        """
        Create metadata dictionary from recipe data
        """
        metadata = {}
        
        # Essential IDs
        metadata['recipe_id'] = str(row.get('RecipeId', ''))
        metadata['name'] = str(row.get('Name', ''))
        metadata['author_id'] = str(row.get('AuthorId', '')) if pd.notna(row.get('AuthorId')) else None
        metadata['author_name'] = str(row.get('AuthorName', '')) if pd.notna(row.get('AuthorName')) else None
        
        # Time fields (convert to minutes for filtering)
        metadata['cook_time_minutes'] = self.clean_and_parse_value(row.get('CookTime', 0))
        metadata['prep_time_minutes'] = self.clean_and_parse_value(row.get('PrepTime', 0))
        metadata['total_time_minutes'] = self.clean_and_parse_value(row.get('TotalTime', 0))
        
        # Date published
        metadata['date_published'] = str(row.get('DatePublished', '')) if pd.notna(row.get('DatePublished')) else None
        
        # Rating and reviews
        rating = self.clean_and_parse_value(row.get('AggregatedRating'))
        metadata['rating'] = float(rating) if rating else None
        
        review_count = self.clean_and_parse_value(row.get('ReviewCount'))
        metadata['review_count'] = int(review_count) if review_count else 0
        
        # Nutritional information (as floats for filtering)
        for nutrient in ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 
                        'SodiumContent', 'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']:
            value = self.clean_and_parse_value(row.get(nutrient))
            metadata[nutrient.lower()] = float(value) if value else None
        
        # Servings and yield
        servings = self.clean_and_parse_value(row.get('RecipeServings'))
        metadata['servings'] = int(servings) if servings else None
        metadata['recipe_yield'] = str(row.get('RecipeYield', '')) if pd.notna(row.get('RecipeYield')) else None
        
        # Store full recipe data as JSON strings for retrieval
        metadata['category'] = str(row.get('RecipeCategory', '')) if pd.notna(row.get('RecipeCategory')) else None
        
        # Handle ingredient quantities
        if pd.notna(row.get('RecipeIngredientQuantities')):
            quantities = row.get('RecipeIngredientQuantities')
            if isinstance(quantities, str):
                metadata['ingredient_quantities'] = quantities
            else:
                metadata['ingredient_quantities'] = json.dumps(quantities)
        
        # Handle recipe instructions
        if pd.notna(row.get('RecipeInstructions')):
            instructions = row.get('RecipeInstructions')
            if isinstance(instructions, str):
                metadata['recipe_instructions'] = instructions
            else:
                metadata['recipe_instructions'] = json.dumps(instructions)
        
        # Create ingredients list for exact matching
        if pd.notna(row.get('RecipeIngredientParts')):
            ingredients = row.get('RecipeIngredientParts')
            if isinstance(ingredients, str) and ingredients.startswith('['):
                try:
                    ingredients_list = json.loads(ingredients)
                    metadata['ingredients_list'] = json.dumps(ingredients_list)
                    metadata['ingredient_count'] = len(ingredients_list)
                except:
                    metadata['ingredients_list'] = ingredients
                    metadata['ingredient_count'] = 1
            else:
                metadata['ingredients_list'] = str(ingredients)
                metadata['ingredient_count'] = 1
        
        # Handle images
        if pd.notna(row.get('Images')):
            metadata['images'] = str(row.get('Images'))
        
        # Clean up None values and ensure all values are JSON serializable
        metadata = {k: v for k, v in metadata.items() if v is not None}
        
        return metadata
    
    def load_and_process_csv(self) -> List[Document]:
        """
        Load CSV and convert to LangChain documents with structured content
        """
        print(f"Loading CSV from {self.csv_path}...")
        
        # Read CSV with pandas for better data handling
        df = pd.read_csv(self.csv_path)
        
        print(f"Processing {len(df)} recipes...")
        
        documents = []
        for idx, row in df.iterrows():
            try:
                # Create structured content
                content = self.create_structured_content(row)
                
                # Create metadata
                metadata = self.create_metadata(row)
                
                # Create document
                doc = Document(
                    page_content=content,
                    metadata=metadata
                )
                documents.append(doc)
                
                if (idx + 1) % 100 == 0:
                    print(f"Processed {idx + 1} recipes...")
                    
            except Exception as e:
                print(f"Error processing recipe at index {idx}: {e}")
                continue
        
        print(f"Successfully processed {len(documents)} recipes")
        return documents
    
    def create_or_update_collection(self, documents: List[Document], batch_size: int = 100):
        """
        Create or update Chroma collection with documents
        """
        print(f"Creating/updating Chroma collection '{self.collection_name}'...")
        
        # Delete existing collection if it exists
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
            print(f"Deleted existing collection '{self.collection_name}'")
        except:
            print(f"No existing collection '{self.collection_name}' found, creating new one")
        
        # Create new vectorstore
        vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            client=self.chroma_client,
            persist_directory=self.persist_directory
        )
        
        # Add documents in batches
        total_docs = len(documents)
        for i in range(0, total_docs, batch_size):
            batch = documents[i:i + batch_size]
            vectorstore.add_documents(documents=batch)
            print(f"Added batch {i//batch_size + 1}/{(total_docs + batch_size - 1)//batch_size}")
        
        print(f"Successfully added {total_docs} documents to Chroma collection")
        return vectorstore
    
    def load(self) -> Chroma:
        """
        Main method to load recipes from CSV into Chroma
        """
        # Load and process CSV
        documents = self.load_and_process_csv()
        
        # Create or update Chroma collection
        vectorstore = self.create_or_update_collection(documents)
        
        print(f"Recipe database ready at {self.persist_directory}")
        print(f"Collection name: {self.collection_name}")
        print(f"Total recipes indexed: {len(documents)}")
        
        return vectorstore


def main():
    """
    Example usage of the RecipeChromaLoader with Ollama
    """
    # Configure paths
    csv_path = "recipes.csv"  # Path to your recipes CSV
    persist_directory = "./chroma_recipes_db"  # Where to store the Chroma database
    
    # Initialize loader with Ollama
    # Make sure Ollama is running: ollama serve
    # Pull an embedding model first: ollama pull nomic-embed-text
    loader = RecipeChromaLoader(
        csv_path=csv_path,
        persist_directory=persist_directory,
        collection_name="recipes",
        embedding_model="nomic-embed-text",  # Good quality embeddings
        ollama_base_url="http://localhost:11434"  # Default Ollama URL
    )
    
    # Load recipes into Chroma
    vectorstore = loader.load()
    
    # Example: Test a simple similarity search
    print("\n" + "="*50)
    print("Testing similarity search...")
    results = vectorstore.similarity_search(
        "chicken pasta italian dinner",
        k=3
    )
    
    for i, doc in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Recipe: {doc.metadata.get('name', 'N/A')}")
        print(f"Category: {doc.metadata.get('category', 'N/A')}")
        print(f"Rating: {doc.metadata.get('rating', 'N/A')}")
        print(f"Cook Time: {doc.metadata.get('cook_time_minutes', 'N/A')} minutes")
    
    # Example: Search with metadata filtering
    print("\n" + "="*50)
    print("Testing filtered search (quick recipes under 30 minutes)...")
    results = vectorstore.similarity_search(
        "easy dinner",
        k=3,
        filter={"total_time_minutes": {"$lte": 30}}
    )
    
    for i, doc in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Recipe: {doc.metadata.get('name', 'N/A')}")
        print(f"Total Time: {doc.metadata.get('total_time_minutes', 'N/A')} minutes")


if __name__ == "__main__":
    main()