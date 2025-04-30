import tkinter as tk
from tkinter import ttk
import ujson
import os

class SceneEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Scene Editor - Stellar Odyssey")
        self.root.geometry("1000x600")

        # Load scenes.json
        self.file_path = "./data/scenes.json"
        with open(self.file_path, 'r') as f:
            self.data = ujson.load(f)
        self.scenes = self.data['scenes']
        self.paths = self.data['paths']

        # Toolbar
        self.toolbar = tk.Frame(self.root, bg="lightgray")
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        tk.Button(self.toolbar, text="Add Scene", command=self.add_scene).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(self.toolbar, text="Delete Scene", command=self.delete_scene).pack(side=tk.LEFT, padx=5, pady=5)

        # Left sidebar: Scene list with scrollbar
        self.frame_left = tk.Frame(self.root)
        self.frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.scrollbar_left = tk.Scrollbar(self.frame_left)
        self.scrollbar_left.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox_scenes = tk.Listbox(self.frame_left, yscrollcommand=self.scrollbar_left.set, width=30, height=20)
        for scene in self.scenes:
            self.listbox_scenes.insert(tk.END, scene)
        self.listbox_scenes.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrollbar_left.config(command=self.listbox_scenes.yview)

        # Right sidebar: Choices list with scrollbar
        self.frame_right = tk.Frame(self.root)
        self.frame_right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.scrollbar_right = tk.Scrollbar(self.frame_right)
        self.scrollbar_right.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox_choices = tk.Listbox(self.frame_right, yscrollcommand=self.scrollbar_right.set, width=30, height=20)
        self.listbox_choices.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrollbar_right.config(command=self.listbox_choices.yview)

        tk.Button(self.frame_right, text="Add Choice", command=self.add_choice).pack(side=tk.LEFT, padx=5)

        # Center panel: Properties
        self.frame_center = tk.Frame(self.root)
        self.frame_center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Dialogue List
        tk.Label(self.frame_center, text="Dialogue Steps:").pack(anchor="w")
        self.frame_dialogue = tk.Frame(self.frame_center)
        self.frame_dialogue.pack(fill=tk.X, pady=5)

        self.scrollbar_dialogue = tk.Scrollbar(self.frame_dialogue)
        self.scrollbar_dialogue.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox_dialogue = tk.Listbox(self.frame_dialogue, yscrollcommand=self.scrollbar_dialogue.set, width=50, height=5)
        self.listbox_dialogue.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.scrollbar_dialogue.config(command=self.listbox_dialogue.yview)

        self.frame_dialogue_buttons = tk.Frame(self.frame_center)
        self.frame_dialogue_buttons.pack(fill=tk.X)
        tk.Button(self.frame_dialogue_buttons, text="Add Dialogue", command=self.add_dialogue).pack(side=tk.LEFT, padx=5)
        tk.Button(self.frame_dialogue_buttons, text="Delete Dialogue", command=self.delete_dialogue).pack(side=tk.LEFT, padx=5)

        tk.Label(self.frame_center, text="Edit Selected Dialogue:").pack(anchor="w", pady=5)
        self.entry_dialogue = tk.Entry(self.frame_center, width=50)
        self.entry_dialogue.pack(anchor="w")

        # Scene Properties
        tk.Label(self.frame_center, text="Scene Name:").pack(anchor="w", pady=5)
        self.entry_name = tk.Entry(self.frame_center, width=50)
        self.entry_name.pack(anchor="w")

        tk.Label(self.frame_center, text="Background:").pack(anchor="w", pady=5)
        self.combo_background = ttk.Combobox(self.frame_center, values=list(self.paths['images'].keys()), width=47)
        self.combo_background.pack(anchor="w")

        tk.Label(self.frame_center, text="Audio:").pack(anchor="w", pady=5)
        self.combo_audio = ttk.Combobox(self.frame_center, values=list(self.paths['audio'].keys()), width=47)
        self.combo_audio.pack(anchor="w")

        # Choice Properties
        tk.Label(self.frame_center, text="Next Scene:").pack(anchor="w", pady=5)
        self.combo_next_scene = ttk.Combobox(self.frame_center, values=list(self.scenes.keys()), width=47)
        self.combo_next_scene.pack(anchor="w")

        tk.Button(self.frame_center, text="Delete Choice", command=self.delete_choice).pack(anchor="w", pady=5)

        # Save Button
        tk.Button(self.frame_center, text="Save Changes", command=self.save_changes).pack(anchor="w", pady=10)

        # Bind events
        self.listbox_scenes.bind('<<ListboxSelect>>', self.update_scene_properties)
        self.listbox_choices.bind('<<ListboxSelect>>', self.update_choice_properties)
        self.listbox_dialogue.bind('<<ListboxSelect>>', self.update_dialogue_entry)

    def update_scene_properties(self, event):
        if self.listbox_scenes.curselection():
            selected = self.listbox_scenes.get(self.listbox_scenes.curselection())
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, selected)
            
            self.combo_background.set(self.scenes[selected]["background_path"])
            self.combo_audio.set(self.scenes[selected]["background_audio"])

            # Update dialogue list
            self.listbox_dialogue.delete(0, tk.END)
            for step in self.scenes[selected]["steps"]:
                if "text" in step:
                    self.listbox_dialogue.insert(tk.END, step["text"][:50] + ("..." if len(step["text"]) > 50 else ""))
            
            # Update choices list
            self.listbox_choices.delete(0, tk.END)
            step = self.scenes[selected]["steps"][-1]
            if "choices" in step:
                for choice in step["choices"]:
                    self.listbox_choices.insert(tk.END, choice["text"])
            
            # Clear dialogue entry and choice properties
            self.entry_dialogue.delete(0, tk.END)
            self.combo_next_scene.set("")

    def update_dialogue_entry(self, event):
        if self.listbox_scenes.curselection() and self.listbox_dialogue.curselection():
            selected_scene = self.listbox_scenes.get(self.listbox_scenes.curselection())
            selected_index = self.listbox_dialogue.curselection()[0]
            dialogue_steps = [step for step in self.scenes[selected_scene]["steps"] if "text" in step]
            if selected_index < len(dialogue_steps):
                self.entry_dialogue.delete(0, tk.END)
                self.entry_dialogue.insert(0, dialogue_steps[selected_index]["text"])
            # Clear choice selection to avoid confusion
            self.listbox_choices.selection_clear(0, tk.END)
            self.combo_next_scene.set("")

    def update_choice_properties(self, event):
        if self.listbox_scenes.curselection() and self.listbox_choices.curselection():
            selected_scene = self.listbox_scenes.get(self.listbox_scenes.curselection())
            selected_index = self.listbox_choices.curselection()[0]
            step = self.scenes[selected_scene]["steps"][-1]
            if "choices" in step and selected_index < len(step["choices"]):
                choice = step["choices"][selected_index]
                # Populate Edit Selected Dialogue with choice text
                self.entry_dialogue.delete(0, tk.END)
                self.entry_dialogue.insert(0, choice["text"])
                self.combo_next_scene.set(choice["next"])
            # Clear dialogue selection to avoid confusion
            self.listbox_dialogue.selection_clear(0, tk.END)

    def add_scene(self):
        # Find a unique scene name
        i = 1
        while f"NewScene_{i}" in self.scenes:
            i += 1
        new_scene_name = f"NewScene_{i}"
        
        # Add a basic scene structure
        self.scenes[new_scene_name] = {
            "background_path": list(self.paths['images'].keys())[0],
            "background_audio": list(self.paths['audio'].keys())[0],
            "steps": [
                {"type": "dialogue", "text": "New dialogue"}
            ]
        }
        self.listbox_scenes.insert(tk.END, new_scene_name)
        self.listbox_scenes.selection_clear(0, tk.END)
        self.listbox_scenes.selection_set(tk.END)
        self.update_scene_properties(None)

    def delete_scene(self):
        if self.listbox_scenes.curselection():
            selected = self.listbox_scenes.get(self.listbox_scenes.curselection())
            # Update references in choices
            for scene in self.scenes.values():
                for step in scene["steps"]:
                    if "choices" in step:
                        for choice in step["choices"]:
                            if choice["next"] == selected:
                                choice["next"] = "start"
            del self.scenes[selected]
            self.listbox_scenes.delete(self.listbox_scenes.curselection())
            self.listbox_choices.delete(0, tk.END)
            self.listbox_dialogue.delete(0, tk.END)
            self.entry_name.delete(0, tk.END)
            self.entry_dialogue.delete(0, tk.END)
            self.combo_next_scene.set("")
            self.save_changes()

    def add_dialogue(self):
        if self.listbox_scenes.curselection():
            selected = self.listbox_scenes.get(self.listbox_scenes.curselection())
            # Add a new dialogue step before the last step (which may contain choices)
            new_step = {"type": "dialogue", "text": "New dialogue"}
            if len(self.scenes[selected]["steps"]) == 1:
                self.scenes[selected]["steps"].insert(0, new_step)
            else:
                self.scenes[selected]["steps"].insert(-1, new_step)
            self.update_scene_properties(None)

    def delete_dialogue(self):
        if self.listbox_scenes.curselection() and self.listbox_dialogue.curselection():
            selected_scene = self.listbox_scenes.get(self.listbox_scenes.curselection())
            selected_index = self.listbox_dialogue.curselection()[0]
            dialogue_steps = [i for i, step in enumerate(self.scenes[selected_scene]["steps"]) if "text" in step]
            if selected_index < len(dialogue_steps):
                step_index = dialogue_steps[selected_index]
                del self.scenes[selected_scene]["steps"][step_index]
                self.update_scene_properties(None)
                self.entry_dialogue.delete(0, tk.END)

    def add_choice(self):
        if self.listbox_scenes.curselection():
            selected = self.listbox_scenes.get(self.listbox_scenes.curselection())
            step = self.scenes[selected]["steps"][-1]
            if "choices" not in step:
                step["choices"] = []
            step["choices"].append({"text": "New Choice", "next": "start"})
            self.listbox_choices.insert(tk.END, "New Choice")
            self.listbox_choices.selection_clear(0, tk.END)
            self.listbox_choices.selection_set(tk.END)
            self.update_choice_properties(None)

    def delete_choice(self):
        if self.listbox_scenes.curselection() and self.listbox_choices.curselection():
            selected_scene = self.listbox_scenes.get(self.listbox_scenes.curselection())
            selected_index = self.listbox_choices.curselection()[0]
            step = self.scenes[selected_scene]["steps"][-1]
            if "choices" in step and selected_index < len(step["choices"]):
                del step["choices"][selected_index]
                self.listbox_choices.delete(selected_index)
                self.entry_dialogue.delete(0, tk.END)
                self.combo_next_scene.set("")

    def save_changes(self):
        if self.listbox_scenes.curselection():
            selected = self.listbox_scenes.get(self.listbox_scenes.curselection())
            new_name = self.entry_name.get()
            
            # Update scene name if changed
            if new_name != selected:
                self.scenes[new_name] = self.scenes.pop(selected)
                # Update references in choices
                for scene in self.scenes.values():
                    for step in scene["steps"]:
                        if "choices" in step:
                            for choice in step["choices"]:
                                if choice["next"] == selected:
                                    choice["next"] = new_name
                selected = new_name
                # Update listbox
                self.listbox_scenes.delete(0, tk.END)
                for scene in self.scenes:
                    self.listbox_scenes.insert(tk.END, scene)
            
            # Update dialogue if edited
            if self.listbox_dialogue.curselection():
                selected_index = self.listbox_dialogue.curselection()[0]
                dialogue_steps = [i for i, step in enumerate(self.scenes[selected]["steps"]) if "text" in step]
                if selected_index < len(dialogue_steps):
                    step_index = dialogue_steps[selected_index]
                    self.scenes[selected]["steps"][step_index]["text"] = self.entry_dialogue.get()

            # Update choice if edited
            if self.listbox_choices.curselection():
                selected_index = self.listbox_choices.curselection()[0]
                step = self.scenes[selected]["steps"][-1]
                if "choices" in step and selected_index < len(step["choices"]):
                    step["choices"][selected_index]["text"] = self.entry_dialogue.get()
                    step["choices"][selected_index]["next"] = self.combo_next_scene.get()

            # Update other properties
            self.scenes[selected]["background_path"] = self.combo_background.get()
            self.scenes[selected]["background_audio"] = self.combo_audio.get()
            
            # Save to file
            self.data["scenes"] = self.scenes
            with open(self.file_path, 'w') as f:
                ujson.dump(self.data, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = SceneEditor(root)
    root.mainloop()