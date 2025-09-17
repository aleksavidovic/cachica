import random
import string
import time
from locust import User, task, between

# Import your actual client
from cachica import client

# --- Helper functions (from your previous script) ---
def generate_random_string(length=8):
    """Generates a random string for keys and values."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

class CacheClient:
    """A wrapper for your client to handle timing and events for Locust."""
    def __init__(self, user: User):
        self._user = user
        # Each virtual user gets its own client instance
        self._client = client.Client()

    def _request_wrapper(self, name: str, func, *args, **kwargs):
        """Measures request time and fires success/failure events."""
        start_time = time.monotonic()
        try:
            result = func(*args, **kwargs)
            total_time = int((time.monotonic() - start_time) * 1000)
            self._user.environment.events.request.fire(
                request_type="CACHE",
                name=name,
                response_time=total_time,
                response_length=len(result) if result else 0,
            )
            return result
        except Exception as e:
            total_time = int((time.monotonic() - start_time) * 1000)
            self._user.environment.events.request.fire(
                request_type="CACHE",
                name=name,
                response_time=total_time,
                response_length=0,
                exception=e,
            )
            raise

    def GET(self, key):
        return self._request_wrapper("GET", self._client.GET, key)

    def SET(self, key, value, *args):
        return self._request_wrapper("SET", self._client.SET, key, value, *args)


class CacheUser(User):
    # Each virtual user will wait 10 to 100ms between tasks
    wait_time = between(0.01, 0.1)

    def __init__(self, environment):
        super().__init__(environment)
        # Give each User its own client instance with event hooks
        self.client = CacheClient(self)

    def on_start(self):
        """Called when a virtual user starts running."""
        print("A new user is starting")

    @task(4)  # This task will be picked 4 times more often than the one below
    def read_heavy_workload(self):
        """80% GET, 20% SET"""
        key = generate_random_string(10)
        if random.random() < 0.80:
            self.client.GET(key)
        else:
            value = generate_random_string(20)
            self.client.SET(key, value, "EX", "60")

    @task(1) # This task has a weight of 1
    def set_and_get_workload(self):
        """Simulates setting a key and immediately getting it back."""
        key = generate_random_string()
        value = generate_random_string(16)
        
        set_response = self.client.SET(key, value, "EX", "30")
        if set_response == "OK":
            self.client.GET(key)


