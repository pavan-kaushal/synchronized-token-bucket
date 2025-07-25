import threading
import time

class TokenBucket:
    def __init__( self, capacity: int, refill_rate: int, initial_token_count: int ):
        self._capacity = capacity
        self._refill_rate = refill_rate
        self._tokens = initial_token_count

        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        
        self._start_refill_timer()

        print(
            f"TokenBucket Created: capacity={capacity}, refill_rate={refill_rate}, initial_token_count={initial_token_count}"
        )

    def _start_refill_timer(self):
        threading.Thread(target=self._refill_tokens, daemon=True).start()

    def _refill_tokens(self):
        while True:
            time.sleep(1)
            with self._condition:
                if self._tokens < self._capacity:
                    self._tokens += 1
                    print(f"[Refill Thread] Refilled 1 token. Current: {self._tokens}/{self._capacity}")
                    self._condition.notify_all()

    def acquire_token(self, task_id) -> bool:

        print(f"Thread with [Task {task_id}] requesting token")

        with self._condition:

            while self._tokens <= 0:
                self._condition.wait()

            self._tokens -= 1
            print(f"Thread with [Task {task_id}] acquired token. "
                  f"Remaining: {self._tokens}/{self._capacity}")
            return True

    def __enter__(self):
        """Bucket Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Bucket Context manager exit"""