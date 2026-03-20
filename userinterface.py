import customtkinter as ctk
import requests
import json
import subprocess
import threading
import os

# ── Ollama Config ─────────────────────────────
OLLAMA_EXE = r"C:\Users\nyark\AppData\Local\Programs\Ollama\ollama.exe"
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3"

SYSTEM_PROMPT = """
You are Bob, a friendly Windows tech support assistant.
Help users fix their Windows PC problems step by step in plain simple English.
Rules:
- Be friendly and simple. No jargon.
- Only suggest ONE thing at a time.
- Wait for the user to respond before doing anything else.
- Never chain multiple actions automatically.
- Do NOT use <SCRIPT> tags ever. Scripts are handled separately.
- Keep replies short and clear.
"""

KEYWORD_SCRIPTS = {
    ("slow", "cpu", "lag", "freeze", "hanging", "performance"): "scripts/slow_pc.ps1",
    ("wifi", "internet", "network", "connection", "ping", "offline"): "scripts/network.ps1",
    ("disk", "storage", "space", "full", "drive"): "scripts/disk.ps1",
    ("startup", "boot", "slow start", "taking long"): "scripts/startup.ps1",
    ("error", "crash", "blue screen", "bsod", "event log"): "scripts/windows_errors.ps1",
}

SCRIPT_DESCRIPTIONS = {
    "scripts/slow_pc.ps1": "I want to peek at which apps are using the most CPU and memory on your PC right now. I won't change or delete anything — just looking!",
    "scripts/network.ps1": "I want to check your internet connection — look at your network adapter and test if you can reach the internet. Read only, nothing changes!",
    "scripts/disk.ps1": "I want to check how much storage space you have left and make sure your drives are healthy. Just reading info, nothing gets deleted!",
    "scripts/startup.ps1": "I want to see which programs launch automatically when your PC starts. Too many can slow things down. Just looking for now!",
    "scripts/windows_errors.ps1": "I want to check your Windows error log from the last 24 hours to spot anything unusual. Read-only scan!",
}

# ── App ───────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("🤓 FixIt Bob — Your Reliable Tech Support")
app.geometry("820x640")
app.minsize(600, 400)

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# ── Header ────────────────────────────────────
ctk.CTkLabel(app, text="🤓 FixIt Bob", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(20, 2))
ctk.CTkLabel(app, text="Your Everyday Reliable Tech Support", font=ctk.CTkFont(size=13), text_color="#888888").pack(pady=(0, 4))
status_label = ctk.CTkLabel(app, text="⏳ Starting Bob...", font=ctk.CTkFont(size=11), text_color="orange")
status_label.pack(pady=(0, 10))

# ── Chat Area ─────────────────────────────────
chat_frame = ctk.CTkScrollableFrame(app, corner_radius=10)
chat_frame.pack(padx=20, pady=(0, 10), fill="both", expand=True)

# ── Watermark ─────────────────────────────────
watermark = ctk.CTkLabel(
    chat_frame,
    text="🤓        🤓        🤓\n\n        🤓        🤓\n\n🤓        🤓        🤓",
    font=ctk.CTkFont(size=42),
    text_color="#222222",
    fg_color="transparent"
)
watermark.place(relx=0.5, rely=0.5, anchor="center")

# ── Add normal chat bubble ─────────────────────
def add_message(sender, message, color):
    frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
    frame.pack(fill="x", pady=4, padx=5)

    ctk.CTkLabel(
        frame, text=sender,
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color="gray"
    ).pack(anchor="e" if sender == "You" else "w", padx=12)

    bubble = ctk.CTkLabel(
        frame, text=message,
        fg_color=color,
        corner_radius=12,
        font=ctk.CTkFont(size=13),
        wraplength=530,
        justify="left",
        padx=14, pady=10
    )
    bubble.pack(anchor="e" if sender == "You" else "w", padx=12)
    chat_frame._parent_canvas.yview_moveto(1.0)
    return bubble

# ── Add inline Yes/No confirmation in chat ────
def add_confirmation(description, script):
    frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
    frame.pack(fill="x", pady=4, padx=5)

    ctk.CTkLabel(
        frame, text="🤓 Bob",
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color="gray"
    ).pack(anchor="w", padx=12)

    # The bubble
    bubble = ctk.CTkFrame(frame, fg_color="#1f538d", corner_radius=12)
    bubble.pack(anchor="w", padx=12, fill="x", ipadx=10, ipady=10)

    ctk.CTkLabel(
        bubble,
        text=description,
        font=ctk.CTkFont(size=13),
        text_color="white",
        wraplength=500,
        justify="left"
    ).pack(anchor="w", padx=14, pady=(12, 8))

    btn_row = ctk.CTkFrame(bubble, fg_color="transparent")
    btn_row.pack(anchor="w", padx=14, pady=(0, 12))

    def on_yes():
        yes_btn.configure(state="disabled")
        no_btn.configure(state="disabled")
        add_message("You", "Yes, go ahead! ✅", "#2d4a2d")
        add_message("🤓 Bob", "On it! Give me a sec... ⚙️", "#1f538d")
        threading.Thread(target=run_script, args=(script,), daemon=True).start()

    def on_no():
        yes_btn.configure(state="disabled")
        no_btn.configure(state="disabled")
        add_message("You", "No thanks ❌", "#2d4a2d")
        add_message("🤓 Bob", "No problem! Let me know if there's anything else I can help with 🤓", "#1f538d")
        send_button.configure(state="normal")

    yes_btn = ctk.CTkButton(
        btn_row, text="✅ Yes, go ahead!",
        width=150, height=36,
        fg_color="#2d6a2d", hover_color="#3a8a3a",
        font=ctk.CTkFont(size=12, weight="bold"),
        command=on_yes
    )
    yes_btn.pack(side="left", padx=(0, 10))

    no_btn = ctk.CTkButton(
        btn_row, text="❌ No thanks",
        width=150, height=36,
        fg_color="#6a2d2d", hover_color="#8a3a3a",
        font=ctk.CTkFont(size=12, weight="bold"),
        command=on_no
    )
    no_btn.pack(side="left")

    chat_frame._parent_canvas.yview_moveto(1.0)

