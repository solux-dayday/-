import requests
from bs4 import BeautifulSoup
import json

## 함수 부분
# 재료와 양 분리하는 함수
def separate_amount_ingredient(input_string):
    # 입력 문자열을 콤마를 기준으로 분리하여 리스트로 만듭니다.
    parts = input_string.split(',')
    ingredient_name_list = []          # 각 재료에 해당하는 재료 이름을 저장하는 리스트
    amount_list = []                # 각 재료에 해당하는 재료 양을 저장하는 리스트   

    for part in parts:
        # 각 부분에 대해 '재료'와 '양'을 분리
        ingredient_amount = part.split(' ', 1)  # 첫 번째 공백을 기준으로 재료와 양을 분리

        ingredient_name = ingredient_amount[0].strip()  # 재료 이름
        amount = ingredient_amount[1].strip() if len(ingredient_amount) > 1 else None  # 양

        ingredient_name_list.append(ingredient_name)
        amount_list.append(amount)

    return ingredient_name_list, amount_list


# 만개의 레시피에서 검색어(음식 리스트)에 해당하는 데이터를 가져오는 함수
def food_info(name):
    url = f"https://www.10000recipe.com/recipe/list.html?q={name}"      # 원하는 검색어(name)을 검색했을 때 주소
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
    else : 
        print("HTTP response error :", response.status_code)
        return
    
    food_list = soup.find_all(attrs={'class':'common_sp_link'})
    food_id = food_list[0]['href'].split('/')[-1]
    new_url = f'https://www.10000recipe.com/recipe/{food_id}'
    new_response = requests.get(new_url)
    if new_response.status_code == 200:
        html = new_response.text
        soup = BeautifulSoup(html, 'html.parser')
    else : 
        print("HTTP response error :", response.status_code)
        return
    
    food_info = soup.find(attrs={'type':'application/ld+json'})
    result = json.loads(food_info.text)

    # 재료 가져오기
    ingredient = ','.join(result['recipeIngredient'])
    ingredient_amount_list = list(separate_amount_ingredient(ingredient))              # 호출

    # 레시피 가져오기
    recipe = [result['recipeInstructions'][i]['text'] for i in range(len(result['recipeInstructions']))]
    for i in range(len(recipe)):
        recipe[i] = f'{i+1}. ' + recipe[i]

    # 조리시간 가져오기
    cooking_time_tag = soup.find('span', {'class': 'view2_summary_info2'})
    if cooking_time_tag:
        cooking_time = cooking_time_tag.get_text(strip=True)
    else:
        cooking_time = "조리시간 정보 없음"
    
    # 한 음식의 데이터들을 dictionary 형태로 저장하여 리턴
    res = {
        'name': name,
        'ingredient': ingredient_amount_list[0],
        'amount' : ingredient_amount_list[1],
        'recipe': recipe,
        'cooking_time': cooking_time,
    }
    return res


