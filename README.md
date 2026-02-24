# TasteMatch + Smart Refrigerator Integration

> **Health-Condition-Aware Nutrition Guidance Using Smart Home Appliances**  
> Academic Project - Spring 2026

## 🎯 Project Overview

This project addresses a critical gap identified in current dietary intake tools by integrating Samsung Family Hub smart refrigerator data with health-condition-specific meal planning. While existing smart fridges focus on convenience and inventory management, **TasteMatch adds the missing health intelligence layer** for users with chronic conditions like diabetes and hypertension.

### Novel Contribution

- **First system** to combine real-time smart refrigerator inventory with health-condition-specific meal planning
- **Health-condition filtering** that goes beyond generic calorie tracking
- **Privacy-first architecture** using local LLM processing (Ollama) for sensitive health data
- **Evidence-based nutrition guidance** tailored to specific chronic conditions

## 🔬 Academic Context

### Research Gap Analysis

Based on comprehensive research of current dietary tools and smart appliance capabilities, we identified three key limitations:

1. **Traditional dietary assessment tools** suffer from 4.6-42% underreporting rates and lack real-time data
2. **Mobile nutrition apps** focus on generic tracking without health-condition-specific guidance  
3. **Smart refrigerators** provide inventory management but no health-aware meal planning

### Market Opportunity

- Smart refrigerator market projected to reach $125.7 billion
- No current solution adequately addresses chronic disease nutrition management
- Samsung, LG, and GE focus on convenience rather than health outcomes

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Samsung Family  │    │ TasteMatch       │    │ Health-Aware    │
│ Hub API         │───▶│ Integration      │───▶│ Meal            │
│ (AI Vision)     │    │ Layer            │    │ Recommendations │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Food Inventory  │    │ Health Condition │    │ Local LLM       │
│ • 37+ fresh     │    │ Filters:         │    │ (Ollama)        │
│   foods         │    │ • Diabetes       │    │ Processing      │
│ • 50+ packaged  │    │ • Hypertension   │    │                 │
│ • Expiry dates  │    │ • Kidney Disease │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
tastematch-smart-fridge/
├── mock_smartthings_api.py          # Samsung SmartThings API simulator
├── tastematch_fridge_integration.py # Integration layer between fridge and TasteMatch
├── tastematch_smart_fridge_demo.py  # Streamlit demo interface
├── run_demo.py                      # One-click demo launcher
├── requirements.txt                 # Python dependencies
├── setup_demo.sh                    # Setup script
└── README.md                        # This file
```

### Key Components

1. **Mock Samsung SmartThings API** (`mock_smartthings_api.py`)
   - Simulates Family Hub refrigerator with AI Vision Inside
   - Realistic food inventory with nutrition data
   - Health condition filtering endpoints

2. **TasteMatch Integration Layer** (`tastematch_fridge_integration.py`)
   - Bridges smart fridge data with health guidance system
   - Applies condition-specific filters (diabetes, hypertension, kidney disease)
   - Generates context-rich prompts for LLM processing

3. **Streamlit Demo Interface** (`tastematch_smart_fridge_demo.py`)
   - Interactive demonstration of the complete system
   - Real-time inventory filtering based on health conditions
   - Visual representation of TasteMatch's value proposition

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### One-Click Demo
```bash
# Setup and run complete demo
bash setup_demo.sh
python run_demo.py
```

This will start:
- Samsung SmartThings API simulator on `http://localhost:5000`
- TasteMatch demo interface on `http://localhost:8501`

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Terminal 1: Start Samsung API simulator
python mock_smartthings_api.py

