import customtkinter as ctk
from huggingface_hub import InferenceClient
import json
import os

# --- SETTINGS ---
API_TOKEN = "YOUR_TOKEN_HERE"
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

client = InferenceClient(model=MODEL_ID, token=API_TOKEN)
MEMORY_FILE = "memory.json"

# --- LOGIC ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_memory(history):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# --- UI SETUP ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Py-AI Assistant v14.0")
        self.geometry("600x700")
        self.history = load_memory()

        # Chat Window
        self.chat_display = ctk.CTkTextbox(self, width=580, height=550, state="disabled")
        self.chat_display.pack(padx=10, pady=10)

        # Input Frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(padx=10, pady=10, fill="x")

        self.user_input = ctk.CTkEntry(self.input_frame, placeholder_text="Ask me anything...", width=450)
        self.user_input.pack(side="left", padx=5)
        self.user_input.bind("<Return>", lambda e: self.send_message())

        self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message, width=100)
        self.send_button.pack(side="right", padx=5)

        self.display_history()

    def display_history(self):
        self.chat_display.configure(state="normal")
        for msg in self.history:
            role = "You" if msg["role"] == "user" else "Py-AI"
            self.chat_display.insert("end", f"{role}: {msg['content']}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def send_message(self):
        text = self.user_input.get()
        if not text: return

        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"You: {text}\n\n")
        self.user_input.delete(0, "end")
        
        # AI Logic
        messages = [{"role": "system", "content": "You are a helpful assistant named Py-AI."}]
        messages.extend(self.history[-10:]) # Last 10 messages for context
        messages.append({"role": "user", "content": text})

        try:
            response = client.chat_completion(messages=messages, max_tokens=500)
            answer = response.choices[0].message.content.strip()
            
            self.chat_display.insert("end", f"Py-AI: {answer}\n\n")
            self.history.append({"role": "user", "content": text})
            self.history.append({"role": "assistant", "content": answer})
            save_memory(self.history)
        except Exception as e:
            self.chat_display.insert("end", f"Error: {e}\n\n")
        
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
