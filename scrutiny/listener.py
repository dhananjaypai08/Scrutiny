import time
import subprocess

def read_logs(filename):
    process = subprocess.Popen(['tail', '-f', filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        while True:
            line = process.stdout.readline().decode().strip()
            if line:
                # Process the log data here
                print(line)
            time.sleep(1)  # Adjust sleep time as needed
    except KeyboardInterrupt:
        process.terminate()

# Example usage:
read_logs("../client/logfile.log")



