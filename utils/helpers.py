"""
Music helper utilities for Augy Music Bot.
"""

import re
from typing import Optional
from datetime import timedelta
import discord


def format_duration(milliseconds: int) -> str:
    """
    Format duration from milliseconds to human readable format.

    Args:
        milliseconds: Duration in milliseconds

    Returns:
        Formatted string like "3:45" or "1:23:45"
    """
    if milliseconds <= 0:
        return "0:00"

    seconds = milliseconds // 1000
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def parse_duration(duration_str: str) -> Optional[int]:
    """
    Parse duration string to milliseconds.

    Args:
        duration_str: Duration string like "3:45" or "1:23:45"

    Returns:
        Duration in milliseconds or None if invalid
    """
    parts = duration_str.split(":")
    try:
        if len(parts) == 1:
            return int(parts[0]) * 1000
        elif len(parts) == 2:
            minutes, seconds = int(parts[0]), int(parts[1])
            return (minutes * 60 + seconds) * 1000
        elif len(parts) == 3:
            hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
            return (hours * 3600 + minutes * 60 + seconds) * 1000
    except ValueError:
        return None
    return None


def create_progress_bar(current: int, total: int, length: int = 15) -> str:
    """
    Create a text progress bar.

    Args:
        current: Current position
        total: Total duration
        length: Length of the bar in characters

    Returns:
        Progress bar string like "▬▬▬▬🔘▬▬▬▬▬"
    """
    if total <= 0:
        return "▬" * length

    progress = min(current / total, 1.0)
    position = int(progress * length)

    bar = "▬" * position + "🔘" + "▬" * (length - position - 1)
    return bar


def get_source_emoji(source: str) -> str:
    """
    Get emoji for music source.

    Args:
        source: Source name (youtube, spotify, soundcloud, etc.)

    Returns:
        Corresponding emoji
    """
    emojis = {
        "youtube": "🔴",
        "youtubemusic": "🎵",
        "spotify": "💚",
        "soundcloud": "🟠",
        "bandcamp": "🟦",
        "twitch": "🟣",
        "vimeo": "🔵",
        "http": "🌐",
        "local": "📁",
        "unknown": "🎵"
    }
    return emojis.get(source.lower(), "🎵")


def truncate_string(text: str, max_length: int = 50) -> str:
    """
    Truncate a string to a maximum length with ellipsis.

    Args:
        text: The text to truncate
        max_length: Maximum length

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def is_url(text: str) -> bool:
    """
    Check if a string is a URL.

    Args:
        text: String to check

    Returns:
        True if it's a URL
    """
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return url_pattern.match(text) is not None


def get_platform_from_url(url: str) -> str:
    """
    Detect platform from URL.

    Args:
        url: The URL to check

    Returns:
        Platform name
    """
    url_lower = url.lower()

    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    elif "music.youtube.com" in url_lower:
        return "youtubemusic"
    elif "spotify.com" in url_lower or "open.spotify.com" in url_lower:
        return "spotify"
    elif "soundcloud.com" in url_lower:
        return "soundcloud"
    elif "bandcamp.com" in url_lower:
        return "bandcamp"
    elif "twitch.tv" in url_lower:
        return "twitch"
    elif "vimeo.com" in url_lower:
        return "vimeo"
    elif "deezer.com" in url_lower:
        return "deezer"
    elif "music.apple.com" in url_lower:
        return "applemusic"

    return "http"


class LoopMode:
    """Loop mode constants."""
    NONE = 0
    TRACK = 1
    QUEUE = 2

    @staticmethod
    def to_string(mode: int) -> str:
        """Convert loop mode to string."""
        if mode == LoopMode.NONE:
            return "Off"
        elif mode == LoopMode.TRACK:
            return "Track"
        elif mode == LoopMode.QUEUE:
            return "Queue"
        return "Unknown"

    @staticmethod
    def to_emoji(mode: int) -> str:
        """Convert loop mode to emoji."""
        if mode == LoopMode.NONE:
            return "➡️"
        elif mode == LoopMode.TRACK:
            return "🔂"
        elif mode == LoopMode.QUEUE:
            return "🔁"
        return "❓"


class EmbedBuilder:
    """Helper class to build consistent embeds."""

    @staticmethod
    def create_music_embed(
        title: str,
        description: str = None,
        color: int = 0x5865F2,
        thumbnail_url: str = None,
        footer_text: str = None
    ) -> discord.Embed:
        """Create a standardized music embed."""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )

        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        if footer_text:
            embed.set_footer(text=footer_text)

        return embed

    @staticmethod
    def error_embed(message: str) -> discord.Embed:
        """Create an error embed."""
        return discord.Embed(
            title="❌ Error",
            description=message,
            color=0xED4245
        )

    @staticmethod
    def success_embed(message: str) -> discord.Embed:
        """Create a success embed."""
        return discord.Embed(
            title="✅ Success",
            description=message,
            color=0x57F287
        )

    @staticmethod
    def warning_embed(message: str) -> discord.Embed:
        """Create a warning embed."""
        return discord.Embed(
            title="⚠️ Warning",
            description=message,
            color=0xFEE75C
        )


class MusicChecks:
    """Helper class for music command checks."""

    @staticmethod
    def in_voice_channel(ctx_or_interaction) -> bool:
        """Check if the user is in a voice channel."""
        if isinstance(ctx_or_interaction, discord.Interaction):
            member = ctx_or_interaction.user
        else:
            member = ctx_or_interaction.author

        return member.voice is not None and member.voice.channel is not None

    @staticmethod
    def in_same_voice_channel(ctx_or_interaction, bot_user: discord.User) -> bool:
        """Check if the user is in the same voice channel as the bot."""
        if isinstance(ctx_or_interaction, discord.Interaction):
            member = ctx_or_interaction.user
            guild = ctx_or_interaction.guild
        else:
            member = ctx_or_interaction.author
            guild = ctx_or_interaction.guild

        if not member.voice or not member.voice.channel:
            return False

        bot_member = guild.get_member(bot_user.id)
        if not bot_member or not bot_member.voice:
            return True  # Bot not in voice, allow

        return member.voice.channel.id == bot_member.voice.channel.id
