import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# Function to separate amount and ingredient
def separate_amount_ingredient(input_string):
    parts = input_string.split(',')
    ingredient_name_list, amount_list = [], []

    for part in parts:
        ingredient_amount = part.split(' ', 1)
        ingredient_name = ingredient_amount[0].strip()
        amount = ingredient_amount[1].strip() if len(ingredient_amount) > 1 else None
        ingredient_name_list.append(ingredient_name)
        amount_list.append(amount)

    return ingredient_name_list, amount_list

# Function to get food information from www.10000recipe.com
def food_info(name):
    url = f"https://www.10000recipe.com/recipe/list.html?q={name}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("HTTP response error:", response.status_code)
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    food_list = soup.find_all(attrs={'class': 'common_sp_link'})
    
    if not food_list:
        print(f"No recipe found for '{name}'.")
        return
    
    food_id = food_list[0]['href'].split('/')[-1]
    new_url = f'https://www.10000recipe.com/recipe/{food_id}'
    new_response = requests.get(new_url)
    
    if new_response.status_code != 200:
        print("HTTP response error:", new_response.status_code)
        return
    
    soup = BeautifulSoup(new_response.text, 'html.parser')
    food_info = soup.find(attrs={'type': 'application/ld+json'})
    
    if not food_info:
        print(f"No recipe information found for '{name}'.")
        return
    
    result = json.loads(food_info.text)

    ingredient = ','.join(result.get('recipeIngredient', []))
    ingredient_name_list, amount_list = separate_amount_ingredient(ingredient)

    recipe = [f'{i + 1}. {step["text"]}' for i, step in enumerate(result.get('recipeInstructions', []))]

    cooking_time_tag = soup.find('span', {'class': 'view2_summary_info2'})
    cooking_time = cooking_time_tag.get_text(strip=True) if cooking_time_tag else "조리시간 정보 없음"

    return {
        'name': name,
        'ingredient': ingredient_name_list,
        'amount': amount_list,
        'recipe': recipe,
        'cooking_time': cooking_time,
    }



# Food list
food_list = [
    "잡곡밥", "옥수수밥", "감자밥", "무밥", "명란버터밥", "비빔밥", "가지밥", "전복밥", "콩나물밥", "곤드레비빔밥",
    "표고버섯영양밥", "쌈밥", "야채죽", "전복죽", "새우죽", "삼계죽", "미역죽", "참치죽", "소고기버섯죽", "팥죽",
    "단호박죽", "베이컨볶음밥", "김치볶음밥", "간장계란밥", "소고기볶음밥", "스팸볶음밥", "해물볶음밥", "새우볶음밥",
    "카레덮밥", "짜장밥", "오징어덮밥", "오므라이스", "육회비빔밥", "김치알밥", "미역국", "무국", "콩나물국",
    "김치콩나물국", "사골곰탕", "북엇국", "우거지국", "시래기국", "배추된장국", "매생이국", "올갱이국", "뼈해장국",
    "된장국", "계란감자국", "계란국", "감자국", "오징어무국", "어묵탕", "육개장", "갈비탕", "삼계탕", "추어탕",
    "꽃게탕", "홍합탕", "해물누룽지탕", "된장찌개", "차돌된장찌개", "꽃게된장찌개", "김치찌개", "순두부찌개", 
    "부대찌개", "청국장", "동태찌개", "비지찌개", "고추장찌개", "짜글이찌개", "버섯찌개", "소고기찌개", 
    "새우찌개", "밀폐유나베", "소고기버섯전골"]

# Data storage
data_food_name, data_food_ingredient, data_food_amount, data_food_recipe, data_food_time = [], [], [], [], []

for food_name in food_list:
    food_data = food_info(food_name)
    if food_data:
        data_food_name.append(food_name)
        data_food_ingredient.append(food_data['ingredient'])
        data_food_amount.append(food_data['amount'])
        data_food_recipe.append(food_data['recipe'])
        data_food_time.append(food_data['cooking_time'])

# Create DataFrame and save to CSV
food_dataframe = {
    'food_name': data_food_name,
    'food_ingredient': data_food_ingredient,
    'food_amount': data_food_amount,
    'food_recipe': data_food_recipe,
    'food_time': data_food_time
}

df = pd.DataFrame(food_dataframe)
df.to_csv('food_dataframe2.csv', index=False)
#print(df)
print("food_dataframe2.csv가 만들어졌습니다.")
