module.exports = {
    name: 'ready',
    once: true,
    async execute(client) {
        console.log(`[INFO] Logged in as ${client.user.tag}`);
        console.log(`[INFO] Bot is ready and serving ${client.guilds.cache.size} guilds`);
        
        // Initialize Lavalink
        client.lavalink.init(client.user.id);
        console.log('[INFO] Lavalink manager initialized');
    },
};
