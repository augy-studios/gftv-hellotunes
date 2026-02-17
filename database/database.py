"""
Database management for Augy Music Bot.
Uses SQLite with aiosqlite for async operations.
"""

import aiosqlite
import logging
import os
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GuildSettings:
    """Guild settings data class."""
    guild_id: int
    prefix: str = "!"
    language: str = "en"
    dj_role_id: Optional[int] = None
    dj_only: bool = False
    stay_connected: bool = False  # 24/7 mode
    announce_songs: bool = True
    default_volume: int = 100
    request_channel_id: Optional[int] = None


@dataclass
class Playlist:
    """Playlist data class."""
    id: int
    name: str
    user_id: int
    guild_id: int
    tracks: list[dict]
    created_at: str


class Database:
    """Async database handler using SQLite."""

    def __init__(self, db_path: str = None) -> None:
        """Initialize database connection."""
        self.db_path = db_path or os.getenv("DATABASE_URL", "data/augymusic.db")
        # Handle SQLite file:// prefix
        if self.db_path.startswith("file:"):
            self.db_path = self.db_path.replace("file:", "").lstrip("/")

        self.connection: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        """Initialize the database and create tables."""
        # Ensure data directory exists
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row

        await self._create_tables()
        logger.info(f"Database initialized: {self.db_path}")

    async def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        async with self.connection.cursor() as cursor:
            # Guild settings table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS guilds (
                    guild_id INTEGER PRIMARY KEY,
                    prefix TEXT DEFAULT '!',
                    language TEXT DEFAULT 'en',
                    dj_role_id INTEGER,
                    dj_only INTEGER DEFAULT 0,
                    stay_connected INTEGER DEFAULT 0,
                    announce_songs INTEGER DEFAULT 1,
                    default_volume INTEGER DEFAULT 100,
                    request_channel_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Playlists table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    tracks TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, user_id)
                )
            """)

            # DJ roles table (for multiple DJ roles)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS dj_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    UNIQUE(guild_id, role_id)
                )
            """)

            await self.connection.commit()

    async def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            await self.connection.close()

    # ============== Guild Settings ==============

    async def create_guild(self, guild_id: int) -> None:
        """Create a new guild entry or ignore if exists."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "INSERT OR IGNORE INTO guilds (guild_id) VALUES (?)",
                (guild_id,)
            )
            await self.connection.commit()

    async def get_guild_settings(self, guild_id: int) -> Optional[GuildSettings]:
        """Get guild settings."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM guilds WHERE guild_id = ?",
                (guild_id,)
            )
            row = await cursor.fetchone()

            if row:
                return GuildSettings(
                    guild_id=row["guild_id"],
                    prefix=row["prefix"],
                    language=row["language"],
                    dj_role_id=row["dj_role_id"],
                    dj_only=bool(row["dj_only"]),
                    stay_connected=bool(row["stay_connected"]),
                    announce_songs=bool(row["announce_songs"]),
                    default_volume=row["default_volume"],
                    request_channel_id=row["request_channel_id"]
                )
            return None

    async def get_prefix(self, guild_id: int) -> Optional[str]:
        """Get the prefix for a guild."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT prefix FROM guilds WHERE guild_id = ?",
                (guild_id,)
            )
            row = await cursor.fetchone()
            return row["prefix"] if row else None

    async def set_prefix(self, guild_id: int, prefix: str) -> None:
        """Set the prefix for a guild."""
        await self.create_guild(guild_id)
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE guilds SET prefix = ? WHERE guild_id = ?",
                (prefix, guild_id)
            )
            await self.connection.commit()

    async def set_language(self, guild_id: int, language: str) -> None:
        """Set the language for a guild."""
        await self.create_guild(guild_id)
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE guilds SET language = ? WHERE guild_id = ?",
                (language, guild_id)
            )
            await self.connection.commit()

    async def set_dj_only(self, guild_id: int, dj_only: bool) -> None:
        """Set DJ only mode for a guild."""
        await self.create_guild(guild_id)
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE guilds SET dj_only = ? WHERE guild_id = ?",
                (int(dj_only), guild_id)
            )
            await self.connection.commit()

    async def set_stay_connected(self, guild_id: int, stay: bool) -> None:
        """Set 24/7 mode for a guild."""
        await self.create_guild(guild_id)
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE guilds SET stay_connected = ? WHERE guild_id = ?",
                (int(stay), guild_id)
            )
            await self.connection.commit()

    async def set_default_volume(self, guild_id: int, volume: int) -> None:
        """Set default volume for a guild."""
        await self.create_guild(guild_id)
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE guilds SET default_volume = ? WHERE guild_id = ?",
                (volume, guild_id)
            )
            await self.connection.commit()

    async def set_request_channel(self, guild_id: int, channel_id: Optional[int]) -> None:
        """Set the request channel for a guild."""
        await self.create_guild(guild_id)
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE guilds SET request_channel_id = ? WHERE guild_id = ?",
                (channel_id, guild_id)
            )
            await self.connection.commit()

    # ============== DJ Roles ==============

    async def add_dj_role(self, guild_id: int, role_id: int) -> bool:
        """Add a DJ role to a guild."""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO dj_roles (guild_id, role_id) VALUES (?, ?)",
                    (guild_id, role_id)
                )
                await self.connection.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

    async def remove_dj_role(self, guild_id: int, role_id: int) -> bool:
        """Remove a DJ role from a guild."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM dj_roles WHERE guild_id = ? AND role_id = ?",
                (guild_id, role_id)
            )
            await self.connection.commit()
            return cursor.rowcount > 0

    async def get_dj_roles(self, guild_id: int) -> list[int]:
        """Get all DJ roles for a guild."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT role_id FROM dj_roles WHERE guild_id = ?",
                (guild_id,)
            )
            rows = await cursor.fetchall()
            return [row["role_id"] for row in rows]

    # ============== Playlists ==============

    async def create_playlist(self, name: str, user_id: int, guild_id: int) -> bool:
        """Create a new playlist."""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO playlists (name, user_id, guild_id) VALUES (?, ?, ?)",
                    (name, user_id, guild_id)
                )
                await self.connection.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

    async def delete_playlist(self, name: str, user_id: int) -> bool:
        """Delete a playlist."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM playlists WHERE name = ? AND user_id = ?",
                (name, user_id)
            )
            await self.connection.commit()
            return cursor.rowcount > 0

    async def get_playlist(self, name: str, user_id: int) -> Optional[dict]:
        """Get a playlist by name and user."""
        import json
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM playlists WHERE name = ? AND user_id = ?",
                (name, user_id)
            )
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row["id"],
                    "name": row["name"],
                    "user_id": row["user_id"],
                    "guild_id": row["guild_id"],
                    "tracks": json.loads(row["tracks"]),
                    "created_at": row["created_at"]
                }
            return None

    async def get_user_playlists(self, user_id: int) -> list[dict]:
        """Get all playlists for a user."""
        import json
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM playlists WHERE user_id = ?",
                (user_id,)
            )
            rows = await cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "user_id": row["user_id"],
                    "guild_id": row["guild_id"],
                    "tracks": json.loads(row["tracks"]),
                    "created_at": row["created_at"]
                }
                for row in rows
            ]

    async def add_track_to_playlist(self, name: str, user_id: int, track: dict) -> bool:
        """Add a track to a playlist."""
        import json
        playlist = await self.get_playlist(name, user_id)
        if not playlist:
            return False

        tracks = playlist["tracks"]
        tracks.append(track)

        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE playlists SET tracks = ? WHERE name = ? AND user_id = ?",
                (json.dumps(tracks), name, user_id)
            )
            await self.connection.commit()
        return True

    async def remove_track_from_playlist(self, name: str, user_id: int, index: int) -> bool:
        """Remove a track from a playlist by index."""
        import json
        playlist = await self.get_playlist(name, user_id)
        if not playlist or index < 0 or index >= len(playlist["tracks"]):
            return False

        tracks = playlist["tracks"]
        tracks.pop(index)

        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE playlists SET tracks = ? WHERE name = ? AND user_id = ?",
                (json.dumps(tracks), name, user_id)
            )
            await self.connection.commit()
        return True
