/**
 * Get or create a player for a guild
 * @param {Object} client - Discord client
 * @param {Object} interaction - Discord interaction
 * @returns {Object} Player instance
 */
async function getPlayer(client, interaction) {
    let player = client.lavalink.getPlayer(interaction.guild.id);
    
    if (!player) {
        const voiceChannel = interaction.member.voice.channel;
        
        if (!voiceChannel) {
            throw new Error('You need to be in a voice channel!');
        }

        player = await client.lavalink.createPlayer({
            guildId: interaction.guild.id,
            voiceChannelId: voiceChannel.id,
            textChannelId: interaction.channel.id,
            selfDeaf: true,
            selfMute: false,
            volume: 100,
        });
    }
    
    return player;
}

/**
 * Check if user is in the same voice channel as the bot
 * @param {Object} interaction - Discord interaction
 * @param {Object} player - Lavalink player
 * @returns {Boolean}
 */
function checkVoiceChannel(interaction, player) {
    const memberChannel = interaction.member.voice.channel;
    const botChannel = interaction.guild.channels.cache.get(player.voiceChannelId);
    
    if (!memberChannel) {
        return { valid: false, message: 'You need to be in a voice channel!' };
    }
    
    if (botChannel && memberChannel.id !== botChannel.id) {
        return { valid: false, message: 'You need to be in the same voice channel as the bot!' };
    }
    
    return { valid: true };
}

/**
 * Format duration from milliseconds to mm:ss
 * @param {Number} ms - Duration in milliseconds
 * @returns {String}
 */
function formatDuration(ms) {
    const seconds = Math.floor((ms / 1000) % 60);
    const minutes = Math.floor((ms / (1000 * 60)) % 60);
    const hours = Math.floor(ms / (1000 * 60 * 60));
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

/**
 * Create an embed for now playing
 * @param {Object} track - Track object
 * @returns {Object} Embed object
 */
function createNowPlayingEmbed(track) {
    return {
        color: 0x0099ff,
        title: '🎵 Now Playing',
        description: `**[${track.info.title}](${track.info.uri})**`,
        fields: [
            {
                name: 'Author',
                value: track.info.author,
                inline: true,
            },
            {
                name: 'Duration',
                value: track.info.isStream ? '🔴 LIVE' : formatDuration(track.info.duration),
                inline: true,
            },
        ],
        thumbnail: {
            url: track.info.artworkUrl || 'https://via.placeholder.com/300',
        },
        timestamp: new Date().toISOString(),
    };
}

module.exports = {
    getPlayer,
    checkVoiceChannel,
    formatDuration,
    createNowPlayingEmbed,
};
