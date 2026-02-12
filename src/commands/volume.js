const { SlashCommandBuilder } = require('discord.js');
const { checkVoiceChannel } = require('../utils/musicUtils');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('volume')
        .setDescription('Adjust the player volume')
        .addIntegerOption(option =>
            option.setName('level')
                .setDescription('Volume level (0-100)')
                .setRequired(true)
                .setMinValue(0)
                .setMaxValue(100)),
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

        const volume = interaction.options.getInteger('level');
        await player.setVolume(volume);

        await interaction.reply({ 
            content: `🔊 Volume set to **${volume}%**` 
        });
    },
};
