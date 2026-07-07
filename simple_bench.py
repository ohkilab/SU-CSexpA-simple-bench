import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor


def send_request(url):
    try:
        response = requests.get(url)
        return response.status_code
    except Exception as e:
        return None


def judge_end(local_end_time, global_end_time):
    now_time = time.time()
    return (now_time >= local_end_time) or (now_time >= global_end_time)


def benchmark(url, max_worker, max_time, global_end_time):
    start_time = time.time()
    end_time = start_time + max_time
    completed_requests = 0
    total_requests = 0
    lock = threading.Lock()

    # print(f"local start time: {start_time}, local end_time: {end_time}")

    req_limit = 500

    def request_worker():
        nonlocal completed_requests, total_requests
        while (completed_requests < req_limit) and (
            not judge_end(end_time, global_end_time)
        ):
            status_code = send_request(url)
            with lock:
                total_requests += 1
                if status_code is not None:
                    completed_requests += 1

    with ThreadPoolExecutor(max_workers=max_worker) as executor:
        futures = {executor.submit(request_worker) for _ in range(max_worker)}

        while (completed_requests < req_limit) and (
            not judge_end(end_time, global_end_time)
        ):
            time.sleep(0.1)  # Polling interval to check active threads
            with lock:
                active_threads = sum(1 for future in futures if not future.done())
            if active_threads < max_worker:
                futures.update(
                    {
                        executor.submit(request_worker)
                        for _ in range(max_worker - active_threads)
                    }
                )

    elapsed_time = time.time() - start_time
    return completed_requests, elapsed_time


def build_request_url(base_url, query):
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{query}"


def main():
    url = "http://{your-server-ip}" # Replace with your server address
    queries = [
        "sortOrder=desc&tag=dollfie",
        "sortOrder=asc&tag=folklore",
        "sortOrder=desc&tag=kudus&tag=midcity&tagOperator=or",
        "sortOrder=asc&tag=partidadiscoteca26812&tag=lis&tagOperator=and",
        "sortOrder=desc&tag=gnimocemoh",
        "sortOrder=asc&tag=cabaret",
        "sortOrder=desc&tag=margarita&tag=bottles&tagOperator=or",
    ]

    max_worker = 5  # Number of concurrent threads
    max_time = 500
    max_time_per_query = 60  # Duration in seconds

    start_time = time.time()
    end_time = start_time + max_time

    # print(f"global start time: {time.time()}, end_time: {end_time}")

    for query in queries:
        req_url = build_request_url(url, query)

        results = benchmark(req_url, max_worker, max_time_per_query, end_time)
        print(f"score: {results[0]/results[1]}")
        # print(f"Completed requests: {results[0]}, Elapsed time: {results[1]} seconds")
        # print(f"now: {time.time()}\n")


if __name__ == "__main__":
    main()
