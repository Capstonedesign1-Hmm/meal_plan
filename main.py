from fastapi import FastAPI
from databases import Database
from routes.users import user_router
from routes.food import food_router

import uvicorn

app = FastAPI()

DATABASE_URL = "postgresql://admin:hmm12345@database-1.cynzq75zj9kj.us-east-1.rds.amazonaws.com/hmmDB"

database = Database(DATABASE_URL)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app = FastAPI()
#라우트 등록
app.include_router(user_router, prefix="/user")
app.include_router(food_router, prefix="/food")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
