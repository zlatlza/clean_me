import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import re
import csv
import io

class DataCleaner:
    def __init__(self, delimiter=","):
        self.delimiter = delimiter
        self.data = []
        self.history = []
    
    def load_data(self, text):
        self.data = text.split("\n")
        self.history.append(self.data.copy())
    
    def set_delimiter(self, delimiter):
        self.delimiter = delimiter
    
    def separate_data_into_rows(self):
        return [line.split(self.delimiter) for line in self.data]
    
    def find_pattern_instances(self, pattern):
        regex = re.compile(rf"\s*{pattern}\s*")
        instances = [(i, match.start(), match.end()) for i, line in enumerate(self.data) for match in regex.finditer(line)]
        return instances
    
    def cleanse_instance(self, index, start, end):
        if 0 <= index < len(self.data):
            line = self.data[index]
            self.data[index] = line[:start] + line[end:]
            self.history.append(self.data.copy())
    
    def delete_line(self, index):
        if 0 <= index < len(self.data):
            self.data.pop(index)
            self.history.append(self.data.copy())
    
    def cleanse_all(self, pattern):
        regex = re.compile(rf"\s*{pattern}\s*")
        for i, line in enumerate(self.data):
            self.data[i] = regex.sub("", line)
        self.history.append(self.data.copy())
    
    def cleanse_short_lines(self, length):
        self.data = [line for line in self.data if len(line.strip()) >= length]
        self.history.append(self.data.copy())
    
    def set_delimiters_from_pattern(self, pattern, start, end):
        regex = re.compile(rf"\s*{pattern}\s*")
        for i, line in enumerate(self.data):
            part_to_modify = line[start:end]
            modified_part = regex.sub(self.delimiter, part_to_modify)
            self.data[i] = line[:start] + modified_part + line[end:]
        self.history.append(self.data.copy())

    def cleanse_range(self, start, end):
        for i in range(len(self.data)):
            line = self.data[i]
            if len(line) >= end:
                self.data[i] = line[:start] + line[end:]
            else:
                self.data[i] = line[:start]
        self.history.append(self.data.copy())
    
    def cleanse_pattern_in_range(self, pattern, start, end):
        regex = re.compile(rf"\s*{pattern}\s*")
        for i in range(start, end):
            if 0 <= i < len(self.data):
                self.data[i] = regex.sub("", self.data[i])
        self.history.append(self.data.copy())
    
    def get_cleaned_data(self):
        return "\n".join(self.data)
    
    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            file.write(self.get_cleaned_data())
    
    def undo(self):
        if len(self.history) > 1:
            self.history.pop()
            self.data = self.history[-1].copy()
            return "\n".join(self.data)
        return "\n".join(self.data)
    
    def clear_blank_lines(self):
        self.data = [line for line in self.data if line.strip() != ""]
        self.history.append(self.data.copy())

    def convert_to_csv(self):
        csv_data = self.separate_data_into_rows()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        return output.getvalue()

class DataCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CLEAN ME!!!! 1.0")
        
        self.cleaner = DataCleaner()
        
        self.create_widgets()
        self.pattern_instances = []
    
    def create_widgets(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, pady=5)
        
        delimiter_frame = tk.Frame(control_frame)
        delimiter_frame.grid(row=0, column=0, padx=5, pady=5)
        
        self.delimiter_label = tk.Label(delimiter_frame, text="Delimiter:")
        self.delimiter_label.grid(row=0, column=0, padx=5)
        
        self.delimiter_entry = tk.Entry(delimiter_frame, width=5)
        self.delimiter_entry.grid(row=0, column=1, padx=5)
        self.delimiter_entry.insert(0, ",")
        
        self.set_delimiter_button = tk.Button(delimiter_frame, text="Set Delimiter", command=self.set_delimiter)
        self.set_delimiter_button.grid(row=0, column=2, padx=5)
        
        load_save_frame = tk.Frame(control_frame)
        load_save_frame.grid(row=0, column=1, padx=5, pady=5)
        
        self.load_button = tk.Button(load_save_frame, text="Load Data", command=self.load_data)
        self.load_button.grid(row=0, column=0, padx=5)
        
        self.save_csv_button = tk.Button(load_save_frame, text="Save as CSV", command=self.save_as_csv)
        self.save_csv_button.grid(row=0, column=1, padx=5)
        
        pattern_frame = tk.Frame(control_frame)
        pattern_frame.grid(row=1, column=0, padx=5, pady=5)
        
        self.pattern_label = tk.Label(pattern_frame, text="Pattern:")
        self.pattern_label.grid(row=0, column=0, padx=5)
        
        self.pattern_entry = tk.Entry(pattern_frame, width=10)
        self.pattern_entry.grid(row=0, column=1, padx=5)
        
        range_frame = tk.Frame(control_frame)
        range_frame.grid(row=1, column=1, padx=5, pady=5)
        
        self.range_label = tk.Label(range_frame, text="Range (start-end):")
        self.range_label.grid(row=0, column=0, padx=5)
        
        self.range_entry = tk.Entry(range_frame, width=10)
        self.range_entry.grid(row=0, column=1, padx=5)
        self.range_entry.bind('<Button-3>', self.set_range_from_selection)
        
        action_frame = tk.Frame(control_frame)
        action_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        self.cleanse_button = tk.Button(action_frame, text="Cleanse Data", command=self.find_pattern_instances)
        self.cleanse_button.grid(row=0, column=0, padx=5)
        
        self.clear_blank_button = tk.Button(action_frame, text="Clear Blanks", command=self.clear_blank_lines)
        self.clear_blank_button.grid(row=0, column=1, padx=5)
        
        self.cleanse_short_lines_button = tk.Button(action_frame, text="Cleanse Short Lines", command=self.cleanse_short_lines)
        self.cleanse_short_lines_button.grid(row=0, column=2, padx=5)
        
        self.set_delimiters_button = tk.Button(action_frame, text="Set Delimiters from Pattern", command=self.set_delimiters_from_pattern)
        self.set_delimiters_button.grid(row=0, column=3, padx=5)
        
        self.cleanse_range_button = tk.Button(action_frame, text="Cleanse Range", command=self.cleanse_range)
        self.cleanse_range_button.grid(row=0, column=4, padx=5)
        
        self.cleanse_pattern_in_range_button = tk.Button(action_frame, text="Cleanse Pattern in Range", command=self.cleanse_pattern_in_range)
        self.cleanse_pattern_in_range_button.grid(row=0, column=5, padx=5)
        
        self.undo_button = tk.Button(action_frame, text="Undo", command=self.undo)
        self.undo_button.grid(row=0, column=6, padx=5)
        
        text_frame = tk.Frame(self.root)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.data_text = tk.Text(text_frame, height=20, width=80, wrap=tk.NONE)
        self.data_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.data_text.bind('<ButtonRelease-1>', self.show_line_info)
        self.data_text.bind('<B1-Motion>', self.show_line_info)
        
        self.scrollbar_y = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.data_text.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_text.config(yscrollcommand=self.scrollbar_y.set)
        
        self.scrollbar_x = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.data_text.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.data_text.config(xscrollcommand=self.scrollbar_x.set)
        
        self.line_info_label = tk.Label(self.root, text="Line info: ")
        self.line_info_label.pack(pady=5)
    
    def set_delimiter(self):
        delimiter = self.delimiter_entry.get()
        self.cleaner.set_delimiter(delimiter)
        messagebox.showinfo("CLEAN ME!!!!!", f"Delimiter set to '{delimiter}'")
    
    def set_delimiters_from_pattern(self):
        pattern = self.pattern_entry.get()
        range_str = self.range_entry.get()
        try:
            start, end = map(int, range_str.split('-'))
        except ValueError:
            messagebox.showerror("CLEAN ME!!!!!", "Please enter a valid range (start-end)")
            return
        if pattern and start >= 0 and end > start:
            self.cleaner.set_delimiters_from_pattern(pattern, start, end)
            self.update_main_textbox()
            messagebox.showinfo("CLEAN ME!!!!!", f"Delimiters set from pattern '{pattern}' in range {start}-{end}")
        else:
            messagebox.showerror("CLEAN ME!!!!!", "Please enter a valid pattern and range")
    
    def cleanse_range(self):
        range_str = self.range_entry.get()
        try:
            start, end = map(int, range_str.split('-'))
        except ValueError:
            messagebox.showerror("CLEAN ME!!!!!", "Please enter a valid range (start-end)")
            return
        if start >= 0 and end > start:
            self.cleaner.cleanse_range(start, end)
            self.update_main_textbox()
            messagebox.showinfo("CLEAN ME!!!!!", f"Cleared range {start}-{end}")
        else:
            messagebox.showerror("CLEAN ME!!!!!", "Please enter a valid range")
    
    def cleanse_pattern_in_range(self):
        pattern = self.pattern_entry.get()
        range_str = self.range_entry.get()
        try:
            start, end = map(int, range_str.split('-'))
        except ValueError:
            messagebox.showerror("CLEAN ME!!!!!", "Please enter a valid range (start-end)")
            return
        if pattern and start >= 0 and end > start:
            self.cleaner.cleanse_pattern_in_range(pattern, start, end)
            self.update_main_textbox()
            messagebox.showinfo("CLEAN ME!!!!!", f"Cleared pattern '{pattern}' in range {start}-{end}")
        else:
            messagebox.showerror("CLEAN ME!!!!!", "Please enter a valid pattern and range")
    
    def load_data(self):
        filename = filedialog.askopenfilename(title="Select Data File", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if filename:
            with open(filename, 'r') as file:
                data = file.read()
                self.data_text.delete(1.0, tk.END)
                self.data_text.insert(tk.END, data)
                self.cleaner.load_data(data)
                self.adjust_text_box_size(data)
    
    def find_pattern_instances(self):
        pattern = self.pattern_entry.get()
        self.pattern_instances = self.cleaner.find_pattern_instances(pattern)
        if self.pattern_instances:
            self.show_instances_window(pattern)
        else:
            messagebox.showinfo("CLEAN ME!!!!!", "No instances found for the pattern.")
    
    def show_instances_window(self, pattern):
        instance_window = tk.Toplevel(self.root)
        instance_window.title("Pattern Instances")

        instance_listbox = tk.Listbox(instance_window, selectmode=tk.MULTIPLE, width=100, height=20)
        instance_listbox.pack(pady=5)

        for index, start, end in self.pattern_instances:
            line = self.cleaner.data[index]
            instance_listbox.insert(tk.END, f"Line {index + 1}, Pos {start + 1}-{end}: {line[start:end]}")
        
        def delete_selected_pattern():
            selected_indices = instance_listbox.curselection()
            for selected in reversed(selected_indices):
                index, start, end = self.pattern_instances[selected]
                self.cleaner.cleanse_instance(index, start, end)
                instance_listbox.delete(selected)
            self.update_main_textbox()
        
        def delete_selected_line():
            selected_indices = instance_listbox.curselection()
            for selected in reversed(selected_indices):
                index, start, end = self.pattern_instances[selected]
                self.cleaner.delete_line(index)
                instance_listbox.delete(selected)
            self.update_main_textbox()
        
        def cleanse_all():
            self.cleaner.cleanse_all(pattern)
            self.update_main_textbox()
            instance_window.destroy()
        
        def jump_to_instance(event):
            selected = instance_listbox.curselection()
            if selected:
                index, start, end = self.pattern_instances[selected[0]]
                self.highlight_text(index)
        
        def select_all():
            instance_listbox.select_set(0, tk.END)

        instance_listbox.bind('<Double-Button-1>', jump_to_instance)

        select_all_button = tk.Button(instance_window, text="Select All", command=select_all)
        select_all_button.pack(pady=5)
        
        delete_pattern_button = tk.Button(instance_window, text="Delete Selected Pattern", command=delete_selected_pattern)
        delete_pattern_button.pack(pady=5)
        
        delete_line_button = tk.Button(instance_window, text="Delete Selected Line", command=delete_selected_line)
        delete_line_button.pack(pady=5)
        
        cleanse_all_button = tk.Button(instance_window, text="Cleanse All", command=cleanse_all)
        cleanse_all_button.pack(pady=5)
    
    def highlight_text(self, line_index):
        self.data_text.tag_remove('highlight', '1.0', tk.END)
        line_start = f"{line_index + 1}.0"
        line_end = f"{line_index + 1}.end"
        self.data_text.tag_add('highlight', line_start, line_end)
        self.data_text.tag_config('highlight', background='yellow')
        self.data_text.see(line_start)
    
    def update_main_textbox(self):
        current_width = int(self.data_text['width'])
        current_height = int(self.data_text['height'])
        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(tk.END, self.cleaner.get_cleaned_data())
        self.data_text.config(width=current_width, height=current_height)
    
    def undo(self):
        undone_data = self.cleaner.undo()
        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(tk.END, undone_data)
    
    def save_cleaned_data(self):
        filename = filedialog.asksaveasfilename(title="Save Cleaned Data", defaultextension=".txt", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if filename:
            self.cleaner.save_to_file(filename)
            messagebox.showinfo("CLEAN ME!!!!!", "Cleaned data saved successfully!")
    
    def save_as_csv(self):
        filename = filedialog.asksaveasfilename(title="Save as CSV", defaultextension=".csv", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if filename:
            csv_data = self.cleaner.convert_to_csv()
            with open(filename, 'w', newline='') as file:
                file.write(csv_data)
            messagebox.showinfo("CLEAN ME!!!!!", "CSV file saved successfully!")
    
    def clear_blank_lines(self):
        self.cleaner.clear_blank_lines()
        self.update_main_textbox()
    
    def cleanse_short_lines(self):
        length = tk.simpledialog.askinteger("Input", "Enter the minimum number of non-whitespace characters:")
        if length is not None:
            self.cleaner.cleanse_short_lines(length)
            self.update_main_textbox()
    
    def adjust_text_box_size(self, text):
        lines = text.split('\n')
        max_width = max(len(line) for line in lines)
        num_lines = len(lines)
        self.data_text.config(width=max_width + 2, height=min(num_lines, 30))
    
    def show_line_info(self, event):
        try:
            start_idx = self.data_text.index(tk.SEL_FIRST)
            end_idx = self.data_text.index(tk.SEL_LAST)
            start_pos = int(start_idx.split('.')[1])
            end_pos = int(end_idx.split('.')[1])
            self.line_info_label.config(text=f"Selected range: {start_pos}-{end_pos}")
        except tk.TclError:
            cursor_index = self.data_text.index(tk.CURRENT)
            line_index = int(cursor_index.split('.')[0]) - 1
            char_index = int(cursor_index.split('.')[1])
            if 0 <= line_index < len(self.cleaner.data):
                line_length = len(self.cleaner.data[line_index])
                self.line_info_label.config(text=f"Line {line_index + 1} length: {line_length} characters, Position: {char_index}")

    def set_range_from_selection(self, event):
        try:
            start_idx = self.data_text.index(tk.SEL_FIRST)
            end_idx = self.data_text.index(tk.SEL_LAST)
            start_pos = int(start_idx.split('.')[1])
            end_pos = int(end_idx.split('.')[1])
            self.range_entry.delete(0, tk.END)
            self.range_entry.insert(0, f"{start_pos}-{end_pos}")
        except tk.TclError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = DataCleanerApp(root)
    root.mainloop()
