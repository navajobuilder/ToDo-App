import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
from datetime import datetime
from plyer import notification

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart ToDo Manager")
        self.root.geometry("500x550")
        
        self.tasks = []
        self.priority_keywords = {
            "high": ["urgent", "deadline", "exam", "must", "important", "usmle"],
            "medium": ["call", "email", "meeting", "study"]
        }

        # --- UI Elements ---
        tk.Label(root, text="Task Description:", font=("Arial", 10, "bold")).pack(pady=5)
        self.task_entry = tk.Entry(root, width=40)
        self.task_entry.pack(pady=5)

        tk.Label(root, text="Alarm (HH:MM) - 24hr format:", font=("Arial", 10)).pack()
        self.time_entry = tk.Entry(root, width=15)
        self.time_entry.pack(pady=5)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Task", command=self.add_task, bg="#4CAF50", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_task, bg="#f44336", fg="white", width=12).pack(side=tk.LEFT, padx=5)

        # Treeview for the "List" display
        self.tree = ttk.Treeview(root, columns=("Priority", "Task", "Alarm"), show='headings', height=12)
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Task", text="Task Name")
        self.tree.heading("Alarm", text="Alarm Time")
        self.tree.column("Priority", width=80)
        self.tree.column("Task", width=250)
        self.tree.column("Alarm", width=100)
        self.tree.pack(pady=10, padx=10)

        # Coloring the priorities
        self.tree.tag_configure('HIGH', foreground='red')
        self.tree.tag_configure('MEDIUM', foreground='orange')
        self.tree.tag_configure('LOW', foreground='green')

        # Start background alarm thread
        threading.Thread(target=self.alarm_checker, daemon=True).start()

    def get_priority(self, name):
        name_lower = name.lower()
        if any(word in name_lower for word in self.priority_keywords["high"]):
            return (1, "HIGH")
        elif any(word in name_lower for word in self.priority_keywords["medium"]):
            return (2, "MEDIUM")
        return (3, "LOW")

    def add_task(self):
        name = self.task_entry.get()
        alarm = self.time_entry.get()
        
        if not name:
            messagebox.showwarning("Warning", "You must enter a task!")
            return

        priority_val, priority_label = self.get_priority(name)
        
        task = {
            "name": name,
            "priority_val": priority_val,
            "priority_label": priority_label,
            "time": alarm if alarm else "--:--",
            "notified": False
        }
        
        self.tasks.append(task)
        self.refresh_list()
        self.task_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)

    def delete_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            return
        
        for item in selected_item:
            # Find task by name in our list and remove it
            task_name = self.tree.item(item)['values'][1]
            self.tasks = [t for t in self.tasks if t['name'] != task_name]
            self.tree.delete(item)

    def refresh_list(self):
        # Clear and re-sort
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.tasks.sort(key=lambda x: x['priority_val'])
        
        for t in self.tasks:
            self.tree.insert('', tk.END, values=(t['priority_label'], t['name'], t['time']), tags=(t['priority_label'],))

    def alarm_checker(self):
        while True:
            now = datetime.now().strftime("%H:%M")
            for t in self.tasks:
                if t['time'] == now and not t['notified']:
                    notification.notify(
                        title="Task Alert!",
                        message=t['name'],
                        timeout=5
                    )
                    t['notified'] = True
            time.sleep(20)

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()