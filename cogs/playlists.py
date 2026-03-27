"""
Playlist Cog - Playlist management.
"""

import logging
import wavelink
import discord
from discord import app_commands
from discord.ext import commands
from typing import cast, Optional

from utils.helpers import truncate_string, format_duration

logger = logging.getLogger(__name__)


class PlaylistModal(discord.ui.Modal, title="Create Playlist"):
    """Modal for creating a new playlist."""

    name = discord.ui.TextInput(
        label="Playlist Name",
        placeholder="Enter playlist name...",
        min_length=1,
        max_length=50,
        required=True
    )

    def __init__(self, cog: "Playlists") -> None:
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Handle modal submission."""
        name = str(self.name)

        # Check if playlist already exists
        existing = await self.cog.bot.db.get_playlist(name, interaction.user.id)
        if existing:
            return await interaction.response.send_message(
                f"❌ You already have a playlist named **{name}**!",
                ephemeral=True
            )

        # Create the playlist
        success = await self.cog.bot.db.create_playlist(
            name, interaction.user.id, interaction.guild.id
        )

        if success:
            await interaction.response.send_message(
                f"✅ Created playlist **{name}**!\n"
                f"Use `/playlist add {name} <song>` to add tracks."
            )
        else:
            await interaction.response.send_message(
                "❌ Failed to create playlist!", ephemeral=True
            )


class PlaylistView(discord.ui.View):
    """View for playlist navigation."""

    def __init__(
        self,
        cog: "Playlists",
        playlist: dict,
        page: int = 0,
        timeout: float = 180
    ) -> None:
        super().__init__(timeout=timeout)
        self.cog = cog
        self.playlist = playlist
        self.page = page
        self.per_page = 10

    @property
    def max_pages(self) -> int:
        """Get total number of pages."""
        return max(1, (len(self.playlist["tracks"]) + self.per_page - 1) // self.per_page)

    def get_embed(self) -> discord.Embed:
        """Generate the embed for the current page."""
        tracks = self.playlist["tracks"]
        start = self.page * self.per_page
        end = start + self.per_page
        page_tracks = tracks[start:end]

        embed = discord.Embed(
            title=f"📋 Playlist: {self.playlist['name']}",
            color=0x5865F2
        )

        if page_tracks:
            track_list = []
            for i, track in enumerate(page_tracks, start + 1):
                track_list.append(
                    f"`{i}.` **{truncate_string(track['title'], 40)}** "
                    f"[{format_duration(track['duration'])}]"
                )
            embed.description = "\n".join(track_list)
        else:
            embed.description = "*This playlist is empty.*"

        embed.set_footer(
            text=f"Page {self.page + 1}/{self.max_pages} • "
                 f"{len(tracks)} track(s) • "
                 f"Created: {self.playlist['created_at'][:10]}"
        )

        return embed

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Go to previous page."""
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Go to next page."""
        if self.page < self.max_pages - 1:
            self.page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.primary, label="Load")
    async def load_playlist(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Load the playlist into the queue."""
        if not interaction.user.voice:
            return await interaction.response.send_message(
                "❌ You must be in a voice channel!", ephemeral=True
            )

        tracks = self.playlist["tracks"]
        if not tracks:
            return await interaction.response.send_message(
                "❌ This playlist is empty!", ephemeral=True
            )

        await interaction.response.defer()

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        # Connect if not connected
        if not player:
            try:
                player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
                player.text_channel = interaction.channel
                player.loop_mode = 0
            except Exception as e:
                return await interaction.followup.send(f"❌ Could not connect: {e}")

        loaded = 0
        for track_data in tracks:
            try:
                # Search for the track
                results = await wavelink.Playable.search(track_data["uri"])
                if results:
                    track = results[0] if not isinstance(results, wavelink.Playlist) else results.tracks[0]
                    track.requester = interaction.user.mention
                    player.queue.put(track)
                    loaded += 1
            except Exception:
                continue

        # Start playing if not already
        if not player.playing and player.queue:
            track = player.queue.get()
            await player.play(track)

        await interaction.followup.send(
            f"✅ Loaded **{loaded}** tracks from **{self.playlist['name']}**!"
        )


