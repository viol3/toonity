import shapE
from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/generateFromText/{prompt}")
def read_item(prompt: Union[str, None] = None):
    return {"prompt": prompt}
