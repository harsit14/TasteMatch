"""
TasteMatch MVP with Smart Fridge Integration
Enhanced version of the original demo with Samsung Family Hub integration
"""

import streamlit as st
from recipe_search import RecipeSearcher
from langchain_ollama import OllamaLLM
import json
import requests
from datetime import datetime
import threading
import time

# Page configuration
st.set_page_config(
    page_title="TasteMatch + Smart Fridge - Your AI Dietitian",
    page_icon="🍎",
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
    .smart-fridge-connected {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    .smart-fridge-disconnected {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    .inventory-item {
        background-color: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 0.25rem;
    }
    .expiring-item {
        border-left-color: #ffc107 !important;
        background-color: #fff3cd;
    }
    .expired-item {
        border-left-color: #dc3545 !important;
        background-color: #f8d7da;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Smart Fridge Integration Functions
def check_smart_fridge_connection():
    """Check if the mock Samsung SmartThings API is running"""
    try:
        response = requests.get("http://localhost:5000/v1/devices/12345678-1234-1234-abcd-123456789012/status", timeout=3)
        return response.status_code == 200
    except:
        return False

def get_smart_fridge_inventory():
    """Get inventory from Samsung Family Hub"""
    try:
        response = requests.get(
            "http://localhost:5000/v1/devices/12345678-1234-1234-abcd-123456789012/components/main/capabilities/samsungce.aiVisionInside/foodInventory",
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_health_filtered_inventory(health_conditions, dietary_restrictions):
    """Get health-filtered inventory from smart fridge"""
    try:
        payload = {
            "health_conditions": [c.lower().replace(" ", "_").replace("blood_pressure", "hypertension") for c in health_conditions if c != "None"],
            "dietary_restrictions": dietary_restrictions
        }
        
        response = requests.post(
            "http://localhost:5000/v1/devices/12345678-1234-1234-abcd-123456789012/components/main/capabilities/samsungce.aiVisionInside/foodInventory/filter",
            json=payload,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def format_expiry_warning(expiry_date):
    """Format expiry date with warning"""
    try:
        expiry = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
        days_until_expiry = (expiry - datetime.now(expiry.tzinfo)).days
        
        if days_until_expiry < 0:
            return "⚠️ EXPIRED", "expired-item"
        elif days_until_expiry <= 2:
            return f"🔶 {days_until_expiry} day{'s' if days_until_expiry != 1 else ''} left", "expiring-item"
        else:
            return "", "inventory-item"
    except:
        return "", "inventory-item"

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

# Check smart fridge connection
smart_fridge_connected = check_smart_fridge_connection()

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
    
    # Kitchen Inventory - Enhanced with Smart Fridge
    st.subheader("🥘 Kitchen Inventory")
    
    # Smart Fridge Connection Status
    if smart_fridge_connected:
        st.markdown("""
        <div class="smart-fridge-connected">
            <strong>🍎 Samsung Family Hub Connected</strong><br>
            Smart fridge inventory available
        </div>
        """, unsafe_allow_html=True)
        
        inventory_mode = st.radio(
            "Inventory Source:",
            ["🤖 Smart Fridge (Samsung Family Hub)", "✋ Manual Entry"],
            key="inventory_mode"
        )
    else:
        st.markdown("""
        <div class="smart-fridge-disconnected">
            <strong>📱 Smart Fridge Offline</strong><br>
            Using manual inventory entry
        </div>
        """, unsafe_allow_html=True)
        inventory_mode = "✋ Manual Entry"
        
        if st.button("🔄 Reconnect Smart Fridge"):
            st.rerun()
    
    available_ingredients = ""
    smart_inventory_data = None
    
    if inventory_mode == "🤖 Smart Fridge (Samsung Family Hub)" and smart_fridge_connected:
        # Smart Fridge Mode
        st.write("**📦 Smart Fridge Inventory:**")
        
        # Get health-filtered inventory
        health_conditions_for_api = [c for c in conditions if c != "None"]
        dietary_restrictions_for_api = []
        
        if diet_type != "No Restrictions":
            dietary_restrictions_for_api.append(diet_type.lower())
        
        if allergies and "None" not in allergies:
            for allergy in allergies:
                if allergy == "Nuts":
                    dietary_restrictions_for_api.append("nut_free")
                elif allergy == "Gluten":
                    dietary_restrictions_for_api.append("gluten_free")
        
        # Get smart fridge inventory
        smart_inventory_data = get_health_filtered_inventory(health_conditions_for_api, dietary_restrictions_for_api)
        
        if smart_inventory_data:
            filtered_items = smart_inventory_data.get('filtered_items', {})
            total_items = sum(len(items) for items in filtered_items.values())
            
            if total_items > 0:
                st.write(f"*{total_items} health-appropriate items available*")
                
                ingredient_list = []
                
                # Display items by category with health indicators
                for category, items in filtered_items.items():
                    if items:
                        category_display = category.replace('_', ' ').title()
                        with st.expander(f"📂 {category_display} ({len(items)} items)"):
                            for item in items:
                                # Format item display
                                name = item['name']
                                quantity = f"{item['quantity']} {item['unit']}"
                                
                                # Check expiry
                                expiry_warning, css_class = format_expiry_warning(item.get('expiry_date', ''))
                                
                                # Health indicators
                                nutrition = item.get('nutrition_info', {})
                                health_indicators = []
                                
                                if 'glycemic_index' in nutrition:
                                    gi = nutrition['glycemic_index']
                                    if gi <= 55:
                                        health_indicators.append("Low GI ✅")
                                    elif gi > 70:
                                        health_indicators.append("High GI ⚠️")
                                
                                if 'sodium_mg' in nutrition:
                                    sodium = nutrition['sodium_mg']
                                    if sodium <= 140:
                                        health_indicators.append("Low Na ✅")
                                    elif sodium > 400:
                                        health_indicators.append("High Na ⚠️")
                                
                                health_str = " | ".join(health_indicators)
                                
                                # Display item
                                item_display = f"**{name}** ({quantity})"
                                if expiry_warning:
                                    item_display += f" - {expiry_warning}"
                                if health_str:
                                    item_display += f" | {health_str}"
                                
                                st.markdown(f"""
                                <div class="{css_class}">
                                    {item_display}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Add to ingredient list for AI
                                ingredient_list.append(name.lower())
                
                available_ingredients = ", ".join(ingredient_list)
                
            else:
                st.warning("No items match your health condition filters.")
        else:
            st.error("Could not retrieve smart fridge inventory")
    
    else:
        # Manual Mode
        available_ingredients = st.text_area(
            "What's in your kitchen?",
            placeholder="e.g., chicken, rice, tomatoes, garlic...",
            height=100,
            key="manual_ingredients"
        )
    
    st.divider()
    
    # Quick Actions
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("💡 Get Suggestions"):
        if available_ingredients or smart_inventory_data:
            if smart_inventory_data:
                suggestion_prompt = "Based on my smart fridge inventory, what can I make for dinner?"
            else:
                suggestion_prompt = f"I have {available_ingredients}. What can I make?"
            st.session_state.messages.append({"role": "user", "content": suggestion_prompt})
            st.rerun()

# Main Content
st.markdown("<h1 class='main-header'>🍎 TasteMatch + Smart Fridge</h1>", unsafe_allow_html=True)
st.markdown("### Your AI-Powered Personal Dietitian with Smart Kitchen Integration")

# Enhanced Stats with Smart Fridge Info
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Health Conditions", len([c for c in conditions if c != "None"]))
with col2:
    st.metric("Diet Type", diet_type.split()[0])
with col3:
    st.metric("Max Time", f"{max_time}m")
with col4:
    st.metric("Max Calories", max_calories)
with col5:
    if smart_fridge_connected:
        if smart_inventory_data:
            total_smart_items = sum(len(items) for items in smart_inventory_data.get('filtered_items', {}).values())
            st.metric("Smart Fridge Items", total_smart_items)
        else:
            st.metric("Smart Fridge", "Connected")
    else:
        st.metric("Smart Fridge", "Offline")

st.divider()

# Smart Fridge Integration Demo Section
if smart_fridge_connected and inventory_mode == "🤖 Smart Fridge (Samsung Family Hub)":
    with st.expander("🔧 Smart Fridge Integration Demo", expanded=True):
        col_demo1, col_demo2 = st.columns(2)
        
        with col_demo1:
            st.subheader("🍎 AI Vision Inside Technology")
            st.write("**Samsung Family Hub Features:**")
            st.write("• Automatic food recognition (37+ fresh items)")
            st.write("• Expiry date tracking")
            st.write("• Real-time inventory updates")
            st.write("• Nutritional data integration")
            
            if smart_inventory_data:
                st.subheader("🏥 Health-Condition Filtering")
                filter_criteria = smart_inventory_data.get('filter_criteria', {})
                health_conds = filter_criteria.get('health_conditions', [])
                dietary_prefs = filter_criteria.get('dietary_restrictions', [])
                
                if health_conds:
                    st.write("**Active Health Filters:**")
                    for condition in health_conds:
                        st.write(f"• {condition.replace('_', ' ').title()}")
                
                if dietary_prefs:
                    st.write("**Dietary Restrictions:**")
                    for pref in dietary_prefs:
                        st.write(f"• {pref.replace('_', ' ').title()}")
        
        with col_demo2:
            if smart_inventory_data and 'meal_suggestions' in smart_inventory_data:
                st.subheader("🍽️ Smart Meal Suggestions")
                meal_suggestions = smart_inventory_data['meal_suggestions']
                
                for meal in meal_suggestions[:2]:  # Show top 2
                    with st.container():
                        st.write(f"**{meal['meal']}**")
                        st.write(f"*{meal['description']}*")
                        
                        # Health metrics
                        col_metric1, col_metric2 = st.columns(2)
                        with col_metric1:
                            gi = meal.get('estimated_gi', 'N/A')
                            if isinstance(gi, int) and gi <= 55:
                                st.success(f"GI: {gi} (Low)")
                            else:
                                st.info(f"GI: {gi}")
                        
                        with col_metric2:
                            sodium = meal.get('sodium_mg', 'N/A')
                            if isinstance(sodium, int) and sodium <= 300:
                                st.success(f"Na: {sodium}mg")
                            else:
                                st.info(f"Na: {sodium}mg")
                        
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
    
    # Build enhanced context with smart fridge data
    context = f"""
You are TasteMatch, an AI nutritional assistant with smart kitchen integration. Help the user with their dietary needs.

USER PROFILE:
- Health Conditions: {', '.join(conditions)}
- Diet Type: {diet_type}
- Allergies: {', '.join(allergies)}
- Max Cooking Time: {max_time} minutes
- Max Calories: {max_calories}
- Minimum Rating: {min_rating}
"""

    # Add smart fridge context if available
    if smart_inventory_data and inventory_mode == "🤖 Smart Fridge (Samsung Family Hub)":
        context += f"""
- SMART FRIDGE INTEGRATION: User has Samsung Family Hub with AI Vision Inside
- Available Ingredients (Health-Filtered): {available_ingredients}
- Health Filtering Applied: {', '.join(smart_inventory_data.get('filter_criteria', {}).get('health_conditions', []))}
- Inventory Last Updated: {smart_inventory_data.get('timestamp', 'Recently')}
"""
        
        # Add meal suggestions from smart fridge
        if 'meal_suggestions' in smart_inventory_data:
            context += "\n- SMART FRIDGE MEAL SUGGESTIONS:\n"
            for meal in smart_inventory_data['meal_suggestions']:
                context += f"  • {meal['meal']}: {meal['description']}\n"
    
    elif available_ingredients:
        context += f"\n- Available Ingredients (Manual Entry): {available_ingredients}"
    
    # Build conversation history
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

Provide a helpful, conversational response considering the conversation history and smart fridge integration if available. 
Consider their health conditions and preferences. Be encouraging and supportive. Keep the response concise (2-3 paragraphs).
Mention the recipes naturally in your response if relevant.

If using smart fridge data, acknowledge the technology and health filtering capabilities."""
        
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
    welcome_text = """
    👋 **Welcome to TasteMatch + Smart Fridge Integration!**
    
    I'm your AI-powered personal dietitian with smart kitchen integration. I can help you:
    - Find recipes based on your smart fridge inventory (Samsung Family Hub)
    - Get personalized meal recommendations for your health conditions
    - Plan nutritious meals within your dietary restrictions
    - Discover quick and healthy recipes using what you actually have
    
    **Try asking:**
    """
    
    if smart_fridge_connected:
        welcome_text += """
    - "What can I make with what's in my smart fridge?"
    - "Show me heart-healthy recipes using my current ingredients"
    - "Which items in my fridge are expiring soon?"
    - "Suggest a diabetic-friendly meal from my inventory"
    """
    else:
        welcome_text += """
    - "What can I make with chicken and rice?"
    - "I need a quick dinner under 30 minutes"
    - "Show me heart-healthy recipes"
    - "What's a good breakfast for diabetics?"
    """
    
    welcome_text += """
    
    🍎 **Smart Fridge Features:**
    - Real-time inventory from Samsung AI Vision Inside
    - Health-condition-aware ingredient filtering
    - Automatic expiry tracking and warnings
    - Nutrition-optimized meal suggestions
    """
    
    st.info(welcome_text)

# Footer
st.divider()
footer_text = "TasteMatch MVP + Smart Fridge Integration • Powered by Ollama + LangChain • 100% Local & Private"
if smart_fridge_connected:
    footer_text += " • 🍎 Samsung Family Hub Connected"
st.caption(footer_text)

# Instructions for starting the mock API
if not smart_fridge_connected:
    with st.expander("🔧 How to Enable Smart Fridge Demo"):
        st.write("""
        **To test the Samsung Family Hub integration:**
        
        1. Open a new terminal
        2. Navigate to your project directory  
        3. Run: `python mock_smartthings_api.py`
        4. Refresh this page
        
        This will start a mock Samsung SmartThings API that simulates a Family Hub refrigerator 
        with AI Vision Inside technology, including realistic food inventory and health-condition filtering.
        """)
