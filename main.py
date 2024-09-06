import pyautogui
import tkinter as tk
from PIL import ImageTk, ImageDraw
from openai import OpenAI
import base64
import requests
import os



def on_mouse_down(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y


def on_mouse_drag(event):
    global rect
    canvas.delete(rect)
    rect = canvas.create_rectangle(start_x, start_y, event.x, event.y, outline="red")


def on_mouse_up(event):
    global start_x, start_y
    # Draw the red rectangle on the image
    draw = ImageDraw.Draw(screenshot)
    draw.rectangle([start_x, start_y, event.x, event.y], outline="red", width=2)

    center_x = (start_x + event.x) // 2
    center_y = (start_y + event.y) // 2
    
    # Define the bounding box for the 512x512 crop
    left = max(center_x - 256, 0)
    upper = max(center_y - 256, 0)
    right = min(center_x + 256, screenshot.width)
    lower = min(center_y + 256, screenshot.height)
    
    # Crop the screenshot
    cropped_screenshot = screenshot.crop((left, upper, right, lower))
    cropped_screenshot = cropped_screenshot.convert("RGB")
    cropped_screenshot.save("screenshot.jpg")
    print("Screenshot saved with a red rectangle!")

    root.destroy()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')









if __name__ == "__main__":
    root = tk.Tk()

    screenshot = pyautogui.screenshot()
    # screenshot.save("screenshot.png")
    screenshot_tk = ImageTk.PhotoImage(screenshot)


    
    canvas = tk.Canvas(root, width=screenshot.width, height=screenshot.height)
    canvas.pack()

    # Add screenshot to the canvas
    canvas.create_image(0, 0, anchor=tk.NW, image=screenshot_tk)

    # Initialize rectangle variable
    rect = None

    # Bind mouse events
    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    root.mainloop()

    

    

    # Path to your image
    image_path = "screenshot.jpg"

    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }

    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Describe what is in the red rectangle"
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json())