class Playlists(commands.Cog):
    """Playlist management commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    playlist_group = app_commands.Group(name="playlist", description="Playlist management commands")

    @playlist_group.command(name="create", description="Create a new playlist")
    async def playlist_create(self, interaction: discord.Interaction) -> None:
        """Create a new playlist using a modal."""
        await interaction.response.send_modal(PlaylistModal(self))

    @playlist_group.command(name="delete", description="Delete a playlist")
    @app_commands.describe(name="Name of the playlist to delete")
    async def playlist_delete(self, interaction: discord.Interaction, name: str) -> None:
        """Delete a playlist."""
        success = await self.bot.db.delete_playlist(name, interaction.user.id)

        if success:
            await interaction.response.send_message(f"🗑️ Deleted playlist **{name}**!")
        else:
            await interaction.response.send_message(
                f"❌ Playlist **{name}** not found or you don't own it!",
                ephemeral=True
            )

    @playlist_group.command(name="view", description="View a playlist")
    @app_commands.describe(name="Name of the playlist to view")
    async def playlist_view(self, interaction: discord.Interaction, name: str) -> None:
        """View a playlist's contents."""
        playlist = await self.bot.db.get_playlist(name, interaction.user.id)

        if not playlist:
            return await interaction.response.send_message(
                f"❌ Playlist **{name}** not found!",
                ephemeral=True
            )

        view = PlaylistView(self, playlist)
        await interaction.response.send_message(embed=view.get_embed(), view=view)

    @playlist_group.command(name="list", description="List all your playlists")
    async def playlist_list(self, interaction: discord.Interaction) -> None:
        """List all playlists owned by the user."""
        playlists = await self.bot.db.get_user_playlists(interaction.user.id)

        if not playlists:
            return await interaction.response.send_message(
                "📋 You don't have any playlists yet!\n"
                "Use `/playlist create` to create one.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="📋 Your Playlists",
            color=self.bot.config.color["main"]
        )

        playlist_list = []
        for pl in playlists:
            track_count = len(pl["tracks"])
            playlist_list.append(
                f"**{pl['name']}** - {track_count} track(s)"
            )

        embed.description = "\n".join(playlist_list)
        embed.set_footer(text=f"Total: {len(playlists)} playlist(s)")

        await interaction.response.send_message(embed=embed)

    @playlist_group.command(name="add", description="Add the current song to a playlist")
    @app_commands.describe(name="Name of the playlist")
    async def playlist_add(self, interaction: discord.Interaction, name: str) -> None:
        """Add the currently playing song to a playlist."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player or not player.current:
            return await interaction.response.send_message(
                "❌ Nothing is playing!",
                ephemeral=True
            )

        playlist = await self.bot.db.get_playlist(name, interaction.user.id)
        if not playlist:
            return await interaction.response.send_message(
                f"❌ Playlist **{name}** not found!",
                ephemeral=True
            )

        # Check playlist size limit
        if len(playlist["tracks"]) >= self.bot.config.max_playlist_size:
            return await interaction.response.send_message(
                f"❌ Playlist has reached the maximum size ({self.bot.config.max_playlist_size} tracks)!",
                ephemeral=True
            )

        track = player.current
        track_data = {
            "title": track.title,
            "uri": track.uri,
            "duration": track.length,
            "author": track.author
        }

        success = await self.bot.db.add_track_to_playlist(name, interaction.user.id, track_data)

        if success:
            await interaction.response.send_message(
                f"✅ Added **{truncate_string(track.title, 50)}** to **{name}**!"
            )
        else:
            await interaction.response.send_message(
                "❌ Failed to add track to playlist!",
                ephemeral=True
            )

    @playlist_group.command(name="addquery", description="Add a song by search to a playlist")
    @app_commands.describe(name="Name of the playlist", query="Song to search and add")
    async def playlist_addquery(
        self,
        interaction: discord.Interaction,
        name: str,
        query: str
    ) -> None:
        """Add a song by search query to a playlist."""
        playlist = await self.bot.db.get_playlist(name, interaction.user.id)
        if not playlist:
            return await interaction.response.send_message(
                f"❌ Playlist **{name}** not found!",
                ephemeral=True
            )

        # Check playlist size limit
        if len(playlist["tracks"]) >= self.bot.config.max_playlist_size:
            return await interaction.response.send_message(
                f"❌ Playlist has reached the maximum size ({self.bot.config.max_playlist_size} tracks)!",
                ephemeral=True
            )

        await interaction.response.defer()

        try:
            results = await wavelink.Playable.search(query)
        except Exception as e:
            return await interaction.followup.send(f"❌ Search failed: {e}")

        if not results:
            return await interaction.followup.send("❌ No results found!")

        # Get first result
        track = results[0] if not isinstance(results, wavelink.Playlist) else results.tracks[0]

        track_data = {
            "title": track.title,
            "uri": track.uri,
            "duration": track.length,
            "author": track.author
        }

        success = await self.bot.db.add_track_to_playlist(name, interaction.user.id, track_data)

        if success:
            await interaction.followup.send(
                f"✅ Added **{truncate_string(track.title, 50)}** to **{name}**!"
            )
        else:
            await interaction.followup.send("❌ Failed to add track to playlist!")

    @playlist_group.command(name="remove", description="Remove a song from a playlist")
    @app_commands.describe(name="Name of the playlist", position="Position of the track (1-based)")
    async def playlist_remove(
        self,
        interaction: discord.Interaction,
        name: str,
        position: int
    ) -> None:
        """Remove a song from a playlist by position."""
        playlist = await self.bot.db.get_playlist(name, interaction.user.id)
        if not playlist:
            return await interaction.response.send_message(
                f"❌ Playlist **{name}** not found!",
                ephemeral=True
            )

        if position < 1 or position > len(playlist["tracks"]):
            return await interaction.response.send_message(
                f"❌ Invalid position! Must be between 1 and {len(playlist['tracks'])}.",
                ephemeral=True
            )

        track = playlist["tracks"][position - 1]
        success = await self.bot.db.remove_track_from_playlist(name, interaction.user.id, position - 1)

        if success:
            await interaction.response.send_message(
                f"🗑️ Removed **{truncate_string(track['title'], 50)}** from **{name}**!"
            )
        else:
            await interaction.response.send_message(
                "❌ Failed to remove track from playlist!",
                ephemeral=True
            )

    @playlist_group.command(name="load", description="Load a playlist into the queue")
    @app_commands.describe(name="Name of the playlist to load")
    async def playlist_load(self, interaction: discord.Interaction, name: str) -> None:
        """Load a playlist into the queue."""
        if not interaction.user.voice:
            return await interaction.response.send_message(
                "❌ You must be in a voice channel!",
                ephemeral=True
            )

        playlist = await self.bot.db.get_playlist(name, interaction.user.id)
        if not playlist:
            return await interaction.response.send_message(
                f"❌ Playlist **{name}** not found!",
                ephemeral=True
            )

        if not playlist["tracks"]:
            return await interaction.response.send_message(
                "❌ This playlist is empty!",
                ephemeral=True
            )

        await interaction.response.defer()

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        # Connect if not connected
        if not player:
            try:
                player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
                player.text_channel = interaction.channel
                player.loop_mode = 0
            except Exception as e:
                return await interaction.followup.send(f"❌ Could not connect: {e}")

        loaded = 0
        for track_data in playlist["tracks"]:
            try:
                results = await wavelink.Playable.search(track_data["uri"])
                if results:
                    track = results[0] if not isinstance(results, wavelink.Playlist) else results.tracks[0]
                    track.requester = interaction.user.mention
                    player.queue.put(track)
                    loaded += 1
            except Exception:
                continue

        # Start playing if not already
        if not player.playing and player.queue:
            track = player.queue.get()
            await player.play(track)

        await interaction.followup.send(
            f"✅ Loaded **{loaded}** tracks from **{name}**!"
        )


async def setup(bot: commands.Bot) -> None:
    """Setup function for the cog."""
    await bot.add_cog(Playlists(bot))
