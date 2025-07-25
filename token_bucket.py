import threading
import time

class TokenBucket:
    def __init__( self, capacity: int, refill_interval: int, refill_count: int, initial_token_count: int ):
        self._capacity = capacity
        self._tokens = initial_token_count
        self._refill_interval = refill_interval
        self._refill_count = refill_count

        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        
        self._start_refill_timer()

        print(
            f"TokenBucket Created: capacity={capacity}, refill_interval={refill_interval}, refill_count={refill_count}, initial_token_count={initial_token_count}"
        )

    def _start_refill_timer(self):
        # Launches a daemon thread that runs the token refill loop
        threading.Thread(target=self._refill_tokens, daemon=True).start()

    def _refill_tokens(self):
        # Waits for an interval to refill the bucket with the given refill count (ex. 5 tokens in 3 seconds)
        while True:
            time.sleep(self._refill_interval)
            with self._condition:
                if self._tokens < self._capacity:
                    self._tokens = max(self._tokens + self._refill_count, self._capacity)
                    print(f"[Refill Thread] Refilled 1 token. Current: {self._tokens}/{self._capacity}")
                    self._condition.notify_all()

    def acquire_token(self, task_id) -> bool:
        # Called by threads when they need to acquire a token
        print(f"Thread with [Task {task_id}] requesting token")

        with self._condition:
            # Wait if there are no tokens available
            while self._tokens <= 0:
                self._condition.wait()

            # Consume a token and proceed
            self._tokens -= 1
            print(f"Thread with [Task {task_id}] acquired token. "
                  f"Remaining: {self._tokens}/{self._capacity}")
            return True

    def __enter__(self):
        """Bucket Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Bucket Context manager exit"""