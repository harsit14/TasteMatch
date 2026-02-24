"""
Quick test script to verify your setup is working
Run this BEFORE your pitch to make sure everything works!
"""

import sys

def test_ollama_connection():
    """Test if Ollama is running"""
    print("\n1. Testing Ollama connection...")
    try:
        import requests
        response = requests.get("http://localhost:11434")
        if response.status_code == 200:
            print("   ✓ Ollama is running!")
            return True
        else:
            print("   ❌ Ollama responded but with error")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to Ollama: {e}")
        print("   → Make sure 'ollama serve' is running!")
        return False


def test_models():
    """Test if required models are downloaded"""
    print("\n2. Testing AI models...")
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        models = result.stdout
        
        has_embedding = 'nomic-embed-text' in models
        has_llm = 'llama3.2' in models or 'llama3.1' in models
        
        if has_embedding:
            print("   ✓ Embedding model found (nomic-embed-text)")
        else:
            print("   ❌ Embedding model missing")
            print("   → Run: ollama pull nomic-embed-text")
        
        if has_llm:
            print("   ✓ Chat model found (llama)")
        else:
            print("   ❌ Chat model missing")
            print("   → Run: ollama pull llama3.2")
        
        return has_embedding and has_llm
    except Exception as e:
        print(f"   ❌ Error checking models: {e}")
        return False


def test_database():
    """Test if recipe database exists"""
    print("\n3. Testing recipe database...")
    import os
    
    if os.path.exists("./chroma_recipes_db"):
        print("   ✓ Database folder found!")
        
        # Try to connect
        try:
            from recipe_search import RecipeSearcher
            searcher = RecipeSearcher()
            print("   ✓ Successfully connected to database!")
            
            # Try a simple search
            results = searcher.search_by_ingredients("chicken", k=1)
            if results:
                print(f"   ✓ Database has recipes! Found: {results[0]['name']}")
                return True
            else:
                print("   ⚠️ Database is empty!")
                return False
                
        except Exception as e:
            print(f"   ❌ Error accessing database: {e}")
            return False
    else:
        print("   ❌ Database not found!")
        print("   → Run: python load_recipes.py")
        return False


def test_python_packages():
    """Test if required Python packages are installed"""
    print("\n4. Testing Python packages...")
    required_packages = {
        'langchain': 'langchain',
        'chromadb': 'chromadb',
        'streamlit': 'streamlit',
        'ollama': 'ollama'
    }
    
    all_installed = True
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"   ✓ {package} installed")
        except ImportError:
            print(f"   ❌ {package} missing")
            print(f"   → Run: pip install {package}")
            all_installed = False
    
    return all_installed


def main():
    print("="*60)
    print("TasteMatch MVP - System Test")
    print("="*60)
    print("\nRunning pre-flight checks...\n")
    
    results = {
        "Ollama": test_ollama_connection(),
        "Models": test_models(),
        "Python Packages": test_python_packages(),
        "Database": test_database()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{test}: {status}")
    
    if all(results.values()):
        print("\n🎉 All tests passed! You're ready for your pitch!")
        print("\nRun the demo with: streamlit run demo_app.py")
        return 0
    else:
        print("\n⚠️ Some tests failed. Fix the issues above before your pitch.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
