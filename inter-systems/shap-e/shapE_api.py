from shapE import ShapEModule
from typing import Union
from fastapi import FastAPI

app = FastAPI()
shapE = ShapEModule("ShapE_100");

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/generateFromText/{prompt}")
def read_item(prompt: Union[str, None] = None):
    shapE.generateFromText(prompt)
    return {"Completed prompt": prompt}
