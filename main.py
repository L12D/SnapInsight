import pyautogui
import tkinter as tk
from tkhtmlview import HTMLLabel
import markdown
from PIL import ImageTk, ImageDraw, ImageOps
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

    new_center_x = center_x - left
    new_center_y = center_y - upper
    width, height = cropped_screenshot.size

    pad_left = max(256 - new_center_x, 0)
    pad_top = max(256 - new_center_y, 0)
    pad_right = max(512 - width, 0)
    pad_bottom = max(512 - height, 0)

    padded_screenshot = ImageOps.expand(cropped_screenshot, (pad_left, pad_top, pad_right, pad_bottom), fill="black")
    padded_screenshot = padded_screenshot.crop((0, 0, 512, 512))
    padded_screenshot.save(os.environ["PROJECT_PATH"] + "screenshot.jpg")

    screenshotWindow.destroy()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def send_message():
    global html_content

    user_message = user_input.get()
    
    user_message_html = markdown.markdown(user_message)
    
    html_content += f"<p style='font-size:11px;color:white;'><h4 style='color:green;'>You:</h4> {user_message_html}</p>"
    chat_log.set_html(html_content)
    
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
        "max_tokens": 400
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_message = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    
    conversation_history.append({"role": "assistant", "content": response_message})

    response_message_html = markdown.markdown(response_message)
    
    html_content += f"<p style='font-size:11px;color:white;'><h4 style='color:green;'>Assistant:</h4> {response_message_html}</p>"
    chat_log.set_html(html_content)


def openChatWindow():
    def on_enter_key(event):
        if user_input.get().strip():
            send_message()
    
    chat_window = tk.Tk()
    chat_window.title("SnapInsight")
    chat_window.geometry("512x950+1360+60")
    chat_window.resizable(False, False)

    global chat_log
    chat_log = HTMLLabel(chat_window, html="", background="black", foreground="white", highlightthickness=0)
    chat_log.pack(expand=True, fill='both')

    global html_content
    html_content = f'<img src="{os.environ["PROJECT_PATH"] + "/" + image_path}" /><h2 style="color:white;">Chat :</h2>'
    chat_log.set_html(html_content)


    input_frame = tk.Frame(chat_window)
    input_frame.pack(side=tk.BOTTOM, fill='x')

    global user_input
    user_input = tk.Entry(input_frame)
    user_input.pack(side=tk.LEFT, fill='x', expand=True)
    user_input.bind("<Return>", on_enter_key)

    send_button = tk.Button(input_frame, text="Send", command=send_message)
    send_button.pack(side=tk.RIGHT)

    chat_window.mainloop()






if __name__ == "__main__":

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

    image_path = "screenshot.jpg"
    base64_image = encode_image(os.environ["PROJECT_PATH"] + image_path)

    conversation_history = []

    openChatWindow()
    os.remove(os.environ["PROJECT_PATH"] + "screenshot.jpg")
