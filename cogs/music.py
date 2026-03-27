"""
Music Cog - Core music functionality.
Uses Wavelink for Lavalink integration.
"""

import logging
import wavelink
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Union, cast

from utils.helpers import (
    format_duration, create_progress_bar, get_source_emoji,
    truncate_string, is_url, LoopMode, EmbedBuilder
)

logger = logging.getLogger(__name__)


class MusicPlayerView(discord.ui.View):
    """Interactive player controls view."""

    def __init__(self, cog: "Music", timeout: float = 180):
        super().__init__(timeout=timeout)
        self.cog = cog

    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.secondary)
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Pause or resume playback."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return await interaction.response.send_message("No active player!", ephemeral=True)

        if player.paused:
            await player.pause(False)
            button.emoji = "⏸️"
            await interaction.response.send_message("▶️ Resumed!", ephemeral=True)
        else:
            await player.pause(True)
            button.emoji = "▶️"
            await interaction.response.send_message("⏸️ Paused!", ephemeral=True)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Skip current track."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return await interaction.response.send_message("No active player!", ephemeral=True)

        await player.skip()
        await interaction.response.send_message("⏭️ Skipped!", ephemeral=True)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Stop playback and disconnect."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return await interaction.response.send_message("No active player!", ephemeral=True)

        await player.disconnect()
        await interaction.response.send_message("⏹️ Stopped and disconnected!", ephemeral=True)

    @discord.ui.button(emoji="🔀", style=discord.ButtonStyle.secondary)
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Shuffle the queue."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return await interaction.response.send_message("No active player!", ephemeral=True)

        player.queue.shuffle()
        await interaction.response.send_message("🔀 Queue shuffled!", ephemeral=True)

    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary)
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle loop mode."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return await interaction.response.send_message("No active player!", ephemeral=True)

        # Cycle through loop modes
        if not hasattr(player, "loop_mode"):
            player.loop_mode = LoopMode.NONE

        player.loop_mode = (player.loop_mode + 1) % 3

        mode_str = LoopMode.to_string(player.loop_mode)
        await interaction.response.send_message(f"🔁 Loop mode: **{mode_str}**", ephemeral=True)


