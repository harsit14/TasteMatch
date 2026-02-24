"""
TasteMatch + Smart Fridge Demo
Streamlit app demonstrating health-condition-aware meal recommendations using smart refrigerator data
"""

import streamlit as st
import sys
import os
import requests
import json
from datetime import datetime
import subprocess
import time

# Add current directory to path for imports
sys.path.append('/home/claude')

try:
    from tastematch_fridge_integration import SmartFridgeIntegration
except ImportError:
    st.error("Could not import TasteMatch integration. Please ensure tastematch_fridge_integration.py is available.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="TasteMatch + Smart Fridge Demo",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 0.5rem 0;
    }
    .health-warning {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_status():
    """Check if the mock Samsung API is running"""
    try:
        response = requests.get("http://localhost:5000/v1/devices/12345678-1234-1234-abcd-123456789012/status", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_mock_api():
    """Start the mock Samsung API in background"""
    try:
        # Start the API in background
        subprocess.Popen([
            sys.executable, 
            '/home/claude/mock_smartthings_api.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for it to start
        time.sleep(3)
        return True
    except Exception as e:
        st.error(f"Failed to start mock API: {e}")
        return False

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🍎 TasteMatch + Smart Fridge Integration Demo</h1>
        <p>Health-Condition-Aware Nutrition Guidance Using Samsung Family Hub Data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - User Profile Setup
    st.sidebar.header("👤 User Health Profile")
    
    # Health conditions selection
    health_conditions = st.sidebar.multiselect(
        "Select Health Conditions:",
        ["diabetes", "hypertension", "kidney_disease", "heart_disease", "obesity"],
        default=["diabetes", "hypertension"],
        help="Choose the health conditions that apply to this user"
    )
    
    # Dietary preferences
    dietary_prefs = st.sidebar.multiselect(
        "Dietary Preferences:",
        ["low_carb", "low_sodium", "vegetarian", "gluten_free", "keto"],
        default=["low_carb"],
        help="Additional dietary restrictions or preferences"
    )
    
    st.sidebar.markdown("---")
    
    # API Connection Status
    st.sidebar.header("🔌 Smart Fridge Connection")
    api_running = check_api_status()
    
    if api_running:
        st.sidebar.success("✅ Samsung SmartThings API Connected")
    else:
        st.sidebar.error("❌ Samsung SmartThings API Disconnected")
        if st.sidebar.button("🚀 Start Mock API"):
            with st.spinner("Starting Samsung Family Hub simulator..."):
                if start_mock_api():
                    time.sleep(2)
                    st.rerun()
    
    if not api_running:
        st.warning("⚠️ Please start the Samsung SmartThings API simulator to see the demo.")
        st.code("python /home/claude/mock_smartthings_api.py", language="bash")
        return
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    # Left column - Smart Fridge Data
    with col1:
        st.header("🧊 Samsung Family Hub Data")
        
        # Initialize integration
        fridge = SmartFridgeIntegration()
        
        # Get inventory summary
        summary = fridge.get_inventory_summary()
        
        if summary:
            # Display metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric("Total Items", summary.get('total_items', 0))
            
            with metric_col2:
                st.metric("Expiring Soon", summary.get('expiring_soon', 0))
            
            with metric_col3:
                st.metric("Diabetic Friendly", summary.get('diabetic_friendly_count', 0))
            
            # Show last updated
            st.caption(f"Last Updated: {summary.get('last_updated', 'Unknown')}")
            
            # Category breakdown
            st.subheader("📦 Inventory by Category")
            categories = summary.get('categories', {})
            
            for category, count in categories.items():
                if count > 0:
                    st.markdown(f"**{category.replace('_', ' ').title()}**: {count} items")
            
            # Health filtering demo
            st.subheader("🏥 Health-Filtered Inventory")
            
            if health_conditions:
                filtered_data = fridge.get_health_filtered_inventory(health_conditions, dietary_prefs)
                
                if filtered_data and 'filtered_items' in filtered_data:
                    filtered_items = filtered_data['filtered_items']
                    
                    for category, items in filtered_items.items():
                        if items:
                            with st.expander(f"📂 {category.replace('_', ' ').title()} ({len(items)} items)"):
                                for item in items:
                                    nutrition = item.get('nutrition_info', {})
                                    
                                    # Item display with health indicators
                                    col_item, col_nutrition = st.columns([2, 1])
                                    
                                    with col_item:
                                        st.write(f"**{item['name']}**")
                                        st.write(f"Quantity: {item['quantity']} {item['unit']}")
                                        
                                        # Expiry warning
                                        expiry_date = item.get('expiry_date', '')
                                        if expiry_date:
                                            try:
                                                expiry = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                                                days_left = (expiry - datetime.now(expiry.tzinfo)).days
                                                
                                                if days_left < 0:
                                                    st.error("⚠️ EXPIRED")
                                                elif days_left <= 2:
                                                    st.warning(f"🔶 Expires in {days_left} day(s)")
                                            except:
                                                pass
                                    
                                    with col_nutrition:
                                        # Health indicators
                                        if 'glycemic_index' in nutrition:
                                            gi = nutrition['glycemic_index']
                                            if gi <= 55:
                                                st.success(f"GI: {gi} ✅")
                                            else:
                                                st.warning(f"GI: {gi} ⚠️")
                                        
                                        if 'sodium_mg' in nutrition:
                                            sodium = nutrition['sodium_mg']
                                            if sodium <= 140:
                                                st.success(f"Na: {sodium}mg ✅")
                                            else:
                                                st.warning(f"Na: {sodium}mg ⚠️")
                                    
                                    st.markdown("---")
                else:
                    st.warning("No items match your health condition filters.")
            else:
                st.info("Select health conditions to see filtered inventory.")
        
        else:
            st.error("Could not retrieve smart fridge data.")
    
    # Right column - TasteMatch Integration
    with col2:
        st.header("🤖 TasteMatch Analysis")
        
        if health_conditions and api_running:
            
            # Generate TasteMatch prompt
            with st.spinner("Generating health-aware meal recommendations..."):
                prompt = fridge.generate_tastematch_prompt(health_conditions, dietary_prefs)
            
            # Show integration success
            st.markdown("""
            <div class="success-box">
                ✅ <strong>Smart Fridge Integration Active</strong><br>
                TasteMatch is now analyzing your refrigerator contents with your health conditions in mind.
            </div>
            """, unsafe_allow_html=True)
            
            # Mock TasteMatch response (in real app, this would go to Ollama)
            st.subheader("🍽️ Personalized Meal Recommendations")
            
            # Get meal suggestions from filtered inventory
            filtered_data = fridge.get_health_filtered_inventory(health_conditions, dietary_prefs)
            meal_suggestions = filtered_data.get('meal_suggestions', [])
            
            if meal_suggestions:
                for i, meal in enumerate(meal_suggestions, 1):
                    with st.expander(f"🍽️ Meal Option {i}: {meal['meal']}"):
                        st.write(f"**Description:** {meal['description']}")
                        
                        # Health metrics
                        col_gi, col_sodium = st.columns(2)
                        with col_gi:
                            gi = meal.get('estimated_gi', 'N/A')
                            if isinstance(gi, int) and gi <= 55:
                                st.success(f"Glycemic Impact: {gi} (Low)")
                            else:
                                st.info(f"Glycemic Impact: {gi}")
                        
                        with col_sodium:
                            sodium = meal.get('sodium_mg', 'N/A')
                            if isinstance(sodium, int) and sodium <= 300:
                                st.success(f"Sodium: {sodium}mg (Low)")
                            else:
                                st.info(f"Sodium: {sodium}mg")
                        
                        # Ingredients used
                        ingredients = meal.get('ingredients_used', [])
                        if ingredients:
                            st.write("**Uses these ingredients from your fridge:**")
                            for ingredient in ingredients:
                                st.write(f"• {ingredient.replace('_', ' ').title()}")
            
            # Health-specific guidance
            st.subheader("⚕️ Health Guidance")
            
            if "diabetes" in health_conditions:
                st.markdown("""
                <div class="health-warning">
                    <strong>🩺 Diabetes Management Tips:</strong><br>
                    • Focus on low glycemic index foods (GI < 55)<br>
                    • Pair carbohydrates with protein or fiber<br>
                    • Monitor portion sizes carefully<br>
                    • Consider meal timing with medication schedule
                </div>
                """, unsafe_allow_html=True)
            
            if "hypertension" in health_conditions:
                st.markdown("""
                <div class="health-warning">
                    <strong>💓 Blood Pressure Management:</strong><br>
                    • Limit sodium to <300mg per meal<br>
                    • Emphasize potassium-rich foods<br>
                    • Choose fresh over processed foods<br>
                    • Follow DASH diet principles
                </div>
                """, unsafe_allow_html=True)
            
            # Show the prompt that would be sent to Ollama
            with st.expander("🔍 View TasteMatch Prompt (Technical Details)"):
                st.text_area("Generated Prompt for Ollama LLM:", prompt, height=300)
                
                # Integration stats
                st.subheader("Integration Statistics")
                st.write(f"• Prompt Length: {len(prompt)} characters")
                st.write(f"• Health Conditions Applied: {len(health_conditions)}")
                st.write(f"• Dietary Filters: {len(dietary_prefs)}")
                st.write(f"• Available Ingredients: {len([item for category in filtered_data.get('filtered_items', {}).values() for item in category])}")
        
        else:
            st.info("👈 Select health conditions and ensure API connection to see TasteMatch analysis.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    ### 🎯 Academic Project Highlights
    
    **Novel Contribution:** First system to combine smart refrigerator inventory with health-condition-specific meal planning
    
    **Technical Innovation:**
    - Real-time food inventory from Samsung Family Hub AI Vision Inside
    - Health condition filtering (diabetes, hypertension, kidney disease)
    - Local LLM processing for privacy-preserved nutrition guidance
    - Integration with existing dietary assessment tools
    
    **Market Differentiation:** While Samsung focuses on convenience, TasteMatch adds the missing health intelligence layer.
    """)

if __name__ == "__main__":
    main()
