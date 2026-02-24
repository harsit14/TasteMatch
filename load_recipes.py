"""
Simple script to load recipes into the database
Run this ONCE to set up your recipe database
"""

import sys
import os

# Copy the recipe_loader.py content here or import it
from recipe_loader import RecipeChromaLoader


def main():
    print("="*60)
    print("TasteMatch - Recipe Database Setup")
    print("="*60)
    
    # Check if recipes.csv exists
    csv_path = "recipes.csv"
    if not os.path.exists(csv_path):
        print(f"\n❌ ERROR: {csv_path} not found!")
        print("Please make sure recipes.csv is in the same folder as this script.")
        print("\nYou need to get the recipe dataset from your teammate.")
        sys.exit(1)
    
    print(f"\n✓ Found {csv_path}")
    print("\nThis will:")
    print("1. Load all recipes from the CSV")
    print("2. Convert them to embeddings using Ollama")
    print("3. Store them in a searchable database")
    print("\nThis may take 5-10 minutes depending on dataset size...")
    
    input("\nPress Enter to continue...")
    
    try:
        # Initialize loader
        loader = RecipeChromaLoader(
            csv_path=csv_path,
            persist_directory="./chroma_recipes_db",
            collection_name="recipes",
            embedding_model="nomic-embed-text",
            ollama_base_url="http://localhost:11434"
        )
        
        # Load recipes
        print("\nLoading recipes...")
        vectorstore = loader.load()
        
        print("\n" + "="*60)
        print("✓ SUCCESS! Recipe database is ready!")
        print("="*60)
        print(f"\nDatabase location: ./chroma_recipes_db")
        print("\nNext step: Run the demo with: streamlit run demo_app.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nCommon fixes:")
        print("1. Make sure 'ollama serve' is running")
        print("2. Make sure you ran 'ollama pull nomic-embed-text'")
        print("3. Check that recipes.csv has the correct format")
        sys.exit(1)


if __name__ == "__main__":
    main()
