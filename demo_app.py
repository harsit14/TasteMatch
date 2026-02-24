"""
TasteMatch MVP - AI-Powered Nutritional Chatbot
Simple demo for pitch meeting
"""

import streamlit as st
from recipe_search import RecipeSearcher
# from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
import json

# Page configuration
st.set_page_config(
    page_title="TasteMatch - Your AI Dietitian",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: #000000 !important;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        color: #000000 !important;
    }
    .user-message strong {
        color: #1565c0 !important;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
        color: #000000 !important;
    }
    .assistant-message strong {
        color: #6a1b9a !important;
    }
    .recipe-card {
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        background-color: white;
        color: #000000 !important;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'searcher' not in st.session_state:
    try:
        st.session_state.searcher = RecipeSearcher()
    except Exception as e:
        st.error(f"Error loading recipe database: {e}")
        st.stop()

if 'llm' not in st.session_state:
    st.session_state.llm = OllamaLLM(
        model="llama3.2",
        base_url="http://localhost:11434"
    )

# Sidebar - User Profile & Preferences
with st.sidebar:
    st.markdown("<h2 style='color: #667eea;'>👤 Your Profile</h2>", unsafe_allow_html=True)
    
    # Health Conditions
    st.subheader("🏥 Health Conditions")
    conditions = st.multiselect(
        "Select your conditions:",
        ["Diabetes", "High Blood Pressure", "Heart Disease", "High Cholesterol", 
         "Celiac Disease", "Lactose Intolerance", "None"],
        default=["None"]
    )
    
    # Dietary Restrictions
    st.subheader("🥗 Dietary Preferences")
    diet_type = st.selectbox(
        "Diet Type:",
        ["No Restrictions", "Vegetarian", "Vegan", "Pescatarian", "Keto", "Paleo"]
    )
    
    allergies = st.multiselect(
        "Allergies:",
        ["Nuts", "Shellfish", "Dairy", "Eggs", "Soy", "Gluten", "None"],
        default=["None"]
    )
    
    # Quick Filters
    st.subheader("⚡ Quick Filters")
    max_time = st.slider("Max cooking time (minutes):", 10, 120, 60)
    max_calories = st.slider("Max calories per serving:", 100, 1000, 600)
    min_rating = st.slider("Minimum rating:", 1.0, 5.0, 3.5, 0.5)
    
    # Kitchen Inventory
    st.subheader("🥘 Kitchen Inventory")
    available_ingredients = st.text_area(
        "What's in your kitchen?",
        placeholder="e.g., chicken, rice, tomatoes, garlic...",
        height=100
    )
    
    st.divider()
    
    # Quick Actions
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("💡 Get Suggestions"):
        if available_ingredients:
            suggestion_prompt = f"I have {available_ingredients}. What can I make?"
            st.session_state.messages.append({"role": "user", "content": suggestion_prompt})
            st.rerun()

# Main Content
st.markdown("<h1 class='main-header'>🍽️ TasteMatch</h1>", unsafe_allow_html=True)
st.markdown("### Your AI-Powered Personal Dietitian")

# Quick Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Health Conditions", len([c for c in conditions if c != "None"]))
with col2:
    st.metric("Diet Type", diet_type.split()[0])
with col3:
    st.metric("Max Time", f"{max_time}m")
with col4:
    st.metric("Max Calories", max_calories)

st.divider()

# Chat Interface
chat_container = st.container()

# Display chat history
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class='chat-message user-message'>
                <strong>You:</strong><br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='chat-message assistant-message'>
                <strong>TasteMatch:</strong><br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)
            
            # Display recipes if available
            if 'recipes' in message:
                st.markdown("**📋 Recipe Recommendations:**")
                for i, recipe in enumerate(message['recipes'], 1):
                    with st.expander(f"🍳 {recipe['name']} - ⭐{recipe['rating']} ({recipe['total_time']}min, {recipe['calories']} cal)"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**Category:** {recipe['category']}")
                            st.write(f"**Prep Time:** {recipe['prep_time']} min")
                            st.write(f"**Cook Time:** {recipe['cook_time']} min")
                        with col_b:
                            st.write(f"**Servings:** {recipe['servings']}")
                            st.write(f"**Reviews:** {recipe['reviews']}")
                            st.write(f"**Rating:** ⭐ {recipe['rating']}")
                        
                        if 'ingredients' in recipe and recipe['ingredients'] != 'N/A':
                            st.write("**Ingredients:**")
                            if isinstance(recipe['ingredients'], list):
                                for ing in recipe['ingredients'][:8]:  # Show first 8
                                    st.write(f"• {ing}")
                                if len(recipe['ingredients']) > 8:
                                    st.write(f"...and {len(recipe['ingredients']) - 8} more")

# Chat Input
user_input = st.chat_input("Ask me anything about recipes, nutrition, or meal planning...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Build context from user profile
    context = f"""
You are TasteMatch, an AI nutritional assistant. Help the user with their dietary needs.

USER PROFILE:
- Health Conditions: {', '.join(conditions)}
- Diet Type: {diet_type}
- Allergies: {', '.join(allergies)}
- Max Cooking Time: {max_time} minutes
- Max Calories: {max_calories}
- Minimum Rating: {min_rating}
"""
    
    if available_ingredients:
        context += f"\n- Available Ingredients: {available_ingredients}"
    
    # Build conversation history for context
    conversation_history = "\n\nCONVERSATION HISTORY:\n"
    for msg in st.session_state.messages[:-1]:  # Exclude the current message
        role = "User" if msg["role"] == "user" else "TasteMatch"
        conversation_history += f"{role}: {msg['content']}\n"
    
    # Search for relevant recipes
    try:
        # Search with filters
        recipes = st.session_state.searcher.search_by_ingredients(
            user_input, 
            k=5
        )
        
        # Apply additional filters
        filtered_recipes = [
            r for r in recipes 
            if (r['total_time'] == 'N/A' or r['total_time'] <= max_time)
            and (r['calories'] == 'N/A' or r['calories'] <= max_calories)
            and (r['rating'] == 'N/A' or r['rating'] >= min_rating)
        ]
        
        if not filtered_recipes:
            filtered_recipes = recipes[:3]  # Fallback to top 3
        
        # Build prompt for LLM
        recipe_info = "\n\n".join([
            f"Recipe {i+1}: {r['name']}\n"
            f"Category: {r['category']}\n"
            f"Time: {r['total_time']} min\n"
            f"Calories: {r['calories']}\n"
            f"Rating: {r['rating']}"
            for i, r in enumerate(filtered_recipes[:3])
        ])
        
        prompt = f"""{context}
{conversation_history}

RELEVANT RECIPES:
{recipe_info}

USER'S CURRENT QUESTION: {user_input}

Provide a helpful, conversational response considering the conversation history. Consider their health conditions and preferences.
Be encouraging and supportive. Keep the response concise (2-3 paragraphs).
Mention the recipes naturally in your response if relevant."""
        
        # Get LLM response
        with st.spinner("Thinking..."):
            response = st.session_state.llm.invoke(prompt)
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "recipes": filtered_recipes[:3]
        })
        
    except Exception as e:
        error_msg = f"I apologize, I'm having trouble searching recipes right now. Error: {str(e)}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_msg
        })
    
    st.rerun()

# Welcome message if chat is empty
if not st.session_state.messages:
    st.info("""
    👋 **Welcome to TasteMatch!**
    
    I'm your AI-powered personal dietitian. I can help you:
    - Find recipes based on what's in your kitchen
    - Get personalized meal recommendations for your health conditions
    - Plan nutritious meals within your dietary restrictions
    - Discover quick and healthy recipes
    
    **Try asking:**
    - "What can I make with chicken and rice?"
    - "I need a quick dinner under 30 minutes"
    - "Show me heart-healthy recipes"
    - "What's a good breakfast for diabetics?"
    """)

# Footer
st.divider()
st.caption("TasteMatch MVP • Powered by Ollama + LangChain • 100% Local & Free")
