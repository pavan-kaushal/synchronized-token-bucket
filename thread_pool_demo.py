import concurrent.futures
from token_bucket import TokenBucket
import time

def worker_task(task_id: int, arrival: int, duration: int, bucket: TokenBucket):
    if bucket.acquire_token(task_id):
        print(f"[Task {task_id}] executing...")
        time.sleep(duration)
        print(f"[Task {task_id}] completed")
        return f"[Task {task_id}] result"
    else:
        print(f"[Task {task_id}] Couldnot get Token")
        return None

tasks = [
    {"id": 1, "arrival": 0, "duration": 3},
    {"id": 2, "arrival": 1, "duration": 2},
    {"id": 3, "arrival": 1, "duration": 1},
    {"id": 4, "arrival": 0, "duration": 1},
    {"id": 5, "arrival": 0, "duration": 1},
]

start_time = time.time()

with TokenBucket(capacity=5, refill_count=1, refill_interval=1, initial_token_count=0) as bucket:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []

        for task in tasks:
            arrival = task["arrival"] - (time.time() - start_time)
            if arrival > 0:
                time.sleep(arrival)
            futures.append(
                executor.submit(worker_task, task["id"], 0, task["duration"], bucket)
            )

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                print(f"Completed: {result}")