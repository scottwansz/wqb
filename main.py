import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import time

import wqb
from service import alpha, build_alphas
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
# 从 .env 文件中读取用户名和密码
username = os.getenv('API_USERNAME')
password = os.getenv('API_PASSWORD')
wqbs = WQBSession((username, password))
wqbs.auth_request()

# 模拟任务列表
tasks = [f"Task {i}" for i in range(10)]
task_progress = {task: 0 for task in tasks}
task_start_times = {task: None for task in tasks}

# 任务队列
# task_queue = asyncio.Queue(maxsize=5)  # 限制队列的最大长度为10

# 信号量，控制并发任务数量
semaphore = asyncio.Semaphore(5)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 异步任务处理端点
@app.post("/process-task/")
async def process_task_endpoint(task: dict):
    task_id = task.get('task_id')
    result = await process_simple_task(task_id)
    return {"message": result}


@app.post("/start_tasks")
async def start_tasks():
    global task_progress, task_start_times
    task_progress = {task: 0 for task in tasks}
    task_start_times = {task: None for task in tasks}
    # async with semaphore:
    for task in tasks:
        asyncio.create_task(handle_task(task))
    return JSONResponse(content={"message": "Tasks started"})


@app.get("/progress")
async def get_progress():
    # 只返回整体进度
    total_progress = sum(task_progress.values())
    total_tasks = len(tasks)
    overall_progress = (total_progress / 100 / total_tasks) * 100

    return JSONResponse(content={
        "overall_progress": overall_progress
    })


@app.post("/api/data", response_class=JSONResponse)
async def post_data(request: Request):

    print('"/api/data" requested')

    # asyncio.create_task(
    #     wqbs.simulate(
    #         alpha,  # `alpha` or `multi_alpha`
    #         on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
    #         on_start=lambda vars: print(vars['url']),
    #         on_finish=lambda vars: print(vars['resp']),
    #         on_success=lambda vars: print(vars['resp']),
    #         on_failure=lambda vars: print(vars['resp']),
    #     )
    # )

    alphas = build_alphas(wqbs)  # [alpha for _ in range(2)]
    multi_alphas = wqb.to_multi_alphas(alphas, 10)
    concurrency = 8  # 1 <= concurrency <= 10

    asyncio.create_task(
        wqbs.concurrent_simulate(
            multi_alphas,  # `alphas` or `multi_alphas`
            concurrency,
            return_exceptions=True,
            on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
            on_start=lambda vars: print(vars['url']),
            on_finish=lambda vars: print(vars['resp']),
            on_success=lambda vars: print(vars['resp']),
            on_failure=lambda vars: print(vars['resp']),
        )
    )

    return JSONResponse(content={'success': 'alpha submitted'})


# 模拟的任务处理函数
async def process_simple_task(task_id: int):
    await asyncio.sleep(1)  # 模拟任务处理时间
    return f"Task {task_id} completed"


async def handle_task(task):
    async with semaphore:
        task_number = task.split()[1]  # 提取任务号
        print(f"Task {task_number} started.")
        task_start_times[task] = time.time()

        for i in range(1, 11):  # 模拟任务处理进度
            await asyncio.sleep(1)  # 模拟耗时操作
            task_progress[task] = i * 10

            # 输出当前任务进度
            # print(f"Task {task_number} progress: {task_progress[task]}%")
            # 计算并输出整体进度
            # total_progress = sum(task_progress.values())
            # total_tasks = len(tasks)
            # overall_progress = (total_progress / 100 / total_tasks) * 100
            # print(f"Overall progress: {overall_progress:.2f}%")

        task_end_time = time.time()
        task_duration = task_end_time - task_start_times[task]
        task_start_times[task] = task_duration
        print(f"Task {task_number} completed in {task_duration:.2f} seconds.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
