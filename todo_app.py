import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced To-Do List")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize database
        self.conn = sqlite3.connect('todo.db')
        self.create_table()
        
        # GUI Elements
        self.create_widgets()
        
    def create_table(self):
        """Create tasks table if not exists"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 1,
                deadline TEXT,
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def create_widgets(self):
        """Create all GUI elements"""
        # Frame for input fields
        input_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        input_frame.pack(fill=tk.X)
        
        # Task title
        tk.Label(input_frame, text="Task Title:", bg="#f0f0f0").grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(input_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Task description
        tk.Label(input_frame, text="Description:", bg="#f0f0f0").grid(row=1, column=0, sticky="w")
        self.desc_entry = tk.Text(input_frame, width=40, height=3)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Priority
        tk.Label(input_frame, text="Priority:", bg="#f0f0f0").grid(row=2, column=0, sticky="w")
        self.priority_var = tk.IntVar(value=1)
        tk.Radiobutton(input_frame, text="Low", variable=self.priority_var, value=1, bg="#f0f0f0").grid(row=2, column=1, sticky="w")
        tk.Radiobutton(input_frame, text="Medium", variable=self.priority_var, value=2, bg="#f0f0f0").grid(row=2, column=1)
        tk.Radiobutton(input_frame, text="High", variable=self.priority_var, value=3, bg="#f0f0f0").grid(row=2, column=1, sticky="e")
        
        # Deadline
        tk.Label(input_frame, text="Deadline:", bg="#f0f0f0").grid(row=3, column=0, sticky="w")
        self.deadline_entry = tk.Entry(input_frame, width=40)
        self.deadline_entry.grid(row=3, column=1, padx=5, pady=5)
        self.deadline_entry.insert(0, "YYYY-MM-DD")
        
        # Action buttons
        tk.Button(input_frame, text="Add Task", command=self.add_task).grid(row=4, column=1, pady=10, sticky="e")
        tk.Button(input_frame, text="Clear Fields", command=self.clear_fields).grid(row=4, column=0, pady=10, sticky="w")
        
        # Task list frame
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for displaying tasks
        self.task_tree = ttk.Treeview(list_frame, columns=("Title", "Description", "Priority", "Deadline", "Completed"), selectmode="extended")
        
        # Set up columns
        self.task_tree.heading("#0", text="ID")
        self.task_tree.heading("Title", text="Title")
        self.task_tree.heading("Description", text="Description")
        self.task_tree.heading("Priority", text="Priority")
        self.task_tree.heading("Deadline", text="Deadline")
        self.task_tree.heading("Completed", text="Completed")
        
        self.task_tree.column("#0", width=40, stretch=tk.NO)
        self.task_tree.column("Title", width=200)
        self.task_tree.column("Description", width=250)
        self.task_tree.column("Priority", width=80, anchor=tk.CENTER)
        self.task_tree.column("Deadline", width=100, anchor=tk.CENTER)
        self.task_tree.column("Completed", width=80, anchor=tk.CENTER)
        
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.task_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        control_frame.pack(fill=tk.X)
        
        tk.Button(control_frame, text="Mark Complete", command=self.mark_complete).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Delete Task", command=self.delete_task).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Edit Task", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Refresh", command=self.load_tasks).pack(side=tk.RIGHT, padx=5)
        
        # Load existing tasks
        self.load_tasks()
    
    def add_task(self):
        """Add a new task to the database"""
        title = self.title_entry.get().strip()
        description = self.desc_entry.get("1.0", tk.END).strip()
        priority = self.priority_var.get()
        deadline = self.deadline_entry.get().strip()
        
        if not title:
            messagebox.showerror("Error", "Task title is required!")
            return
        
        # Convert deadline to SQL date format if provided
        try:
            if deadline and deadline != "YYYY-MM-DD":
                datetime.strptime(deadline, "%Y-%m-%d")  # Validate date format
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, description, priority, deadline)
            VALUES (?, ?, ?, ?)
        ''', (title, description, priority, deadline if deadline != "YYYY-MM-DD" else None))
        self.conn.commit()
        
        self.clear_fields()
        self.load_tasks()
        messagebox.showinfo("Success", "Task added successfully!")
    
    def load_tasks(self):
        """Load tasks from database into the treeview"""
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks ORDER BY completed, priority DESC, deadline ASC')
        tasks = cursor.fetchall()
        
        for task in tasks:
            task_id = task[0]
            completed = "Yes" if task[5] else "No"
            priority = ["Low", "Medium", "High"][task[3]-1] if task[5] == 0 else "✓"
            deadline = task[4] if task[4] else "None"
            
            self.task_tree.insert("", tk.END, text=task_id, 
                                values=(task[1], task[2], priority, deadline, completed),
                                tags=('completed' if task[5] else '',))
            
            # Style completed tasks differently
            self.task_tree.tag_configure('completed', foreground="gray")
    
    def clear_fields(self):
        """Clear all input fields"""
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete("1.0", tk.END)
        self.priority_var.set(1)
        self.deadline_entry.delete(0, tk.END)
        self.deadline_entry.insert(0, "YYYY-MM-DD")
    
    def mark_complete(self):
        """Mark selected tasks as complete or incomplete"""
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No task selected!")
            return
        
        cursor = self.conn.cursor()
        for item in selected_items:
            task_id = self.task_tree.item(item)['text']
            current_completed = self.task_tree.item(item)['values'][4] == "Yes"
            cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', 
                         (0 if current_completed else 1, task_id))
        self.conn.commit()
        
        self.load_tasks()
    
    def delete_task(self):
        """Delete selected tasks"""
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No task selected!")
            return
        
        if messagebox.askyesno("Confirm", "Delete selected task(s)?"):
            cursor = self.conn.cursor()
            for item in selected_items:
                task_id = self.task_tree.item(item)['text']
                cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            self.conn.commit()
            
            self.load_tasks()
    
    def edit_task(self):
        """Edit selected task"""
        selected_items = self.task_tree.selection()
        if len(selected_items) != 1:
            messagebox.showerror("Error", "Please select exactly one task to edit!")
            return
        
        item = selected_items[0]
        task_id = self.task_tree.item(item)['text']
        
        # Get task details from database
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("400x300")
        
        # Task title
        tk.Label(edit_window, text="Task Title:").pack()
        title_entry = tk.Entry(edit_window, width=40)
        title_entry.insert(0, task[1])
        title_entry.pack()
        
        # Task description
        tk.Label(edit_window, text="Description:").pack()
        desc_entry = tk.Text(edit_window, width=40, height=3)
        desc_entry.insert("1.0", task[2] if task[2] else "")
        desc_entry.pack()
        
        # Priority
        tk.Label(edit_window, text="Priority:").pack()
        priority_var = tk.IntVar(value=task[3])
        tk.Radiobutton(edit_window, text="Low", variable=priority_var, value=1).pack()
        tk.Radiobutton(edit_window, text="Medium", variable=priority_var, value=2).pack()
        tk.Radiobutton(edit_window, text="High", variable=priority_var, value=3).pack()
        
        # Deadline
        tk.Label(edit_window, text="Deadline (YYYY-MM-DD):").pack()
        deadline_entry = tk.Entry(edit_window, width=40)
        deadline_entry.insert(0, task[4] if task[4] else "")
        deadline_entry.pack()
        
        # Save button
        def save_changes():
            """Save edited task to database"""
            new_title = title_entry.get().strip()
            new_description = desc_entry.get("1.0", tk.END).strip()
            new_priority = priority_var.get()
            new_deadline = deadline_entry.get().strip()
            
            if not new_title:
                messagebox.showerror("Error", "Task title is required!")
                return
            
            # Validate date format
            try:
                if new_deadline:
                    datetime.strptime(new_deadline, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            cursor.execute('''
                UPDATE tasks 
                SET title = ?, description = ?, priority = ?, deadline = ?
                WHERE id = ?
            ''', (new_title, new_description, new_priority, new_deadline or None, task_id))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Task updated successfully!")
            edit_window.destroy()
            self.load_tasks()
        
        tk.Button(edit_window, text="Save Changes", command=save_changes).pack(pady=10)
    
    def __del__(self):
        """Close database connection when app closes"""
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
