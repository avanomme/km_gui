import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import json
import os
from typing import List, Dict
from pynput import keyboard

class KeymapperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux Keymapper GUI")
        self.mappings: List[Dict[str, str]] = []
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Mappings frame
        self.mappings_frame = ttk.LabelFrame(self.main_frame, text="Key Mappings", padding="5")
        self.mappings_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add context frame
        self.context_frame = ttk.LabelFrame(self.main_frame, text="Context", padding="5")
        self.context_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Context type dropdown
        self.context_type = ttk.Combobox(self.context_frame, values=[
            "default", "system", "title", "class", "device", "modifier"
        ])
        self.context_type.set("default")
        self.context_type.pack(side=tk.LEFT, padx=5)
        
        # Context value entry
        self.context_value = ttk.Entry(self.context_frame, width=30)
        self.context_value.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Add mapping button
        self.add_btn = ttk.Button(self.main_frame, text="Add Mapping", command=self.add_mapping)
        self.add_btn.grid(row=4, column=0, pady=5)
        
        # Control buttons
        self.save_btn = ttk.Button(self.main_frame, text="Save Config", command=self.save_config)
        self.save_btn.grid(row=5, column=0, pady=5)
        
        self.load_btn = ttk.Button(self.main_frame, text="Load Config", command=self.load_config)
        self.load_btn.grid(row=5, column=1, pady=5)
        
        self.apply_btn = ttk.Button(self.main_frame, text="Apply Mappings", command=self.apply_mappings)
        self.apply_btn.grid(row=6, column=0, columnspan=2, pady=5)

        # Add config file path
        self.config_path = os.path.expanduser("~/.config/keymapper.conf")
        
        # Key detection button
        self.detect_key_button = ttk.Button(self.main_frame, text="Detect Key", command=self.start_key_detection)
        self.detect_key_button.grid(row=2, column=0, pady=5)
        
        # Label to show detected key
        self.detected_key_label = ttk.Label(self.main_frame, text="Detected Key: None")
        self.detected_key_label.grid(row=2, column=1, pady=5)
        
        self.listener = None

    def add_mapping(self):
        mapping_frame = ttk.Frame(self.mappings_frame)
        mapping_frame.pack(fill=tk.X, pady=2)
        
        # Key Input Type
        input_type = ttk.Combobox(mapping_frame, values=[
            "Single Key", "Successive Keys", "Simultaneous Keys", 
            "Hold Modifier", "Character String"
        ], width=15)
        input_type.set("Single Key")
        input_type.pack(side=tk.LEFT, padx=5)
        
        from_entry = ttk.Entry(mapping_frame, width=15)
        from_entry.pack(side=tk.LEFT, padx=5)
        
        # Output Type
        output_type = ttk.Combobox(mapping_frame, values=[
            "Single Key", "Successive Keys", "Simultaneous Keys",
            "Hold Modifier", "Character String", "Command"
        ], width=15)
        output_type.set("Single Key")
        output_type.pack(side=tk.LEFT, padx=5)
        
        to_entry = ttk.Entry(mapping_frame, width=15)
        to_entry.pack(side=tk.LEFT, padx=5)
        
        remove_btn = ttk.Button(mapping_frame, text="Remove", 
                              command=lambda: self.remove_mapping(mapping_frame))
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        self.mappings.append({
            "frame": mapping_frame,
            "input_type": input_type,
            "from": from_entry,
            "output_type": output_type,
            "to": to_entry
        })

    def remove_mapping(self, frame):
        self.mappings = [m for m in self.mappings if m["frame"] != frame]
        frame.destroy()

    def format_mapping(self, mapping: Dict) -> str:
        input_type = mapping["input_type"].get()
        output_type = mapping["output_type"].get()
        from_key = mapping["from"].get()
        to_key = mapping["to"].get()
        
        # Format input based on type
        if input_type == "Successive Keys":
            input_expr = f"{from_key.replace(',', ' ')}"
        elif input_type == "Simultaneous Keys":
            input_expr = f"({from_key.replace(',', ' ')})"
        elif input_type == "Hold Modifier":
            keys = from_key.split(',')
            if len(keys) == 2:
                input_expr = f"{keys[0].strip()}{{{keys[1].strip()}}}"
            else:
                input_expr = from_key
        elif input_type == "Character String":
            input_expr = f'"{from_key}"'
        else:
            input_expr = from_key

        # Format output based on type
        if output_type == "Successive Keys":
            output_expr = f"{to_key.replace(',', ' ')}"
        elif output_type == "Simultaneous Keys":
            output_expr = f"({to_key.replace(',', ' ')})"
        elif output_type == "Hold Modifier":
            keys = to_key.split(',')
            if len(keys) == 2:
                output_expr = f"{keys[0].strip()}{{{keys[1].strip()}}}"
            else:
                output_expr = to_key
        elif output_type == "Character String":
            output_expr = f'"{to_key}"'
        elif output_type == "Command":
            output_expr = f"$({to_key}) ^"
        else:
            output_expr = to_key
            
        return f"{input_expr} >> {output_expr}"

    def save_config(self):
        try:
            context_type = self.context_type.get()
            context_value = self.context_value.get()
            
            with open(self.config_path, "a") as f:
                # Write context if not default
                if context_type != "default":
                    if context_value:
                        f.write(f"\n[{context_type} = {context_value}]\n")
                    else:
                        f.write(f"\n[{context_type}]\n")
                
                # Write mappings
                for mapping in self.mappings:
                    mapping_str = self.format_mapping(mapping)
                    f.write(f"{mapping_str}\n")
                
            messagebox.showinfo("Success", f"Configuration appended to {self.config_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def load_config(self):
        file_path = filedialog.askopenfilename(
            initialdir="~/.config",
            title="Select Keymapper Configuration",
            filetypes=(("conf files", "*.conf"), ("all files", "*.*"))
        )
        if file_path:
            self.config_path = file_path
            messagebox.showinfo("Success", f"Selected configuration file: {file_path}")

    def apply_mappings(self):
        try:
            subprocess.run(["systemctl", "restart", "keymapperd"], check=True)
            messagebox.showinfo("Success", "Keymapper service restarted with new configuration!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to restart keymapper service: {str(e)}")

    def start_key_detection(self):
        self.detected_key_label.config(text="Press any key...")
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def on_key_press(self, key):
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)
        self.detected_key_label.config(text=f"Detected Key: {key_char}")
        if self.listener:
            self.listener.stop()

def main():
    root = tk.Tk()
    app = KeymapperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
