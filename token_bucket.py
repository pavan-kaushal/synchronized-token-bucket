import threading
import time

class TokenBucket:
    def __init__( self, capacity: int, refill_rate: int, initial_token_count: int ):
        self._capacity = capacity
        self._refill_rate = refill_rate
        self._tokens = initial_token_count

        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        
        self._refill_timer = None

        self._start_refill_timer()

        print(
            f"TokenBucket Created: capacity={capacity}, "
            f"refill_rate={refill_rate}"
        )

    def _start_refill_timer(self):
        threading.Thread(target=self._refill_tokens, daemon=True).start()

    def _refill_tokens(self):
        while True:
            time.sleep(1)
            with self._condition:
                if self._tokens < self._capacity:
                    self._tokens += 1
                    print(f"Refilled 1 token. Current: {self._tokens}/{self._capacity}")
                    self._condition.notify_all()

    def acquire_token(self) -> bool:

        thread_name = threading.current_thread().name
        print(f"Thread {thread_name} requesting token")

        with self._condition:

            while self._tokens <= 0:

                self._condition.wait()

            self._tokens -= 1
            print(f"Thread {thread_name} acquired token. "
                              f"Remaining: {self._tokens}/{self._capacity}")
            return True

    def shutdown(self):
        with self._condition:

            print("Shutting down TokenBucket")

            if self._refill_timer:
                self._refill_timer.cancel()
                self._refill_timer = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically shutdown."""
        self.shutdown()


if __name__ == "__main__":
    import concurrent.futures

    def worker_task(task_id: int, bucket: TokenBucket):
        if bucket.acquire_token():
            print(f"Task {task_id} executing...")
            time.sleep(0.5)
            print(f"Task {task_id} completed")
            return f"Task {task_id} result"
        else:
            print(f"Task {task_id} timed out")
            return None

    with TokenBucket(capacity=5, refill_rate=1, initial_token_count=3) as bucket:

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(worker_task, i, bucket) for i in range(5)
            ]

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    print(f"Completed: {result}")