import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import router

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

FORMAT = "%(asctime)s : %(name)s : %(levelname)s : %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
