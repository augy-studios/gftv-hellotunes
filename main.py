"""
A Discord Music Bot powered by Lavalink.
Based on Lavamusic by BotxLab, rewritten in Python.
"""

import asyncio
import logging
import os
import signal
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.logger import setup_logging
from utils.config import Config
from database.database import Database

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class MusicBot(commands.Bot):
    """Main bot class."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        intents.guilds = True
        # intents.members = True  # Requires privileged intent enabled in Developer Portal

        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/play | Music 🎵"
            ),
            status=discord.Status.online
        )

        self.config = Config()
        self.db = Database()
        self.start_time = discord.utils.utcnow()

    async def get_prefix(self, message: discord.Message) -> list[str]:
        """Get the prefix for the guild or default."""
        if not message.guild:
            return commands.when_mentioned_or(self.config.default_prefix)(self, message)

        guild_prefix = await self.db.get_prefix(message.guild.id)
        prefix = guild_prefix or self.config.default_prefix
        return commands.when_mentioned_or(prefix)(self, message)

    async def setup_hook(self) -> None:
        """Setup hook called when bot is starting."""
        logger.info("Setting up bot...")

        # Initialize database
        await self.db.initialize()

        # Load all cogs
        await self.load_cogs()

        # Sync slash commands
        if self.config.guild_id:
            guild = discord.Object(id=self.config.guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"Synced commands to guild {self.config.guild_id}")
        else:
            await self.tree.sync()
            logger.info("Synced commands globally")

    async def load_cogs(self) -> None:
        """Load all cog extensions."""
        cogs_dir = Path(__file__).parent / "cogs"

        for cog_file in cogs_dir.glob("*.py"):
            if cog_file.name.startswith("_"):
                continue

            cog_name = f"cogs.{cog_file.stem}"
            try:
                await self.load_extension(cog_name)
                logger.info(f"Loaded cog: {cog_name}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog_name}: {e}")

    async def on_ready(self) -> None:
        """Event triggered when bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info(f"discord.py version: {discord.__version__}")
        logger.info("Bot is ready!")

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Event triggered when bot joins a guild."""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        await self.db.create_guild(guild.id)

        # Send log to log channel if configured
        if self.config.log_channel_id:
            channel = self.get_channel(self.config.log_channel_id)
            if channel:
                embed = discord.Embed(
                    title="📥 Joined New Guild",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="Guild", value=guild.name, inline=True)
                embed.add_field(name="ID", value=guild.id, inline=True)
                embed.add_field(name="Members", value=guild.member_count, inline=True)
                if guild.icon:
                    embed.set_thumbnail(url=guild.icon.url)
                await channel.send(embed=embed)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Event triggered when bot leaves a guild."""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")

        # Send log to log channel if configured
        if self.config.log_channel_id:
            channel = self.get_channel(self.config.log_channel_id)
            if channel:
                embed = discord.Embed(
                    title="📤 Left Guild",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="Guild", value=guild.name, inline=True)
                embed.add_field(name="ID", value=guild.id, inline=True)
                await channel.send(embed=embed)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Global error handler for commands."""
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
            return

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions to do that.")
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Command on cooldown. Try again in {error.retry_after:.1f}s")
            return

        logger.error(f"Command error in {ctx.command}: {error}")
        await ctx.send("❌ An error occurred while processing the command.")


async def main() -> None:
    """Main entry point."""
    bot = MusicBot()

    token = os.getenv("TOKEN")
    if not token:
        logger.error("No TOKEN found in environment variables!")
        return

    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
