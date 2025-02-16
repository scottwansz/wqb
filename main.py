from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import wqb
from config import settings
from wqb import WQBSession
from dotenv import load_dotenv
import os

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

# logger = wqb.wqb_logger()

# 加载 .env 文件
load_dotenv()

# 添加调试信息，确保 .env 文件被正确加载
# print(f"Loaded environment variables: {os.environ}")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/data", response_class=HTMLResponse)
async def post_data(request: Request):
    # 从 .env 文件中读取用户名和密码
    username = os.getenv('API_USERNAME')
    password = os.getenv('API_PASSWORD')
    # print(f"Username from .env: {username}")
    # print(f"Password from .env: {password}")
    wqbs = WQBSession((username, password))
    resp = wqbs.auth_request()
    # print(resp.status_code)  # 201
    # print(resp.ok)  # True
    # print(resp.json()['user']['id'])  # <Your BRAIN User ID>
    return JSONResponse(content=resp.json())

    # result = {
    #     "api_title": settings.api_title,
    #     "api_version": settings.api_version,
    #     "api_description": settings.api_description,
    #     "database_url": settings.database_url,
    #     "secret_key": settings.secret_key,
    #     "username": settings.account,
    #     "password": settings.password,
    # }
    #
    # print(result)
    #
    # return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn

    # 修改: 传递应用作为导入字符串
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
