from openai import OpenAI
import random

VALID_MEAL_TYPES = {"breakfast", "lunch", "dinner"}

def get_recipe_input():
    """Get food names from user input, one per line."""
    print("\n=== Recipe Generator ===")
    print("Enter the names of foods you'd like recipes for")
    print("Example: Pancakes")
    print("Enter one food per line. Press Enter twice to finish.")
    
    recipes_input = {}  # Changed to dictionary
    recipe_number = 1   # Initialize recipe counter
    
    while True:
        line = input().strip()
        if not line:  # Empty line indicates finish
            break
            
        # Use generate_recipe_details to get recipe information
        recipe_details = generate_recipe_details(line)
        recipe_details['number'] = recipe_number
        recipes_input[line] = recipe_details
        recipe_number += 1
    
    return recipes_input

def predict_ingredients(food_name):
    """Predict ingredients using LLM."""
    client = OpenAI()
    
    prompt = f"""
    Given a recipe for '{food_name}' ,
    list the main ingredients that would typically be used.
    
    Please respond with only the ingredients, separated by commas.
    List only the essential ingredients, maximum 8 items.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional chef listing recipe ingredients."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        ingredients_text = response.choices[0].message.content.strip()
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
    client = OpenAI()
    prompt = f"""Given the dish '{food_name}', classify it into one of these categories:
    - Breakfast
    - Lunch
    - Dinner
    - Dessert
    - Snack
    Return only the category name, no additional text."""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()

def predict_cooking_time(food_name):
    client = OpenAI()
    prompt = f"""Given the dish '{food_name}', provide the estimated cooking time in minutes.
    Return only the number, no additional text."""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return int(response.choices[0].message.content.strip())

def predict_description(food_name):
    client = OpenAI()
    prompt = f"""Given the food name '{food_name}', provide a brief but appetizing description 
    of this dish in 2-3 sentences. Focus on its taste, texture, and what makes it special."""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()


def get_random_dinner_recipe(recipes):
    # Get the total number of recipes
    total_recipes = len(recipes)
    
    # If no recipes exist, return None
    if total_recipes == 0:
        return None, False, None
    
    # Generate a random number between 1 and total recipes
    random_number = random.randint(1, total_recipes)
    
    # Find the recipe with the matching number
    selected_recipe = None
    recipe_name = None
    
    for name, recipe in recipes.items():
        if recipe['number'] == random_number:
            selected_recipe = recipe
            recipe_name = name
            break
    
    # Check if the recipe is labeled as dinner
    is_dinner = 'dinner' in selected_recipe.get('meal_type', '').lower()
    
    return recipe_name, is_dinner, selected_recipe

def get_random_lunch_recipe(recipes):
    # Get the total number of recipes
    total_recipes = len(recipes)
    
    # If no recipes exist, return None
    if total_recipes == 0:
        return None, False, None
    
    # Generate a random number between 1 and total recipes
    random_number = random.randint(1, total_recipes)
    
    # Find the recipe with the matching number
    selected_recipe = None
    recipe_name = None
    
    for name, recipe in recipes.items():
        if recipe['number'] == random_number:
            selected_recipe = recipe
            recipe_name = name
            break
    
    # Check if the recipe is labeled as lunch
    is_lunch = 'lunch' in selected_recipe.get('meal_type', '').lower()
    
    return recipe_name, is_lunch, selected_recipe

def get_random_breakfast_recipe(recipes):
    # Get the total number of recipes
    total_recipes = len(recipes)
    
    # If no recipes exist, return None
    if total_recipes == 0:
        return None, False, None
    
    # Generate a random number between 1 and total recipes
    random_number = random.randint(1, total_recipes)
    
    # Find the recipe with the matching number
    selected_recipe = None
    recipe_name = None
    
    for name, recipe in recipes.items():
        if recipe['number'] == random_number:
            selected_recipe = recipe
            recipe_name = name
            break
    
    # Check if the recipe is labeled as breakfast
    is_breakfast = 'breakfast' in selected_recipe.get('meal_type', '').lower()
    
    return recipe_name, is_breakfast, selected_recipe

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
    
    # Generate meal plan for each day
    for day in range(1, days + 1):
        print(f"\nDay {day}:")
        print("-" * 20)
        
        if meal_choice in [1, 2]:  # All meals or Breakfast only
            recipe_name, is_breakfast, recipe = get_random_breakfast_recipe(recipes)
            display_meal_plan(recipe_name, "Breakfast", recipe)
        
        if meal_choice in [1, 3]:  # All meals or Lunch only
            recipe_name, is_lunch, recipe = get_random_lunch_recipe(recipes)
            display_meal_plan(recipe_name, "Lunch", recipe)
        
        if meal_choice in [1, 4]:  # All meals or Dinner only
            recipe_name, is_dinner, recipe = get_random_dinner_recipe(recipes)
            display_meal_plan(recipe_name, "Dinner", recipe)

if __name__ == "__main__":
    main()
