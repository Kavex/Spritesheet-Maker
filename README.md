<img src="https://github.com/Kavex/Spritesheet-Maker/blob/main/Source/Images/Preview.gif" alt="drawing" width="600"/>

# Spritesheet Maker

Spritesheet Maker is a Python GUI application that allows you to easily create spritesheets from individual sprite images. You can add, remove, and reorder images, preview your spritesheet with adjustable zoom and columns, and export the final spritesheet in various image formats. It also supports transparent backgrounds or custom background colors.

Download: https://github.com/Kavex/Spritesheet-Maker/releases/

A versatile GUI tool built with Python and Tkinter that allows you to create spritesheets from individual images, export JSON metadata, slice spritesheets, and edit pixel art with a dedicated editor featuring MS Paint–like functionality.

## Features

### SpriteSheet Maker

- **Image Management:**  
  - Add, remove, clear, and reorder sprite images.
- **Live Preview:**  
  - View a real-time preview of your spritesheet with adjustable zoom and column settings.
  - Set transparent background color
  - Change Columns on the fly
- **Export Options:**  
  - Export your spritesheet in PNG, JPEG, BMP, TGA, TIFF, and WEBP formats.
  - Optionally export JSON metadata with each sprite’s original filename, dimensions, and position.
- **Spritesheet Slicing:**  
  - Slice an existing spritesheet:
    - **Automatically** using JSON metadata.
    - **Manually** by specifying tile width, height, columns, and rows.

### Simple Sprite Editor

- **Grid-Based Canvas:**  
  - Customizable grid for pixel art creation.
  - Choose between a checkered (transparent) or solid white background.
- **Toolset:**  
  - **Pen:** Draw pixels.
  - **Eraser:** Remove pixels.
  - **Fill Bucket:** Flood-fill contiguous areas.
  - **Eyedropper:** Pick and display the color of a pixel (shows hex code on hover).
- **Color Management:**  
  - Pick colors with a color chooser.
  - View and select from the last 10 colors used.
- **File Operations:**  
  - Open, save, and clear pixel art images in multiple file formats.

## Installation

### Prerequisites

- **Python 3.x**
- **Pillow** – Python Imaging Library

Install dependencies using pip:

```bash
pip install pillow
```

Running the Application:

```bash
python SpriteSheetMaker.py
```


