# Piper TTS Setup Instructions

## Installation

### Windows

1. Download from: https://github.com/rhasspy/piper/releases
2. Extract to `C:\Program Files\piper`
3. Add to PATH
4. Download voice model:
   ```bash
   piper --download ja_JP-kokoro-v1.0.onnx
   ```

### macOS

```bash
brew install piper-phoneme-lookup
piper --download ja_JP-kokoro-v1.0.onnx
```

### Linux

```bash
sudo apt install piper
piper --download ja_JP-kokoro-v1.0.onnx
```

## Verify Installation

```bash
echo "こんにちは" | piper --model ja_JP-kokoro-v1.0.onnx --output-file test.wav
```

A `test.wav` file should be created.

## Voice Models

Other available Japanese voices:
- `ja_JP-kokoro-v1.0.onnx` (Recommended - high quality)
- Other voices available on Piper GitHub
