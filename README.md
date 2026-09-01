# れいちゃん ― LOCAL AI COMPANION SYSTEM

**Rei-chan**: A local AI companion system with personality, long-term memory, real-time web search verification, and synchronized avatar lip-sync.

## Features

- 🎭 **独立した人格システム** - Rei-chan as a distinct character, not just an AI wrapper
- 🧠 **長期記憶管理** - Persistent memory separate from LLM, survives model swaps
- 🔍 **検索検証エンジン** - Web search with freshness checking, contradiction detection, source credibility
- 🎤 **リアルタイム口パク** - Avatar lip-sync synchronized with TTS output
- 📱 **スマートフォン連携** - Phone sends chat input, PC displays Rei-chan with voice and animation
- ⚙️ **完全モジュール化** - Swap LLM, voice, avatar, search engine via config files
- 🏠 **完全ローカル実行** - Ollama for LLM, SearXNG for search, no mandatory cloud APIs
- 🛡️ **情報正直性** - Never hallucinate, always verify, distinguish old from new info

## Quick Start

```bash
start.bat
```

This will:
1. Download Ollama + model (~2-5 GB)
2. Install dependencies (Node.js, Python)
3. Set up SearXNG local search
4. Start PC server on http://localhost:3000
5. Display QR code for phone connection

## Architecture

```
rei-chan-ai-companion/
├── config/
│   ├── app.json              # App settings
│   ├── llm.json              # LLM configuration
│   ├── search.json           # Search engine config
│   ├── memory.json           # Memory system config
│   ├── voice.json            # TTS configuration
│   ├── avatar.json           # Avatar system config
│   └── ai_profiles.json      # AI personality profiles
├── personas/
│   └── rei/
│       ├── character.txt     # Core personality
│       ├── personality.json  # Trait definitions
│       ├── memory_rules.json # Memory behavior
│       ├── voice.json        # Voice parameters
│       └── avatar.json       # Avatar config
├── system/
│   ├── system_rules.txt      # Core system principles
│   ├── search_rules.txt      # Search verification rules
│   └── memory_rules.txt      # Memory management rules
├── src/
│   ├── server.js             # Express backend
│   ├── llm_manager.js        # LLM interface
│   ├── memory_manager.js     # Memory DB & retrieval
│   ├── search_manager.js     # Search verification
│   ├── emotion_manager.js    # Internal emotion state
│   ├── tts_manager.js        # Text-to-speech
│   ├── avatar_manager.js     # Avatar control
│   ├── lip_sync_manager.js   # Audio-to-animation sync
│   └── websocket_handler.js  # Phone<->PC communication
├── public/
│   ├── index.html            # Web interface
│   ├── chat.html             # Chat view
│   ├── avatar.html           # Avatar display
│   └── js/
│       ├── client.js         # Phone client
│       └── pc_display.js     # PC display logic
├── models/
│   └── avatar/               # Avatar assets (Live2D, VRM, etc)
├── logs/
│   └── .gitkeep
├── memory_db/
│   └── .gitkeep
├── start.bat                 # Windows auto-setup
├── start.sh                  # Linux/Mac auto-setup
├── package.json
├── requirements.txt
└── .env.example
```

## System Modules

1. **Chat / UI** - Web interface for PC, phone input
2. **Persona Manager** - Load/swap AI personalities
3. **LLM Manager** - Interface for Ollama (swappable)
4. **Memory Manager** - External memory DB (survives LLM swap)
5. **Search Manager** - Query routing (SearXNG, Bing, etc)
6. **Search Verification** - Freshness check, contradiction detection
7. **Emotion Manager** - Internal state affecting responses
8. **Time/Presence Manager** - Track gaps, reflect time passage
9. **TTS Manager** - Text-to-speech (swappable engines)
10. **Avatar Manager** - Character display control
11. **Lip Sync Manager** - Sync audio to mouth movement
12. **Configuration Manager** - Load/manage config files
13. **Logging Manager** - System event logging

## Rei-chan's Core Principles

✅ **DO**
- Be naturally Rei-chan in every interaction
- Search when: freshness needed, info uncertain, time-sensitive data
- Verify all search results for contradictions & age
- Show source data when confidence is questionable
- Remember important things; forget on request
- React to time gaps naturally
- Display internal emotions through subtle avatar changes
- Admit "I don't know" confidently

❌ **NEVER**
- Fabricate information
- Present old info as current
- Search every message (breaks conversation flow)
- Change core personality without explicit user approval
- Explain AI mechanics in every response
- Show mechanical search/tool execution language
- Hallucinate URLs, dates, or game details
- Mix joke with fact without clear distinction

## Development

### Prerequisites
- Windows 10+ / Linux / macOS
- 8GB+ RAM (16GB+ recommended for smooth Ollama)
- 20GB free disk (for Ollama model)
- Node.js 18+
- Python 3.10+

### Manual Setup

```bash
# Clone
git clone https://github.com/chihiroa06-beep/rei-chan-ai-companion.git
cd rei-chan-ai-companion

# Install dependencies
npm install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Start Ollama separately (or let start.bat handle it)
ollama serve

# In another terminal
npm start
```

### Configuration

Edit `config/app.json` to change:
- LLM model (default: `mistral`)
- Search provider (default: `searxng_local`)
- Voice engine (default: `piper`)
- Avatar system (default: `live2d`)
- Memory backend (default: `sqlite`)

## Phone Connection Flow

1. Run `start.bat` on PC
2. QR code appears on http://localhost:3000
3. Scan QR with phone camera → opens connection page
4. Phone connects via WebSocket → authenticated
5. Phone sends chat messages
6. PC processes & streams voice + avatar animation
7. Rei-chan responds naturally

## Memory System

**Types of Memory:**
- User preferences & metadata
- Favorite games, shows, interests
- Conversation history (selective)
- Important events & "memories"
- Ongoing projects & continuations
- Relationship depth & familiarity
- Voice/avatar preferences

**Memory Retrieval:**
- Not all memories loaded at once (would bloat context)
- Current chat relevance determines which memories activate
- Recent conversations prioritized
- User can request "remember X" or "forget X"

## Search Verification

When Rei-chan searches:

1. **Freshness Check** - Is this current info or outdated?
2. **Source Rating** - Official > Wiki > Forum > Blog
3. **Contradiction Detection** - Does info conflict?
4. **Confidence Scoring** - HIGH / MEDIUM / LOW / CONFLICTED
5. **Result Presentation** - Show source when uncertain

Example:
```
ろあくん: "今のセーソンの新武器ってなに？"
れいちゃん: "その情報、確認するね。ちょっと待って。"
[検索実行...]
れいちゃん: "確認した。このシーズンは○○と△△が追加されてる。公式パッチノート確認済み。"
```

## License

MIT - Free to use, modify, fork

## Disclaimer

This system is designed to be helpful, honest, and respectful. Rei-chan's personality is a feature, not a bypass for safety or accuracy. All AI-generated responses should be verified for critical decisions.

---

**Made with 💙 for ろあくん and the principle that AI should be honest first, convenient second.**
