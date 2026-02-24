"""
Mock Samsung SmartThings API for Family Hub Refrigerator
Simulates AI Vision Inside food tracking and inventory management
"""

from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import json
import random

app = Flask(__name__)

# Mock device ID for Samsung Family Hub
DEVICE_ID = "12345678-1234-1234-abcd-123456789012"

# Realistic food inventory data based on AI Vision Inside capabilities
MOCK_INVENTORY = {
    "fresh_produce": [
        {
            "id": "item_001",
            "name": "Apples",
            "quantity": 6,
            "unit": "pieces",
            "location": "main_compartment_crisper",
            "added_date": "2026-02-20T08:30:00Z",
            "expiry_date": "2026-03-05T00:00:00Z",
            "confidence": 0.95,
            "recognition_method": "ai_vision",
            "nutrition_info": {
                "calories_per_unit": 95,
                "carbs_g": 25,
                "fiber_g": 4,
                "sugar_g": 19,
                "sodium_mg": 2,
                "glycemic_index": 36
            }
        },
        {
            "id": "item_002", 
            "name": "Carrots",
            "quantity": 8,
            "unit": "pieces",
            "location": "main_compartment_crisper",
            "added_date": "2026-02-18T19:45:00Z",
            "expiry_date": "2026-02-28T00:00:00Z",
            "confidence": 0.92,
            "recognition_method": "ai_vision",
            "nutrition_info": {
                "calories_per_unit": 25,
                "carbs_g": 6,
                "fiber_g": 2,
                "sugar_g": 3,
                "sodium_mg": 42,
                "glycemic_index": 35
            }
        },
        {
            "id": "item_003",
            "name": "Spinach",
            "quantity": 1,
            "unit": "bag",
            "location": "main_compartment_crisper", 
            "added_date": "2026-02-21T14:20:00Z",
            "expiry_date": "2026-02-26T00:00:00Z",
            "confidence": 0.88,
            "recognition_method": "ai_vision",
            "nutrition_info": {
                "calories_per_unit": 20,
                "carbs_g": 3,
                "fiber_g": 2,
                "sugar_g": 0,
                "sodium_mg": 65,
                "glycemic_index": 15
            }
        }
    ],
    "packaged_foods": [
        {
            "id": "item_004",
            "name": "Greek Yogurt",
            "brand": "Chobani",
            "quantity": 4,
            "unit": "containers",
            "location": "main_compartment_shelf2",
            "added_date": "2026-02-19T10:15:00Z", 
            "expiry_date": "2026-03-10T00:00:00Z",
            "confidence": 0.98,
            "recognition_method": "barcode_scan",
            "nutrition_info": {
                "calories_per_unit": 100,
                "protein_g": 17,
                "carbs_g": 6,
                "sugar_g": 4,
                "sodium_mg": 65,
                "glycemic_index": 11
            }
        },
        {
            "id": "item_005",
            "name": "Whole Wheat Bread",
            "brand": "Dave's Killer Bread", 
            "quantity": 1,
            "unit": "loaf",
            "location": "main_compartment_shelf1",
            "added_date": "2026-02-20T16:30:00Z",
            "expiry_date": "2026-02-27T00:00:00Z",
            "confidence": 0.94,
            "recognition_method": "package_recognition",
            "nutrition_info": {
                "calories_per_unit": 110,
                "protein_g": 5,
                "carbs_g": 22,
                "fiber_g": 3,
                "sugar_g": 5,
                "sodium_mg": 170,
                "glycemic_index": 51
            }
        }
    ],
    "dairy_proteins": [
        {
            "id": "item_006",
            "name": "Chicken Breast",
            "quantity": 2,
            "unit": "lbs",
            "location": "main_compartment_meat_drawer",
            "added_date": "2026-02-22T11:00:00Z",
            "expiry_date": "2026-02-25T00:00:00Z",
            "confidence": 0.85,
            "recognition_method": "manual_entry",
            "nutrition_info": {
                "calories_per_unit": 540,
                "protein_g": 101,
                "carbs_g": 0,
                "fat_g": 12,
                "sodium_mg": 260,
                "glycemic_index": 0
            }
        },
        {
            "id": "item_007",
            "name": "Eggs",
            "quantity": 10,
            "unit": "pieces",
            "location": "main_compartment_door",
            "added_date": "2026-02-19T07:45:00Z",
            "expiry_date": "2026-03-15T00:00:00Z",
            "confidence": 0.97,
            "recognition_method": "ai_vision",
            "nutrition_info": {
                "calories_per_unit": 70,
                "protein_g": 6,
                "carbs_g": 1,
                "fat_g": 5,
                "sodium_mg": 70,
                "glycemic_index": 0
            }
        }
    ]
}

