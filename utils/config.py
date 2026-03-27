"""
Configuration management.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class LavalinkNode:
    """Lavalink node configuration."""
    host: str = "localhost"
    port: int = 2333
    password: str = "youshallnotpass"
    identifier: str = "MAIN"
    secure: bool = False
    region: Optional[str] = None


@dataclass
class Config:
    """Bot configuration loaded from environment variables."""

    # Environment
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "PROD").upper())

    # Bot settings
    token: str = field(default_factory=lambda: os.getenv("TOKEN", ""))
    client_id: str = field(default_factory=lambda: os.getenv("CLIENT_ID", ""))
    default_prefix: str = field(default_factory=lambda: os.getenv("PREFIX", "!"))
    default_language: str = field(default_factory=lambda: os.getenv("DEFAULT_LANGUAGE", "en"))

    # Owner settings
    owner_ids: list[int] = field(default_factory=lambda: Config._parse_owner_ids())
    guild_id: Optional[int] = field(default_factory=lambda: Config._parse_guild_id())

    # Logging
    log_channel_id: Optional[int] = field(default_factory=lambda: Config._parse_int_env("LOG_CHANNEL_ID"))
    log_commands_id: Optional[int] = field(default_factory=lambda: Config._parse_int_env("LOG_COMMANDS_ID"))

    # Bot status
    bot_status: str = field(default_factory=lambda: os.getenv("BOT_STATUS", "online"))
    bot_activity_type: int = field(default_factory=lambda: int(os.getenv("BOT_ACTIVITY_TYPE", "0")))
    bot_activity_name: str = field(default_factory=lambda: os.getenv("BOT_ACTIVITY_NAME", "/play | Music"))

    # Music settings
    default_volume: int = field(default_factory=lambda: int(os.getenv("DEFAULT_VOLUME", "100")))
    max_queue_size: int = field(default_factory=lambda: int(os.getenv("MAX_QUEUE_SIZE", "1000")))
    max_playlist_size: int = field(default_factory=lambda: int(os.getenv("MAX_PLAYLIST_SIZE", "100")))

    # Lavalink nodes
    lavalink_nodes: list[LavalinkNode] = field(default_factory=lambda: Config._parse_lavalink_nodes())

    # Colors for embeds
    color: dict = field(default_factory=lambda: {
        "main": 0x5865F2,      # Discord blurple
        "success": 0x57F287,   # Green
        "error": 0xED4245,     # Red
        "warning": 0xFEE75C,   # Yellow
        "info": 0x5865F2       # Blue
    })

    @staticmethod
    def _parse_owner_ids() -> list[int]:
        """Parse owner IDs from environment variable."""
        owner_ids_str = os.getenv("OWNER_IDS", "[]")
        try:
            # Handle both JSON array and comma-separated formats
            if owner_ids_str.startswith("["):
                ids = json.loads(owner_ids_str.replace("'", '"'))
            else:
                ids = owner_ids_str.split(",")
            return [int(id_.strip().strip('"').strip("'")) for id_ in ids if id_.strip()]
        except (json.JSONDecodeError, ValueError):
            return []

    @staticmethod
    def _parse_guild_id() -> Optional[int]:
        """Parse guild ID from environment variable."""
        guild_id = os.getenv("GUILD_ID", "")
        if guild_id and guild_id.strip():
            try:
                return int(guild_id.strip())
            except ValueError:
                return None
        return None

    @staticmethod
    def _parse_int_env(key: str) -> Optional[int]:
        """Parse an integer environment variable."""
        value = os.getenv(key, "")
        if value and value.strip():
            try:
                return int(value.strip())
            except ValueError:
                return None
        return None

    @staticmethod
    def _parse_lavalink_nodes() -> list[LavalinkNode]:
        """Parse Lavalink node configuration from environment variables."""
        nodes = []

        # Pick the correct prefix based on environment
        env = os.getenv("ENVIRONMENT", "PROD").upper()
        prefix = "DEV" if env == "DEV" else "PROD"

        host = os.getenv(f"{prefix}_LAVALINK_HOST", "")
        port = int(os.getenv(f"{prefix}_LAVALINK_PORT", "2333"))
        password = os.getenv(f"{prefix}_LAVALINK_PASSWORD", "youshallnotpass")
        secure = os.getenv(f"{prefix}_LAVALINK_SECURE", "false").lower() == "true"

        # Only add the main node if a host is explicitly configured
        if host:
            nodes.append(LavalinkNode(
                host=host,
                port=port,
                password=password,
                identifier=f"{prefix}_MAIN",
                secure=secure
            ))

        # Parse additional nodes from LAVALINK_NODES JSON if provided
        nodes_json = os.getenv("LAVALINK_NODES", "")
        if nodes_json:
            try:
                additional_nodes = json.loads(nodes_json)
                for i, node_data in enumerate(additional_nodes):
                    nodes.append(LavalinkNode(
                        host=node_data.get("host", "localhost"),
                        port=node_data.get("port", 2333),
                        password=node_data.get("password", "youshallnotpass"),
                        identifier=node_data.get("identifier", f"NODE_{i+1}"),
                        secure=node_data.get("secure", False),
                        region=node_data.get("region")
                    ))
            except json.JSONDecodeError:
                pass

        return nodes

    @property
    def is_dev(self) -> bool:
        """Returns True if running in development mode."""
        return self.environment == "DEV"

    @property
    def is_prod(self) -> bool:
        """Returns True if running in production mode."""
        return self.environment == "PROD"

    def is_owner(self, user_id: int) -> bool:
        """Check if a user is a bot owner."""
        return user_id in self.owner_ids