## 메인 부분
# 음식명 리스트
"""
food_list = [
    "잡곡밥", "옥수수밥", "감자밥", "무밥", "명란버터밥", "비빔밥", "가지밥", "전복밥", "콩나물밥", "곤드레비빔밥",
    "표고버섯영양밥", "쌈밥", "야채죽", "전복죽", "새우죽", "삼계죽", "미역죽", "참치죽", "소고기버섯죽", "팥죽",
    "단호박죽", "베이컨볶음밥", "김치볶음밥", "간장계란밥", "소고기볶음밥", "스팸볶음밥", "해물볶음밥", "새우볶음밥",
    "카레덮밥", "짜장밥", "오징어덮밥", "오므라이스", "육회비빔밥", "김치알밥", "미역국", "무국", "콩나물국",
    "김치콩나물국", "사골곰탕", "북엇국", "우거지국", "시래기국", "배추된장국", "매생이국", "올갱이국", "뼈해장국",
    "된장국", "계란감자국", "계란국", "감자국", "오징어무국", "어묵탕", "육개장", "갈비탕", "삼계탕", "추어탕",
    "꽃게탕", "홍합탕", "해물누룽지탕", "된장찌개", "차돌된장찌개", "꽃게된장찌개", "김치찌개", "순두부찌개", 
    "부대찌개", "청국장", "동태찌개", "비지찌개", "고추장찌개", "짜글이찌개", "버섯찌개", "소고기찌개", 
    "새우찌개", "밀폐유나베", "소고기버섯전골", "불고기전골", "어묵전골", "만두전골", "두부전골", "버섯전골", 
    "곱창전골", "대창전골", "아롱사태전골", "불낙전골", "삼겹살", "수육", "스테이크구이", "찹스테이크", 
    "갈비찜", "돼지갈비", "LA갈비", "바베큐", "김치등갈비찜", "묵은지돼지갈비찜", "매운쪽갈비찜", "폭립", 
    "제육볶음","소불고기", "돼지불고기", "닭볶음탕", "닭갈비", "훈제오리구이", "단호박훈제오리찜", "삼겹살숙주볶음", 
    "차돌숙주볶음", "찜닭", "소세지야채볶음", "돈까스", "떡갈비", "함박스테이크", "동그랑땡", "편백나무찜", 
    "곱창구이", "막창구이", "족발", "치킨", "닭강정", "생선까스", "연어스테이크", "오징어볶음", 
    "미나리오징어초무침", "쭈꾸미볶음", "아귀찜", "해물찜", "고등어구이", "고등어조림", "코다리조림", 
    "갈치구이", "갈치조림", "장어구이", "조기구이", "가자미구이", "꽁치조림", "낙곱새", "바지락술찜", 
    "바지락칼국수", "꽃게찜", "대게찜", "랍스터찜", "간장게장", "양념게장", "새우장", "회", "생굴", 
    "잡채", "골뱅이무침","마늘빵", "토스트", "냉면", "잔치국수", "비빔국수", "열무국수", "콩국수", "수제비", "비빔만두", "쫄면",
    "칼국수", "떡국", "만둣국", "우동", "핫도그", "찐만두", "튀김만두", "비빔만두", "김말이튀김", "야채튀김",
    "오징어튀김", "가지튀김", "팝콘치킨", "순대", "짜장면", "짬뽕", "마라탕", "탕수육", "꿔바로우", "마파두부",
    "계란토마토볶음밥", "양장피", "깐풍기", "깐풍새우", "크림새우", "유린기", "팔보채", "고추잡채", "춘권",
    "딤섬", "토마토스파게티", "크림파스타", "명란파스타", "봉골레파스타", "감바스", "스테이크", "또띠아피자",
    "고구마그라탕", "감자그라탕", "피자", "함박스테이크", "리조또", "스테이크", "샐러드", "햄버거", "부리또",
    "해쉬브라운", "감자튀김", "맥앤치즈", "콘샐러드", "초밥", "라멘", "나가사키짬뽕", "오니기리", "연어덮밥",
    "새우장덮밥", "메밀소바", "돈카츠", "야키니쿠", "낫또", "볶음우동", "카레우동", "가츠동", "규동", "쌀국수", "팟타이", "타코"]
"""
food_list = ['계란토마토볶음밥',"마늘빵"]

# 각 데이터들을 저장하는 dictionary
res_dict = {} 

"""
dictionary 형식 대신 list 형태로 저장하고 싶다면, 아래 방식 사용
# 각 데이터들을 저장하는 list
res_list = []

for 문 안에는 res_dict[f'{food_name}'] = food_data 대신
res_list.append(food_data)

"""

# 데이터 출력을 위한 코드 -> 실제 데이터 수집 시에는 if문부터 끝까지는 필요 없음.
for food_name in food_list:
    food_data = food_info(food_name)
    res_dict[f'{food_name}'] = food_data                # 데이터를 ex {'된장찌개' : data...} 식으로 저장함

    if food_data:
        print(f"'{food_name}'에 대한 정보:")
        print("재료:", food_data['ingredient'])
        print("각 재료의 양",food_data['amount'])
        print("레시피:")
        for step in food_data['recipe']:
            print(step)
        print("조리시간:", food_data['cooking_time'])
        print("\n")

print(res_dict)

