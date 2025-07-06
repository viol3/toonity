from hunyuan import HunyuanModule
from typing import Union
from fastapi import FastAPI

app = FastAPI()
hunyuan = HunyuanModule("Hunyuan_100");

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/generateFromText/{prompt}")
def read_item(prompt: Union[str, None] = None):
    hunyuan.generateFromText(prompt)
    return {"Completed prompt": prompt}
