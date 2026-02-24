# TasteMatch MVP Setup Checklist

## Prerequisites Needed:
- [ ] Python 3.12 installed
- [ ] Ollama installed on your system
- [ ] Recipe CSV file (recipes.csv)
- [ ] ~5GB free disk space for models

## Quick Start Steps:

### 1. Install Ollama (5 minutes)
**Windows:** Download from https://ollama.ai/download
**After installing, run:**
```bash
ollama serve
```
Keep this terminal open!

### 2. Download AI Models (10 minutes)
Open a NEW terminal and run:
```bash
# For embeddings (converts text to numbers for search)
ollama pull nomic-embed-text

# For chat (the conversational AI)
ollama pull llama3.2
```

### 3. Install Python Dependencies (2 minutes)
```bash
pip install langchain langchain-community langchain-chroma chromadb ollama streamlit pandas
```

### 4. Load Your Recipe Database (5-10 minutes)
```bash
python load_recipes.py
```
This only needs to be done ONCE!

### 5. Run the Demo (instant!)
```bash
streamlit run demo_app.py
```

---

## What You Need From Your Teammate:
- The `recipes.csv` file with your recipe dataset
- Confirm the CSV has these columns: Name, RecipeIngredientParts, Description, etc.

## Troubleshooting:
- **"Connection refused"**: Make sure `ollama serve` is running
- **"Model not found"**: Run the `ollama pull` commands
- **CSV errors**: Check that recipes.csv is in the same folder
