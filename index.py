import time
import os

def tail_pm2_log(app_name):
    log_path = os.path.expanduser(f"~/.pm2/logs/{app_name}-out.log")
    print(f"Tailing log file: {log_path}")

    try:
        with open(log_path, 'r') as f:
            # Go to end of file
            f.seek(0, os.SEEK_END)

            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.01)  # Wait for new data
                    continue
                print(line, end='')  # Print new log line as it arrives

    except FileNotFoundError:
        print(f"Log file not found: {log_path}")
    except Exception as e:
        print(f"Error reading log file: {e}")

if __name__ == "__main__":
    app_name = "node-server"  # Change this to your PM2 app name
    tail_pm2_log(app_name)
