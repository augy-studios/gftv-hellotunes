# HelloTunes - GFTV's Music Bot

A feature-rich Discord music bot built with Discord.js and Lavalink, featuring slash commands for seamless music playback.

## Features

- 🎵 Play music from YouTube, Spotify, SoundCloud, and more
- ⚡ Modern slash commands interface
- 📜 Queue management system
- 🎚️ Volume control
- ⏯️ Playback controls (pause, resume, skip, stop)
- 🔄 Auto-reconnect and error handling
- 🎨 Rich embed messages

## Commands

| Command | Description |
|---------|-------------|
| `/play <query>` | Play a song from URL or search query |
| `/pause` | Pause the current song |
| `/resume` | Resume playback |
| `/skip` | Skip the current song |
| `/stop` | Stop playback and clear the queue |
| `/queue` | Display the current queue |
| `/nowplaying` | Show currently playing song |
| `/volume <0-100>` | Adjust playback volume |

## Prerequisites

Before running the bot, you need:

1. **Node.js** (v18.0.0 or higher)
2. **Discord Bot Token** from [Discord Developer Portal](https://discord.com/developers/applications)
3. **Lavalink Server** - Download from [Lavalink Releases](https://github.com/lavalink-devs/Lavalink/releases)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/augy-studios/gftv-hellotunes.git
cd gftv-hellotunes
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Edit `.env` with your configuration:
```env
DISCORD_TOKEN=your_discord_bot_token_here
CLIENT_ID=your_discord_application_client_id_here
GUILD_ID=your_guild_id_for_testing_here

LAVALINK_HOST=localhost
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass
```

## Setting up Lavalink

1. Download Lavalink.jar from [GitHub Releases](https://github.com/lavalink-devs/Lavalink/releases)

2. Create an `application.yml` file:
```yaml
server:
  port: 2333
  address: 0.0.0.0

lavalink:
  server:
    password: "youshallnotpass"
    sources:
      youtube: true
      bandcamp: true
      soundcloud: true
      twitch: true
      vimeo: true
      http: true
      local: false
    bufferDurationMs: 400
    frameBufferDurationMs: 5000
    youtubePlaylistLoadLimit: 6
    playerUpdateInterval: 5
    youtubeSearchEnabled: true
    soundcloudSearchEnabled: true
    gc-warnings: true

metrics:
  prometheus:
    enabled: false
    endpoint: /metrics

sentry:
  dsn: ""
  environment: ""

logging:
  file:
    path: ./logs/

  level:
    root: INFO
    lavalink: INFO
```

3. Run Lavalink:
```bash
java -jar Lavalink.jar
```

## Running the Bot

1. Deploy slash commands (required first time and after command changes):
```bash
npm run deploy
```

2. Start the bot:
```bash
npm start
```

## Configuration

Edit `config.json` to customize bot behavior:

```json
{
  "defaultVolume": 100,
  "maxQueueSize": 100,
  "leaveOnEmpty": true,
  "leaveOnEmptyCooldown": 300000,
  "leaveOnEnd": true,
  "leaveOnEndCooldown": 300000
}
```

## Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Enable these Privileged Gateway Intents:
   - Server Members Intent (optional)
   - Message Content Intent (optional)
5. Copy the bot token to your `.env` file
6. Go to OAuth2 → URL Generator
7. Select scopes: `bot` and `applications.commands`
8. Select permissions: `Connect`, `Speak`, `Use Voice Activity`
9. Use the generated URL to invite the bot to your server

## Development

### Project Structure
```
gftv-hellotunes/
├── src/
│   ├── commands/       # Slash command files
│   ├── events/         # Event handlers
│   ├── utils/          # Utility functions
│   ├── index.js        # Main bot file
│   └── deploy-commands.js
├── config.json         # Bot configuration
├── .env               # Environment variables
└── package.json
```

### Adding New Commands

1. Create a new file in `src/commands/`
2. Use this template:
```javascript
const { SlashCommandBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('commandname')
        .setDescription('Command description'),
    async execute(interaction, client) {
        // Command logic here
    },
};
```
3. Run `npm run deploy` to register the command

## Troubleshooting

### Bot not responding to commands
- Make sure you've run `npm run deploy` to register slash commands
- Check that the bot has proper permissions in your server
- Verify your bot token is correct in `.env`

### Music not playing
- Ensure Lavalink server is running
- Check Lavalink connection settings in `.env`
- Verify the bot has permission to join and speak in voice channels

### "No results found" error
- Check your internet connection
- Verify Lavalink is configured correctly
- Try using a direct URL instead of search query

## License

This project is licensed under the ISC License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/augy-studios/gftv-hellotunes/issues) page.

## Credits

Built with:
- [Discord.js](https://discord.js.org/)
- [Lavalink](https://github.com/lavalink-devs/Lavalink)
- [lavalink-client](https://www.npmjs.com/package/lavalink-client)
