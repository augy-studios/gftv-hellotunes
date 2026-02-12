const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const { formatDuration } = require('../utils/musicUtils');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('queue')
        .setDescription('Display the current song queue'),
    async execute(interaction, client) {
        const player = client.lavalink.getPlayer(interaction.guild.id);

        if (!player || !player.queue.current) {
            return await interaction.reply({ 
                content: '❌ Nothing is currently playing!', 
                ephemeral: true 
            });
        }

        const current = player.queue.current;
        const queue = player.queue.tracks;

        const embed = new EmbedBuilder()
            .setColor(0x0099ff)
            .setTitle('🎵 Music Queue')
            .setDescription(`**Now Playing:**\n[${current.info.title}](${current.info.uri}) - ${current.info.isStream ? '🔴 LIVE' : formatDuration(current.info.duration)}`);

        if (queue.length > 0) {
            const queueList = queue.slice(0, 10).map((track, index) => {
                return `${index + 1}. [${track.info.title}](${track.info.uri}) - ${track.info.isStream ? '🔴 LIVE' : formatDuration(track.info.duration)}`;
            }).join('\n');

            embed.addFields({ 
                name: `Up Next (${queue.length} songs)`, 
                value: queueList 
            });

            if (queue.length > 10) {
                embed.setFooter({ text: `And ${queue.length - 10} more...` });
            }
        } else {
            embed.addFields({ 
                name: 'Up Next', 
                value: 'No songs in queue' 
            });
        }

        await interaction.reply({ embeds: [embed] });
    },
};
