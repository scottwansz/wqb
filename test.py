import asyncio
import os

import httpx
from dotenv import load_dotenv

import wqb
from service import build_alphas
from wqb import WQBSession


# 异步任务发送和结果处理函数
async def send_and_process_task(task_id, semaphore):
    async with semaphore:
        print(f"{task_id} started")
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 修改: 将 task_id 作为请求体传递
            response = await client.post("http://localhost:8000/process-task/", json={"task_id": task_id})
            # if response.status_code != 200:
            print(response.json())

# 主函数
async def main():
    # 任务列表
    tasks = [i for i in range(1, 11)]  # 假设有20个任务
    # 控制并发量的信号量
    semaphore = asyncio.Semaphore(5)

    # 创建任务列表
    task_coroutines = [send_and_process_task(task_id, semaphore) for task_id in tasks]

    # 等待所有任务完成
    await asyncio.gather(*task_coroutines)

if __name__ == "__main__":
    # asyncio.run(main())

    load_dotenv()
    # 从 .env 文件中读取用户名和密码
    username = os.getenv('API_USERNAME')
    password = os.getenv('API_PASSWORD')
    wqbs = WQBSession((username, password))
    resp = wqbs.auth_request()
    print(resp.status_code)  # 201
    print(resp.ok)  # True
    print(resp.json()['user']['id'])  # <Your BRAIN User ID>

    region = 'USA'  # 'USA', 'EUR'
    universe = 'ILLIQUID_MINVOL1M'  # 'TOP3000', 'ILLIQUID_MINVOL1M', 'GLB_MINVOL1M'
    delay = 1
    dataset_id = 'insiders1'

    alpha_list = build_alphas(wqbs, region, delay, universe, dataset_id)

    # for alpha in alpha_list:
    #     print(alpha)

    # resp = asyncio.run(
    #     wqbs.simulate(
    #         alpha,  # `alpha` or `multi_alpha`
    #         on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
    #         on_start=lambda vars: print(vars['url']),
    #         on_finish=lambda vars: print(vars['resp']),
    #         on_success=lambda vars: print(vars['resp']),
    #         on_failure=lambda vars: print(vars['resp']),
    #     )
    # )
    # print(resp.status_code)
    # print(resp.text)

    multi_alphas = wqb.to_multi_alphas(alpha_list, 10)

    for m in multi_alphas:
        print(len(m), m)