@app.route('/v1/devices/<device_id>/status', methods=['GET'])
def get_device_status(device_id):
    """
    Mock Samsung SmartThings device status endpoint
    Returns refrigerator component status including food inventory
    """
    if device_id != DEVICE_ID:
        return jsonify({"error": "Device not found"}), 404
    
    # Simulate realistic SmartThings API response structure
    status = {
        "deviceId": device_id,
        "components": {
            "main": {
                "contactSensor": {
                    "contact": {
                        "value": "closed",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                },
                "temperatureMeasurement": {
                    "temperature": {
                        "value": 37,
                        "unit": "F",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                },
                "samsungce.aiVisionInside": {
                    "foodInventory": {
                        "value": flatten_inventory_for_api(),
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    },
                    "lastScanTime": {
                        "value": datetime.utcnow().isoformat() + "Z",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                }
            },
            "freezer": {
                "temperatureMeasurement": {
                    "temperature": {
                        "value": 0,
                        "unit": "F", 
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                },
                "contactSensor": {
                    "contact": {
                        "value": "closed",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                }
            },
            "icemaker": {
                "switch": {
                    "switch": {
                        "value": "on",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                }
            }
        }
    }
    
    return jsonify(status)

@app.route('/v1/devices/<device_id>/components/main/capabilities/samsungce.aiVisionInside/foodInventory', methods=['GET'])
def get_food_inventory(device_id):
    """
    Dedicated endpoint for food inventory data
    This is what TasteMatch would primarily use
    """
    if device_id != DEVICE_ID:
        return jsonify({"error": "Device not found"}), 404
    
    # Return detailed food inventory for TasteMatch processing
    inventory_response = {
        "deviceId": device_id,
        "lastUpdated": datetime.utcnow().isoformat() + "Z",
        "totalItems": sum(len(category) for category in MOCK_INVENTORY.values()),
        "categories": MOCK_INVENTORY,
        "summary": {
            "expiring_soon": get_expiring_items(days=3),
            "expired": get_expired_items(),
            "low_sodium_items": get_low_sodium_items(),
            "diabetic_friendly": get_diabetic_friendly_items()
        }
    }
    
    return jsonify(inventory_response)

@app.route('/v1/devices/<device_id>/components/main/capabilities/samsungce.aiVisionInside/foodInventory/filter', methods=['POST'])
def filter_inventory_by_health_condition(device_id):
    """
    TasteMatch-specific endpoint to filter inventory by health conditions
    This is where we add our health-condition-aware logic
    """
    if device_id != DEVICE_ID:
        return jsonify({"error": "Device not found"}), 404
    
    data = request.get_json()
    health_conditions = data.get('health_conditions', [])
    dietary_restrictions = data.get('dietary_restrictions', [])
    
    # Apply health condition filters
    filtered_inventory = apply_health_filters(health_conditions, dietary_restrictions)
    
    response = {
        "deviceId": device_id,
        "filtered_items": filtered_inventory,
        "filter_criteria": {
            "health_conditions": health_conditions,
            "dietary_restrictions": dietary_restrictions
        },
        "meal_suggestions": generate_meal_suggestions(filtered_inventory, health_conditions),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return jsonify(response)

# Helper functions

def flatten_inventory_for_api():
    """Convert inventory to flat list for basic SmartThings API compatibility"""
    items = []
    for category, category_items in MOCK_INVENTORY.items():
        for item in category_items:
            items.append({
                "id": item["id"],
                "name": item["name"],
                "quantity": item["quantity"],
                "location": item["location"],
                "expiry": item["expiry_date"]
            })
    return items

def get_expiring_items(days=3):
    """Get items expiring within specified days"""
    cutoff = datetime.utcnow() + timedelta(days=days)
    expiring = []
    
    for category, items in MOCK_INVENTORY.items():
        for item in items:
            expiry = datetime.fromisoformat(item["expiry_date"].replace('Z', '+00:00'))
            if expiry <= cutoff:
                expiring.append(item)
    
    return expiring

def get_expired_items():
    """Get items that have already expired"""
    now = datetime.utcnow()
    expired = []
    
    for category, items in MOCK_INVENTORY.items():
        for item in items:
            expiry = datetime.fromisoformat(item["expiry_date"].replace('Z', '+00:00'))
            if expiry <= now:
                expired.append(item)
    
    return expired

def get_low_sodium_items():
    """Filter items with low sodium content (<140mg per serving)"""
    low_sodium = []
    
    for category, items in MOCK_INVENTORY.items():
        for item in items:
            if item.get("nutrition_info", {}).get("sodium_mg", 0) < 140:
                low_sodium.append(item)
    
    return low_sodium

def get_diabetic_friendly_items():
    """Filter items with low glycemic index (<55)"""
    diabetic_friendly = []
    
    for category, items in MOCK_INVENTORY.items():
        for item in items:
            gi = item.get("nutrition_info", {}).get("glycemic_index", 100)
            if gi < 55:
                diabetic_friendly.append(item)
    
    return diabetic_friendly

def apply_health_filters(health_conditions, dietary_restrictions):
    """Apply health condition and dietary restriction filters to inventory"""
    filtered = {}
    
    for category, items in MOCK_INVENTORY.items():
        filtered_items = []
        
        for item in items:
            include_item = True
            nutrition = item.get("nutrition_info", {})
            
            # Apply health condition filters
            if "diabetes" in health_conditions:
                # Filter high glycemic index foods
                if nutrition.get("glycemic_index", 0) > 70:
                    include_item = False
                    
            if "hypertension" in health_conditions:
                # Filter high sodium foods (>480mg per serving is high)
                if nutrition.get("sodium_mg", 0) > 480:
                    include_item = False
                    
            if "kidney_disease" in health_conditions:
                # Filter high sodium and high protein
                if (nutrition.get("sodium_mg", 0) > 200 or 
                    nutrition.get("protein_g", 0) > 20):
                    include_item = False
            
            # Apply dietary restrictions
            if "low_carb" in dietary_restrictions:
                if nutrition.get("carbs_g", 0) > 15:
                    include_item = False
                    
            if "vegetarian" in dietary_restrictions:
                if item["name"].lower() in ["chicken breast", "beef", "pork", "fish"]:
                    include_item = False
            
            if include_item:
                filtered_items.append(item)
        
        if filtered_items:
            filtered[category] = filtered_items
    
    return filtered

def generate_meal_suggestions(filtered_inventory, health_conditions):
    """Generate meal suggestions based on available ingredients and health conditions"""
    
    # Simple meal suggestion logic based on available ingredients
    suggestions = []
    
    # Check what ingredient categories are available
    has_protein = "dairy_proteins" in filtered_inventory
    has_vegetables = "fresh_produce" in filtered_inventory  
    has_carbs = "packaged_foods" in filtered_inventory
    
    if has_protein and has_vegetables:
        if "diabetes" in health_conditions:
            suggestions.append({
                "meal": "Grilled Chicken & Vegetable Salad",
                "description": "Low-carb, diabetes-friendly meal",
                "ingredients_used": ["chicken_breast", "spinach", "carrots"],
                "estimated_gi": 25,
                "sodium_mg": 300
            })
        else:
            suggestions.append({
                "meal": "Chicken Stir Fry",
                "description": "Balanced protein and vegetables",
                "ingredients_used": ["chicken_breast", "carrots", "spinach"],
                "estimated_gi": 35,
                "sodium_mg": 450
            })
    
    if has_vegetables and "greek_yogurt" in str(filtered_inventory):
        suggestions.append({
            "meal": "Greek Yogurt Parfait with Fruit",
            "description": "High protein, probiotic-rich breakfast",
            "ingredients_used": ["greek_yogurt", "apples"],
            "estimated_gi": 30,
            "sodium_mg": 70
        })
    
    return suggestions

if __name__ == '__main__':
    print(f"🔧 Mock Samsung SmartThings API starting...")
    print(f"📱 Device ID: {DEVICE_ID}")
    print(f"🍎 Mock inventory contains {sum(len(items) for items in MOCK_INVENTORY.values())} food items")
    print(f"🌐 API endpoints:")
    print(f"   • Device Status: GET /v1/devices/{DEVICE_ID}/status")
    print(f"   • Food Inventory: GET /v1/devices/{DEVICE_ID}/components/main/capabilities/samsungce.aiVisionInside/foodInventory")
    print(f"   • Health Filtering: POST /v1/devices/{DEVICE_ID}/components/main/capabilities/samsungce.aiVisionInside/foodInventory/filter")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
