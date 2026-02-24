# TasteMatch Pitch Demo Script

## 🎬 5-Minute Demo Flow

---

## BEFORE YOU START

**Pre-demo setup (do this BEFORE the audience sees):**

1. Open terminal: `ollama serve` (minimize/hide it)
2. Open another terminal: `streamlit run demo_app.py`
3. In the Streamlit app sidebar, set up a sample profile:
   - Health Conditions: Select "Diabetes" and "High Blood Pressure"
   - Diet Type: "No Restrictions"
   - Allergies: "None"
   - Max cooking time: 45 minutes
   - Max calories: 600
   - Kitchen Inventory: "chicken, rice, broccoli, garlic, olive oil"

4. Clear the chat if there's any old conversation
5. **Maximize the browser window** so it looks professional
6. Ready to present!

---

## SLIDE 1: The Problem (30 seconds)

**SAY:**
> "Imagine you're diabetic and just got diagnosed with high blood pressure. Your doctor hands you a list of dos and don'ts. You go home, open your fridge, and think... 'What can I actually eat with what I have?'
> 
> Generic diet advice is overwhelming. 87% of people with chronic conditions struggle to follow dietary recommendations because they're not personalized to their real-world situation."

**DO:** Show empathy, make it relatable

---

## SLIDE 2: Meet TasteMatch (30 seconds)

**SAY:**
> "That's why we built TasteMatch - your AI-powered personal dietitian. Instead of generic meal plans, you have a conversation. Tell TasteMatch your health conditions, what's in your kitchen, and what you're craving. It handles the rest."

**DO:** Now switch to the demo screen (Streamlit app)

---

## DEMO PART 1: Show the Profile (45 seconds)

**SAY:**
> "First, TasteMatch learns about you."

**DO:** Point to the sidebar
> "Here we've set up a profile for someone with diabetes and high blood pressure. They're watching their calories and cook time. And critically - they've told us what's actually in their kitchen: chicken, rice, broccoli, garlic, and olive oil."

**SAY:**
> "This is the key difference - we're not suggesting recipes you can't make. We work with what you have."

---

## DEMO PART 2: Simple Query (60 seconds)

**TYPE IN CHAT:** "What can I make for dinner tonight?"

**SAY while it's thinking:**
> "Now watch this. I'm asking a simple, natural question. No forms, no complex searches. Just conversation."

**WAIT FOR RESPONSE**

**SAY:**
> "TasteMatch understands my health conditions, knows what I have in my kitchen, and gives me actionable recipes. Look at these recommendations..."

**DO:** Point to the recipe cards that appear
> "Each recipe shows:
> - Time to cook
> - Calorie count
> - Rating from real users
> - Full ingredient list"

**DO:** Expand one recipe to show details
> "And I can see the full recipe right here."

---

## DEMO PART 3: Health-Aware Query (60 seconds)

**TYPE IN CHAT:** "Which of these is best for managing my blood sugar?"

**SAY:**
> "Now here's where it gets smart. I'm asking a follow-up question about my specific health condition."

**WAIT FOR RESPONSE**

**SAY:**
> "TasteMatch doesn't just search recipes - it understands nutritional science. It's considering my diabetes diagnosis and recommending recipes that help manage blood sugar levels."

**DO:** Point to the response
> "And it explains WHY these choices are good for me. That's educational value on top of practical guidance."

---

## DEMO PART 4: Show Personalization (45 seconds)

**SAY:**
> "Let me show you how this adapts. Let's say my dietary needs change."

**DO:** Go to sidebar
> "I'll change my diet type to vegetarian and add a nut allergy."

**DO:** Change the settings

**TYPE IN CHAT:** "Quick lunch ideas?"

**SAY while waiting:**
> "Now the same query gives totally different results, filtered for vegetarian, nut-free options."

**SHOW RESULTS:**
> "See? Completely personalized."

---

## CLOSING: The Vision (30 seconds)

**SAY:**
> "This is our MVP. We're running 100% locally - no expensive API calls, complete data privacy. 
>
> Our vision: TasteMatch becomes your daily food companion. It learns your preferences, tracks your nutrition, plans your meals, and even generates shopping lists. All while keeping your health data completely private."

