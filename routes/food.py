from fastapi import APIRouter, HTTPException, status, Body
from models.food import food, food_class, food_component
from typing import List, Optional
from pydantic import BaseModel
from itertools import combinations

food_router = APIRouter(
    tags=["food"],
)

class MealPlanRequest(BaseModel):
    food_class: str
    food_mainIngre: Optional[str] = None
    food_calorie: Optional[int] = None
    food_salt: Optional[int] = None

class MealPlanResponse(BaseModel):
    food_id: int
    food_name: str
    food_image: str

food_dict = {}

# 사용자에게 이미 전송된 조합을 추적
sent_combinations = set()

# 가능한 모든 식단 조합을 저장
meal_combinations = []

food_router = APIRouter(
    tags=["food"]
)

@food_router.post("/make_meal", response_model=List[MealPlanResponse]) #한번에 하나씩만 넘기기
async def make_meal(meal_plan: MealPlanRequest) -> List[MealPlanResponse]:
    selected_foods = []
    food_class = meal_plan.food_class
    food_mainIngre = meal_plan.food_mainIngre
    food_calorie = meal_plan.food_calorie
    food_salt = meal_plan.food_salt
    meal_combinations.clear()
    sent_combinations.clear()

    for food_id, food in food_dict.items():
        if food.food_class == food_class:
            if food_mainIngre is not None and food_mainIngre not in food.food_mainIngre:
                continue
            if food_calorie is not None and food.calorie > food_calorie:
                continue
            if food_salt is not None and food.salt > food_salt:
                continue

            selected_foods.append(MealPlanResponse(food_name=food.name, food_image=food.food_image))

    meal_combinations.extend(combinations(selected_foods, 3))

    return await send_meals()

async def send_meals() -> List[MealPlanResponse]:
    for combination in meal_combinations:
        if combination not in sent_combinations:
            sent_combinations.add(combination)
            return list(combination)
    return []

@food_router.post("/reset_meal", response_model=List[MealPlanResponse])
async def reset_meal() -> List[MealPlanResponse]:
    return await send_meals()

@food_router.get("/search_food/{food_name}", response_model=dict)
async def search_food(food_name: str) -> dict:
    #try:
        for food_id, food_item in food_dict.items():
            if food_item.name == food_name:
                food_component = await fetch_food_component(food_id)
                return {
                    "food": food_item.dict(),
                    "food_component": food_component.dict(),
                }
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")
    #except DatabaseError:
        #raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

async def fetch_food_component(food_id: int) -> food_component:
    # 데이터베이스나 다른 데이터 소스에서 food_component를 가져옴
    return food_component(id=food_id, calorie=200, protein=10, fat=5, carbohydrate=30, fiber=2, calcium=100, salt=1)