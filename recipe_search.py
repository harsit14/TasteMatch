"""
Recipe Search Examples
Demonstrates different ways to query the recipe database using Ollama
"""

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
import chromadb
import json


class RecipeSearcher:
    """
    Simple interface for searching recipes in Chroma
    """
    
    def __init__(
        self,
        persist_directory: str = "./chroma_recipes_db",
        collection_name: str = "recipes",
        embedding_model: str = "nomic-embed-text",
        ollama_base_url: str = "http://localhost:11434"
    ):
        """Initialize the recipe searcher with Ollama"""
        self.embeddings = OllamaEmbeddings(
            model=embedding_model,
            base_url=ollama_base_url
        )
        
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            client=self.chroma_client,
            persist_directory=persist_directory
        )
    
    def search_by_ingredients(self, ingredients: str, k: int = 5):
        """
        Search recipes by ingredients
        
        Args:
            ingredients: String of ingredients (e.g., "chicken rice vegetables")
            k: Number of results to return
        """
        query = f"Ingredients: {ingredients}"
        results = self.vectorstore.similarity_search(query, k=k)
        return self._format_results(results)
    
    def search_by_cuisine(self, cuisine: str, k: int = 5):
        """
        Search recipes by cuisine type
        
        Args:
            cuisine: Type of cuisine (e.g., "Italian", "Thai", "Mexican")
            k: Number of results to return
        """
        query = f"Category: {cuisine} cuisine, Keywords: {cuisine}"
        results = self.vectorstore.similarity_search(query, k=k)
        return self._format_results(results)
    
    def search_quick_recipes(self, query: str, max_time: int = 30, k: int = 5):
        """
        Search for quick recipes under a certain time limit
        
        Args:
            query: Search query
            max_time: Maximum total time in minutes
            k: Number of results to return
        """
        results = self.vectorstore.similarity_search(
            query,
            k=k,
            filter={"total_time_minutes": {"$lte": max_time}}
        )
        return self._format_results(results)
    
    def search_healthy_recipes(self, query: str, max_calories: int = 500, k: int = 5):
        """
        Search for healthy recipes under a calorie limit
        
        Args:
            query: Search query
            max_calories: Maximum calories per serving
            k: Number of results to return
        """
        results = self.vectorstore.similarity_search(
            query,
            k=k,
            filter={"calories": {"$lte": max_calories}}
        )
        return self._format_results(results)
    
    def search_highly_rated(self, query: str, min_rating: float = 4.0, k: int = 5):
        """
        Search for highly rated recipes
        
        Args:
            query: Search query
            min_rating: Minimum rating threshold
            k: Number of results to return
        """
        results = self.vectorstore.similarity_search(
            query,
            k=k,
            filter={"rating": {"$gte": min_rating}}
        )
        return self._format_results(results)
    
    def search_similar_recipes(self, recipe_name: str, k: int = 5):
        """
        Find recipes similar to a given recipe
        
        Args:
            recipe_name: Name of the recipe to find similar ones
            k: Number of results to return
        """
        query = f"Recipe: {recipe_name}"
        results = self.vectorstore.similarity_search(query, k=k)
        return self._format_results(results)
    
    def _format_results(self, results):
        """Format search results for display"""
        formatted = []
        for doc in results:
            recipe = {
                'name': doc.metadata.get('name', 'Unknown'),
                'category': doc.metadata.get('category', 'N/A'),
                'rating': doc.metadata.get('rating', 'N/A'),
                'reviews': doc.metadata.get('review_count', 0),
                'prep_time': doc.metadata.get('prep_time_minutes', 'N/A'),
                'cook_time': doc.metadata.get('cook_time_minutes', 'N/A'),
                'total_time': doc.metadata.get('total_time_minutes', 'N/A'),
                'calories': doc.metadata.get('calories', 'N/A'),
                'servings': doc.metadata.get('servings', 'N/A'),
                'recipe_id': doc.metadata.get('recipe_id', 'N/A')
            }
            
            # Get ingredients if available
            if 'ingredients_list' in doc.metadata:
                try:
                    ingredients = json.loads(doc.metadata['ingredients_list'])
                    recipe['ingredients'] = ingredients if isinstance(ingredients, list) else [ingredients]
                except:
                    ing_str = doc.metadata['ingredients_list']
                    if ing_str.startswith('[') and ing_str.endswith(']'):
                    # Remove brackets and split by comma
                        ing_str = ing_str.strip('[]')
                        recipe['ingredients'] = [i.strip().strip("'\"") for i in ing_str.split(',')]
                    else:
                        recipe['ingredients'] = [doc.metadata.get('ingredients_list', 'N/A')]
        else:
            recipe['ingredients'] = []
            
            formatted.append(recipe)
        
        return formatted
    
    def get_full_recipe(self, recipe_id: str):
        """
        Get full recipe details by recipe ID
        
        Args:
            recipe_id: The recipe ID to retrieve
        """
        # Search by recipe ID in metadata
        results = self.vectorstore.similarity_search(
            "",  # Empty query since we're filtering by ID
            k=1,
            filter={"recipe_id": recipe_id}
        )
        
        if results:
            doc = results[0]
            recipe = {
                'name': doc.metadata.get('name', 'Unknown'),
                'category': doc.metadata.get('category', 'N/A'),
                'author': doc.metadata.get('author_name', 'N/A'),
                'rating': doc.metadata.get('rating', 'N/A'),
                'reviews': doc.metadata.get('review_count', 0),
                'prep_time': doc.metadata.get('prep_time_minutes', 'N/A'),
                'cook_time': doc.metadata.get('cook_time_minutes', 'N/A'),
                'total_time': doc.metadata.get('total_time_minutes', 'N/A'),
                'servings': doc.metadata.get('servings', 'N/A'),
                'calories': doc.metadata.get('calories', 'N/A'),
                'fat': doc.metadata.get('fatcontent', 'N/A'),
                'protein': doc.metadata.get('proteincontent', 'N/A'),
                'carbs': doc.metadata.get('carbohydratecontent', 'N/A'),
            }
            
            # Get ingredients with quantities
            if 'ingredient_quantities' in doc.metadata:
                try:
                    recipe['ingredient_quantities'] = json.loads(doc.metadata['ingredient_quantities'])
                except:
                    recipe['ingredient_quantities'] = doc.metadata['ingredient_quantities']
            
            # Get instructions
            if 'recipe_instructions' in doc.metadata:
                try:
                    recipe['instructions'] = json.loads(doc.metadata['recipe_instructions'])
                except:
                    recipe['instructions'] = doc.metadata['recipe_instructions']
            
            return recipe
        
        return None


