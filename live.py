import subprocess
import time

def keep_alive(script_name):
    while True:
        print(f"Starting {script_name}...")
        process = subprocess.Popen(["python", script_name])

        # Wait for the process to finish
        process.wait()

        print(f"{script_name} stopped. Restarting in 5 seconds...")
        time.sleep(5)  # Wait before restarting

if __name__ == "__main__":
    keep_alive("h.py")
