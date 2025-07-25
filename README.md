# Thread-Safe Token Bucket in Python

## Problem Statement

In a multithreaded environment, when multiple threads try to acquire tokens concurrently from a shared token bucket, the following issues can occur:

- Race conditions causing inconsistent token counts
- Unfair execution order where later threads may proceed before earlier ones
- Uncontrolled CPU usage if threads keep retrying without waiting

## Solution

To address these problems, a `threading.Condition` is used:

- Only one thread can access or modify the token count at a time
- Threads that fail to get a token wait on the condition
- When a token is added, one waiting thread is notified
- This coordination ensures safe, fair, and efficient token consumption

## File Overview

### `token_bucket.py`
- Implements the token bucket logic
- Uses a daemon thread to refill tokens periodically
- Employs `threading.Condition` for safe access and thread coordination

### `thread_pool_demo.py`
- Simulates a real-time scenario using `ThreadPoolExecutor`
- Tasks arrive with a delay and try to acquire a token before executing
- Demonstrates thread-safe usage of the token bucket

### `custom_queue_demo.py`
- Adds a `PriorityQueue` to handle tasks based on arrival time
- Ensures fair execution in the order of task arrival
- Useful when order and predictability are required

## Key Features

- Thread-safe token bucket
- Blocking mechanism with condition variables
- Fair task execution using priority queue
- Real-time simulation of rate-limited task processing

## Use Cases

- API rate limiting in concurrent systems
- Controlled execution of background jobs
- Simulating traffic shaping in local or test environments