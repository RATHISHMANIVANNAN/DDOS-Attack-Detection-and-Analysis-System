import threading
import requests
import time
import csv
from datetime import datetime

# Web server URL (replace with your ESP32's IP address)
url = 'http://10.123.75.4:8000'  # Replace with your ESP32's IP address
log_file = 'traffic_log.csv'

# Initialize the log file with headers
with open(log_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Request_Status", "Response_Time", "Requests_Per_Second"])

# Track request count and time window
request_count, start_time_window = 0, time.time()

def log_request(status_code, response_time):
    global request_count, start_time_window
    current_time = time.time()
    requests_per_second = request_count if current_time - start_time_window < 1 else 0
    
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), status_code, response_time, requests_per_second])

    request_count = request_count + 1 if current_time - start_time_window < 1 else 1
    start_time_window = current_time if current_time - start_time_window >= 1 else start_time_window

def send_request():
    start_time = time.time()
    try:
        response = requests.get(url, timeout=5)
        log_request(response.status_code, round(time.time() - start_time, 2))
    except requests.exceptions.RequestException:
        log_request("Failed", round(time.time() - start_time, 2))

def simulate_traffic(requests_per_second, burst_size=1, delay=1):
    print(f"Simulating traffic at {requests_per_second} requests per second. Press Ctrl + C to stop.")
    try:
        while True:
            threads = [threading.Thread(target=send_request) for _ in range(burst_size)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nTraffic simulation stopped.")

if __name__ == "__main__":
    print("Choose the type of traffic to simulate:")
    print("1. Normal Traffic (1 request every 2 seconds)")
    print("2. Low-Rate DDoS Attack (50 requests in 0.5s bursts)")
    print("3. High-Rate DDoS Attack (5000 requests per burst)")

    choice = input("Enter your choice (1/2/3): ")
    
    if choice == '1':
        simulate_traffic(requests_per_second=0.5, burst_size=1, delay=2)
    elif choice == '2':
        simulate_traffic(requests_per_second=100, burst_size=50, delay=0.5)
    elif choice == '3':
        simulate_traffic(requests_per_second=10000, burst_size=5000, delay=0.1)
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")
