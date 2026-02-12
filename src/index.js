require('dotenv').config();
const { Client, Collection, GatewayIntentBits } = require('discord.js');
const { LavalinkManager } = require('lavalink-client');
const fs = require('fs');
const path = require('path');

// Create Discord client
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildVoiceStates,
        GatewayIntentBits.GuildMessages,
    ],
});

// Initialize commands collection
client.commands = new Collection();

// Load command files
const commandsPath = path.join(__dirname, 'commands');
const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));

for (const file of commandFiles) {
    const filePath = path.join(commandsPath, file);
    const command = require(filePath);
    if ('data' in command && 'execute' in command) {
        client.commands.set(command.data.name, command);
        console.log(`[INFO] Loaded command: ${command.data.name}`);
    } else {
        console.log(`[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`);
    }
}

// Initialize Lavalink Manager
client.lavalink = new LavalinkManager({
    nodes: [
        {
            authorization: process.env.LAVALINK_PASSWORD || 'youshallnotpass',
            host: process.env.LAVALINK_HOST || 'localhost',
            port: parseInt(process.env.LAVALINK_PORT) || 2333,
            id: 'main_node',
        },
    ],
    sendToShard: (guildId, payload) => client.guilds.cache.get(guildId)?.shard?.send(payload),
    client: {
        id: process.env.CLIENT_ID,
        username: 'HelloTunes',
    },
    autoSkip: true,
    playerOptions: {
        defaultSearchPlatform: 'ytsearch',
        volumeDecrementer: 0.75,
        onDisconnect: {
            autoReconnect: true,
            destroyPlayer: false,
        },
        onEmptyQueue: {
            destroyAfterMs: 300000,
        },
    },
});

// Load event files
const eventsPath = path.join(__dirname, 'events');
const eventFiles = fs.readdirSync(eventsPath).filter(file => file.endsWith('.js'));

for (const file of eventFiles) {
    const filePath = path.join(eventsPath, file);
    const event = require(filePath);
    if (event.once) {
        client.once(event.name, (...args) => event.execute(...args, client));
    } else {
        client.on(event.name, (...args) => event.execute(...args, client));
    }
    console.log(`[INFO] Loaded event: ${event.name}`);
}

// Error handling
process.on('unhandledRejection', error => {
    console.error('Unhandled promise rejection:', error);
});

// Login to Discord
client.login(process.env.DISCORD_TOKEN).catch(error => {
    console.error('Failed to login:', error);
    process.exit(1);
});
