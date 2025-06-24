from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
import json
from chat.chatbot import client
import requests
PROMPT_TEMPLATE = """
You are a professional bartender and drinks expert. Use the given alcohol metadata to generate a cocktail recipe in this exact structure and format:

---

Cocktail Metadata:
- Title: {title}
- Category: {category}
- Alcohol Content: {alcohol_content}%
- Flavor Profile: {flavor_profile}
- Drink Strength: {drink_strength}
- Glass Type: {glass_type}



How to Make It
[Detailed drink preparation instructions here.]

---

### Step - 01
Ingredients
| Ingredient       | ml/oz |
|------------------|-------|
{ingredients_table}

---

### Step - 02
Prepare the Glass
- [Instruction 1]
🎥 *Visual Tip: [Tip here]*

---

### Step - 03
Mix the Ingredients
- [Instruction 1]
💡 *Tip: [Tip here]*

---

### Step - 04
Strain & Serve
- [Instruction 1]

---

### Step - 05
Garnish & Enjoy
- [Instruction 1]
🎥 *Optional: [Extra fun line]*

---
"""

def generate_recipe(request):
    if 'metadata' not in request.data:
        return JsonResponse({"success": False, "error": "No metadata provided."}, status=400)

    try:
        metadata = json.loads(request.data['metadata'])
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid metadata JSON."}, status=400)

    try:
        # Validate ingredients in metadata
        if 'ingredients' not in metadata or not metadata['ingredients']:
            return JsonResponse({"success": False, "error": "No ingredients provided in metadata."}, status=400)

        # Create ingredients table for the prompt
        ingredients_table = "".join([
            f"| {i['name']} | {i['quantity']} {i['unit']} |\n" for i in metadata['ingredients']
        ])

        # Format the prompt with the ingredients table
        prompt = PROMPT_TEMPLATE.format(
            title=metadata.get('title', 'Unknown Cocktail'),
            category=metadata.get('category', 'Uncategorized'),
            alcohol_content=metadata.get('alcohol_content', 'N/A'),
            flavor_profile=metadata.get('flavor_profile', 'Balanced'),
            drink_strength=metadata.get('drink_strength', 'Medium'),
            glass_type=metadata.get('glass_type', 'Standard Glass'),
            servings=metadata.get('servings', 1),
            ingredients_table=ingredients_table
        )


        # Call the AI model to generate the recipe
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ],
                }
            ],
            max_tokens=1200,
        )

        recipe = response.choices[0].message.content

        # Attempt to find a YouTube tutorial link
        tutorial_link = None
        if 'title' in metadata:
            search_query = f"{metadata['title']} cocktail tutorial site:youtube.com"
            try:
                # Simple web search using a hypothetical API (replace with actual API like YouTube Data API)
                # This is a placeholder; you need a real search mechanism (e.g., Google Custom Search or YouTube API)
                search_response = requests.get(
                    f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&key=AIzaSyBx-Iu8aur6-Tme8v_Ug18eQknincyqtMg",
                    timeout=5
                )

                print("tutorial_link",tutorial_link)
                search_data = search_response.json() 
                print("da", search_data)
                if search_data.get('items'):
                    tutorial_link = f"https://www.youtube.com/watch?v={search_data['items'][0]['id']['videoId']}"
            except Exception:
                tutorial_link = None  # Fallback if search fails

        return JsonResponse({"success": True, "recipe": recipe, "tutorial_link": tutorial_link})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)