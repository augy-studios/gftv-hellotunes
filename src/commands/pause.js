const { SlashCommandBuilder } = require('discord.js');
const { checkVoiceChannel } = require('../utils/musicUtils');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('pause')
        .setDescription('Pause the current song'),
    async execute(interaction, client) {
        const player = client.lavalink.getPlayer(interaction.guild.id);

        if (!player || !player.queue.current) {
            return await interaction.reply({ 
                content: '❌ Nothing is currently playing!', 
                ephemeral: true 
            });
        }

        const check = checkVoiceChannel(interaction, player);
        if (!check.valid) {
            return await interaction.reply({ 
                content: `❌ ${check.message}`, 
                ephemeral: true 
            });
        }

        if (player.paused) {
            return await interaction.reply({ 
                content: '⏸️ The player is already paused!', 
                ephemeral: true 
            });
        }

        await player.pause();
        await interaction.reply({ content: '⏸️ Paused the player!' });
    },
};