class Music(commands.Cog):
    """Music commands for playing and controlling music."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        """Called when the cog is loaded."""
        self._lavalink_connected = False

        if not self.bot.config.lavalink_nodes:
            logger.warning("No Lavalink nodes configured. Music commands will not work.")
            return

        # Setup Wavelink nodes
        nodes = []
        for node_config in self.bot.config.lavalink_nodes:
            node = wavelink.Node(
                uri=f"{'https' if node_config.secure else 'http'}://{node_config.host}:{node_config.port}",
                password=node_config.password,
                retries=0
            )
            nodes.append(node)

        try:
            await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=100)
            self._lavalink_connected = True
            logger.info(f"Connected to {len(nodes)} Lavalink node(s)")
        except Exception:
            logger.warning("Could not connect to Lavalink. Music commands will not be available.")

    async def cog_unload(self) -> None:
        """Called when the cog is unloaded."""
        if self._lavalink_connected:
            await wavelink.Pool.close()

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        """Event fired when a Lavalink node is ready."""
        logger.info(f"Lavalink node '{payload.node.identifier}' is ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        """Event fired when a track starts playing."""
        player: wavelink.Player = payload.player
        track: wavelink.Playable = payload.track

        # Get guild settings
        settings = await self.bot.db.get_guild_settings(player.guild.id)
        if settings and not settings.announce_songs:
            return

        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**[{truncate_string(track.title, 60)}]({track.uri})**",
            color=self.bot.config.color["main"]
        )
        embed.add_field(name="Duration", value=format_duration(track.length), inline=True)
        embed.add_field(name="Requested by", value=getattr(track, "requester", "Unknown"), inline=True)

        if track.artwork:
            embed.set_thumbnail(url=track.artwork)

        # Try to send to the channel
        if hasattr(player, "text_channel") and player.text_channel:
            try:
                await player.text_channel.send(embed=embed, view=MusicPlayerView(self))
            except discord.HTTPException:
                pass

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        """Event fired when a track ends."""
        player: wavelink.Player = payload.player

        # Handle loop modes
        if hasattr(player, "loop_mode"):
            if player.loop_mode == LoopMode.TRACK:
                # Replay the same track
                await player.play(payload.track)
                return
            elif player.loop_mode == LoopMode.QUEUE:
                # Add track back to end of queue
                player.queue.put(payload.track)

        # Play next track if available
        if player.queue:
            next_track = player.queue.get()
            await player.play(next_track)

    @commands.Cog.listener()
    async def on_wavelink_inactive_player(self, player: wavelink.Player) -> None:
        """Event fired when a player becomes inactive."""
        # Check if 24/7 mode is enabled
        settings = await self.bot.db.get_guild_settings(player.guild.id)
        if settings and settings.stay_connected:
            return

        await player.disconnect()
        if hasattr(player, "text_channel") and player.text_channel:
            try:
                await player.text_channel.send("👋 Disconnected due to inactivity.")
            except discord.HTTPException:
                pass

    # ============== Play Commands ==============

    async def _connect_player(self, interaction: discord.Interaction) -> Optional[wavelink.Player]:
        """Connect to the user's voice channel and return the player, or None on failure."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            try:
                player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
                player.text_channel = interaction.channel
                player.loop_mode = LoopMode.NONE

                settings = await self.bot.db.get_guild_settings(interaction.guild.id)
                if settings:
                    await player.set_volume(settings.default_volume)
            except Exception as e:
                await interaction.followup.send(f"❌ Could not connect: {e}")
                return None

        if player.channel.id != interaction.user.voice.channel.id:
            await interaction.followup.send("❌ You must be in the same voice channel as me!")
            return None

        return player

    async def _play_tracks(self, interaction: discord.Interaction, player: wavelink.Player, tracks: wavelink.Search) -> None:
        """Add tracks to the queue and send the appropriate embed."""
        if isinstance(tracks, wavelink.Playlist):
            for track in tracks.tracks:
                track.requester = interaction.user.mention
                player.queue.put(track)

            embed = discord.Embed(
                title="📋 Playlist Added",
                description=f"**{tracks.name}**\nAdded **{len(tracks.tracks)}** tracks to the queue!",
                color=self.bot.config.color["success"]
            )
        else:
            track = tracks[0]
            track.requester = interaction.user.mention

            if player.playing:
                player.queue.put(track)
                embed = discord.Embed(
                    title="📝 Added to Queue",
                    description=f"**[{truncate_string(track.title, 50)}]({track.uri})**",
                    color=self.bot.config.color["success"]
                )
                embed.add_field(name="Duration", value=format_duration(track.length), inline=True)
                embed.add_field(name="Position", value=f"#{len(player.queue)}", inline=True)
            else:
                await player.play(track)
                embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**[{truncate_string(track.title, 50)}]({track.uri})**",
                    color=self.bot.config.color["main"]
                )
                embed.add_field(name="Duration", value=format_duration(track.length), inline=True)

            if track.artwork:
                embed.set_thumbnail(url=track.artwork)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="play", description="Play a song or add it to the queue")
    @app_commands.describe(query="Song name or URL to play")
    async def play(self, interaction: discord.Interaction, query: str) -> None:
        """Play a song or add it to the queue. Searches SoundCloud by default."""
        if not interaction.user.voice:
            return await interaction.response.send_message(
                "❌ You must be in a voice channel!", ephemeral=True
            )

        await interaction.response.defer()

        player = await self._connect_player(interaction)
        if not player:
            return

        try:
            if is_url(query):
                tracks: wavelink.Search = await wavelink.Playable.search(query)
            else:
                tracks = await wavelink.Playable.search(
                    query, source=wavelink.TrackSource.SoundCloud
                )
                if not tracks:
                    tracks = await wavelink.Playable.search(
                        query, source=wavelink.TrackSource.YouTubeMusic
                    )
        except Exception as e:
            return await interaction.followup.send(f"❌ Search failed: {e}")

        if not tracks:
            return await interaction.followup.send("❌ No results found!")

        await self._play_tracks(interaction, player, tracks)

    @app_commands.command(name="youtube", description="Search and play a song from YouTube")
    @app_commands.describe(query="Song name to search on YouTube")
    async def youtube(self, interaction: discord.Interaction, query: str) -> None:
        """Search YouTube specifically and play the result."""
        if not interaction.user.voice:
            return await interaction.response.send_message(
                "❌ You must be in a voice channel!", ephemeral=True
            )

        await interaction.response.defer()

        player = await self._connect_player(interaction)
        if not player:
            return

        try:
            if is_url(query):
                tracks: wavelink.Search = await wavelink.Playable.search(query)
            else:
                tracks = await wavelink.Playable.search(
                    query, source=wavelink.TrackSource.YouTubeMusic
                )
                if not tracks:
                    tracks = await wavelink.Playable.search(
                        query, source=wavelink.TrackSource.YouTube
                    )
        except Exception as e:
            return await interaction.followup.send(f"❌ YouTube search failed: {e}")

        if not tracks:
            return await interaction.followup.send("❌ No results found on YouTube!")

        await self._play_tracks(interaction, player, tracks)

    @app_commands.command(name="pause", description="Pause the current song")
    async def pause(self, interaction: discord.Interaction) -> None:
        """Pause playback."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.playing:
            return await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)

        if player.paused:
            return await interaction.response.send_message("⏸️ Already paused!", ephemeral=True)

        await player.pause(True)
        await interaction.response.send_message("⏸️ Paused the music!")

    @app_commands.command(name="resume", description="Resume the paused song")
    async def resume(self, interaction: discord.Interaction) -> None:
        """Resume playback."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            return await interaction.response.send_message("❌ No active player!", ephemeral=True)

        if not player.paused:
            return await interaction.response.send_message("▶️ Already playing!", ephemeral=True)

        await player.pause(False)
        await interaction.response.send_message("▶️ Resumed the music!")

    @app_commands.command(name="skip", description="Skip the current song")
    async def skip(self, interaction: discord.Interaction) -> None:
        """Skip the current track."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.playing:
            return await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)

        await player.skip()
        await interaction.response.send_message("⏭️ Skipped!")

    @app_commands.command(name="stop", description="Stop playback, clear the queue, and disconnect")
    async def stop(self, interaction: discord.Interaction) -> None:
        """Stop playback, clear queue, and disconnect from voice channel."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            return await interaction.response.send_message("❌ Not connected!", ephemeral=True)

        player.queue.clear()
        await player.disconnect()
        await interaction.response.send_message("⏹️ Stopped and disconnected!")

    @app_commands.command(name="disconnect", description="Disconnect from voice channel")
    async def disconnect(self, interaction: discord.Interaction) -> None:
        """Disconnect from voice channel."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            return await interaction.response.send_message("❌ Not connected!", ephemeral=True)

        await player.disconnect()
        await interaction.response.send_message("👋 Disconnected!")

    # ============== Queue Commands ==============

    @app_commands.command(name="queue", description="View the current queue")
    async def queue(self, interaction: discord.Interaction) -> None:
        """View the current queue."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            return await interaction.response.send_message("❌ No active player!", ephemeral=True)

        embed = discord.Embed(
            title="📋 Music Queue",
            color=self.bot.config.color["main"]
        )

        # Current track
        if player.current:
            current = player.current
            progress = create_progress_bar(player.position, current.length)
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**[{truncate_string(current.title, 40)}]({current.uri})**\n"
                      f"{progress}\n"
                      f"`{format_duration(player.position)}` / `{format_duration(current.length)}`",
                inline=False
            )

        # Queue
        if player.queue:
            queue_list = []
            for i, track in enumerate(list(player.queue)[:10], 1):
                queue_list.append(
                    f"`{i}.` **[{truncate_string(track.title, 35)}]({track.uri})** "
                    f"[{format_duration(track.length)}]"
                )

            remaining = len(player.queue) - 10
            if remaining > 0:
                queue_list.append(f"\n*...and {remaining} more track(s)*")

            embed.add_field(
                name=f"📝 Up Next ({len(player.queue)} tracks)",
                value="\n".join(queue_list),
                inline=False
            )
        else:
            embed.add_field(name="📝 Up Next", value="*Queue is empty*", inline=False)

        # Footer with loop mode
        loop_mode = getattr(player, "loop_mode", LoopMode.NONE)
        embed.set_footer(text=f"Loop: {LoopMode.to_string(loop_mode)} | Volume: {player.volume}%")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nowplaying", description="Show the currently playing song")
    async def nowplaying(self, interaction: discord.Interaction) -> None:
        """Show currently playing track."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.current:
            return await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)

        track = player.current
        progress = create_progress_bar(player.position, track.length, 20)

        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**[{track.title}]({track.uri})**",
            color=self.bot.config.color["main"]
        )

        embed.add_field(
            name="Progress",
            value=f"{progress}\n`{format_duration(player.position)}` / `{format_duration(track.length)}`",
            inline=False
        )

        if track.author:
            embed.add_field(name="Artist", value=track.author, inline=True)

        embed.add_field(name="Requested by", value=getattr(track, "requester", "Unknown"), inline=True)

        loop_mode = getattr(player, "loop_mode", LoopMode.NONE)
        embed.add_field(name="Loop", value=LoopMode.to_string(loop_mode), inline=True)

        if track.artwork:
            embed.set_thumbnail(url=track.artwork)

        await interaction.response.send_message(embed=embed, view=MusicPlayerView(self))

    @app_commands.command(name="shuffle", description="Shuffle the queue")
    async def shuffle(self, interaction: discord.Interaction) -> None:
        """Shuffle the queue."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.queue:
            return await interaction.response.send_message("❌ Queue is empty!", ephemeral=True)

        player.queue.shuffle()
        await interaction.response.send_message(f"🔀 Shuffled {len(player.queue)} tracks!")

    @app_commands.command(name="loop", description="Toggle loop mode")
    @app_commands.describe(mode="Loop mode to set")
    @app_commands.choices(mode=[
        app_commands.Choice(name="Off", value=0),
        app_commands.Choice(name="Track", value=1),
        app_commands.Choice(name="Queue", value=2),
    ])
    async def loop(self, interaction: discord.Interaction, mode: int = None) -> None:
        """Set loop mode."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            return await interaction.response.send_message("❌ No active player!", ephemeral=True)

        if not hasattr(player, "loop_mode"):
            player.loop_mode = LoopMode.NONE

        if mode is not None:
            player.loop_mode = mode
        else:
            # Cycle through modes
            player.loop_mode = (player.loop_mode + 1) % 3

        emoji = LoopMode.to_emoji(player.loop_mode)
        mode_str = LoopMode.to_string(player.loop_mode)
        await interaction.response.send_message(f"{emoji} Loop mode set to: **{mode_str}**")

    @app_commands.command(name="volume", description="Set the player volume")
    @app_commands.describe(volume="Volume level (0-150)")
    async def volume(self, interaction: discord.Interaction, volume: int) -> None:
        """Set player volume."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            return await interaction.response.send_message("❌ No active player!", ephemeral=True)

        if not 0 <= volume <= 150:
            return await interaction.response.send_message("❌ Volume must be between 0 and 150!", ephemeral=True)

        await player.set_volume(volume)

        # Volume emoji based on level
        if volume == 0:
            emoji = "🔇"
        elif volume < 50:
            emoji = "🔉"
        else:
            emoji = "🔊"

        await interaction.response.send_message(f"{emoji} Volume set to **{volume}%**")

    @app_commands.command(name="seek", description="Seek to a position in the current track")
    @app_commands.describe(position="Position to seek to (e.g., 1:30 or 90)")
    async def seek(self, interaction: discord.Interaction, position: str) -> None:
        """Seek to a position in the track."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.current:
            return await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)

        from utils.helpers import parse_duration
        ms = parse_duration(position)

        if ms is None:
            return await interaction.response.send_message(
                "❌ Invalid position format! Use `1:30` or `90` (seconds).",
                ephemeral=True
            )

        if ms > player.current.length:
            return await interaction.response.send_message(
                f"❌ Position exceeds track length ({format_duration(player.current.length)})!",
                ephemeral=True
            )

        await player.seek(ms)
        await interaction.response.send_message(f"⏩ Seeked to `{format_duration(ms)}`")

    @app_commands.command(name="remove", description="Remove a track from the queue")
    @app_commands.describe(position="Position of the track to remove (1-based)")
    async def remove(self, interaction: discord.Interaction, position: int) -> None:
        """Remove a track from the queue."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.queue:
            return await interaction.response.send_message("❌ Queue is empty!", ephemeral=True)

        if position < 1 or position > len(player.queue):
            return await interaction.response.send_message(
                f"❌ Invalid position! Must be between 1 and {len(player.queue)}.",
                ephemeral=True
            )

        # Convert to 0-based index
        track = player.queue[position - 1]
        del player.queue[position - 1]

        await interaction.response.send_message(
            f"🗑️ Removed **{truncate_string(track.title, 50)}** from the queue."
        )

    @app_commands.command(name="clear", description="Clear the entire queue")
    async def clear(self, interaction: discord.Interaction) -> None:
        """Clear the queue."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.queue:
            return await interaction.response.send_message("❌ Queue is already empty!", ephemeral=True)

        count = len(player.queue)
        player.queue.clear()
        await interaction.response.send_message(f"🗑️ Cleared **{count}** tracks from the queue!")


async def setup(bot: commands.Bot) -> None:
    """Setup function for the cog."""
    await bot.add_cog(Music(bot))
