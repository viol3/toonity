from typing import Union
from fastapi import FastAPI
import sys
sys.path.append('../inter-systems/shap-e')
sys.path.append('../inter-systems/')
from shapE import ShapEModule

shapE = ShapEModule("ShapE_100");
hunyuan = HunyuanModule("Hunyuan_100")

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/generateFromText/{prompt}")
def read_item(prompt: Union[str, None] = None):
    shapE.generateFromText(prompt)
    ## post production functions
    ## Mesh Simplification
    ## Laplace Smoothing
    return {"Completed prompt from mainframe": prompt}
