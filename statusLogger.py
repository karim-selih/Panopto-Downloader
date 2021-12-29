import threading
import sys

class Task:
    def __init__(self, task_name: str, progress: int) -> None:
        self.task_name = task_name
        self.progress = progress
        self.lock = threading.Lock()

    def update_progress(self, progress: int):
        self.lock.acquire()
        self.progress = progress
        self.lock.release()


class StatusLogger:
    
    def __init__(self) -> None:
        self.active_tasks = {} # task_id -> task
        self.completed_tasks = []
        self.lock = threading.RLock()

    def add_task (self, task_name: str, task_id: int):
        self.lock.acquire()
        new_task = Task(task_name, 0)
        self.active_tasks[task_id] = new_task
        self.lock.release()
    
    def update_state(self, task_id: int, progress: int):
        self.lock.acquire()
        self.active_tasks[task_id].update_progress(progress)
        self.lock.release()

    def finished_task(self, task_id: int):
        self.lock.acquire()
        completed = self.active_tasks.pop(task_id)
        self.completed_tasks.append(completed)
        self.lock.release()

    def print_progress_bar(self,status,max,text):
        n_bar =10 #size of progress bar
        j= status/max
        sys.stdout.write("\033[K") # clear line
        sys.stdout.write(f"[{'=' * int(n_bar * j):{n_bar}s}] {int(100 * j)}%  {text}\n")
    
    def reprint(self):
        self.lock.acquire()
        for compl in self.completed_tasks:
            sys.stdout.write("\033[K") # clear line
            sys.stdout.write(f"Downloaded  {compl.task_name}\n")
        self.completed_tasks = []

        for key in sorted(self.active_tasks.keys()):
            st = self.active_tasks[key]
            self.print_progress_bar(st.progress, 100, st.task_name)

        if not self.finished():
            sys.stdout.write("\033[{}F".format(str(len(self.active_tasks.keys())))) # Cursor up number of lines

        self.lock.release()

    def finished(self):
        self.lock.acquire()
        remain = len(self.active_tasks.keys())
        self.lock.release()
        return remain == 0


