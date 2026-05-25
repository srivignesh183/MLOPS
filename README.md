# ⚡ Gemini Interactive CLI Chat Client

A premium, interactive command-line interface (CLI) for chatting with Google Gemini models. Powered by the official, state-of-the-art **`google-genai`** Python SDK.

---

## ✨ Features

- **Real-Time Streaming:** Responses are streamed word-by-word into your terminal with zero delay.
- **Persistent Conversations:** Full multi-turn support. Gemini remembers context across the entire session.
- **Dynamic Model Switching:** Switch between `gemini-2.5-flash`, `gemini-2.5-pro`, or other models mid-conversation while *retaining* your conversation history.
- **Dynamic System Prompts:** Change Gemini's instructions or persona (e.g., `/system You are a sarcastic pirate code auditor`) on the fly while retaining conversation history.
- **Rich Command Shell:** Control the session using built-in slash (`/`) commands.
- **Aesthetic Terminal Design:** Elegant ANSI-color console dashboard, micro-metric trackers (time to first token, total duration), and keyboard interrupt handling.
- **Secure Configuration:** Automatic lookup for `GEMINI_API_KEY` via env/dotenv, with a secure CLI fallback prompt that can generate a `.env` file for you automatically.

---

## 🚀 Quick Start

### 1. Prerequisites

Make sure you have Python 3.10 or newer installed:
```bash
python3 --version
```

### 2. Installation

Clone this repository or navigate to its directory, then install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. API Key Configuration

To chat with Gemini, you need a free API Key from **Google AI Studio**.
Get one at [aistudio.google.com](https://aistudio.google.com/).

You have three options to configure it:

#### Option A (Recommended): Create a `.env` file
Duplicate the `.env.example` file and rename it to `.env`, then add your key:
```env
GEMINI_API_KEY=AIzaSy...your_actual_key...
```

#### Option B: Export the environment variable
In your terminal, run:
```bash
export GEMINI_API_KEY="AIzaSy...your_actual_key..."
```

#### Option C: Secure CLI Fallback
If no key is configured, the application will securely prompt you for your key on launch and offer to write a `.env` file for you.

---

## 💬 Usage

Start the interactive session:
```bash
python main.py
```

### 🎮 Built-in Slash Commands

Type these commands directly into the prompt to manage your chat:

| Command | Action | Example |
| :--- | :--- | :--- |
| `/help` | Displays command assistance | `/help` |
| `/clear` | Resets the conversation history (starts fresh) | `/clear` |
| `/history` | Displays the formatted chat log of the current session | `/history` |
| `/system [text]` | Updates Gemini's system instructions (preserves history) | `/system You are a senior Python tutor` |
| `/model [name]` | Dynamically switches models (preserves history) | `/model gemini-2.5-pro` |
| `/exit` | Safely ends the conversation and quits the terminal | `/exit` |

---

## 🛠️ Deep Dive: How It Works

Under the hood, the client wraps the **Google GenAI SDK**:

1. **State Management:** When you send a message, it uses `chat.send_message_stream()` within a stateful session constructed with `client.chats.create()`.
2. **Dynamic Context Transfers:** When using `/model` or `/system`, the wrapper retrieves the active conversation history with `chat.get_history()`. It then spawns a new chat session on the new model/system prompt and passes the existing history list back to the engine. This makes switching completely seamless!
