import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
from typing import List, Dict

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
        
        # Add mapping button
        self.add_btn = ttk.Button(self.main_frame, text="Add Mapping", command=self.add_mapping)
        self.add_btn.grid(row=1, column=0, pady=5)
        
        # Control buttons
        self.save_btn = ttk.Button(self.main_frame, text="Save Config", command=self.save_config)
        self.save_btn.grid(row=2, column=0, pady=5)
        
        self.load_btn = ttk.Button(self.main_frame, text="Load Config", command=self.load_config)
        self.load_btn.grid(row=2, column=1, pady=5)
        
        self.apply_btn = ttk.Button(self.main_frame, text="Apply Mappings", command=self.apply_mappings)
        self.apply_btn.grid(row=3, column=0, columnspan=2, pady=5)

    def add_mapping(self):
        mapping_frame = ttk.Frame(self.mappings_frame)
        mapping_frame.pack(fill=tk.X, pady=2)
        
        from_label = ttk.Label(mapping_frame, text="From:")
        from_label.pack(side=tk.LEFT, padx=5)
        
        from_entry = ttk.Entry(mapping_frame, width=15)
        from_entry.pack(side=tk.LEFT, padx=5)
        
        to_label = ttk.Label(mapping_frame, text="To:")
        to_label.pack(side=tk.LEFT, padx=5)
        
        to_entry = ttk.Entry(mapping_frame, width=15)
        to_entry.pack(side=tk.LEFT, padx=5)
        
        remove_btn = ttk.Button(mapping_frame, text="Remove", 
                              command=lambda: self.remove_mapping(mapping_frame))
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        self.mappings.append({"frame": mapping_frame, "from": from_entry, "to": to_entry})

    def remove_mapping(self, frame):
        self.mappings = [m for m in self.mappings if m["frame"] != frame]
        frame.destroy()

    def save_config(self):
        config = []
        for mapping in self.mappings:
            config.append({
                "from": mapping["from"].get(),
                "to": mapping["to"].get()
            })
        
        try:
            with open("keymapper_config.json", "w") as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def load_config(self):
        try:
            with open("keymapper_config.json", "r") as f:
                config = json.load(f)
            
            # Clear existing mappings
            for mapping in self.mappings:
                mapping["frame"].destroy()
            self.mappings.clear()
            
            # Load saved mappings
            for mapping in config:
                self.add_mapping()
                current = self.mappings[-1]
                current["from"].insert(0, mapping["from"])
                current["to"].insert(0, mapping["to"])
                
        except FileNotFoundError:
            messagebox.showwarning("Warning", "No configuration file found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")

    def apply_mappings(self):
        # Implement the CLI interaction here
        # Example: subprocess.run(["keymapper", "map", "key1", "key2"])
        try:
            for mapping in self.mappings:
                from_key = mapping["from"].get()
                to_key = mapping["to"].get()
                if from_key and to_key:
                    subprocess.run(["keymapper", "map", from_key, to_key], check=True)
            messagebox.showinfo("Success", "Mappings applied successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to apply mappings: {str(e)}")

def main():
    root = tk.Tk()
    app = KeymapperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
