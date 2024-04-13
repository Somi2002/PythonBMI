import time
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("bmi.py"):
            print(f"{event.src_path} has changed, restarting...")
            os.system("python bmi.py")

if __name__ == "__main__":
    path = "C:\\Users\\siman\\Desktop\\PythonBMI"  # Set the directory you want to monitor
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
