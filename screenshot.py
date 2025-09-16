import tkinter as tk
from PIL import ImageTk, ImageDraw, ImageOps
import pyautogui
import base64
import os

# Global variable to store the screenshot path
screenshot_path = None

def on_mouse_down(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y


def on_mouse_drag(event):
    global rect
    if rect is not None:
        canvas.delete(rect)
    rect = canvas.create_rectangle(start_x, start_y, event.x, event.y, outline="red")


def on_mouse_up(event):
    global start_x, start_y, screenshot_path

    draw = ImageDraw.Draw(screenshot)
    draw.rectangle([start_x, start_y, event.x, event.y], outline="red", width=2)

    center_x = (start_x + event.x) // 2
    center_y = (start_y + event.y) // 2
    
    left = max(center_x - 256, 0)
    upper = max(center_y - 256, 0)
    right = min(center_x + 256, screenshot.width)
    lower = min(center_y + 256, screenshot.height)
    
    cropped_screenshot = screenshot.crop((left, upper, right, lower))
    cropped_screenshot = cropped_screenshot.convert("RGB")

    new_center_x = center_x - left
    new_center_y = center_y - upper
    width, height = cropped_screenshot.size

    pad_left = max(256 - new_center_x, 0)
    pad_top = max(256 - new_center_y, 0)
    pad_right = max(512 - width, 0)
    pad_bottom = max(512 - height, 0)

    padded_screenshot = ImageOps.expand(cropped_screenshot, (pad_left, pad_top, pad_right, pad_bottom), fill="black")
    padded_screenshot = padded_screenshot.crop((0, 0, 512, 512))
    
    # Ensure the .images directory exists
    os.makedirs(".images", exist_ok=True)
    screenshot_path = ".images/screenshot.jpg"
    padded_screenshot.save(screenshot_path)

    screenshotWindow.destroy()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def take_screenshot():
    """Main function to take screenshot and return the path"""
    global canvas, screenshotWindow, screenshot, rect, screenshot_path

    screenshotWindow = tk.Tk()
    screenshotWindow.attributes("-fullscreen", True)
    screenshotWindow.attributes("-topmost", True)
    screenshot = pyautogui.screenshot()
    screenshot_tk = ImageTk.PhotoImage(screenshot)
    canvas = tk.Canvas(screenshotWindow, width=screenshot.width, height=screenshot.height)
    canvas.pack(expand=True, fill='both')
    canvas.create_image(0, 0, anchor=tk.NW, image=screenshot_tk)

    rect = None

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    screenshotWindow.mainloop()
    
    return screenshot_path


def main():
    """For standalone screenshot functionality"""
    return take_screenshot()


if __name__ == "__main__":
    path = main()
    print(f"Screenshot saved to: {path}")