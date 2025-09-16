import concurrent.futures
import random
import string
import time
import argparse
import numpy as np  # For Zipfian distribution

from cachica import client

# --- Configuration ---
NUM_REQUESTS = 20000
NUM_WORKERS = 500
KEY_POPULATION = 3000 # How many unique keys to work with

# --- Key Generation ---
def generate_random_string(length=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_zipfian_keys(a=1.2, size=NUM_REQUESTS, num_keys=KEY_POPULATION):
    """Generates a list of keys following a Zipfian distribution."""
    # Generate unique base keys
    base_keys = [f"key_{i}" for i in range(num_keys)]
    
    # Generate indices based on Zipf's law
    # Values will be clustered around the lower indices (0, 1, 2...)
    indices = np.random.zipf(a, size) % num_keys
    
    # Map indices back to the base keys
    return [base_keys[i] for i in indices]

# --- Worker Tasks for Different Workloads ---

def simple_set_get_worker(client_id, key):
    """Original worker: SET a key, then immediately GET it."""
    cl = client.Client(f"client_{client_id}")
    value = generate_random_string(16)
    
    try:
        if cl.SET(key, value, "EX", "30") != "OK":
            return (client_id, "FAIL", f"SET failed for key {key}")
        if cl.GET(key) != value:
            return (client_id, "FAIL", f"GET validation failed for key {key}")
        return (client_id, "SUCCESS", key)
    except Exception as e:
        return (client_id, "ERROR", str(e))

def read_heavy_worker(client_id, key):
    """80/20 Read/Write worker."""
    cl = client.Client(f"client_{client_id}")
    
    try:
        # 80% chance to GET, 20% chance to SET
        if random.random() < 0.80:
            cl.GET(key)
        else:
            value = generate_random_string(16)
            cl.SET(key, value, "EX", "60")
        return (client_id, "SUCCESS", key)
    except Exception as e:
        return (client_id, "ERROR", str(e))

# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load tester for Cachica.")
    parser.add_argument(
        "--workload", 
        choices=["simple", "read-heavy-zipf"], 
        default="simple",
        help="The type of workload to run."
    )
    args = parser.parse_args()

    print(f"Starting load test with workload: {args.workload}")
    print(f"Total requests: {NUM_REQUESTS}, Concurrent workers: {NUM_WORKERS}")

    # Prepare keys based on workload
    if args.workload == "simple":
        keys_for_test = [generate_random_string() for _ in range(NUM_REQUESTS)]
        worker_func = simple_set_get_worker
    elif args.workload == "read-heavy-zipf":
        print("Generating Zipfian key distribution...")
        keys_for_test = generate_zipfian_keys()
        worker_func = read_heavy_worker

    start_time = time.monotonic()
    success_count = 0
    fail_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = [executor.submit(worker_func, i, keys_for_test[i]) for i in range(NUM_REQUESTS)]

        for future in concurrent.futures.as_completed(futures):
            _, status, _ = future.result()
            if status == "SUCCESS":
                success_count += 1
            else:
                fail_count += 1
    
    # ... (rest of the summary printing code is the same)
    end_time = time.monotonic()
    duration = end_time - start_time
    rps = NUM_REQUESTS / duration if duration > 0 else 0
    
    print("\n--- Test Summary ---")
    print(f"Successful: {success_count}, Failed/Errors: {fail_count}")
    print(f"Total duration: {duration:.2f}s, Requests Per Second (RPS): {rps:.2f}")