# ── Run PowerShell script ──────────────────────
def run_script(script):
    script_file = "_bob_temp.ps1"
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(script)
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_file],
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout.strip()
        errors = result.stderr.strip()
        combined = output + ("\n\nErrors:\n" + errors if errors else "")
        if not combined.strip():
            combined = "(Script ran but produced no output)"
    except Exception as e:
        combined = f"Error running script: {e}"
    finally:
        if os.path.exists(script_file):
            os.remove(script_file)

    feedback = (
        f"The scan finished. Here is the output:\n\n{combined}\n\n"
        f"Explain what this means in simple plain English. "
        f"Give 1-2 clear recommendations. "
        f"Do NOT suggest running more scripts. Just explain and wait."
    )
    messages.append({"role": "user", "content": feedback})
    app.after(0, lambda: threading.Thread(target=ask_bob, args=(feedback,), daemon=True).start())
    app.after(0, lambda: send_button.configure(state="normal"))

# ── Detect keyword → script ────────────────────
def detect_script(text):
    text_lower = text.lower()
    for keywords, path in KEYWORD_SCRIPTS.items():
        if any(kw in text_lower for kw in keywords):
            if os.path.exists(path):
                with open(path, "r") as f:
                    return path, f.read()
    return None, None

# ── Talk to Ollama ────────────────────────────
def ask_bob(user_text):
    messages.append({"role": "user", "content": user_text})
    typing = add_message("🤓 Bob", "✏️ Bob is thinking...", "#1f538d")
    full = ""
    try:
        with requests.post(OLLAMA_URL, json={"model": MODEL, "messages": messages, "stream": True}, stream=True, timeout=120) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    chunk = data.get("message", {}).get("content", "")
                    full += chunk
                    typing.configure(text=full)
                    chat_frame._parent_canvas.yview_moveto(1.0)
                    if data.get("done"):
                        break
        messages.append({"role": "assistant", "content": full})
    except Exception as e:
        typing.configure(text=f"❌ Could not reach Bob's brain.\nError: {e}")
    app.after(0, lambda: send_button.configure(state="normal"))

# ── Send ──────────────────────────────────────
def on_send():
    text = input_box.get("1.0", "end").strip()
    if not text:
        return
    input_box.delete("1.0", "end")
    add_message("You", text, "#2d4a2d")
    send_button.configure(state="disabled")

    matched_path, script = detect_script(text)
    if script:
        desc = SCRIPT_DESCRIPTIONS.get(matched_path, "I'd like to run a quick scan on your PC. Nothing will be changed!")
        add_message("🤓 Bob", "Hey! I think I know what to check. Here's what I'd like to do 👇", "#1f538d")
        app.after(400, lambda: add_confirmation(desc, script))
    else:
        threading.Thread(target=ask_bob, args=(text,), daemon=True).start()

def on_enter(event):
    on_send()
    return "break"

# ── Input Area ────────────────────────────────
input_frame = ctk.CTkFrame(app, fg_color="transparent")
input_frame.pack(padx=20, pady=(0, 5), fill="x")

input_box = ctk.CTkTextbox(input_frame, height=60, corner_radius=10)
input_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
input_box.bind("<Return>", on_enter)

send_button = ctk.CTkButton(
    input_frame, text="Send ➤",
    width=100, height=60,
    corner_radius=10,
    font=ctk.CTkFont(size=14, weight="bold"),
    command=on_send
)
send_button.pack(side="right")

# ── Footer ────────────────────────────────────
ctk.CTkLabel(app, text="🤓 FixIt Bob  •  Powered by Ollama  •  🤓", font=ctk.CTkFont(size=10), text_color="#333333").pack(pady=(2, 8))

# ── Auto Start Ollama ─────────────────────────
def start_ollama():
    import time
    try:
        subprocess.Popen([OLLAMA_EXE, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    for _ in range(15):
        try:
            requests.get("http://localhost:11434", timeout=2)
            app.after(0, lambda: status_label.configure(text="● Bob is Online and Ready! 🤓", text_color="#4CAF50"))
            app.after(0, lambda: add_message("🤓 Bob", "Hey! I'm Bob — your everyday tech support buddy 🤓\nTell me what's going wrong with your PC and I'll sort it out step by step!", "#1f538d"))
            return
        except:
            time.sleep(1)
    app.after(0, lambda: status_label.configure(text="● Offline — Could not connect", text_color="red"))

threading.Thread(target=start_ollama, daemon=True).start()
app.mainloop()
