const { SlashCommandBuilder } = require('discord.js');
const { getPlayer, createNowPlayingEmbed } = require('../utils/musicUtils');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('play')
        .setDescription('Play a song from YouTube or other sources')
        .addStringOption(option =>
            option.setName('query')
                .setDescription('Song name or URL')
                .setRequired(true)),
    async execute(interaction, client) {
        await interaction.deferReply();

        try {
            // Check if user is in a voice channel
            const voiceChannel = interaction.member.voice.channel;
            if (!voiceChannel) {
                return await interaction.editReply({ content: '❌ You need to be in a voice channel!' });
            }

            // Get or create player
            const player = await getPlayer(client, interaction);
            
            const query = interaction.options.getString('query');
            
            // Search for the track
            const result = await player.search({ query }, interaction.user);
            
            if (!result || !result.tracks || result.tracks.length === 0) {
                return await interaction.editReply({ content: '❌ No results found!' });
            }

            // Add track(s) to queue
            if (result.loadType === 'playlist') {
                for (const track of result.tracks) {
                    player.queue.add(track);
                }
                
                await interaction.editReply({
                    content: `✅ Added **${result.tracks.length}** tracks from playlist **${result.playlistInfo.name}** to the queue!`,
                });
            } else {
                const track = result.tracks[0];
                player.queue.add(track);
                
                if (player.playing) {
                    await interaction.editReply({
                        content: `✅ Added to queue: **${track.info.title}**`,
                    });
                } else {
                    await interaction.editReply({
                        embeds: [createNowPlayingEmbed(track)],
                    });
                }
            }

            // Start playing if not already playing
            if (!player.playing) {
                await player.play();
            }

        } catch (error) {
            console.error('[ERROR] Play command error:', error);
            await interaction.editReply({ 
                content: `❌ An error occurred: ${error.message}` 
            });
        }
    },
};
