import concurrent.futures
import time
from token_bucket import TokenBucket
from queue import PriorityQueue

def worker_task(task_id: int, duration: int, bucket: TokenBucket):
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
    {"id": 2, "arrival": 4, "duration": 2},
    {"id": 3, "arrival": 5, "duration": 4},
]

task_queue = PriorityQueue()
for i, task in enumerate(tasks):
    task_queue.put((task["arrival"], i, task))

start_time = time.time()

with TokenBucket(capacity=5, refill_rate=1, initial_token_count=3) as bucket:
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = []

        while not task_queue.empty():
            arrival, _, task = task_queue.get()
            now = time.time()
            elapsed = now - start_time
            wait_time = max(0, arrival - elapsed)
            if wait_time > 0:
                time.sleep(wait_time)

            future = executor.submit(worker_task, task["id"], task["duration"], bucket)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                print(f"Completed: {result}")
