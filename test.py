import asyncio
import httpx

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
    asyncio.run(main())