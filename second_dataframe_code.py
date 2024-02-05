import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# 양과 재료를 분리하는 함수
def separate_amount_ingredient(input_string):
    parts = input_string.split(',')
    ingredient_name_list, amount_list = [], []

    for part in parts:
        ingredient_amount = part.split(' ', 1)
        ingredient_name = ingredient_amount[0].strip()
        amount = ingredient_amount[1].strip() if len(ingredient_amount) > 1 else "None"
        ingredient_name_list.append(ingredient_name)
        amount_list.append(amount)

    return ingredient_name_list, amount_list

# www.10000recipe.com에서 음식 정보를 가져오는 함수
def food_info(name):
    url = f"https://www.10000recipe.com/recipe/list.html?q={name}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("HTTP 응답 오류:", response.status_code)
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    food_list = soup.find_all(attrs={'class': 'common_sp_link'})
    
    if not food_list:
        print(f"'{name}'에 대한 레시피를 찾을 수 없습니다.")
        return
    
    food_id = food_list[0]['href'].split('/')[-1]
    new_url = f'https://www.10000recipe.com/recipe/{food_id}'
    new_response = requests.get(new_url)
    
    if new_response.status_code != 200:
        print("HTTP 응답 오류:", new_response.status_code)
        return
    
    soup = BeautifulSoup(new_response.text, 'html.parser')
    food_info = soup.find(attrs={'type': 'application/ld+json'})
    
    if not food_info:
        print(f"'{name}'에 대한 레시피 정보를 찾을 수 없습니다.")
        return
    
    result = json.loads(food_info.text)

    ingredient = ','.join(result.get('recipeIngredient', []))
    ingredient_name_list, amount_list = separate_amount_ingredient(ingredient)

    recipe = [f'{i + 1}. {step["text"]}' for i, step in enumerate(result.get('recipeInstructions', []))]

    cooking_time_tag = soup.find('span', {'class': 'view2_summary_info2'})
    cooking_time = cooking_time_tag.get_text(strip=True) if cooking_time_tag else "None"

    # 이미지 URL 추출
    menu_img_tag = soup.find('div', 'centeredcrop')
    menu_img_tag = menu_img_tag.find('img') if menu_img_tag else "None"
    menu_img = menu_img_tag.get('src') if menu_img_tag else "None"

    # 메뉴 정보 추출
    menu_info_1_tag = soup.find('span', 'view2_summary_info1')  # menu_info_1
    menu_info_1 = menu_info_1_tag.get_text() if menu_info_1_tag else "None"
    
    menu_info_3_tag = soup.find('span', 'view2_summary_info3')  # menu_info_3
    menu_info_3 = menu_info_3_tag.get_text() if menu_info_3_tag else "None"

    return {
        'name': name,
        'ingredient': ingredient_name_list,
        'amount': amount_list,
        'recipe': recipe,
        'cooking_time': cooking_time,
        'menu_img': menu_img,
        'people': menu_info_1,  # people 인덱스 추가 => 몇 인분
        'nando': menu_info_3   # nando 인덱스 추가 => 난이도 
    }

# Food list
food_list = [
    "딤섬", "토마토스파게티", "크림파스타", "명란파스타", "봉골레파스타", "감바스", "스테이크", "또띠아피자",
    "고구마그라탕", "감자그라탕", "피자", "함박스테이크", "리조또", "스테이크", "샐러드", "햄버거", "부리또",
    "해쉬브라운", "감자튀김", "맥앤치즈", "콘샐러드", "초밥", "라멘", "나가사키짬뽕", "오니기리", "연어덮밥",
    "새우장덮밥", "메밀소바", "돈카츠", "야키니쿠", "낫또", "볶음우동", "카레우동", "가츠동", "규동", "쌀국수", "팟타이", "타코"]

# Data storage
data_food_name, data_food_ingredient, data_food_amount, data_food_recipe, data_food_time, data_food_img, data_food_people, data_food_nando = [], [], [], [], [], [], [], []

for food_name in food_list:
    food_data = food_info(food_name)
    if food_data:
        data_food_name.append(food_name)
        data_food_ingredient.append(food_data['ingredient'])
        data_food_amount.append(food_data['amount'])
        data_food_recipe.append(food_data['recipe'])
        data_food_time.append(food_data['cooking_time'])
        data_food_img.append(food_data['menu_img'])
        data_food_people.append(food_data['people'])

        # 난이도 크롤링 후 숫자로 변환
        if food_data['nando'] == "아무나" :
            food_data['nando'] = 1
        elif food_data['nando'] == "초급" :
            food_data['nando'] = 2
        elif food_data['nando'] == "중급" :
            food_data['nando'] = 3
        elif food_data['nando'] == "고급" :
            food_data['nando'] = 4
        elif food_data['nando'] == "신의경지":
            food_data['nando'] = 5

        data_food_nando.append(food_data['nando'])


# DataFrame 생성 및 CSV로 저장
food_dataframe = {
    'food_name': data_food_name,
    'food_ingredient': data_food_ingredient,
    'food_amount': data_food_amount,
    'food_recipe': data_food_recipe,
    'food_time': data_food_time,
    'menu_img': data_food_img,
    'people': data_food_people,  # people 인덱스를 DataFrame에 추가
    'nando': data_food_nando,  # nando 인덱스를 DataFrame에 추가
}

df = pd.DataFrame(food_dataframe)
df.to_csv('food_dataframe14.csv', index=False)
print("food_dataframe14.csv가 만들어졌습니다.")