---

## HANDLING Q&A

### Q: "How accurate is the nutritional advice?"
**A:** "The recipes come from verified databases with nutritional information. The AI uses this data to make recommendations. For medical advice, we always recommend consulting healthcare providers - TasteMatch is a tool to help implement dietary guidance, not replace medical professionals."

### Q: "What if I don't know what ingredients I have?"
**A:** "Great question. In the full version, we're planning image recognition - take a photo of your fridge, and TasteMatch automatically identifies ingredients. For now, users can skip the inventory and just search freely."

### Q: "How does this make money?"
**A:** "Multiple paths:
1. **Freemium Model**: Basic version free, premium features (meal planning, nutrition tracking) paid
2. **B2B**: License to healthcare providers, insurance companies who want to help patients manage diet
3. **Partnerships**: Grocery delivery integration - 'Order ingredients for this recipe'
4. **White Label**: Sell the technology to health apps and telehealth platforms"

### Q: "What about competition? MyFitnessPal, etc.?"
**A:** "Great question. MyFitnessPal focuses on tracking. We focus on guidance. The magic is:
1. **Conversational**: Talk naturally, not fill forms
2. **Contextual**: We consider what you HAVE, not just what exists
3. **Condition-Specific**: Optimized for chronic conditions, not just weight loss
4. **Privacy-First**: Local processing, your data stays yours"

### Q: "Why local/Ollama vs cloud AI?"
**A:** "Three reasons:
1. **Privacy**: Health data never leaves the device
2. **Cost**: No per-query fees means we can scale without crushing API costs
3. **Control**: We can customize and fine-tune the AI for nutrition-specific tasks

For the future, we might offer a cloud option for users who prefer it, but local-first is our differentiation."

### Q: "How big is the market?"
**A:** "60% of Americans have at least one chronic condition that requires dietary management. That's 190 million potential users. Healthcare costs related to poor diet: $300 billion annually. Even capturing 1% would be massive."

### Q: "What do you need from us/What's the ask?"
**A:** [Adjust based on whether this is for funding, competition, etc.]

**For Funding:**
"We're raising $X for:
1. Full-time engineering team
2. Partnerships with healthcare providers for data/validation  
3. Mobile app development
4. Clinical studies to validate outcomes

With this, we can launch in 6 months and prove real health outcomes."

**For Competition:**
"We're competing for recognition and potential partnerships. Our goal is to show this technology can actually improve health outcomes, not just track them."

---

## 🎯 Key Messages to Emphasize

1. **Personal**: Not generic advice, but tailored to YOUR situation
2. **Practical**: Based on what you HAVE, not theoretical meal plans
3. **Private**: Your health data stays on your device
4. **Actionable**: Real recipes you can cook today
5. **Educational**: Learn WHY certain choices are better for you

---

## ⚠️ Things to Avoid Saying

- ❌ "This replaces your doctor" → ✅ "This helps implement your doctor's guidance"
- ❌ "It's perfect" → ✅ "It's our MVP, we're learning and improving"
- ❌ "We'll definitely do X" → ✅ "We're exploring X as a future feature"
- ❌ Technical jargon → ✅ Simple, benefit-focused language

---

## 💡 Pro Tips

1. **Practice the demo 5 times** before the real pitch
2. **Have backup queries ready** that you KNOW work well
3. **If something breaks**, have screenshots as backup
4. **Smile and show enthusiasm** - you're solving a real problem!
5. **Time yourself** - don't rush, but don't go over time
6. **End with a clear ask** - what do you want from the audience?

---

## 🎬 One More Thing...

**If you have extra time at the end (30 seconds):**

**TYPE:** "Create a 3-day meal plan for my conditions, under 1800 calories per day"

**SAY:**
> "And here's a glimpse of what's coming - full meal planning. Imagine getting a whole week's worth of healthy, personalized meals planned in seconds."

**SHOW THE RESPONSE:**
> "This is the future of dietary management."

---

## Good luck! You've got this! 🚀

Remember: You're not just showing a demo. You're showing how TasteMatch will help millions of people live healthier lives. That's powerful. Believe in it!
