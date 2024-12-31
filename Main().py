import random
import requests  
VALID_MEAL_TYPES = {"breakfast", "lunch", "dinner"}
# Add Grok API configuration
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_API_KEY = "xai-YO5gjtorWRnzjcT7dO8Nvk6IcvgpZt9nAnTjsMPKlVIIkGsChcLO7NshKwC18VkRR7D049lNgE1uw0Ow"  # Replace with your actual API key
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GROK_API_KEY}"
}

def get_recipe_input():
    """Get food names from user input, supporting multiple input formats."""
    print("\n=== Recipe Generator ===")
    print("Enter the names of foods you'd like recipes for")
    print("Example: Pancakes, Spaghetti Carbonara, Chicken Curry")
    print("You can separate foods with commas, spaces, or new lines")
    print("Press Enter twice to finish.")
    
    recipes_input = {}  # Dictionary for recipes
    recipe_number = 1   # Initialize recipe counter
    current_input = []  # Collect all input lines
    
    while True:
        line = input().strip()
        if not line:  # Empty line indicates finish
            break
        # Split each line by commas first
        items = [item.strip() for item in line.split(',')]
        current_input.extend(items)
    
    # Remove empty strings and duplicates while preserving order
    food_items = list(dict.fromkeys(item for item in current_input if item))
    
    # Process each food item
    for food in food_items:
        recipe_details = generate_recipe_details(food)
        recipe_details['number'] = recipe_number
        recipes_input[food] = recipe_details
        recipe_number += 1
    
    return recipes_input
