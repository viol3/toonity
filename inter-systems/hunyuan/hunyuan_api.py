from hunyuan import *
from typing import Union
from fastapi import FastAPI
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
import threading
import uuid
import uvicorn

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

SAVE_DIR = './exports'

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

worker = HunyuanModule("Hunyuan_100")

@app.post("/generate")
async def generate(request: Request):
    params = await request.json()
    uid = uuid.uuid4()
    params["uid"] = uid
    threading.Thread(target=worker.generate, args=(params,)).start()
    ret = {"uid": str(uid)}
    return JSONResponse(ret, status_code=200)

@app.get("/status/{uid}")
async def status(uid: str):
    save_file_path = os.path.join(SAVE_DIR, f'{uid}.obj')
    print(save_file_path, os.path.exists(save_file_path))
    if not os.path.exists(save_file_path):
        response = {'status': 'processing'}
        return JSONResponse(response, status_code=200)
    else:
        response = {'status': 'completed', 'path': save_file_path}
        return JSONResponse(response, status_code=200)



uvicorn.run(app, host="127.0.0.1", port=1381, log_level="info")
