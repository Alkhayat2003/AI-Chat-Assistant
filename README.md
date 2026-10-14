# AI Chat Assistant

A Python chat application with two interfaces: an interactive command-line interface and a Tkinter graphical interface. It connects to a local server that supports the OpenAI API, such as LM Studio.

## Features

- Switch between models configured in the application.
- Save and load conversations as JSON files.
- Interactive terminal and graphical user interfaces.
- Configurable server URL, model, and message limits.
- Retry handling for failed requests and request rate limiting.

## Requirements

- Python 3.8 or later.
- LM Studio or another local server compatible with the OpenAI API.
- Tkinter for the graphical interface. It is usually included with Python on Windows and macOS; Linux may require installing a separate Tkinter package.

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone <repository-url>
cd <project-directory>
```

Create a virtual environment and install the dependencies. On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Configure the Server

1. Start a local server in LM Studio and load the model you want to use.
2. Enable LM Studio's local server with OpenAI API compatibility. The application defaults to `http://127.0.0.1:1234/v1/chat/completions`.
3. Edit `config/config.json` as needed. The names in `models.available` and `models.default` must match model names accepted by your server.
4. Make sure the default model is included in the available models list.

The server URL, timeout, default model, chat parameters, security limits, and UI settings can all be changed in `config/config.json`.

## Run the Application

Start the terminal interface:

```bash
python app.py
```

Or start the graphical interface:

```bash
python app.py --gui
```

On Windows, you can use `py` instead of `python`.

Terminal commands:

- `model <name>` switches to an available model.
- `save` saves the current conversation.
- `exit`, `quit`, or `q` exits and saves the conversation.

## Project Structure

```text
app.py                 Application entry point
ai_model/model.py      Model server communication and conversation handling
config/config.json     Application settings
config/messages.json   UI messages
ui/terminal.py         Command-line interface
ui/gui.py              Tkinter graphical interface
requirements.txt       Python dependencies
```

## Privacy

Conversations are saved locally in `conversation.json`. This file is excluded from Git through `.gitignore` to help prevent chat history from being uploaded to the repository accidentally.

## License

No license has been selected for this project yet. Add a `LICENSE` file with your chosen license before publishing if you want to grant others permission to use, modify, or distribute the project.