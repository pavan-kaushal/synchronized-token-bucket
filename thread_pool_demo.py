import concurrent.futures
from token_bucket import TokenBucket
import time

def worker_task(task_id: int, arrival: int, duration: int, bucket: TokenBucket):
    time.sleep(arrival)
    if bucket.acquire_token(task_id):
        print(f"[Task {task_id}] executing...")
        time.sleep(duration)
        print(f"[Task {task_id}] completed")
        return f"[Task {task_id}] result"
    else:
        print(f"[Task {task_id}] Couldnot get Token")
        return None

tasks = [
    {"id": 1, "arrival": 3, "duration": 3},
    {"id": 2, "arrival": 1, "duration": 2},
    {"id": 3, "arrival": 2, "duration": 4},
]

with TokenBucket(capacity=5, refill_rate=1, initial_token_count=3) as bucket:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(worker_task, tasks[i]["id"], tasks[i]["arrival"], tasks[i]["duration"], bucket) for i in range(len(tasks))
        ]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                print(f"Completed: {result}")