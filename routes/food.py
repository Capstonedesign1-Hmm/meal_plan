from fastapi import APIRouter, HTTPException, status
from models.food import Food, FoodClass, FoodComponent, MealPlanRequest, MealPlanResponse
from typing import List
from databases import Database
from sqlalchemy import create_engine, MetaData, Table, select, Column, Integer, String, Float, func
from sqlalchemy.sql.expression import cast
from fastapi import FastAPI

DATABASE_URL = "postgresql://admin:hmm12345@database-1.cynzq75zj9kj.us-east-1.rds.amazonaws.com/hmmDB"
database = Database(DATABASE_URL)
metadata = MetaData()
engine = create_engine(DATABASE_URL)

# Define tables
foods = Table("foods", metadata, autoload_with=engine)
food_classes = Table("food_classes", metadata, autoload_with=engine)
food_components = Table("food_components", metadata, autoload_with=engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

food_router = APIRouter(
    tags=["food"]
)

@food_router.post("/make_meal", response_model=List[MealPlanResponse]) 
async def make_meal(meal_plan: MealPlanRequest) -> List[MealPlanResponse]:
    selected_foods = []
    food_class = meal_plan.food_class
    food_mainIngre = meal_plan.food_mainIngre
    food_calorie = meal_plan.food_calorie
    food_salt = meal_plan.food_salt

    # Food class and main ingredient condition
    if food_mainIngre is not None:
        query = select([foods]).where((foods.c.food_type == food_class) & (foods.c.food_mainIngre.contains(food_mainIngre)))
    else:
        query = select([foods]).where(foods.c.food_type == food_class)

    results = await database.fetch_all(query)

    # Get side dish or soup
    for result in results:
        if result["food_type"] not in ["반찬", "국"]:
            continue
        query = select([food_components]).where(food_components.c.id == result["id"])
        food_component = await database.fetch_one(query)
        if food_component is None:
            continue
        if food_calorie is not None and food_component["calorie"] > food_calorie:
            continue
        if food_salt is not None and food_component["salt"] > food_salt:
            continue
        selected_foods.append(MealPlanResponse(food_id=result["id"], food_name=result["name"], food_image=result["food_image"]))
        food_calorie -= food_component["calorie"]
        food_salt -= food_component["salt"]
        break  # We only need one side dish or soup

    # Get rice dish
    for result in results:
        if result["food_type"] != "밥":
            continue
        query = select([food_components]).where(food_components.c.id == result["id"])
        food_component = await database.fetch_one(query)
        if food_component is None:
            continue
        if food_calorie is not None and food_component["calorie"] > food_calorie:
            continue
        if food_salt is not None and food_component["salt"] > food_salt:
            continue
        selected_foods.append(MealPlanResponse(food_id=result["id"], food_name=result["name"], food_image=result["food_image"]))
        food_calorie -= food_component["calorie"]
        food_salt -= food_component["salt"]
        break  # We only need one rice dish

    # Get another dish
    for result in results:
        if result["food_type"] == "밥":
            continue
        query = select([food_components]).where(food_components.c.id == result["id"])
        food_component = await database.fetch_one(query)
        if food_component is None:
            continue
        if food_calorie is not None and food_component["calorie"] > food_calorie:
            continue
        if food_salt is not None and food_component["salt"] > food_salt:
            continue
        selected_foods.append(MealPlanResponse(food_id=result["id"], food_name=result["name"], food_image=result["food_image"]))
        break  # We only need one more dish

    if not selected_foods:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No foods found")

    return selected_foods


@food_router.get("/search_food/{food_name}", response_model=dict)
async def search_food(food_name: str) -> dict:
    query = select([foods]).where(func.lower(foods.c.name) == func.lower(food_name))
    result = await database.fetch_one(query)

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")

    query = select([food_components]).where(food_components.c.id == result["id"])
    food_component_result = await database.fetch_one(query)

    if food_component_result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food component not found")

    return {
        "food": {
            "id": result["id"],
            "name": result["name"],
            "food_type": result["food_type"],
            "food_mainIngre": result["food_mainIngre"],
            "food_ingredient": result["food_ingredient"],
            "food_image": result["food_image"],
            "youtubelink": result["youtubelink"],
        },
        "food_component": dict(food_component_result),
    }
