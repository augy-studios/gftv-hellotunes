"""
Info Cog - Information and utility commands for Augy Music Bot.
"""

import logging
import platform
import psutil
import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from datetime import datetime

logger = logging.getLogger(__name__)


class Info(commands.Cog):
    """Information and utility commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _format_uptime(self) -> str:
        """Format bot uptime."""
        delta = datetime.utcnow() - self.bot.start_time.replace(tzinfo=None)
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")

        return " ".join(parts)

    @app_commands.command(name="help", description="Show help information")
    async def help(self, interaction: discord.Interaction) -> None:
        """Show help information."""
        embed = discord.Embed(
            title="🎵 Augy Music Bot - Help",
            description="A powerful Discord music bot powered by Lavalink!",
            color=self.bot.config.color["main"]
        )

        # Music commands
        embed.add_field(
            name="🎵 Music",
            value=(
                "`/play` - Play a song\n"
                "`/pause` - Pause playback\n"
                "`/resume` - Resume playback\n"
                "`/skip` - Skip current track\n"
                "`/stop` - Stop and clear queue\n"
                "`/disconnect` - Disconnect from VC"
            ),
            inline=True
        )

        # Queue commands
        embed.add_field(
            name="📋 Queue",
            value=(
                "`/queue` - View queue\n"
                "`/nowplaying` - Current track\n"
                "`/shuffle` - Shuffle queue\n"
                "`/loop` - Toggle loop mode\n"
                "`/remove` - Remove track\n"
                "`/clear` - Clear queue"
            ),
            inline=True
        )

        # Filter commands
        embed.add_field(
            name="🎛️ Filters",
            value=(
                "`/bassboost` - Bass boost\n"
                "`/nightcore` - Nightcore effect\n"
                "`/vaporwave` - Vaporwave effect\n"
                "`/karaoke` - Karaoke mode\n"
                "`/rotation` - 8D audio\n"
                "`/resetfilters` - Reset all"
            ),
            inline=True
        )

        # Playlist commands
        embed.add_field(
            name="📂 Playlists",
            value=(
                "`/playlist create` - Create\n"
                "`/playlist delete` - Delete\n"
                "`/playlist view` - View tracks\n"
                "`/playlist add` - Add track\n"
                "`/playlist load` - Load playlist\n"
                "`/playlist list` - Your playlists"
            ),
            inline=True
        )

        # Settings commands
        embed.add_field(
            name="⚙️ Settings",
            value=(
                "`/prefix` - Set prefix\n"
                "`/language` - Set language\n"
                "`/247` - Toggle 24/7\n"
                "`/dj add/remove` - DJ roles\n"
                "`/defaultvolume` - Default vol\n"
                "`/settings` - View settings"
            ),
            inline=True
        )

        # Info commands
        embed.add_field(
            name="ℹ️ Info",
            value=(
                "`/help` - This menu\n"
                "`/botinfo` - Bot statistics\n"
                "`/ping` - Check latency\n"
                "`/invite` - Invite link\n"
                "`/node` - Lavalink stats"
            ),
            inline=True
        )

        embed.set_footer(text="Use / to see all available commands!")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="botinfo", description="Show bot information and statistics")
    async def botinfo(self, interaction: discord.Interaction) -> None:
        """Show bot information."""
        embed = discord.Embed(
            title="🤖 Bot Information",
            color=self.bot.config.color["main"]
        )

        # Bot stats
        total_members = sum(g.member_count for g in self.bot.guilds)
        voice_clients = len(self.bot.voice_clients)

        embed.add_field(name="Servers", value=f"{len(self.bot.guilds):,}", inline=True)
        embed.add_field(name="Users", value=f"{total_members:,}", inline=True)
        embed.add_field(name="Voice Connections", value=str(voice_clients), inline=True)

        # System stats
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = psutil.cpu_percent()

        embed.add_field(name="Memory", value=f"{memory_mb:.1f} MB", inline=True)
        embed.add_field(name="CPU", value=f"{cpu_percent}%", inline=True)
        embed.add_field(name="Uptime", value=self._format_uptime(), inline=True)

        # Version info
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)
        embed.add_field(name="Wavelink", value=wavelink.__version__, inline=True)

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Bot ID: {self.bot.user.id}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Check bot latency."""
        # Discord WebSocket latency
        ws_latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="🏓 Pong!",
            color=self.bot.config.color["success"]
        )

        # Determine emoji based on latency
        if ws_latency < 100:
            emoji = "🟢"
            status = "Excellent"
        elif ws_latency < 200:
            emoji = "🟡"
            status = "Good"
        else:
            emoji = "🔴"
            status = "High"

        embed.add_field(
            name="WebSocket",
            value=f"{emoji} {ws_latency}ms ({status})",
            inline=False
        )

        # Lavalink node latency
        nodes = wavelink.Pool.nodes
        if nodes:
            for identifier, node in nodes.items():
                embed.add_field(
                    name=f"Lavalink ({identifier})",
                    value=f"🟢 Connected" if node.status.is_connected else "🔴 Disconnected",
                    inline=True
                )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invite", description="Get the bot invite link")
    async def invite(self, interaction: discord.Interaction) -> None:
        """Get bot invite link."""
        permissions = discord.Permissions(
            send_messages=True,
            embed_links=True,
            connect=True,
            speak=True,
            use_voice_activation=True,
            read_message_history=True,
            add_reactions=True,
            use_external_emojis=True,
            manage_messages=True
        )

        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=permissions,
            scopes=["bot", "applications.commands"]
        )

        embed = discord.Embed(
            title="📨 Invite Augy Music Bot",
            description=(
                f"Click the button below to add me to your server!\n\n"
                f"[Direct Link]({invite_url})"
            ),
            color=self.bot.config.color["main"]
        )

        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Invite Bot",
            url=invite_url,
            style=discord.ButtonStyle.link,
            emoji="🎵"
        ))

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="node", description="Show Lavalink node information")
    async def node(self, interaction: discord.Interaction) -> None:
        """Show Lavalink node statistics."""
        nodes = wavelink.Pool.nodes

        if not nodes:
            return await interaction.response.send_message(
                "❌ No Lavalink nodes connected!",
                ephemeral=True
            )

        embed = discord.Embed(
            title="🎛️ Lavalink Nodes",
            color=self.bot.config.color["main"]
        )

        for identifier, node in nodes.items():
            status_emoji = "🟢" if node.status.is_connected else "🔴"
            status_text = "Connected" if node.status.is_connected else "Disconnected"

            # Get node stats if available
            stats_info = "N/A"
            try:
                if hasattr(node, 'stats') and node.stats:
                    stats = node.stats
                    players = getattr(stats, 'players', 0)
                    playing = getattr(stats, 'playing_players', 0)
                    stats_info = f"Players: {playing}/{players}"
            except Exception:
                pass

            embed.add_field(
                name=f"{status_emoji} {identifier}",
                value=(
                    f"**Status:** {status_text}\n"
                    f"**{stats_info}**"
                ),
                inline=True
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Show server information")
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        """Show server information."""
        guild = interaction.guild

        embed = discord.Embed(
            title=guild.name,
            color=self.bot.config.color["main"]
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="Owner", value=f"<@{guild.owner_id}>", inline=True)
        embed.add_field(name="Members", value=f"{guild.member_count:,}", inline=True)
        embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Emojis", value=str(len(guild.emojis)), inline=True)
        embed.add_field(
            name="Created",
            value=f"<t:{int(guild.created_at.timestamp())}:R>",
            inline=True
        )

        embed.set_footer(text=f"Server ID: {guild.id}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="status", description="Check bot component status")
    async def status(self, interaction: discord.Interaction) -> None:
        """Quick health check of all bot components."""
        embed = discord.Embed(
            title="Bot Status",
            color=self.bot.config.color["main"]
        )

        # Bot connection
        ws_latency = round(self.bot.latency * 1000)
        embed.add_field(
            name="Discord",
            value=f"Connected ({ws_latency}ms)",
            inline=True
        )

        # Database
        try:
            await self.bot.db.get_guild_settings(interaction.guild.id)
            db_status = "Connected"
        except Exception as e:
            db_status = f"Error: {e}"
        embed.add_field(name="Database", value=db_status, inline=True)

        # Lavalink
        try:
            nodes = wavelink.Pool.nodes
            if nodes:
                connected = sum(1 for n in nodes.values() if n.status.is_connected)
                lavalink_status = f"{connected}/{len(nodes)} node(s)"
            else:
                lavalink_status = "Not configured"
        except Exception:
            lavalink_status = "Not configured"
        embed.add_field(name="Lavalink", value=lavalink_status, inline=True)

        # Loaded cogs
        cog_names = [name for name in self.bot.cogs]
        embed.add_field(
            name=f"Cogs ({len(cog_names)})",
            value=", ".join(cog_names) or "None",
            inline=False
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Setup function for the cog."""
    await bot.add_cog(Info(bot))
