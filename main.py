import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

from wqb import WQBSession

app = FastAPI(
    title="FastAPI Task Processor",
    version="1.0.0",
    description="A FastAPI application to process tasks with progress tracking"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

# 加载 .env 文件
load_dotenv()

# 模拟任务列表
tasks = [f"Task {i}" for i in range(500)]
task_progress = {task: 0 for task in tasks}

# 任务队列
task_queue = asyncio.Queue()

# 信号量，控制并发任务数量
semaphore = asyncio.Semaphore(100)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start_tasks")
async def start_tasks():
    global task_progress
    task_progress = {task: 0 for task in tasks}
    for task in tasks:
        await task_queue.put(task)
    asyncio.create_task(process_tasks())
    return JSONResponse(content={"message": "Tasks started"})


@app.get("/progress")
async def get_progress():
    # 只返回正在处理的那100个任务的进度
    current_tasks = list(task_progress.keys())[-100:]
    return JSONResponse(content={task: task_progress[task] for task in current_tasks})

@app.post("/api/data", response_class=HTMLResponse)
async def post_data(request: Request):
    # 从 .env 文件中读取用户名和密码
    username = os.getenv('API_USERNAME')
    password = os.getenv('API_PASSWORD')
    wqbs = WQBSession((username, password))
    # resp = wqbs.auth_request()

    alpha = {
        'type': 'REGULAR',
        'settings': {
            'instrumentType': 'EQUITY',
            'region': 'USA',
            'universe': 'TOP3000',
            'delay': 1,
            'decay': 13,
            'neutralization': 'INDUSTRY',
            'truncation': 0.13,
            'pasteurization': 'ON',
            'unitHandling': 'VERIFY',
            'nanHandling': 'OFF',
            'language': 'FASTEXPR',
            'visualization': False
        },
        'regular': 'liabilities/assets',
    }
    # multi_alpha = [<alpha_0>, <alpha_1>, <alpha_2>]
    asyncio.create_task(
        wqbs.simulate(
            alpha,  # `alpha` or `multi_alpha`
            on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
            on_start=lambda vars: print(vars['url']),
            on_finish=lambda vars: print(vars['resp']),
            # on_success=lambda vars: print(vars['resp']),
            # on_failure=lambda vars: print(vars['resp']),
        )
    )

    return JSONResponse(content={'success': 'alpha submitted'})


async def process_tasks():
    while not task_queue.empty():
        async with semaphore:
            task = await task_queue.get()
            await handle_task(task)
            task_queue.task_done()

async def handle_task(task):
    for i in range(1, 11):  # 模拟任务处理进度
        await asyncio.sleep(0.1)  # 模拟耗时操作
        task_progress[task] = i * 10

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
