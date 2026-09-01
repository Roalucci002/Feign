# SearXNG Setup Instructions

## Docker (Recommended)

```bash
docker run -d -p 8888:8080 searxng/searxng
```

## Local Installation

### Linux/macOS

```bash
git clone https://github.com/searxng/searxng.git
cd searxng
python -m pip install -r requirements.txt
python -m searx.webapp
```

### Windows

1. Install Python 3.10+
2. Clone: `git clone https://github.com/searxng/searxng.git`
3. Install requirements: `pip install -r requirements.txt`
4. Run: `python -m searx.webapp`

## Configuration

Edit `config.json` to set:
- Port: 8888
- Language: Japanese (ja)
- Safe search: moderate

## Verify Installation

```bash
curl "http://localhost:8888/search?q=test&format=json"
```

You should see JSON search results.
