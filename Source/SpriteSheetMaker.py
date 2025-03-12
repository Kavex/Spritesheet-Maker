import tkinter as tk
from tkinter import filedialog, messagebox, Menu, colorchooser
from PIL import Image, ImageTk
import os
import json
import math
import webbrowser

# Determine the appropriate resampling filter.
if hasattr(Image, "Resampling"):
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
else:
    RESAMPLE_FILTER = Image.LANCZOS  # For older Pillow versions

#########################
# Main SpriteSheet Maker
#########################
class SpriteSheetMaker:
    def __init__(self, master):
        self.master = master
        self.master.title("SpriteSheet Maker by Kavex")
        self.image_list = []  # List of file paths
        self.default_columns = 4  # Default columns set to at least 4
        self.zoom_factor = 1.0  # 1.0 = 100%
        
        # Background settings.
        self.transparent_bg = tk.BooleanVar(value=True)
        self.bg_color = "#ffffff"  # Default background color (if transparency is disabled)
        
        # Option to export JSON metadata along with the spritesheet.
        self.export_json_metadata = tk.BooleanVar(value=False)
        
        self.build_menu()
        self.setup_widgets()
    
    def build_menu(self):
        menu_bar = Menu(self.master)
        
        # File Menu: New, Save, Load, Export, Slice, Pixel Art Editor, Exit
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_command(label="Load Project", command=self.load_project)
        file_menu.add_separator()
        file_menu.add_command(label="Export Spritesheet", command=self.export_spritesheet)
        file_menu.add_command(label="Slice Spritesheet", command=self.open_slice_window)
        file_menu.add_separator()
        file_menu.add_command(label="Pixel Art Editor", command=self.open_pixel_art_editor)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Help Menu: About
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.master.config(menu=menu_bar)
    
    def setup_widgets(self):
        # Main layout: left frame for image list controls; right frame for preview/settings.
        self.left_frame = tk.Frame(self.master)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        self.right_frame = tk.Frame(self.master)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Frame for the listbox with a scrollbar.
        list_frame = tk.Frame(self.left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, width=40)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=list_scroll.set)
        
        # Buttons for list management.
        btn_frame = tk.Frame(self.left_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Button(btn_frame, text="Add", command=self.add_image).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(btn_frame, text="Remove", command=self.remove_image).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(btn_frame, text="Clear", command=self.clear_images).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons for ordering images.
        order_frame = tk.Frame(self.left_frame)
        order_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Button(order_frame, text="Move Up", command=self.move_up).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(order_frame, text="Move Down", command=self.move_down).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Top-right controls: Columns, Refresh, Size display, Zoom slider, Background options, and JSON export.
        top_right = tk.Frame(self.right_frame)
        top_right.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(top_right, text="Columns:").pack(side=tk.LEFT)
        self.columns_var = tk.IntVar(value=self.default_columns)
        self.spin_columns = tk.Spinbox(top_right, from_=1, to=100, width=5, textvariable=self.columns_var, command=self.update_preview)
        self.spin_columns.pack(side=tk.LEFT)
        
        refresh_button = tk.Button(top_right, text="Refresh Preview", command=self.update_preview)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        self.size_label = tk.Label(top_right, text="Size: 0 x 0")
        self.size_label.pack(side=tk.LEFT, padx=5)
        
        # Zoom slider to adjust zoom percentage.
        self.zoom_slider = tk.Scale(top_right, from_=25, to=400, orient=tk.HORIZONTAL, label="Zoom (%)", command=self.zoom_changed)
        self.zoom_slider.set(100)
        self.zoom_slider.pack(side=tk.LEFT, padx=5)
        
        # Background options.
        self.transparent_cb = tk.Checkbutton(top_right, text="Transparent BG", variable=self.transparent_bg, command=self.toggle_bg_controls)
        self.transparent_cb.pack(side=tk.LEFT, padx=5)
        
        self.bg_color_button = tk.Button(top_right, text="Set BG Color", command=self.choose_bg_color, state=tk.DISABLED)
        self.bg_color_button.pack(side=tk.LEFT, padx=5)
        self.bg_color_label = tk.Label(top_right, text=self.bg_color)
        self.bg_color_label.pack(side=tk.LEFT, padx=5)
        
        # Checkbox for JSON metadata export.
        self.json_export_cb = tk.Checkbutton(top_right, text="Export JSON Metadata", variable=self.export_json_metadata)
        self.json_export_cb.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the preview canvas and its scrollbars.
        self.preview_frame = tk.Frame(self.right_frame)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas for previewing the spritesheet.
        self.preview_canvas = tk.Canvas(self.preview_frame, bg="gray")
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Vertical scrollbar for the preview canvas.
        self.v_scroll = tk.Scrollbar(self.preview_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        # Horizontal scrollbar for the preview canvas.
        self.h_scroll = tk.Scrollbar(self.right_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.preview_canvas.config(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
    
    def toggle_bg_controls(self):
        if self.transparent_bg.get():
            self.bg_color_button.config(state=tk.DISABLED)
        else:
            self.bg_color_button.config(state=tk.NORMAL)
        self.update_preview()
    
    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose background color", initialcolor=self.bg_color)
        if color and color[1]:
            self.bg_color = color[1]
            self.bg_color_label.config(text=self.bg_color)
            self.update_preview()
    
    def zoom_changed(self, value):
        try:
            self.zoom_factor = float(value) / 100.0
            self.update_preview()
        except Exception as e:
            print("Error in zoom_changed:", e)
    
    def add_image(self):
        file_paths = filedialog.askopenfilenames(title="Select Sprite Images",
                                                 filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_paths:
            for path in file_paths:
                self.image_list.append(path)
                self.listbox.insert(tk.END, os.path.basename(path))
            self.update_preview()
    
    def remove_image(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            self.listbox.delete(index)
            del self.image_list[index]
            self.update_preview()
    
    def clear_images(self):
        self.listbox.delete(0, tk.END)
        self.image_list = []
        self.update_preview()
    
    def move_up(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            if index > 0:
                self.image_list[index], self.image_list[index-1] = self.image_list[index-1], self.image_list[index]
                text = self.listbox.get(index)
                self.listbox.delete(index)
                self.listbox.insert(index-1, text)
                self.listbox.selection_set(index-1)
                self.update_preview()
    
    def move_down(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            if index < self.listbox.size() - 1:
                self.image_list[index], self.image_list[index+1] = self.image_list[index+1], self.image_list[index]
                text = self.listbox.get(index)
                self.listbox.delete(index)
                self.listbox.insert(index+1, text)
                self.listbox.selection_set(index+1)
                self.update_preview()
    
    def update_preview(self):
        if not self.image_list:
            self.preview_canvas.delete("all")
            self.size_label.config(text="Size: 0 x 0")
            return
        
        try:
            cols = int(self.columns_var.get())
        except ValueError:
            cols = 1
        
        images = []
        for path in self.image_list:
            try:
                img = Image.open(path).convert("RGBA")
                images.append(img)
            except Exception as e:
                print(f"Error loading image {path}: {e}")
        
        if not images:
            self.preview_canvas.delete("all")
            self.size_label.config(text="Size: 0 x 0")
            return
        
        cell_width = max(img.width for img in images)
        cell_height = max(img.height for img in images)
        rows = math.ceil(len(images) / cols)
        sheet_width = cell_width * cols
        sheet_height = cell_height * rows
        
        self.size_label.config(text=f"Size: {sheet_width} x {sheet_height}")
        
        if self.transparent_bg.get():
            bg = (0, 0, 0, 0)
        else:
            r = int(self.bg_color[1:3], 16)
            g = int(self.bg_color[3:5], 16)
            b = int(self.bg_color[5:7], 16)
            bg = (r, g, b, 255)
        
        self.cell_width = cell_width
        self.cell_height = cell_height
        
        spritesheet = Image.new("RGBA", (sheet_width, sheet_height), bg)
        self.metadata = []
        for idx, img in enumerate(images):
            row = idx // cols
            col = idx % cols
            x = col * cell_width
            y = row * cell_height
            spritesheet.paste(img, (x, y), img)
            self.metadata.append({
                "filename": os.path.basename(self.image_list[idx]),
                "order": idx,
                "width": img.width,
                "height": img.height,
                "x": x,
                "y": y
            })
        
        zoomed_width = int(sheet_width * self.zoom_factor)
        zoomed_height = int(sheet_height * self.zoom_factor)
        spritesheet_zoomed = spritesheet.resize((zoomed_width, zoomed_height), RESAMPLE_FILTER)
        
        self.preview_image = ImageTk.PhotoImage(spritesheet_zoomed)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_image)
        self.preview_canvas.config(scrollregion=(0, 0, zoomed_width, zoomed_height))
        self.spritesheet_image = spritesheet
    
    def export_spritesheet(self):
        if not self.image_list:
            messagebox.showwarning("Warning", "No images to export")
            return
        
        try:
            cols = int(self.columns_var.get())
        except ValueError:
            cols = 1
        
        images = []
        for path in self.image_list:
            try:
                img = Image.open(path).convert("RGBA")
                images.append(img)
            except Exception as e:
                print(f"Error loading image {path}: {e}")
        
        if not images:
            messagebox.showwarning("Warning", "No valid images to export")
            return
        
        cell_width = max(img.width for img in images)
        cell_height = max(img.height for img in images)
        rows = math.ceil(len(images) / cols)
        sheet_width = cell_width * cols
        sheet_height = cell_height * rows
        
        if self.transparent_bg.get():
            bg = (0, 0, 0, 0)
        else:
            r = int(self.bg_color[1:3], 16)
            g = int(self.bg_color[3:5], 16)
            b = int(self.bg_color[5:7], 16)
            bg = (r, g, b, 255)
        
        spritesheet = Image.new("RGBA", (sheet_width, sheet_height), bg)
        metadata = []
        for idx, img in enumerate(images):
            row = idx // cols
            col = idx % cols
            x = col * cell_width
            y = row * cell_height
            spritesheet.paste(img, (x, y), img)
            metadata.append({
                "filename": os.path.basename(self.image_list[idx]),
                "order": idx,
                "width": img.width,
                "height": img.height,
                "x": x,
                "y": y
            })
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg;*.jpeg"),
                ("BMP", "*.bmp"),
                ("TGA", "*.tga"),
                ("TIFF", "*.tiff"),
                ("WEBP", "*.webp")
            ]
        )
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".jpg", ".jpeg"]:
                file_format = "JPEG"
            elif ext == ".bmp":
                file_format = "BMP"
            elif ext == ".tga":
                file_format = "TGA"
            elif ext == ".tiff":
                file_format = "TIFF"
            elif ext == ".webp":
                file_format = "WEBP"
            else:
                file_format = "PNG"
            try:
                spritesheet.save(file_path, file_format)
                messagebox.showinfo("Success", f"Spritesheet saved to {file_path}")
                if self.export_json_metadata.get():
                    metadata_dict = {
                        "spritesheet_width": sheet_width,
                        "spritesheet_height": sheet_height,
                        "cell_width": cell_width,
                        "cell_height": cell_height,
                        "sprites": metadata
                    }
                    json_path = os.path.splitext(file_path)[0] + ".json"
                    with open(json_path, 'w') as f:
                        json.dump(metadata_dict, f, indent=4)
                    messagebox.showinfo("Success", f"JSON metadata saved to {json_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save spritesheet: {e}")
    
    def new_project(self):
        if messagebox.askyesno("New Project", "Are you sure you want to start a new project? Unsaved changes will be lost."):
            self.clear_images()
            self.columns_var.set(self.default_columns)
    
    def save_project(self):
        project_data = {
            "image_list": self.image_list,
            "columns": self.columns_var.get()
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(project_data, f)
            messagebox.showinfo("Success", f"Project saved to {file_path}")
    
    def load_project(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                project_data = json.load(f)
            self.image_list = project_data.get("image_list", [])
            self.listbox.delete(0, tk.END)
            for path in self.image_list:
                self.listbox.insert(tk.END, os.path.basename(path))
            self.columns_var.set(project_data.get("columns", self.default_columns))
            self.update_preview()
    
    def show_about(self):
        about_text = "SpriteSheet Maker\nMade by Kavex\nGitHub: https://github.com/Kavex/Spritesheet-Maker"
        if messagebox.showinfo("About", about_text):
            webbrowser.open("https://github.com/Kavex/Spritesheet-Maker")
    
    def open_slice_window(self):
        self.slice_window = tk.Toplevel(self.master)
        self.slice_window.title("Slice Spritesheet")
        
        self.slice_image_path = tk.StringVar()
        self.slice_json_path = tk.StringVar()
        self.use_json_metadata = tk.BooleanVar(value=False)
        self.manual_tile_width = tk.StringVar()
        self.manual_tile_height = tk.StringVar()
        self.manual_columns = tk.StringVar()
        self.manual_rows = tk.StringVar()
        
        frame1 = tk.Frame(self.slice_window)
        frame1.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(frame1, text="Select Spritesheet:").pack(side=tk.LEFT)
        tk.Button(frame1, text="Browse", command=self.select_slice_image).pack(side=tk.LEFT, padx=5)
        tk.Label(frame1, textvariable=self.slice_image_path).pack(side=tk.LEFT)
        
        frame2 = tk.Frame(self.slice_window)
        frame2.pack(fill=tk.X, padx=5, pady=5)
        self.json_checkbox = tk.Checkbutton(frame2, text="Use JSON metadata", variable=self.use_json_metadata, command=self.toggle_slice_options)
        self.json_checkbox.pack(side=tk.LEFT)
        
        self.json_frame = tk.Frame(self.slice_window)
        self.json_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(self.json_frame, text="Select JSON file:").pack(side=tk.LEFT)
        tk.Button(self.json_frame, text="Browse", command=self.select_slice_json).pack(side=tk.LEFT, padx=5)
        tk.Label(self.json_frame, textvariable=self.slice_json_path).pack(side=tk.LEFT)
        
        self.manual_frame = tk.Frame(self.slice_window)
        self.manual_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(self.manual_frame, text="Tile Width:").grid(row=0, column=0, sticky="e")
        tk.Entry(self.manual_frame, textvariable=self.manual_tile_width, width=5).grid(row=0, column=1, padx=5)
        tk.Label(self.manual_frame, text="Tile Height:").grid(row=0, column=2, sticky="e")
        tk.Entry(self.manual_frame, textvariable=self.manual_tile_height, width=5).grid(row=0, column=3, padx=5)
        tk.Label(self.manual_frame, text="Columns:").grid(row=1, column=0, sticky="e")
        tk.Entry(self.manual_frame, textvariable=self.manual_columns, width=5).grid(row=1, column=1, padx=5)
        tk.Label(self.manual_frame, text="Rows:").grid(row=1, column=2, sticky="e")
        tk.Entry(self.manual_frame, textvariable=self.manual_rows, width=5).grid(row=1, column=3, padx=5)
        
        self.toggle_slice_options()
        
        slice_btn = tk.Button(self.slice_window, text="Slice", command=self.slice_spritesheet_action)
        slice_btn.pack(pady=10)
    
    def toggle_slice_options(self):
        if self.use_json_metadata.get():
            for child in self.json_frame.winfo_children():
                child.configure(state=tk.NORMAL)
            for child in self.manual_frame.winfo_children():
                child.configure(state=tk.DISABLED)
        else:
            for child in self.json_frame.winfo_children():
                child.configure(state=tk.DISABLED)
            for child in self.manual_frame.winfo_children():
                child.configure(state=tk.NORMAL)
    
    def select_slice_image(self):
        path = filedialog.askopenfilename(title="Select Spritesheet Image",
                                          filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if path:
            self.slice_image_path.set(path)
    
    def select_slice_json(self):
        path = filedialog.askopenfilename(title="Select JSON Metadata File",
                                          filetypes=[("JSON files", "*.json")])
        if path:
            self.slice_json_path.set(path)
    
    def slice_spritesheet_action(self):
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            messagebox.showwarning("Warning", "No output directory selected")
            return
        
        if not self.slice_image_path.get():
            messagebox.showwarning("Warning", "No spritesheet image selected")
            return
        
        try:
            spritesheet = Image.open(self.slice_image_path.get()).convert("RGBA")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open spritesheet image: {e}")
            return
        
        if self.use_json_metadata.get():
            if not self.slice_json_path.get():
                messagebox.showwarning("Warning", "No JSON metadata file selected")
                return
            try:
                with open(self.slice_json_path.get(), 'r') as f:
                    data = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load JSON metadata: {e}")
                return
            
            sprites = data.get("sprites", [])
            if not sprites:
                messagebox.showwarning("Warning", "JSON metadata does not contain sprite data")
                return
            
            for sprite in sprites:
                x = sprite.get("x", 0)
                y = sprite.get("y", 0)
                width = sprite.get("width", 0)
                height = sprite.get("height", 0)
                filename = sprite.get("filename", "sprite.png")
                crop_box = (x, y, x + width, y + height)
                slice_img = spritesheet.crop(crop_box)
                out_path = os.path.join(output_dir, filename)
                slice_img.save(out_path)
            messagebox.showinfo("Success", f"Slicing completed. {len(sprites)} sprites saved.")
        else:
            try:
                tile_width = int(self.manual_tile_width.get())
                tile_height = int(self.manual_tile_height.get())
                cols = int(self.manual_columns.get())
                rows = int(self.manual_rows.get())
            except Exception as e:
                messagebox.showerror("Error", "Please enter valid numbers for tile dimensions, columns, and rows.")
                return
            
            count = 0
            for r in range(rows):
                for c in range(cols):
                    x = c * tile_width
                    y = r * tile_height
                    crop_box = (x, y, x + tile_width, y + tile_height)
                    slice_img = spritesheet.crop(crop_box)
                    out_filename = f"tile_r{r}_c{c}.png"
                    out_path = os.path.join(output_dir, out_filename)
                    slice_img.save(out_path)
                    count += 1
            messagebox.showinfo("Success", f"Slicing completed. {count} tiles saved.")
    
    def open_pixel_art_editor(self):
        PixelArtEditor(self.master)

##################################
# Pixel Art Editor with Sidebar
##################################
class PixelArtEditor:
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("Pixel Art Editor")
        # Default grid settings.
        self.grid_width = 32
        self.grid_height = 32
        self.cell_size = 16
        self.current_color = "#000000"  # default drawing color
        self.show_grid = tk.BooleanVar(value=True)
        self.transparent_bg = tk.BooleanVar(value=True)
        self.current_tool = "pen"  # Options: pen, eraser, fill, eyedropper
        self.color_history = []  # Last 10 colors used
        
        # 2D lists for pixel data and canvas cell rectangles.
        self.pixel_data = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.cell_rectangles = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        self.create_widgets()
        self.draw_grid()
    
    def create_widgets(self):
        # Top toolbar.
        toolbar = tk.Frame(self.window)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        tk.Button(toolbar, text="New", command=self.new_canvas).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Open", command=self.open_image).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Save", command=self.save_image).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Choose Color", command=self.choose_color).pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(toolbar, text="Show Grid", variable=self.show_grid, command=self.redraw_grid).pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(toolbar, text="Transparent BG", variable=self.transparent_bg, command=self.draw_grid).pack(side=tk.LEFT, padx=2)
        
        # Main frame holds the canvas and the sidebar.
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas_width = self.grid_width * self.cell_size
        canvas_height = self.grid_height * self.cell_size
        self.canvas = tk.Canvas(main_frame, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.pack(side=tk.LEFT)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
        # Sidebar with tool buttons and color history.
        self.sidebar = tk.Frame(main_frame, padx=5, pady=5, bg="#e0e0e0", relief=tk.RAISED, borderwidth=2)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(self.sidebar, text="Tools:", bg="#e0e0e0").pack(pady=5)
        tk.Button(self.sidebar, text="Pen", command=lambda: self.set_tool("pen")).pack(fill=tk.X, pady=2)
        tk.Button(self.sidebar, text="Eraser", command=lambda: self.set_tool("eraser")).pack(fill=tk.X, pady=2)
        tk.Button(self.sidebar, text="Fill Bucket", command=lambda: self.set_tool("fill")).pack(fill=tk.X, pady=2)
        tk.Button(self.sidebar, text="Eyedropper", command=lambda: self.set_tool("eyedropper")).pack(fill=tk.X, pady=2)
        
        tk.Label(self.sidebar, text="Last Colors:", bg="#e0e0e0").pack(pady=5)
        self.color_history_frame = tk.Frame(self.sidebar, bg="#e0e0e0")
        self.color_history_frame.pack(pady=5)
        
        self.eyedropper_label = tk.Label(self.sidebar, text="Hovered: None", bg="#e0e0e0")
        self.eyedropper_label.pack(pady=5)
        
        tk.Label(self.sidebar, text="Current Color:", bg="#e0e0e0").pack(pady=5)
        self.current_color_display = tk.Label(self.sidebar, bg=self.current_color, width=10, height=2)
        self.current_color_display.pack(pady=5)
    
    def set_tool(self, tool):
        self.current_tool = tool
    
    def update_color_history(self, color):
        if color in self.color_history:
            self.color_history.remove(color)
        self.color_history.insert(0, color)
        if len(self.color_history) > 10:
            self.color_history = self.color_history[:10]
        self.refresh_color_history()
    
    def refresh_color_history(self):
        for widget in self.color_history_frame.winfo_children():
            widget.destroy()
        for col in self.color_history:
            btn = tk.Button(self.color_history_frame, bg=col, width=2, command=lambda c=col: self.use_color(c))
            btn.pack(side=tk.LEFT, padx=1)
    
    def use_color(self, color):
        self.current_color = color
        self.current_color_display.config(bg=color)
    
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Color", initialcolor=self.current_color)
        if color and color[1]:
            self.current_color = color[1]
            self.current_color_display.config(bg=self.current_color)
            self.update_color_history(self.current_color)
    
    def draw_grid(self):
        self.canvas.delete("all")
        self.cell_rectangles = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                if self.pixel_data[row][col] is not None:
                    fill_color = self.pixel_data[row][col]
                else:
                    if self.transparent_bg.get():
                        fill_color = "#cccccc" if (row + col) % 2 == 0 else "#ffffff"
                    else:
                        fill_color = "#ffffff"
                rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                    fill=fill_color,
                                                    outline="gray" if self.show_grid.get() else "")
                self.cell_rectangles[row][col] = rect
    
    def update_cell(self, row, col):
        if self.pixel_data[row][col] is not None:
            fill_color = self.pixel_data[row][col]
        else:
            if self.transparent_bg.get():
                fill_color = "#cccccc" if (row + col) % 2 == 0 else "#ffffff"
            else:
                fill_color = "#ffffff"
        rect = self.cell_rectangles[row][col]
        self.canvas.itemconfig(rect, fill=fill_color)
    
    def redraw_grid(self):
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                self.canvas.itemconfig(self.cell_rectangles[row][col],
                                       outline="gray" if self.show_grid.get() else "")
    
    def on_canvas_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if not (0 <= col < self.grid_width and 0 <= row < self.grid_height):
            return
        if self.current_tool == "pen":
            self.pixel_data[row][col] = self.current_color
            self.update_cell(row, col)
        elif self.current_tool == "eraser":
            self.pixel_data[row][col] = None
            self.update_cell(row, col)
        elif self.current_tool == "fill":
            self.flood_fill(row, col, self.current_color)
            self.draw_grid()
        elif self.current_tool == "eyedropper":
            picked = self.pixel_data[row][col]
            if picked is not None:
                self.current_color = picked
                self.current_color_display.config(bg=picked)
                self.update_color_history(picked)
                self.eyedropper_label.config(text=f"Eyedropper: {picked}")
    
    def on_canvas_motion(self, event):
        if self.current_tool == "eyedropper":
            col = event.x // self.cell_size
            row = event.y // self.cell_size
            if 0 <= row < self.grid_height and 0 <= col < self.grid_width:
                color = self.pixel_data[row][col]
                if color is not None:
                    self.eyedropper_label.config(text=f"Hovered: {color}")
                else:
                    self.eyedropper_label.config(text="Hovered: None")
    
    def flood_fill(self, row, col, new_color):
        original_color = self.pixel_data[row][col]
        if original_color == new_color:
            return
        stack = [(row, col)]
        while stack:
            r, c = stack.pop()
            if r < 0 or r >= self.grid_height or c < 0 or c >= self.grid_width:
                continue
            if self.pixel_data[r][c] != original_color:
                continue
            self.pixel_data[r][c] = new_color
            stack.extend([(r-1, c), (r+1, c), (r, c-1), (r, c+1)])
    
    def clear_canvas(self):
        self.pixel_data = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.draw_grid()
    
    def new_canvas(self):
        new_win = tk.Toplevel(self.window)
        new_win.title("New Canvas")
        tk.Label(new_win, text="Grid Width:").grid(row=0, column=0)
        tk.Label(new_win, text="Grid Height:").grid(row=1, column=0)
        tk.Label(new_win, text="Cell Size:").grid(row=2, column=0)
        width_var = tk.StringVar(value=str(self.grid_width))
        height_var = tk.StringVar(value=str(self.grid_height))
        cell_size_var = tk.StringVar(value=str(self.cell_size))
        tk.Entry(new_win, textvariable=width_var, width=5).grid(row=0, column=1)
        tk.Entry(new_win, textvariable=height_var, width=5).grid(row=1, column=1)
        tk.Entry(new_win, textvariable=cell_size_var, width=5).grid(row=2, column=1)
        def create_new():
            try:
                w = int(width_var.get())
                h = int(height_var.get())
                cs = int(cell_size_var.get())
                self.grid_width = w
                self.grid_height = h
                self.cell_size = cs
                self.pixel_data = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
                self.canvas.config(width=self.grid_width * self.cell_size, height=self.grid_height * self.cell_size)
                self.draw_grid()
                new_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", "Invalid input for dimensions.")
        tk.Button(new_win, text="Create", command=create_new).grid(row=3, column=0, columnspan=2)
    
    def open_image(self):
        path = filedialog.askopenfilename(title="Open Image",
                                          filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if path:
            try:
                img = Image.open(path).convert("RGBA")
                w, h = img.size
                self.grid_width = w
                self.grid_height = h
                self.pixel_data = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
                self.canvas.config(width=self.grid_width * self.cell_size, height=self.grid_height * self.cell_size)
                for y in range(h):
                    for x in range(w):
                        r, g, b, a = img.getpixel((x, y))
                        if a == 0:
                            self.pixel_data[y][x] = None
                        else:
                            self.pixel_data[y][x] = '#%02x%02x%02x' % (r, g, b)
                self.draw_grid()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image: {e}")
    
    def save_image(self):
        out_img = Image.new("RGBA", (self.grid_width, self.grid_height), (255, 255, 255, 0))
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                color = self.pixel_data[y][x]
                if color is not None:
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    out_img.putpixel((x, y), (r, g, b, 255))
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg;*.jpeg"),
                ("BMP", "*.bmp"),
                ("TGA", "*.tga"),
                ("TIFF", "*.tiff"),
                ("WEBP", "*.webp")
            ]
        )
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".jpg", ".jpeg"]:
                file_format = "JPEG"
            elif ext == ".bmp":
                file_format = "BMP"
            elif ext == ".tga":
                file_format = "TGA"
            elif ext == ".tiff":
                file_format = "TIFF"
            elif ext == ".webp":
                file_format = "WEBP"
            else:
                file_format = "PNG"
            try:
                out_img = out_img.resize((self.grid_width * self.cell_size, self.grid_height * self.cell_size), RESAMPLE_FILTER)
                out_img.save(file_path, file_format)
                messagebox.showinfo("Success", f"Image saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x800")
    root.wm_attributes('-toolwindow', 'True')
    app = SpriteSheetMaker(root)
    root.mainloop()