# Terminal 2: Start TasteMatch demo
streamlit run tastematch_smart_fridge_demo.py
```

## 🔧 Usage Guide

### Demo Workflow

1. **Configure Health Profile**
   - Select health conditions (diabetes, hypertension, etc.)
   - Choose dietary preferences (low-carb, low-sodium)

2. **View Smart Fridge Data**  
   - See realistic inventory from Samsung Family Hub
   - Review AI Vision Inside food recognition results
   - Check expiry dates and nutritional information

3. **Experience Health Filtering**
   - Watch inventory get filtered based on health conditions
   - See diabetic-friendly foods (low glycemic index)
   - Identify low-sodium options for hypertension

4. **Get TasteMatch Recommendations**
   - Receive meal suggestions using available ingredients
   - See health-specific guidance and warnings
   - View the generated prompt for LLM processing

### Health Condition Filters

| Condition | Filter Criteria | Examples |
|-----------|----------------|----------|
| **Diabetes** | Glycemic Index < 55, Low sugar | Spinach, chicken breast, eggs |
| **Hypertension** | Sodium < 300mg per serving | Fresh fruits, unsalted nuts |
| **Kidney Disease** | Low sodium + protein limits | Limited dairy, fresh vegetables |
| **Heart Disease** | Low sodium + saturated fat | Lean proteins, whole grains |

## 📊 Academic Impact

### Addresses Professor's Requirements

✅ **Challenges of current dietary tools**: Documented 4.6-42% underreporting, lack of health-specific guidance  
✅ **Hardware solution exploration**: Samsung SmartThings API integration with Family Hub  
✅ **Augmenting existing solutions**: Building health intelligence on top of Samsung's platform  

### Research Contributions

1. **Gap Analysis**: Comprehensive review of dietary tool limitations and smart appliance capabilities
2. **Technical Innovation**: First proof-of-concept for health-aware smart kitchen integration  
3. **Privacy Architecture**: Local processing approach for sensitive health data
4. **Market Positioning**: Clear differentiation strategy for academic and commercial development

## 🏥 Health Condition Support

### Currently Implemented
- **Type 2 Diabetes**: Glycemic index filtering, carbohydrate awareness
- **Hypertension**: Sodium restrictions, DASH diet principles  
- **Kidney Disease**: Protein and sodium limitations
- **Heart Disease**: Saturated fat and sodium controls

### Planned Extensions
- **Celiac Disease**: Gluten-free ingredient detection
- **Food Allergies**: Allergen identification and avoidance
- **Gestational Diabetes**: Pregnancy-specific nutrition guidance

## 🔮 Future Development

### Phase 1: Foundation (Current)
- ✅ Mock Samsung API with realistic data
- ✅ Health condition filtering logic
- ✅ Streamlit demonstration interface

### Phase 2: Real Integration (Next Semester)
- Samsung SmartThings Developer Program enrollment
- Live API integration with actual Family Hub devices
- Beta testing with users who have chronic conditions

### Phase 3: Production Ready
- Multiple smart fridge platform support (LG ThinQ, GE Profile)
- Clinical validation of nutrition recommendations
- Integration with electronic health records (EHR)

## 🔍 Technical Details

### Samsung SmartThings API Simulation

The mock API replicates the actual Samsung Family Hub data structure:

```json
{
  "deviceId": "12345678-1234-1234-abcd-123456789012",
  "components": {
    "main": {
      "samsungce.aiVisionInside": {
        "foodInventory": {
          "value": [...],
          "timestamp": "2026-02-23T10:30:00Z"
        }
      }
    }
  }
}
```

### Health Filtering Algorithm

```python
def apply_health_filters(health_conditions, dietary_restrictions):
    for item in inventory:
        if "diabetes" in health_conditions:
            if item.glycemic_index > 55:
                exclude_item()
        
        if "hypertension" in health_conditions:
            if item.sodium_mg > 300:
                exclude_item()
```

## 📈 Academic Presentation

### Key Talking Points

1. **Problem Definition**: Current tools don't bridge inventory awareness with health guidance
2. **Technical Solution**: Health-condition filtering layer on smart appliance data  
3. **Market Differentiation**: First health-intelligent kitchen system
4. **Academic Rigor**: Evidence-based nutrition filtering, literature-supported gap analysis
5. **Future Viability**: Clear path from proof-of-concept to commercial product

### Demonstration Flow

1. Show research document (gap analysis)
2. Demo mock Samsung API with realistic data
3. Live filtering demonstration (diabetes + hypertension user)
4. TasteMatch prompt generation for existing LLM system
5. Discuss commercial and academic implications

## 🤝 Contributing

This is an academic project, but feedback and suggestions are welcome:

- **Health condition logic**: Additional medical conditions to support
- **Smart appliance APIs**: Other manufacturer integration opportunities  
- **UI/UX improvements**: Enhanced demonstration interface
- **Academic rigor**: Additional research sources and validation methods

## 📚 References

- **Samsung Family Hub Documentation**: SmartThings API capabilities and AI Vision Inside
- **Dietary Assessment Literature**: Underreporting rates, tool limitations, validation studies
- **Smart Appliance Market Research**: Adoption rates, feature gaps, commercial opportunities
- **Medical Nutrition Therapy**: Evidence-based guidelines for chronic condition management

## 📝 License

Academic project for educational purposes. Mock API data is for demonstration only and does not represent actual Samsung SmartThings data.

**Institution**: [University Name]
