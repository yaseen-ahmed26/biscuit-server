from fastapi import FastAPI

app = FastAPI()

@app.get("/", include_in_schema = False)
def home():
    return {"messgae": "Biscuit Backend is running"}