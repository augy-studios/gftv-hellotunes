const { SlashCommandBuilder } = require('discord.js');
const { checkVoiceChannel } = require('../utils/musicUtils');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('stop')
        .setDescription('Stop playback and clear the queue'),
    async execute(interaction, client) {
        const player = client.lavalink.getPlayer(interaction.guild.id);

        if (!player) {
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

        player.queue.clear();
        await player.destroy();
        
        await interaction.reply({ content: '⏹️ Stopped playback and cleared the queue!' });
    },
};
