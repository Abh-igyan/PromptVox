# PromptVox 🎙️⚡
> **Universal Voice Interface & Bilingual Speech-to-Code Layer for AI Coding Agents**  
> *Zero-lag dictation, code-aware formatting, and flawless Hinglish-to-Latin transliteration across Google Antigravity, Cursor, Claude Code, and VS Code.*

---

## ⚡ The Motivation & Challenges

AI coding workflows thrive on long, detailed prompts containing architecture context, algorithmic edge cases, and technical requirements. However, using voice dictation in developer workflows introduces key challenges:

1. **The Multilingual / Indian Accent Breakdown:** Standard speech-to-text models either output Devanagari Hindi script (`क्या आप सुन रहे हो`), hallucinate unwanted English translations (*"Bhai optimize karo"* $\rightarrow$ *"Brother optimize"*), or drop words during natural bilingual code-switching.
2. **Technical Vocabulary & Developer Tokens:** General-purpose STT models often fumble programming syntax and acronyms (`C++`, `DSA`, `CP`, `FastAPI`, `LeetCode`, `gVisor`, `SQL`), altering proper casing and punctuation.
3. **In-Built Mic for Antigravity in VS Code:** While Antigravity IDE and CLI have native voice capabilities, the Antigravity VS Code extension did not include a native in-panel mic button. PromptVox provides an integrated microphone icon directly inside the Antigravity panel header in VS Code, alongside a universal OS-level shortcut (`Alt + V`).

**PromptVox solves these challenges completely.**

---

## ✨ Features

- **🚀 Sub-Second Transcription Latency:** Powered by Groq-accelerated `whisper-large-v3` (~200ms processing time) with automatic fallback to local `faster-whisper`.
- **🗣️ Flawless Bilingual Code-Switching (Hinglish $\rightarrow$ Latin Script):**
  - Speaks naturally mixing Hindi and English: *"Bhai ye wala binary search function optimize kar do in C++ for CP"*.
  - Transcribes cleanly into the **English/Latin alphabet** without Hindi script and without translating meaning.
  - Features algorithmic **Hindi Schwa Syncope** rules (`sun`, `agar`, `bhai`, `kar do`) for authentic Romanization.
- **🧩 Silence-Partitioned Parallel Chunking:** Automatically segments audio on pauses $\ge 300\text{ ms}$ and processes chunks in parallel via a thread pool, breaking Whisper's single-language decoder lock.
- **🛠️ Deterministic Developer Formatter:** Retains developer casing and acronyms (`C++`, `DSA`, `CP`, `FastAPI`, `LeetCode`, `API`, `SQL`, `gVisor`) without LLM hallucination.
- **🌐 Universal OS-Level Injection:** Types directly into whichever window has active focus:
  - Antigravity Chat (VS Code)
  - Terminals & IDE Editors
  - Cursor, Claude, or any text/chat input
- **🔌 First-Class Antigravity VS Code Extension:**
  - Adds a native microphone icon inside the Antigravity chat panel header (`antigravity.panel`).
  - Status Bar item showing live recording status.
  - Auto-spawns and manages the backend daemon silently.
- **🎨 Non-Focus-Stealing Floating HUD:** Sleek Tkinter waveform visualizer with Windows `WS_EX_NOACTIVATE` so your cursor never leaves your chat input box.

---

## 🏗️ Architecture

```
                       ┌────────────────────────────┐
                       │  User Speech (Mic Stream)  │
                       └──────────────┬─────────────┘
                                      │
                         [ sounddevice 16kHz Mono ]
                                      │
                       ┌──────────────▼─────────────┐
                       │ Pause-Segmented Chunking   │
                       │ (Splits on silence >=300ms)│
                       └──────────────┬─────────────┘
                                      │
                 ┌────────────────────┴────────────────────┐
                 │                                         │
       [ Chunk 1: Hindi/Hinglish ]               [ Chunk 2: English/Code ]
                 │                                         │
        Groq Whisper Large-v3                     Groq Whisper Large-v3
                 │                                         │
        Devanagari $\rightarrow$ Latin                     Direct Latin Text
      Phonetic Transliteration                             │
                 │                                         │
                 └────────────────────┬────────────────────┘
                                      │
                       ┌──────────────▼─────────────┐
                       │ Deterministic Code Cleaner │
                       │ (Casing, Tech Acronyms)    │
                       └──────────────┬─────────────┘
                                      │
                       ┌──────────────▼─────────────┐
                       │ OS Active Window Injection │
                       │ (Antigravity / Cursor / CLI)│
                       └────────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.10+
- A free [Groq API Key](https://console.groq.com) (for Whisper Large-v3 speed)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/Abh-igyan/PromptVox.git
cd PromptVox

# Install python dependencies
pip install -r requirements.txt

# Configure your Groq API Key
cp config.example.json config.json
# Edit config.json and paste your groq_api_key
```

### 3. Run the Backend

```bash
# Normal runner
python main.py

# Or background headless runner (Windows)
launch_voice.vbs
```

### 4. Install the VS Code / Antigravity Extension

Copy or symlink `vscode-extension` into your VS Code extensions folder:
```bash
# Windows
xcopy /E /I vscode-extension "%USERPROFILE%\.vscode\extensions\antigravity-voice-helper"
```

Restart or reload VS Code. You will now see:
- A `$(mic)` button in your VS Code Status Bar.
- An in-built mic icon in the Antigravity Chat panel title header.

---

## ⌨️ Shortcuts & Controls

| Action | Shortcut / Trigger |
|---|---|
| **Toggle Mic (Start / Stop)** | `Alt + V` (Global Hotkey) |
| **Alternative Hotkeys** | `F8` or `Ctrl + Alt + V` |
| **VS Code Header Button** | Click mic icon in Antigravity Chat Header |
| **VS Code Status Bar** | Click `$(mic) Voice Type` in status bar |
| **Cancel Recording** | `Escape` |

---

## 🔧 Configuration (`config.json`)

```json
{
  "groq_api_key": "gsk_...",
  "use_cloud_stt": true,
  "use_smart_refiner": false
}
```

- `groq_api_key`: Your Groq Cloud API key.
- `use_cloud_stt`: `true` to use Groq Whisper Large-v3 (~200ms latency); `false` to run fully offline with local `faster-whisper`.
- `use_smart_refiner`: `false` by default to preserve deterministic verbatim dictation without LLM hallucinations.

---

## 🛡️ License

MIT License. Crafted with ❤️ for AI-native software engineering.