def predict_ingredients(food_name):
    """Predict ingredients using LLM."""
    prompt = f"""
    Given a recipe for '{food_name}' ,
    list the main ingredients that would typically be used.
    
    Please respond with only the ingredients, separated by commas.
    List only the essential ingredients, maximum 8 items.
    """
    
    try:
        response = requests.post(
            GROK_API_URL,
            headers=HEADERS,
            json={
                "messages": [
                    {"role": "system", "content": "You are a professional chef listing recipe ingredients."},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok-beta",
                "temperature": 0.7,
                "stream": False
            }
        )
        response_json = response.json()
        ingredients_text = response_json['choices'][0]['message']['content'].strip()
        return [ing.strip() for ing in ingredients_text.split(',')]
    except Exception as e:
        return []  # Fallback empty list

def generate_recipe_details(food_name):
    """Generate detailed recipe information using AI categorization."""
    description = predict_description(food_name)
    # Predict ingredients using LLM
    ingredients = predict_ingredients(food_name) 

    # Use LLM to categorize meal type
    meal_type = predict_meal_type(food_name)

    # Estimate time to cook
    time_to_cook = predict_cooking_time(food_name)

    return {
        "name": food_name,
        "description": description,
        "meal_type": meal_type,
        "time_to_cook": time_to_cook,
        "main_ingredients": ingredients,
    }

def predict_meal_type(food_name):
    prompt = f"""Given the dish '{food_name}', classify it into one of these categories:
    - Breakfast
    - Lunch
    - Dinner
    Return only the category name, no additional text."""
    
    response = requests.post(
        GROK_API_URL,
        headers=HEADERS,
        json={
            "messages": [{"role": "user", "content": prompt}],
            "model": "grok-beta",
            "stream": False
        }
    )
    
    response_json = response.json()
    return response_json['choices'][0]['message']['content'].strip()

def predict_cooking_time(food_name):
    prompt = f"""Given the dish '{food_name}', provide the estimated cooking time in minutes.
    Return only the number, no additional text."""
    
    try:
        response = requests.post(
            GROK_API_URL,
            headers=HEADERS,
            json={
                "messages": [{"role": "user", "content": prompt}],
                "model": "grok-beta",
                "stream": False
            }
        )
        
        response_json = response.json()
        print(f"Debug - API Response: {response_json}")  # Add this line to see the actual response
        
        # Add more robust response handling
        if 'choices' in response_json:
            return int(response_json['choices'][0]['message']['content'].strip())
        else:
            print(f"Unexpected API response format: {response_json}")
            return 30  # Default cooking time in minutes
            
    except Exception as e:
        print(f"Error in predict_cooking_time: {str(e)}")
        return 30  # Default cooking time in minutes
def predict_description(food_name):
    prompt = f"""Given the food name '{food_name}', provide a brief but appetizing description 
    of this dish in 2-3 sentences. Focus on its taste, texture, and what makes it special."""
    
    response = requests.post(
        GROK_API_URL,
        headers=HEADERS,
        json={
            "messages": [{"role": "user", "content": prompt}],
            "model": "grok-beta",
            "stream": False
        }
    )
    
    response_json = response.json()
    return response_json['choices'][0]['message']['content'].strip()


def get_random_dinner_recipe(recipes, planning_days=1, current_day=1, used_dinners=None):
    # Initialize used_dinners set if None
    if used_dinners is None:
        used_dinners = set()
    
    # If no recipes exist or all recipes have been used, return None
    available_recipes = {name: details for name, details in recipes.items() 
                        if name not in used_dinners}
    if not available_recipes:
        print("\nWarning: No more unique recipes available. Some meals will be repeated.")
        # Reset available recipes if we run out
        available_recipes = recipes
        used_dinners.clear()
    
    # Create a list of available recipes with their details
    recipe_list = "\n".join([
        f"- {name}: {details['description']} (Ingredients: {', '.join(details['main_ingredients'])})"
        for name, details in available_recipes.items()
    ])
    
    prompt = f"""Given these recipes:
    {recipe_list}
    
    Select the most nutritionally appropriate dinner option for day {current_day}, 
    considering meal planning for the next {planning_days} days. Consider:
    1. Balance of proteins, carbs, and vegetables
    2. Variety and nutrition across the {planning_days} day period
    3. Seasonal appropriateness and meal complexity
    4. How this meal might complement other meals in a {planning_days}-day rotation
    
    Return only the exact name of the chosen recipe, no additional text."""
    
    try:
        response = requests.post(
            GROK_API_URL,
            headers=HEADERS,
            json={
                "messages": [
                    {"role": "system", "content": "You are a nutritionist creating varied, balanced meal plans."},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok-beta",
                "temperature": 0.7,
                "stream": False
            }
        )
        
        response_json = response.json()
        selected_name = response_json['choices'][0]['message']['content'].strip()
        if selected_name in available_recipes:
            selected_recipe = available_recipes[selected_name]
            is_dinner = 'dinner' in selected_recipe.get('meal_type', '').lower()
            used_dinners.add(selected_name)
            return selected_name, is_dinner, selected_recipe
            
    except Exception as e:
        print(f"Warning: AI selection failed, falling back to random selection")
    
    # Fallback to random selection if AI selection fails
    random_name = random.choice(list(available_recipes.keys()))
    selected_recipe = available_recipes[random_name]
    is_dinner = 'dinner' in selected_recipe.get('meal_type', '').lower()
    used_dinners.add(random_name)
    
    return random_name, is_dinner, selected_recipe

def get_random_lunch_recipe(recipes, planning_days=1, current_day=1, used_lunches=None):
    # Initialize used_lunches set if None
    if used_lunches is None:
        used_lunches = set()
    
    available_recipes = {name: details for name, details in recipes.items() 
                        if name not in used_lunches}
    if not available_recipes:
        print("\nWarning: No more unique lunch recipes available. Some meals will be repeated.")
        available_recipes = recipes
        used_lunches.clear()
    
    recipe_list = "\n".join([
        f"- {name}: {details['description']} (Ingredients: {', '.join(details['main_ingredients'])})"
        for name, details in available_recipes.items()
    ])
    
    prompt = f"""Given these recipes:
    {recipe_list}
    
    Select the most appropriate lunch option for day {current_day}, 
    considering meal planning for the next {planning_days} days. Consider:
    1. Balance of proteins, carbs, and vegetables
    2. Energy levels needed for afternoon activities
    3. Variety across the {planning_days} day period
    4. Portability and suitability for midday meals
    
    Return only the exact name of the chosen recipe, no additional text."""
    
    try:
        response = requests.post(
            GROK_API_URL,
            headers=HEADERS,
            json={
                "messages": [
                    {"role": "system", "content": "You are a nutritionist creating varied, balanced lunch plans."},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok-beta",
                "temperature": 0.7,
                "stream": False
            }
        )
        
        response_json = response.json()
        selected_name = response_json['choices'][0]['message']['content'].strip()
        if selected_name in available_recipes:
            selected_recipe = available_recipes[selected_name]
            is_lunch = 'lunch' in selected_recipe.get('meal_type', '').lower()
            used_lunches.add(selected_name)
            return selected_name, is_lunch, selected_recipe
            
    except Exception as e:
        print(f"Warning: AI selection failed, falling back to random selection")
    
    random_name = random.choice(list(available_recipes.keys()))
    selected_recipe = available_recipes[random_name]
    is_lunch = 'lunch' in selected_recipe.get('meal_type', '').lower()
    used_lunches.add(random_name)
    
    return random_name, is_lunch, selected_recipe

def get_random_breakfast_recipe(recipes, planning_days=1, current_day=1, used_breakfasts=None):
    # Initialize used_breakfasts set if None
    if used_breakfasts is None:
        used_breakfasts = set()
    
    available_recipes = {name: details for name, details in recipes.items() 
                        if name not in used_breakfasts}
    if not available_recipes:
        print("\nWarning: No more unique breakfast recipes available. Some meals will be repeated.")
        available_recipes = recipes
        used_breakfasts.clear()
    
    recipe_list = "\n".join([
        f"- {name}: {details['description']} (Ingredients: {', '.join(details['main_ingredients'])})"
        for name, details in available_recipes.items()
    ])
    
    prompt = f"""Given these recipes:
    {recipe_list}
    
    Select the most appropriate breakfast option for day {current_day}, 
    considering meal planning for the next {planning_days} days. Consider:
    1. Balance of proteins, carbs, and healthy fats
    2. Energy levels needed for the start of the day
    3. Variety across the {planning_days} day period
    4. Preparation time suitable for morning routines
    
    Return only the exact name of the chosen recipe, no additional text."""
    
    try:
        response = requests.post(
            GROK_API_URL,
            headers=HEADERS,
            json={
                "messages": [
                    {"role": "system", "content": "You are a nutritionist creating varied, balanced breakfast plans."},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok-beta",
                "temperature": 0.7,
                "stream": False
            }
        )
        
        response_json = response.json()
        selected_name = response_json['choices'][0]['message']['content'].strip()
        if selected_name in available_recipes:
            selected_recipe = available_recipes[selected_name]
            is_breakfast = 'breakfast' in selected_recipe.get('meal_type', '').lower()
            used_breakfasts.add(selected_name)
            return selected_name, is_breakfast, selected_recipe
            
    except Exception as e:
        print(f"Warning: AI selection failed, falling back to random selection")
    
    random_name = random.choice(list(available_recipes.keys()))
    selected_recipe = available_recipes[random_name]
    is_breakfast = 'breakfast' in selected_recipe.get('meal_type', '').lower()
    used_breakfasts.add(random_name)
    
    return random_name, is_breakfast, selected_recipe

def display_meal_plan(recipe_name, meal_type, recipe):
    """Helper function to display a meal in a formatted way"""
    if recipe_name and recipe:
        print(f"\n{meal_type}: {recipe_name}")
        print(f"Description: {recipe['description']}")
        print(f"Cooking Time: {recipe['time_to_cook']}")
        print(f"Main Ingredients: {', '.join(recipe['main_ingredients'])}")
    else:
        print(f"\n{meal_type}: No suitable recipe found")


def main():
    print("Welcome to the Meal Planner!")
    print("\nFirst, let's collect some recipes...")
    
    # Collect recipes from user
    recipes = get_recipe_input()
    
    if not recipes:
        print("No recipes were added. Exiting program.")
        return
    
    # Get number of days for meal planning
    while True:
        try:
            days = int(input("\nHow many days of meal plans would you like to create? "))
            if days > 0:
                if days > len(recipes):
                    print(f"\nWarning: You've requested {days} days of meals but only provided {len(recipes)} recipes.")
                    print("This will result in repeated meals. Continue anyway? (y/n)")
                    if input().lower() != 'y':
                        continue
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get number of planning days for AI
    while True:
        try:
            planning_days = int(input("\nHow many future days should the AI consider when planning meals? "))
            if planning_days > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get meal type preference
    print("\nWhich meals would you like to plan?")
    print("1. All meals")
    print("2. Breakfast only")
    print("3. Lunch only")
    print("4. Dinner only")
    
    while True:
        try:
            meal_choice = int(input("Enter your choice (1-4): "))
            if 1 <= meal_choice <= 4:
                break
            print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")
    
    print("\n=== Your Meal Plan ===")
    
    # Initialize tracking sets for used meals
    used_breakfasts = set()
    used_lunches = set()
    used_dinners = set()
    
    # Generate meal plan for each day
    for day in range(1, days + 1):
        print(f"\nDay {day}:")
        print("-" * 20)
        
        if meal_choice in [1, 2]:  # All meals or Breakfast only
            recipe_name, is_breakfast, recipe = get_random_breakfast_recipe(
                recipes, 
                planning_days=planning_days, 
                current_day=day, 
                used_breakfasts=used_breakfasts
            )
            display_meal_plan(recipe_name, "Breakfast", recipe)
        
        if meal_choice in [1, 3]:  # All meals or Lunch only
            recipe_name, is_lunch, recipe = get_random_lunch_recipe(
                recipes, 
                planning_days=planning_days, 
                current_day=day, 
                used_lunches=used_lunches
            )
            display_meal_plan(recipe_name, "Lunch", recipe)
        
        if meal_choice in [1, 4]:  # All meals or Dinner only
            recipe_name, is_dinner, recipe = get_random_dinner_recipe(
                recipes, 
                planning_days=planning_days, 
                current_day=day, 
                used_dinners=used_dinners
            )
            display_meal_plan(recipe_name, "Dinner", recipe)

if __name__ == "__main__":
    main()
