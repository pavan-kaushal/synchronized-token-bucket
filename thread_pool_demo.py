import concurrent.futures
from token_bucket import TokenBucket
import time

# Simulates a worker task that requests a token, and if successful, runs for `duration` seconds.
def worker_task(task_id: int, duration: int, bucket: TokenBucket):
    # Try to acquire a token to proceed with execution
    if bucket.acquire_token(task_id):
        print(f"[Task {task_id}] executing...")
        time.sleep(duration)
        print(f"[Task {task_id}] completed")
        return f"[Task {task_id}] result"
    else:
        """
        If token couldn't be acquired 
        (this can be implemented as a custom timeout per task or a fixed timeout 
        whose logic resides in the acquire_token function)
        """
        print(f"[Task {task_id}] Couldnot get Token")
        return None

# Task list with arrival delays and durations ( arrival at 0 means immediate arrival )
tasks = [
    {"id": 1, "arrival": 0, "duration": 3},
    {"id": 2, "arrival": 1, "duration": 2},
    {"id": 3, "arrival": 1, "duration": 1},
    {"id": 4, "arrival": 2, "duration": 1},
    {"id": 5, "arrival": 3, "duration": 1},
]

# Sorting by arrival time so that the sleep logic works
tasks.sort(key=lambda x: x["arrival"])

start_time = time.time()

with TokenBucket(capacity=5, refill_count=1, refill_interval=1, initial_token_count=0) as bucket:
    """
    Use a ThreadPoolExecutor to simulate concurrent task execution
    Max workers = 5 to allow up to 5 concurrent threads
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []

        for task in tasks:
            # calculate how long to sleep till the task arrives
            arrival = task["arrival"] - (time.time() - start_time)
            if arrival > 0:
                time.sleep(arrival)
            """
            Submit the task to the executor
            Tasks will start executing immediately if threads are available
            """
            futures.append(
                executor.submit(worker_task, task["id"], task["duration"], bucket)
            )

        # Wait for all submitted tasks to complete and print results
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                print(f"Completed: {result}")