from fastapi import FastAPI
from api.api import api_router
import uvicorn

app = FastAPI()
@app.get("/health")
def health():
    return {"status": "ok"}
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)