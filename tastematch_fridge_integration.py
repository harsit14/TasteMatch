"""
TasteMatch Smart Fridge Integration
Connects Samsung SmartThings Family Hub API with TasteMatch health-condition-aware recommendations
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartFridgeIntegration:
    """
    Integration layer between Samsung SmartThings Family Hub and TasteMatch
    Handles inventory retrieval and health-condition filtering
    """
    
    def __init__(self, api_base_url: str = "http://localhost:5000", device_id: str = None):
        self.api_base_url = api_base_url.rstrip('/')
        self.device_id = device_id or "12345678-1234-1234-abcd-123456789012"
        self.session = requests.Session()
        
        # Health condition configuration
        self.health_filters = {
            "diabetes": {
                "max_glycemic_index": 55,
                "max_sugar_g": 15,
                "preferred_fiber_g": 3
            },
            "hypertension": {
                "max_sodium_mg": 300,  # Per serving
                "preferred_potassium_foods": ["spinach", "carrots", "apples"]
            },
            "kidney_disease": {
                "max_sodium_mg": 150,
                "max_protein_g": 15,  # Per serving
                "max_phosphorus_mg": 200
            },
            "heart_disease": {
                "max_sodium_mg": 200,
                "max_saturated_fat_g": 3,
                "preferred_omega3_foods": ["fish", "walnuts"]
            }
        }
    
    def test_connection(self) -> bool:
        """Test connection to mock SmartThings API"""
        try:
            response = self.session.get(f"{self.api_base_url}/v1/devices/{self.device_id}/status")
            if response.status_code == 200:
                logger.info("✅ Successfully connected to Samsung SmartThings API")
                return True
            else:
                logger.error(f"❌ Failed to connect: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def get_full_inventory(self) -> Dict[str, Any]:
        """Retrieve complete refrigerator inventory"""
        try:
            url = f"{self.api_base_url}/v1/devices/{self.device_id}/components/main/capabilities/samsungce.aiVisionInside/foodInventory"
            response = self.session.get(url)
            response.raise_for_status()
            
            inventory_data = response.json()
            logger.info(f"📦 Retrieved {inventory_data.get('totalItems', 0)} items from fridge")
            
            return inventory_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve inventory: {e}")
            return {}
    
    def get_health_filtered_inventory(self, health_conditions: List[str], 
                                     dietary_restrictions: List[str] = None) -> Dict[str, Any]:
        """
        Get inventory filtered by health conditions and dietary restrictions
        This is TasteMatch's core differentiator
        """
        try:
            url = f"{self.api_base_url}/v1/devices/{self.device_id}/components/main/capabilities/samsungce.aiVisionInside/foodInventory/filter"
            
            payload = {
                "health_conditions": health_conditions,
                "dietary_restrictions": dietary_restrictions or []
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            filtered_data = response.json()
            logger.info(f"🏥 Applied health filters for: {', '.join(health_conditions)}")
            
            return filtered_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get filtered inventory: {e}")
            return {}
    
    def generate_tastematch_prompt(self, user_health_conditions: List[str], 
                                   dietary_preferences: List[str] = None) -> str:
        """
        Generate TasteMatch prompt with smart fridge inventory data
        This integrates with your existing RAG + Ollama system
        """
        
        # Get health-filtered inventory
        filtered_inventory = self.get_health_filtered_inventory(
            user_health_conditions, 
            dietary_preferences
        )
        
        if not filtered_inventory:
            return "No smart fridge data available. Please check your Samsung Family Hub connection."
        
        # Build context-rich prompt for TasteMatch
        prompt_parts = [
            "🍎 SMART FRIDGE INTEGRATION - TasteMatch Analysis",
            f"📅 Inventory Last Updated: {filtered_inventory.get('timestamp', 'Unknown')}",
            "",
            "👤 USER HEALTH PROFILE:",
            f"   • Health Conditions: {', '.join(user_health_conditions)}",
        ]
        
        if dietary_preferences:
            prompt_parts.append(f"   • Dietary Preferences: {', '.join(dietary_preferences)}")
        
        prompt_parts.extend([
            "",
            "🥗 AVAILABLE INGREDIENTS (Health-Filtered):",
        ])
        
        # Add categorized inventory
        filtered_items = filtered_inventory.get('filtered_items', {})
        total_available_items = 0
        
        for category, items in filtered_items.items():
            if items:
                category_display = category.replace('_', ' ').title()
                prompt_parts.append(f"   📂 {category_display}:")
                
                for item in items:
                    expiry_info = self._format_expiry_warning(item.get('expiry_date'))
                    nutrition_summary = self._format_nutrition_summary(item.get('nutrition_info', {}))
                    
                    prompt_parts.append(
                        f"      • {item['name']} (Qty: {item['quantity']} {item['unit']}) {expiry_info} {nutrition_summary}"
                    )
                    total_available_items += 1
                
                prompt_parts.append("")
        
        # Add meal suggestions from API
        meal_suggestions = filtered_inventory.get('meal_suggestions', [])
        if meal_suggestions:
            prompt_parts.extend([
                "🍽️ RECOMMENDED MEALS (Based on Available Ingredients):",
            ])
            
            for meal in meal_suggestions:
                prompt_parts.extend([
                    f"   • {meal['meal']}",
                    f"     - {meal['description']}",
                    f"     - Estimated Glycemic Impact: {meal.get('estimated_gi', 'N/A')}",
                    f"     - Sodium Content: {meal.get('sodium_mg', 'N/A')}mg",
                    ""
                ])
        
        # Add health-specific guidance
        prompt_parts.extend([
            "⚕️ TASTEMATCH HEALTH GUIDANCE REQUEST:",
            f"Based on the {total_available_items} health-appropriate items in my smart refrigerator",
            "and my health conditions, please provide:",
            "",
            "1. 🎯 Meal recommendations that use available ingredients",
            "2. 🚫 Any ingredients I should avoid despite being in my fridge",  
            "3. 📊 Portion size guidance for my health conditions",
            "4. ⏰ Meal timing suggestions (especially for diabetes management)",
            "5. 🛒 Priority shopping list items to complement current inventory",
            "",
            "Focus on evidence-based nutrition advice specific to my health conditions."
        ])
        
        return "\n".join(prompt_parts)
    
    def _format_expiry_warning(self, expiry_date: str) -> str:
        """Format expiry date with warning if item is expiring soon"""
        try:
            expiry = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
            days_until_expiry = (expiry - datetime.now(expiry.tzinfo)).days
            
            if days_until_expiry < 0:
                return "⚠️ EXPIRED"
            elif days_until_expiry <= 2:
                return f"🔶 Expires in {days_until_expiry} day{'s' if days_until_expiry != 1 else ''}"
            elif days_until_expiry <= 5:
                return f"🟡 {days_until_expiry} days left"
            else:
                return ""
        except:
            return ""
    
    def _format_nutrition_summary(self, nutrition_info: Dict[str, Any]) -> str:
        """Format key nutritional information for display"""
        if not nutrition_info:
            return ""
        
        parts = []
        
        # Key metrics for health conditions
        if 'glycemic_index' in nutrition_info:
            gi = nutrition_info['glycemic_index']
            if gi <= 55:
                parts.append(f"GI: {gi}✅")
            elif gi <= 70:
                parts.append(f"GI: {gi}🟡") 
            else:
                parts.append(f"GI: {gi}🔴")
        
        if 'sodium_mg' in nutrition_info:
            sodium = nutrition_info['sodium_mg']
            if sodium <= 140:
                parts.append(f"Na: {sodium}mg✅")
            elif sodium <= 400:
                parts.append(f"Na: {sodium}mg🟡")
            else:
                parts.append(f"Na: {sodium}mg🔴")
        
        return f"[{', '.join(parts)}]" if parts else ""
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """Get summary stats for dashboard display"""
        full_inventory = self.get_full_inventory()
        
        if not full_inventory:
            return {}
        
        summary_data = full_inventory.get('summary', {})
        categories = full_inventory.get('categories', {})
        
        return {
            "total_items": full_inventory.get('totalItems', 0),
            "categories": {cat: len(items) for cat, items in categories.items()},
            "expiring_soon": len(summary_data.get('expiring_soon', [])),
            "expired": len(summary_data.get('expired', [])),
            "low_sodium_count": len(summary_data.get('low_sodium_items', [])),
            "diabetic_friendly_count": len(summary_data.get('diabetic_friendly', [])),
            "last_updated": full_inventory.get('lastUpdated', 'Unknown')
        }

# Example usage and testing functions
def demo_smart_fridge_integration():
    """Demonstration of TasteMatch + Smart Fridge integration"""
    
    print("🔧 TasteMatch Smart Fridge Integration Demo")
    print("=" * 50)
    
    # Initialize integration
    fridge = SmartFridgeIntegration()
    
    # Test connection
    if not fridge.test_connection():
        print("❌ Could not connect to mock Samsung API. Please start mock_smartthings_api.py first.")
        return
    
    # Get inventory summary
    print("\n📊 INVENTORY SUMMARY:")
    summary = fridge.get_inventory_summary()
    for key, value in summary.items():
        print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    # Demo user with diabetes and hypertension
    print("\n👤 DEMO USER PROFILE:")
    health_conditions = ["diabetes", "hypertension"]
    dietary_prefs = ["low_carb"]
    print(f"   • Health Conditions: {', '.join(health_conditions)}")
    print(f"   • Dietary Preferences: {', '.join(dietary_prefs)}")
    
    # Generate TasteMatch prompt
    print("\n🤖 GENERATING TASTEMATCH PROMPT:")
    prompt = fridge.generate_tastematch_prompt(health_conditions, dietary_prefs)
    
    # Save prompt for integration with existing TasteMatch system
    with open('/home/claude/tastematch_fridge_prompt.txt', 'w') as f:
        f.write(prompt)
    
    print("✅ TasteMatch prompt generated and saved to tastematch_fridge_prompt.txt")
    print(f"📝 Prompt length: {len(prompt)} characters")
    
    # Show preview
    print("\n📋 PROMPT PREVIEW:")
    print("-" * 50)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 50)
    
    return prompt

if __name__ == "__main__":
    demo_smart_fridge_integration()
