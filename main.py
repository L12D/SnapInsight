import pyautogui
import tkinter as tk
from PIL import ImageTk, ImageDraw
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
    cropped_screenshot.save("screenshot.jpg")
    print("Screenshot saved with a red rectangle!")

    screenshotWindow.destroy()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def send_message():
    user_message = user_input.get()
    chat_log.insert(tk.END, f"You: {user_message}\n")
    user_input.delete(0, tk.END)

    if not conversation_history:
        conversation_history.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_message
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        })
    else:
        conversation_history.append({"role": "user", "content": user_message})

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": conversation_history,
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_message = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    
    conversation_history.append({"role": "assistant", "content": response_message})
    
    chat_log.insert(tk.END, f"LLM: {response_message}\n")


def openChatWindow():
    chat_window = tk.Tk()
    chat_window.title("Chat")

    global chat_log
    chat_log = tk.Text(chat_window, state='normal', height=20, width=50)
    chat_log.pack()

    global user_input
    user_input = tk.Entry(chat_window, width=50)
    user_input.pack()

    send_button = tk.Button(chat_window, text="Send", command=send_message)
    send_button.pack()

    chat_window.mainloop()






if __name__ == "__main__":

    screenshotWindow = tk.Tk()
    screenshotWindow.attributes("-fullscreen", True)
    screenshotWindow.attributes("-topmost", True)
    screenshot = pyautogui.screenshot()
    screenshot_tk = ImageTk.PhotoImage(screenshot)
    canvas = tk.Canvas(screenshotWindow, width=screenshot.width, height=screenshot.height)
    canvas.pack()
    canvas.create_image(0, 0, anchor=tk.NW, image=screenshot_tk)

    rect = None

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    screenshotWindow.mainloop()

    image_path = "screenshot.jpg"
    base64_image = encode_image(image_path)

    conversation_history = []

    openChatWindow()
    os.remove("screenshot.jpg")
