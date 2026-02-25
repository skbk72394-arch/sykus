# Sykus 3.0 - The World's Most Frustration-Free Programming Language

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ███████╗██╗   ██╗██╗  ██╗██╗   ██╗███████╗                                ║
║   ██╔════╝╚██╗ ██╔╝██║ ██╔╝██║   ██║██╔════╝                                ║
║   ███████╗ ╚████╔╝ █████╔╝ ██║   ██║███████╗                                ║
║   ╚════██║  ╚██╔╝  ██╔═██╗ ██║   ██║╚════██║                                ║
║   ███████║   ██║   ██║  ██╗╚██████╔╝███████║                                ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝                                ║
║                                                                              ║
║                    The World's Most Frustration-Free Language                ║
║                           v3.0.0 Auto-Healing Edition                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

> **"Line 4 had a typo. I fixed it and ran it."**

## 🌟 The 6 Pillars of Sykus

### 1. Ultra-Minimal Syntax
No brackets, no semicolons, just natural English:

```sykus
name = "Sykus"
age = 25

Agent jarvis = use Gemini(key="YOUR_KEY")

jarvis.listen() ->
    if hear "hello" then
        jarvis.speak("Hello!")
```

### 2. Polyglot Bridge
Embed native code from any language:

```sykus
[[python]]
import os
os.system('clear')
[[end]]

[[bash]]
echo "Hello from Bash!"
[[end]]
```

### 3. Ghost Dependency Manager
Dependencies auto-install in the background:

```sykus
use face_recognition  # pip install happens automatically!
```

### 4. Smart State & Memory
Database operations without SQL:

```sykus
save user_data to local      # Auto-creates SQLite
load users from local        # No queries needed
```

### 5. Auto-Healing Interpreter
Never see confusing tracebacks:

```
🩹 Sykus Auto-Healer
Line 4: Added 'then' to if statement
Before: if hear "hello"
After:  if hear "hello" then
✓ Fixed 1 issue and continued execution
```

### 6. Universal Transpilation
One language, multiple targets:
- Python (AI/Backend)
- JavaScript (Web)
- Kotlin (Android)

---

## 🚀 Quick Start

### Installation

```bash
# Clone or download
cd sykus-final

# Make CLI executable
chmod +x cli/syk_cli.py

# Create symlink (optional)
ln -s $(pwd)/cli/syk_cli.py /usr/local/bin/syk

# Verify
syk --version
```

### Your First Program

Create `hello.syk`:

```sykus
name = "World"
say "Hello, " + name + "!"
```

Run it:

```bash
syk run hello.syk
```

---

## 📖 Syntax Guide

### Variables

```sykus
name = "John"           # String
age = 25                # Number
is_active = true        # Boolean
items = ["a", "b"]      # List
user = {name: "John"}   # Dictionary
```

### AI Agents

```sykus
Agent jarvis = use Gemini(key="YOUR_API_KEY")

jarvis.speak("Hello!")
response = jarvis.ask("What is AI?")
```

### Conditionals

```sykus
if hear "hello" then
    say "Hi!"

if age > 18 then
    say "Adult"
else
    say "Minor"
```

### Loops

```sykus
for item in items ->
    say item

while is_running ->
    listen to mic
```

### Async Operations

```sykus
async ->
    data = fetch "https://api.com" save to result
    say "Loaded!"

background ->
    wait 5 seconds
    say "Background task done"
```

### Database

```sykus
save user to local
users = load users from local
```

### Polyglot Blocks

```sykus
[[python]]
import numpy as np
arr = np.array([1, 2, 3])
print(arr.mean())
[[end]]
```

### Event Handlers

```sykus
create button myBtn text "Click Me"

on click myBtn ->
    say "Button clicked!"
```

---

## 🛠️ CLI Commands

```bash
# Run a Sykus file
syk run app.syk
syk run app.syk --mode web

# Build for platforms
syk build web
syk build apk
syk build python
syk build javascript

# Check system health
syk doctor

# Show version
syk --version
```

---

## 🧠 Auto-Healing Examples

### Before/After

**Your code (with typo):**
```sykus
if hear "hello"
    say "Hi!"
```

**Sykus heals it:**
```
🩹 Sykus Auto-Healer
Line 1: Added 'then' to if statement
Before: if hear "hello"
After:  if hear "hello" then
✓ Fixed 1 issue and continued execution
```

### More Auto-Heals

| Your Code | Auto-Fixed To |
|-----------|---------------|
| `if x = 5` | `if x == 5` |
| `say Hello` | `say "Hello"` |
| `button myBtn` | `create button "myBtn"` |
| `listen to mic` | `listen to mic ->` |
| `"unclosed string` | `"unclosed string"` |

---

## 📦 Ghost Dependencies

Just use a module - Sykus installs it automatically:

```sykus
use speech        # Installs SpeechRecognition, pyaudio
use tts           # Installs pyttsx3
use gemini        # Installs google-generativeai
use face_recognition  # Installs face-recognition, opencv
use http          # Installs requests
```

---

## 🎯 JARVIS Example

See `examples/jarvis.syk` for a complete AI voice assistant:

```sykus
ai JARVIS

use speech
use gemini

Agent jarvis = use Gemini(key="YOUR_KEY")

jarvis.listen() ->
    if hear "hello" then
        jarvis.speak("Hello, Sir!")
    
    if hear "time" then
        async ->
            data = fetch "http://worldtimeapi.org/api/ip" save to result
            jarvis.speak("Time is " + result.datetime)
    
    if hear "goodbye" then
        jarvis.speak("Goodbye!")
        stop
```

---

## 📁 Directory Structure

```
sykus-final/
├── cli/
│   └── syk_cli.py          # Main CLI entry point
├── core/
│   └── syntax.py           # Syntax parser
├── engine/
│   └── syk_engine.py       # Core transpiler
├── ghost/
│   └── dependency_manager.py  # Auto-install deps
├── state/
│   └── smart_memory.py     # Smart database
├── healer/
│   └── auto_healer.py      # Error healing
├── bridge/
│   └── polyglot.py         # Native code embedding
├── examples/
│   └── jarvis.syk          # Ultimate test script
└── README.md               # This file
```

---

## 🔧 Requirements

- Python 3.8+
- Linux/Termux/macOS

Optional (auto-installed when used):
- Node.js (for JavaScript blocks)
- Kotlin (for Kotlin blocks)

---

## 🤝 Contributing

Contributions welcome! Areas to help:
- More language targets (Rust, Go, etc.)
- More auto-heal patterns
- VS Code extension
- Documentation

---

## 📄 License

MIT License - See LICENSE file

---

**Sykus** - *Code like you talk. Fix like magic.* 🚀
