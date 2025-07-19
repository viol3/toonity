import requests
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
import json

generateLocalUrl = 'http://127.0.0.1:1381/generate'
statusLocalUrl = 'http://127.0.0.1:1381/status/'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI()

mesh_path = "../inter-systems/hunyuan/exports/"

@app.post("/generate")
async def generate(request: Request):
    params = await request.json()
    response = requests.post(generateLocalUrl, data=json.dumps(params))
    ret = json.loads(response.content)
    return JSONResponse(ret, status_code=200)

@app.get("/status/{uid}")
async def status(uid: str):
    response = requests.get(statusLocalUrl + uid)
    ret = json.loads(response.content)
    if(ret.status == "completed"):
        os.system("./simplify " + mesh_path + uid + ".obj " + uid + ".obj")
    return JSONResponse(ret, status_code=200)

@app.get("/simplify")
async def simplify():
    os.system("simplify pencil.obj pencil_simplified.obj 0.01")
    return JSONResponse({ 'status': 'completed' }, status_code=200)
uvicorn.run(app, host="127.0.0.1", port=1380, log_level="info")
