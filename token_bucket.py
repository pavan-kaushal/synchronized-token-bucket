import threading
import time

class TokenBucket:
    def __init__( self, capacity: int, refill_interval: int, refill_count: int, initial_token_count: int ):
        # Maximum tokens the bucket can hold
        self._capacity = capacity

        # Current number of tokens
        self._tokens = initial_token_count

        # Time interval (in seconds) between each token refill cycle.
        self._refill_interval = refill_interval

        # Number of tokens to add to the bucket at each refill cycle.
        self._refill_count = refill_count

        # Lock for thread safety
        self._lock = threading.RLock()

        """
        Condition variable used to coordinate access to the token bucket among multiple threads.
        Threads that try to acquire a token when none are available will wait on this condition.
        Once tokens are refilled, the condition is notified to wake up waiting threads.
        """
        self._condition = threading.Condition(self._lock)
        
        self._start_refill_timer()

        print(
            f"TokenBucket Created: capacity={capacity}, refill_interval={refill_interval}, refill_count={refill_count}, initial_token_count={initial_token_count}"
        )

    def _start_refill_timer(self):
        # Launches a daemon thread that runs the token refill loop
        threading.Thread(target=self._refill_tokens, daemon=True).start()

    def _refill_tokens(self):
        """
        Periodically refills the token bucket by a specified number of tokens after each interval.
        Note: Token availability is evaluated only at each interval; intermediate changes are not tracked.
        Example: Adds 5 tokens every 3 seconds, regardless of usage in between.
        """
        while True:
            time.sleep(self._refill_interval)
            with self._condition:
                if self._tokens < self._capacity:
                    self._tokens = min(self._tokens + self._refill_count, self._capacity)
                    print(f"[Refill Thread] Refilled 1 token. Current: {self._tokens}/{self._capacity}")
                    self._condition.notify_all()

    def acquire_token(self, task_id) -> bool:
        # Called by threads when they need to acquire a token
        print(f"Thread with [Task {task_id}] requesting token")

        try:
            with self._condition:
                # Wait if there are no tokens available
                while self._tokens <= 0:
                    """
                    using wait() inside this block releases the lock and makes the thread go to sleep. 
                    waiting to be notified by the refill tokens thread
                    """
                    self._condition.wait()

                # Consume a token and proceed
                self._tokens -= 1
                print(f"Thread with [Task {task_id}] acquired token. "
                    f"Remaining: {self._tokens}/{self._capacity}")
                return True
        except Exception as e:
            print(f"Thread with [Task {task_id}] failed to acquire token, error: {e}")
            return False


    def __enter__(self):
        """Bucket Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Bucket Context manager exit"""