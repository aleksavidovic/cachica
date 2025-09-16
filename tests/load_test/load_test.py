import concurrent.futures
import random
import string
import time
import threading
from cachica import client


NUM_REQUESTS = 1000
NUM_WORKERS = 50  

def generate_random_string(length=8):
    """Generates a random string for keys and values."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def worker_task(client_id):
    """
    A single task performed by one worker.
    It simulates a user session: set a key, then get it back.
    """
    cl = client.Client(client_id) # Each thread gets its own client instance
    
    key = generate_random_string()
    value = generate_random_string(16)
    expiry = str(random.randint(5, 60))

    try:
        set_response = cl.SET(key, value, "EX", expiry)
        if set_response != 'OK':
            return (client_id, "FAIL", f"SET failed for key {key}")
            
        get_response = cl.GET(key)
        if get_response == value:
            return (client_id, "SUCCESS", f"Handled key {key}")
        else:
            return (client_id, "FAILURE", f"Handled key {key}")
    except Exception as e:
        return (client_id, "ERROR", str(e))

# --- Main execution ---
if __name__ == "__main__":
    print(f"Starting load test with {NUM_REQUESTS} requests across {NUM_WORKERS} workers.")
    start_time = time.monotonic()
    
    success_count = 0
    fail_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        # Submit all the tasks to the pool
        futures = [executor.submit(worker_task, i) for i in range(NUM_REQUESTS)]

        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            client_id, status, message = future.result()
            if status == "SUCCESS":
                success_count += 1
            else:
                fail_count += 1
                print(f"Client {client_id} reported {status}: {message}")

    end_time = time.monotonic()
    duration = end_time - start_time
    rps = NUM_REQUESTS / duration

    print("\n--- Test Summary ---")
    print(f"Total requests: {NUM_REQUESTS}")
    print(f"Successful: {success_count}")
    print(f"Failed/Errors: {fail_count}")
    print(f"Total duration: {duration:.2f} seconds")
    print(f"Requests Per Second (RPS): {rps:.2f}")

