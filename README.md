# Omen

A self-hosted personal AI assistant for Windows. It runs a local language model through [Ollama](https://ollama.com), shows a small animated orb in your browser, and lets you control your own PC from your phone.

> **Status: personal project, v0.1.** Built with AI assistance (Claude) and tested on one machine. It has not been security-audited. Do not expose it to the open internet. See [Security](#security-and-limits).

<!-- TODO: add a short demo GIF or screenshots in docs/ (blur your PIN, hostname, files, and any camera images) -->

## What it does

- **Chat** with a local model (default `qwen2.5:7b`), streamed to a web page with an orb that thinks and talks.
- **Voice**: tap Talk to speak and hear replies, using your browser's built-in speech features.
- **Reports**: ask for a report as a background task. Omen searches the web, writes it, saves it, and sends a phone notification. View it as a page or download it as Word or Markdown.
- **Files**: list folders, search file names, read small text files, and send a file to your phone.
- **Apps**: open and close installed apps and File Explorer windows, from a tap-to-use panel or by typing.
- **Reminders and notes**: phone reminders ("remind me in 30 minutes to...") and a small notes memory.
- **Camera (off by default)**: one photo on request, or an overnight watch that alerts your phone when it sees motion.

Risky actions (opening or closing things, sending files, using the camera) always show an **Approve / Deny** card first. Simple commands like `open notepad` skip the model, so they are instant.

## How it works

```
Phone or browser  --(Tailscale, PIN login)-->  Omen (FastAPI, Python)  -->  Ollama (local LLM)
                                                   |
            tools: files | apps | reminders | web search | reports | camera (optional)
```

The server listens on `127.0.0.1` only. For phone access, [Tailscale](https://tailscale.com) publishes it privately to your own devices, so no router ports are opened.

## Requirements

- Windows 10 or 11 (it uses PowerShell, `taskkill`, and `os.startfile`)
- Python 3.12
- [Ollama](https://ollama.com) with a tool-capable model, for example `ollama pull qwen2.5:7b`
- A GPU is recommended. Measured on a GTX 1660 Ti (6 GB) with `qwen2.5:7b`: about 25 tokens per second, replies start in under a second once the prompt is cached, and tool-using requests take roughly 4 to 8 seconds.

## Install

```powershell
git clone https://github.com/arabskimedvit/omen-assistant.git
cd omen-assistant
pip install -r requirements.txt
ollama pull qwen2.5:7b
python omen.py
```

Open http://localhost:8000. On the first run, Omen creates `config.json` in its data folder (`%USERPROFILE%\Omen`, or the folder given by `--home` or the `OMEN_HOME` variable) with a random 6-digit PIN. Read the PIN from that file.

### Use it from your phone

1. Install Tailscale on the PC and the phone and sign in to the same account.
2. Publish Omen to your private network: `tailscale serve --bg 8000`
3. Open the address it prints in Safari or Chrome on the phone and enter your PIN.
4. Optional: install the [ntfy](https://ntfy.sh) app, subscribe to a long random topic, and put it in `config.json` as `ntfy_topic` for notifications.

### Start it at login (optional)

Register a scheduled task that runs `pythonw.exe omen.py --home <your data folder>` at logon.

## Configuration

Settings live in `config.json` inside the data folder. See `config.example.json`.

| Setting | Meaning |
|---|---|
| `name` | Display name |
| `model` | Ollama model, for example `qwen2.5:3b` for more speed |
| `keep_alive` | How long the model stays loaded in memory |
| `pin` | Login PIN (generated on first run) |
| `ntfy_topic` | Private ntfy topic for phone notifications |
| `public_url` | Your Tailscale address, so notifications open the right page |
| `lang` | Speech language, for example `en-US` or `ar-JO` |
| `apps` | Extra apps: `{"name": ["launch.exe", "Process.exe"]}` |
| `features.camera` | `true` to enable the camera tools (off by default) |

## Security and limits

- **Approval cards** guard every risky action. Typing "approved" in chat does nothing.
- **Login:** PIN with random, revocable session tokens, growing lockouts after wrong tries, and a Log out button. The PIN is stored in plain text in your local `config.json`, so keep that file private.
- **Blocked areas:** Windows, Program Files, `AppData`, key folders, and Omen's own settings can't be read or sent. Password and key files can't be sent. PowerShell, terminals, remote-control tools, Python, and Ollama can't be opened or closed from Omen.
- **Everything is logged** to `logs/actions.log` in the data folder.
- **Prompt injection is a real risk.** Small models can be fooled by text in web pages or files. That is why risky actions need your approval, but read each card before you tap.
- **Small models make mistakes.** A 7B model sometimes picks the wrong tool or invents details. Check what it tells you, especially report facts.
- **What leaves your PC:** web search queries (a DuckDuckGo library), ntfy notification text (through ntfy.sh unless you host your own), and voice, which your browser may send to Apple or Google for recognition.
- **Camera:** only use it where you are allowed to, and tell anyone who may be recorded. Recording people without their knowledge is illegal in many places.
- Windows only for now. Web search uses an unofficial library and may break.

## Roadmap

- Live camera view and email drafting (drafts only, with approval)
- Split the code into modules and add automated tests
- A plugin system for tools and a settings screen
- Fully local speech (Whisper and Piper) as an option

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgements

[Ollama](https://ollama.com), [Qwen](https://github.com/QwenLM/Qwen2.5), [FastAPI](https://fastapi.tiangolo.com), [Tailscale](https://tailscale.com), [ntfy](https://ntfy.sh), [OpenCV](https://opencv.org), and [python-docx](https://python-docx.readthedocs.io). Check each model's own license before use.
