import threading
import concurrent.futures
import time
from queue import Queue
from token_bucket import TokenBucket

def worker_task(task_id: int, duration: int):
    print(f"[Task {task_id}] executing...")
    time.sleep(duration)
    print(f"[Task {task_id}] completed")
    return f"[Task {task_id}] result"

def dispatcher(bucket: TokenBucket, task_queue: Queue, executor: concurrent.futures.ThreadPoolExecutor):
    while True:
        task = task_queue.get()
        if task is None:
            break 
        task_id, duration = task["id"], task["duration"]

        # Wait until token is available
        if bucket.acquire_token(task_id):
            executor.submit(worker_task, task_id, duration)

# Input tasks with arrival times
tasks = [
    {"id": 1, "arrival": 0, "duration": 3},
    {"id": 2, "arrival": 1, "duration": 2},
    {"id": 3, "arrival": 1, "duration": 1},
    {"id": 4, "arrival": 3, "duration": 1},
    {"id": 5, "arrival": 4, "duration": 1},
]

# Sorting by arrival time so that the sleep logic works
tasks.sort(key=lambda x: x["arrival"])
start_time = time.time()

task_queue = Queue()
with TokenBucket(capacity=5, refill_count=2, refill_interval=3, initial_token_count=0) as bucket:
    """
    Use a ThreadPoolExecutor to simulate concurrent task execution
    Max workers = 5 to allow up to 5 concurrent threads
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start dispatcher in background
        dispatch_thread = threading.Thread(target=dispatcher, args=(bucket, task_queue, executor), daemon=True)
        dispatch_thread.start()

        for task in tasks:
            # calculate how long to sleep till the task arrives
            arrival = task["arrival"] - (time.time() - start_time)
            if arrival > 0:
                time.sleep(arrival)
            task_queue.put(task)

        task_queue.put(None) # to stop the dispatcher function
        dispatch_thread.join()
