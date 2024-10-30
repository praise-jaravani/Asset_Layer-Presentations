import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from deadline_manager import DocumentDeadlineManager
from pathlib import Path
import os
from datetime import datetime
from ttkthemes import ThemedTk
import pandas as pd

class DeadlineAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Deadline Analyzer")
        self.root.geometry("1200x800")
        
        # Initialize deadline manager
        self.manager = DocumentDeadlineManager()
        
        # Configure styles
        self.setup_styles()
        
        # Create main container
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Create UI elements
        self.create_header()
        self.create_file_section()
        self.create_results_section()
        self.create_deadlines_section()
        
    def setup_styles(self):
        # Configure custom styles
        style = ttk.Style()
        
        # Header style
        style.configure(
            "Header.TLabel",
            font=("Helvetica", 24, "bold"),
            padding=20
        )
        
        # Section header style
        style.configure(
            "SectionHeader.TLabel",
            font=("Helvetica", 16, "bold"),
            padding=10
        )
        
        # Button styles
        style.configure(
            "Action.TButton",
            font=("Helvetica", 12),
            padding=10
        )
        
        # Treeview styles
        style.configure(
            "Treeview",
            font=("Helvetica", 10),
            rowheight=30
        )
        
        style.configure(
            "Treeview.Heading",
            font=("Helvetica", 12, "bold")
        )

    def create_header(self):
        header = ttk.Label(
            self.main_container,
            text="Document Deadline Analyzer",
            style="Header.TLabel"
        )
        header.grid(row=0, column=0, pady=20)

    def create_file_section(self):
        # File section frame
        file_frame = ttk.LabelFrame(
            self.main_container,
            text="Document Analysis",
            padding="20"
        )
        file_frame.grid(row=1, column=0, sticky="ew", pady=10)
        file_frame.grid_columnconfigure(1, weight=1)
        
        # File path entry and button
        self.file_path = tk.StringVar()
        path_entry = ttk.Entry(
            file_frame,
            textvariable=self.file_path,
            font=("Helvetica", 10)
        )
        path_entry.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5)
        
        browse_btn = ttk.Button(
            file_frame,
            text="Browse",
            command=self.browse_file,
            style="Action.TButton"
        )
        browse_btn.grid(row=0, column=2, padx=5)
        
        analyze_btn = ttk.Button(
            file_frame,
            text="Analyze Document",
            command=self.analyze_document,
            style="Action.TButton"
        )
        analyze_btn.grid(row=0, column=3, padx=5)

    def create_results_section(self):
        # Results section frame
        results_frame = ttk.LabelFrame(
            self.main_container,
            text="Analysis Results",
            padding="20"
        )
        results_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        # Results text area
        self.results_text = tk.Text(
            results_frame,
            height=10,
            wrap=tk.WORD,
            font=("Helvetica", 10),
            bg="#f5f5f5"
        )
        self.results_text.grid(row=0, column=0, sticky="ew")
        results_frame.grid_columnconfigure(0, weight=1)

    def create_deadlines_section(self):
        # Deadlines section frame
        deadlines_frame = ttk.LabelFrame(
            self.main_container,
            text="Deadlines Overview",
            padding="20"
        )
        deadlines_frame.grid(row=3, column=0, sticky="nsew", pady=10)
        deadlines_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons frame
        btn_frame = ttk.Frame(deadlines_frame)
        btn_frame.grid(row=0, column=0, pady=10)
        
        # View buttons
        ttk.Button(
            btn_frame,
            text="View All Deadlines",
            command=lambda: self.view_deadlines("all"),
            style="Action.TButton"
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            btn_frame,
            text="View Upcoming Deadlines",
            command=lambda: self.view_deadlines("upcoming"),
            style="Action.TButton"
        ).grid(row=0, column=1, padx=5)
        
        ttk.Button(
            btn_frame,
            text="View Expired Deadlines",
            command=lambda: self.view_deadlines("expired"),
            style="Action.TButton"
        ).grid(row=0, column=2, padx=5)
        
        # Treeview for deadlines
        self.tree = ttk.Treeview(
            deadlines_frame,
            columns=("ID", "Name", "Type", "Deadline", "Source", "Confidence"),
            show="headings",
            height=10
        )
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Document Name")
        self.tree.heading("Type", text="Document Type")
        self.tree.heading("Deadline", text="Deadline Date")
        self.tree.heading("Source", text="Source")
        self.tree.heading("Confidence", text="Confidence")
        
        # Column widths
        self.tree.column("ID", width=100)
        self.tree.column("Name", width=200)
        self.tree.column("Type", width=150)
        self.tree.column("Deadline", width=150)
        self.tree.column("Source", width=100)
        self.tree.column("Confidence", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            deadlines_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid treeview and scrollbar
        self.tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Document",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        self.file_path.set(filename)

    def analyze_document(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file first")
            return
            
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Analyzing document...\n\n")
            self.root.update()
            
            self.manager.process_new_document(content, Path(file_path).name)
            
            # Update results
            self.view_deadlines("all")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error analyzing document: {str(e)}")

    def view_deadlines(self, deadline_type="all"):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Get deadlines based on type
        if deadline_type == "upcoming":
            deadlines = self.manager.get_upcoming_deadlines()
        elif deadline_type == "expired":
            deadlines = self.manager.get_expired_deadlines()
        else:
            deadlines = self.manager.get_all_deadlines()
            
        # Insert deadlines into treeview
        for _, row in deadlines.iterrows():
            self.tree.insert(
                "",
                "end",
                values=(
                    row['document_id'],
                    row['document_name'],
                    row['document_type'],
                    row['deadline_date'].strftime('%Y-%m-%d'),
                    row['deadline_source'],
                    row['confidence_level']
                )
            )

def main():
    root = ThemedTk(theme="arc")  # You can try different themes like "arc", "equilux", "clearlooks"
    app = DeadlineAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
