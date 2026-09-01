# Ollama Setup Instructions

## Windows

1. Download Ollama from https://ollama.ai/download/windows
2. Run the installer
3. Open Command Prompt and run:
   ```bash
   ollama pull mistral
   ```
4. Ollama will start automatically in the system tray

## macOS

1. Download Ollama from https://ollama.ai/download/mac
2. Run the installer
3. Open Terminal and run:
   ```bash
   ollama pull mistral
   ```

## Linux

```bash
curl https://ollama.ai/install.sh | sh
ollama pull mistral
ollama serve
```

## Verify Installation

Test Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

You should see a JSON response with available models.
