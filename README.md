# 🎵 Hello Tunes Music Bot

A powerful Discord music bot written in Python, powered by Lavalink. Based on the popular [Lavamusic](https://github.com/botxlab/lavamusic) bot, rewritten for Python environments.

## ✨ Features

### 🎵 Music Playback
- Play from YouTube, Spotify, SoundCloud, and more (via Lavalink plugins)
- High-quality, lag-free audio streaming
- Queue management with shuffle, loop, and skip controls
- Now playing display with progress bar

### 🎛️ Audio Filters
- **Bass Boost** - Enhance the bass (5 levels)
- **Nightcore** - Faster + higher pitch
- **Vaporwave** - Slower + lower pitch
- **Karaoke** - Reduce vocals
- **Tremolo** - Wavering volume
- **Vibrato** - Wavering pitch
- **8D Rotation** - Audio rotates around your head
- **Low Pass** - Muffled sound effect
- **Speed/Pitch** - Adjust playback speed and pitch

### 📂 Playlist System
- Create, save, and manage personal playlists
- Add tracks from currently playing or by search
- Load playlists directly into the queue

### ⚙️ Server Configuration
- Custom prefix per server
- Multiple language support
- DJ role system with DJ-only mode
- 24/7 mode (stay connected)
- Default volume settings

## 📋 Requirements

- Python 3.10+
- Lavalink server (v4.x)
- Discord Bot Token

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/gftv-hellotunes.git
cd gftv-hellotunes
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- `TOKEN` - Your Discord bot token
- `CLIENT_ID` - Your bot's client ID
- `OWNER_IDS` - Your Discord user ID(s)
- `LAVALINK_*` - Your Lavalink server settings

### 5. Setup Lavalink

Ensure your Lavalink server is running. If you're using Augy's VPS-2:
- Lavalink should already be configured as a service
- Default settings: `localhost:2333` with password `youshallnotpass`

### 6. Run the Bot

```bash
python main.py
```

## 📁 Project Structure

```
gftv-hellotunes/
├── main.py                 # Bot entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── README.md              # This file
│
├── cogs/                  # Command modules
│   ├── __init__.py
│   ├── music.py           # Core music commands
│   ├── filters.py         # Audio filter commands
│   ├── playlists.py       # Playlist management
│   ├── settings.py        # Server configuration
│   └── info.py            # Info & utility commands
│
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── helpers.py         # Helper functions
│   └── logger.py          # Logging setup
│
├── database/              # Database modules
│   ├── __init__.py
│   └── database.py        # SQLite async database
│
├── data/                  # Data storage (created at runtime)
│   └── uwutunes.db        # SQLite database
│
└── logs/                  # Log files (created at runtime)
    └── bot_YYYY-MM-DD.log
```

## 🎮 Commands

### Music
| Command | Description |
|---------|-------------|
| `/play <query>` | Play a song or add to queue |
| `/pause` | Pause playback |
| `/resume` | Resume playback |
| `/skip` | Skip current track |
| `/stop` | Stop and clear queue |
| `/disconnect` | Leave voice channel |

### Queue
| Command | Description |
|---------|-------------|
| `/queue` | View current queue |
| `/nowplaying` | Show current track |
| `/shuffle` | Shuffle the queue |
| `/loop [mode]` | Toggle loop mode |
| `/volume <0-150>` | Set volume |
| `/seek <position>` | Seek to position |
| `/remove <position>` | Remove from queue |
| `/clear` | Clear the queue |

### Filters
| Command | Description |
|---------|-------------|
| `/bassboost [level]` | Bass boost (0-5) |
| `/nightcore` | Nightcore effect |
| `/vaporwave` | Vaporwave effect |
| `/karaoke` | Reduce vocals |
| `/rotation [speed]` | 8D audio effect |
| `/resetfilters` | Reset all filters |

### Playlists
| Command | Description |
|---------|-------------|
| `/playlist create` | Create new playlist |
| `/playlist delete <name>` | Delete playlist |
| `/playlist view <name>` | View playlist |
| `/playlist add <name>` | Add current song |
| `/playlist load <name>` | Load into queue |
| `/playlist list` | List your playlists |

### Settings
| Command | Description |
|---------|-------------|
| `/prefix <prefix>` | Set server prefix |
| `/language <lang>` | Set language |
| `/247` | Toggle 24/7 mode |
| `/dj add/remove <role>` | Manage DJ roles |
| `/defaultvolume <vol>` | Set default volume |
| `/settings` | View all settings |

## 🔧 Lavalink Plugins

For extended platform support, add these plugins to your Lavalink server:

- **[LavaSrc](https://github.com/topi314/LavaSrc)** - Spotify, Deezer, Apple Music
- **[youtube-source](https://github.com/lavalink-devs/youtube-source)** - YouTube support
- **[SponsorBlock](https://github.com/topi314/Sponsorblock-Plugin)** - Skip sponsors

## 🐳 Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## 📝 License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

## 🙏 Credits

- Based on [Lavamusic](https://github.com/botxlab/lavamusic) by BotxLab
- Powered by [Wavelink](https://github.com/PythonistaGuild/Wavelink)
- Built with [discord.py](https://github.com/Rapptz/discord.py)

---

Made with ❤️ by Augy
