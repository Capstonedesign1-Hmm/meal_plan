from fastapi import FastAPI
from routes.users import user_router
from routes.food import food_router

import uvicorn

app = FastAPI()
#라우트 등록
app.include_router(user_router, prefix="/user")
app.include_router(food_router, prefix="/food")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port = 8000,
    reload=True)