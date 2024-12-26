import openai

def get_random_dinner_recipe(recipes, planning_days=1, current_day=1, used_dinners=None):
    # Initialize used_dinners set if None
    if used_dinners is None:
        used_dinners = set()
    
    # If no recipes exist or all recipes have been used, return None
    available_recipes = {name: details for name, details in recipes.items() 
                        if name not in used_dinners}
    if not available_recipes:
        return None, False, None
    
    client = OpenAI()
    
    # Create a list of available recipes with their details
    recipe_list = "\n".join([
        f"- {name}: {details['description']} (Ingredients: {', '.join(details['main_ingredients'])})"
        for name, details in available_recipes.items()
    ])
    
    prompt = f"""Given these recipes:
    {recipe_list}
    
    Select the most nutritionally appropriate dinner option for day {current_day} of {planning_days}. Consider:
    1. Balance of proteins, carbs, and vegetables
    2. Variety across the {planning_days} days
    3. Overall nutritional value
    
    Return only the exact name of the chosen recipe, no additional text."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a nutritionist selecting balanced meals."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        selected_name = response.choices[0].message.content.strip()
        if selected_name in available_recipes:
            selected_recipe = available_recipes[selected_name]
            is_dinner = 'dinner' in selected_recipe.get('meal_type', '').lower()
            used_dinners.add(selected_name)
            return selected_name, is_dinner, selected_recipe
            
   