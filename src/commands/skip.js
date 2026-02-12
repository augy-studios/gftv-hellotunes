const { SlashCommandBuilder } = require('discord.js');
const { checkVoiceChannel } = require('../utils/musicUtils');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('skip')
        .setDescription('Skip the current song'),
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

        const current = player.queue.current;
        await player.skip();
        
        await interaction.reply({ 
            content: `⏭️ Skipped: **${current.info.title}**` 
        });
    },
};
