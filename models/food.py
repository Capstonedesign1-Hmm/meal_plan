from pydantic import BaseModel
from typing import List

class food(BaseModel):
    id : int
    name : str
    food_type : str
    food_mainIngre : str
    food_ingredient : str
    food_image : str
    youtubelink : str

class food_class(BaseModel):
    food_class : str
    id : int

class food_component(BaseModel):
    id : int
    calorie : int
    protein : int
    fat : int
    carbohydrate : int
    fiber : int
    calcium : int
    salt : int