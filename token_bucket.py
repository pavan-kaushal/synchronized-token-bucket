import threading
import time
import random

class BlockingTokenBucket:
    def __init__(self, capacity: int, refill_interval: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_interval = refill_interval
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

        threading.Thread(target=self._refill_tokens, daemon=True).start()

    def _refill_tokens(self):
        while True:
            time.sleep(self.refill_interval)
            with self.condition:
                if self.tokens < self.capacity:
                    self.tokens += 1
                    print(f"[Refill] Token added. Total Tokens = {self.tokens}")
                    self.condition.notify()

    def take(self, thread_name):
        with self.condition:
            while self.tokens == 0:
                print(f"[{thread_name}] Waiting for token...")
                self.condition.wait()

            self.tokens -= 1
            print(f"[{thread_name}] Consumed token. Tokens left = {self.tokens}")

def worker(bucket: BlockingTokenBucket, thread_name: str):
    time.sleep(random.uniform(0, 5))
    bucket.take(thread_name)
    print(f"[{thread_name}] Executing...")
    time.sleep(random.uniform(0, 5))

if __name__ == "__main__":
    bucket = BlockingTokenBucket(capacity=3, refill_interval=2)

    for i in range(5):
        threading.Thread(target=worker, args=(bucket, f"Task-{i+1}")).start()
