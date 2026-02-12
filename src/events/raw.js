module.exports = {
    name: 'raw',
    async execute(data, client) {
        // Forward raw events to Lavalink
        if (client.lavalink) {
            client.lavalink.updateVoiceState(data);
        }
    },
};
