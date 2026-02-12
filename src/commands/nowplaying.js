const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const { createNowPlayingEmbed } = require('../utils/musicUtils');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('nowplaying')
        .setDescription('Show the currently playing song'),
    async execute(interaction, client) {
        const player = client.lavalink.getPlayer(interaction.guild.id);

        if (!player || !player.queue.current) {
            return await interaction.reply({ 
                content: '❌ Nothing is currently playing!', 
                ephemeral: true 
            });
        }

        const track = player.queue.current;
        const embed = createNowPlayingEmbed(track);

        await interaction.reply({ embeds: [embed] });
    },
};