def main():
    """
    Example usage of the RecipeSearcher
    """
    # Initialize searcher
    searcher = RecipeSearcher()
    
    print("="*60)
    print("RECIPE SEARCH EXAMPLES")
    print("="*60)
    
    # Example 1: Search by ingredients
    print("\n1. SEARCHING BY INGREDIENTS: 'chicken garlic pasta'")
    print("-"*40)
    results = searcher.search_by_ingredients("chicken garlic pasta", k=3)
    for i, recipe in enumerate(results, 1):
        print(f"\n{i}. {recipe['name']}")
        print(f"   Category: {recipe['category']}")
        print(f"   Rating: {recipe['rating']} ({recipe['reviews']} reviews)")
        print(f"   Time: {recipe['total_time']} minutes")
    
    # Example 2: Search for quick recipes
    print("\n2. SEARCHING FOR QUICK RECIPES (under 20 minutes)")
    print("-"*40)
    results = searcher.search_quick_recipes("easy dinner", max_time=20, k=3)
    for i, recipe in enumerate(results, 1):
        print(f"\n{i}. {recipe['name']}")
        print(f"   Total Time: {recipe['total_time']} minutes")
        print(f"   Prep: {recipe['prep_time']} min | Cook: {recipe['cook_time']} min")
    
    # Example 3: Search for healthy recipes
    print("\n3. SEARCHING FOR HEALTHY RECIPES (under 400 calories)")
    print("-"*40)
    results = searcher.search_healthy_recipes("salad lunch", max_calories=400, k=3)
    for i, recipe in enumerate(results, 1):
        print(f"\n{i}. {recipe['name']}")
        print(f"   Calories: {recipe['calories']}")
        print(f"   Servings: {recipe['servings']}")
    
    # Example 4: Search by cuisine
    print("\n4. SEARCHING BY CUISINE: 'Italian'")
    print("-"*40)
    results = searcher.search_by_cuisine("Italian", k=3)
    for i, recipe in enumerate(results, 1):
        print(f"\n{i}. {recipe['name']}")
        print(f"   Category: {recipe['category']}")
        if 'ingredients' in recipe and isinstance(recipe['ingredients'], list):
            print(f"   Main ingredients: {', '.join(recipe['ingredients'][:5])}")
    
    # Example 5: Search for highly rated recipes
    print("\n5. SEARCHING FOR HIGHLY RATED RECIPES (4+ stars)")
    print("-"*40)
    results = searcher.search_highly_rated("dessert", min_rating=4.0, k=3)
    for i, recipe in enumerate(results, 1):
        print(f"\n{i}. {recipe['name']}")
        print(f"   Rating: {recipe['rating']} ⭐ ({recipe['reviews']} reviews)")
    
    # Example 6: Get full recipe details (if we have a recipe_id)
    if results and results[0]['recipe_id'] != 'N/A':
        print("\n6. GETTING FULL RECIPE DETAILS")
        print("-"*40)
        recipe_id = results[0]['recipe_id']
        full_recipe = searcher.get_full_recipe(recipe_id)
        if full_recipe:
            print(f"\nRecipe: {full_recipe['name']}")
            print(f"Author: {full_recipe['author']}")
            print(f"Rating: {full_recipe['rating']} ({full_recipe['reviews']} reviews)")
            print(f"Nutritional Info:")
            print(f"  - Calories: {full_recipe['calories']}")
            print(f"  - Protein: {full_recipe['protein']}g")
            print(f"  - Carbs: {full_recipe['carbs']}g")
            print(f"  - Fat: {full_recipe['fat']}g")
            
            if 'instructions' in full_recipe:
                print(f"\nInstructions available: Yes")


if __name__ == "__main__":
    main()