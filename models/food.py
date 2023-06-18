from pydantic import BaseModel

class Food(BaseModel):
    id: int
    name: str
    food_type: str
    food_mainIngre: str
    food_ingredient: str
    food_image: str
    youtubelink: str

class FoodClass(BaseModel):
    id: int
    food_class: str

class FoodComponent(BaseModel):
    id: int
    calorie: float
    protein: float
    fat: float
    carbohydrate: float
    fiber: float
    calcium: float
    salt: float
    
class MealPlanRequest(BaseModel):
    food_class: str
    food_mainIngre: str
    food_calorie: float
    food_salt: float

class MealPlanResponse(BaseModel):
    food_id: int
    food_name: str
    food_image: str
