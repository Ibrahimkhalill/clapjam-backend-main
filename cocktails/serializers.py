from rest_framework import serializers
from .models import Cocktail, Ingredient, BookMark
from .utils.generate_recipe import generate_recipe  # Import the generate_recipe function
from django.http import HttpRequest
import json

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity', 'unit']

class CocktailSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    image = serializers.ImageField(required=False, allow_null=True)
    video = serializers.URLField(required=False, allow_null=True)
    recipe_steps = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Cocktail
        fields = [
            'id', 'category', 'title', 'image', 'video', 'recipe_steps',
            'alcohol_content', 'flavor_profile', 'drink_strength', 'glass_type',
            'rating', 'review_count', 'servings', 'ingredients'
        ]

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        image = validated_data.get('image', None)

        # Prepare metadata for generate_recipe
        metadata = {
            'title': validated_data.get('title', 'Unknown'),
            'alcohol_content': validated_data.get('alcohol_content', 'N/A'),
            'flavor_profile': validated_data.get('flavor_profile', 'N/A'),
            'drink_strength': validated_data.get('drink_strength', 'N/A'),
            'glass_type': validated_data.get('glass_type', 'N/A'),
            'ingredients': [
                {
                    'name': ingredient['name'],
                    'quantity': ingredient['quantity'],
                    'unit': ingredient['unit']
                } for ingredient in ingredients_data
            ]
        }

        # Simulate a request object for generate_recipe
        request = HttpRequest()
        request.method = 'POST'
        request.FILES['image'] = image if image else None
        request.data = {'metadata': json.dumps(metadata)}

        # Call generate_recipe
        response = generate_recipe(request)
        print("dd", response)

        # Access the data directly from JsonResponse
        response_data = json.loads(response.content.decode('utf-8'))

        if not response_data.get('success'):
            raise serializers.ValidationError(f"Recipe generation failed: {response_data.get('error')}")
        # Extract recipe steps from the generated recipe
        recipe = response_data.get('recipe', '')
        tutorial_link = response_data.get('tutorial_link', '')
        print("tutorial_link",tutorial_link)
        recipe_steps = self._extract_recipe_steps(recipe)
        validated_data['recipe_steps'] = recipe_steps
        validated_data['video'] = tutorial_link

        # Create the cocktail instance
        cocktail = Cocktail.objects.create(**validated_data)

        # Create associated ingredients
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(cocktail=cocktail, **ingredient_data)

        return cocktail

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ingredients_data is not None:
            instance.ingredients.all().delete()
            for ingredient_data in ingredients_data:
                Ingredient.objects.create(cocktail=instance, **ingredient_data)
        return instance

    def _extract_recipe_steps(self, recipe_text):
        """
        Extract recipe steps from the generated recipe text and format as JSON.
        Includes 'How to Make It' as the first step and numbered steps.
        """
        steps = []
        lines = recipe_text.split('\n')
        current_step = None
        step_content = []

        for line in lines:
            line = line.strip()
            if line == "How to Make It" or line.startswith('### Step -'):
                if current_step and step_content:
                    steps.append({
                        'step': current_step,
                        'instructions': step_content
                    })
                current_step = line.replace('### ', '').strip()
                step_content = []
            elif line and current_step:
                step_content.append(line)

        if current_step and step_content:
            steps.append({
                'step': current_step,
                'instructions': step_content
            })

        return steps

class BookMarkSerializer(serializers.ModelSerializer):
    cocktail = CocktailSerializer(read_only=True)
    cocktail_id = serializers.PrimaryKeyRelatedField(
        queryset=Cocktail.objects.all(),
        source='cocktail',
        write_only=True
    )

    class Meta:
        model = BookMark
        fields = ['id', 'user', 'cocktail', 'cocktail_id']
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        cocktail = data.get('cocktail')
        if BookMark.objects.filter(user=user, cocktail=cocktail).exists():
            raise serializers.ValidationError("This cocktail is already bookmarked by the user.")
        return data