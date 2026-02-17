"""
Filters Cog - Audio filters and effects for Augy Music Bot.
"""

import logging
import wavelink
import discord
from discord import app_commands
from discord.ext import commands
from typing import cast

logger = logging.getLogger(__name__)


class Filters(commands.Cog):
    """Audio filter commands for music playback."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _get_player(self, interaction: discord.Interaction) -> wavelink.Player | None:
        """Get the player for the guild."""
        return cast(wavelink.Player, interaction.guild.voice_client)

    async def _check_player(self, interaction: discord.Interaction) -> wavelink.Player | None:
        """Check if player exists and is playing."""
        player = self._get_player(interaction)
        if not player:
            await interaction.response.send_message("❌ No active player!", ephemeral=True)
            return None
        if not player.playing:
            await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)
            return None
        return player

    # ============== Filter Commands ==============

    @app_commands.command(name="bassboost", description="Toggle bass boost filter")
    @app_commands.describe(level="Bass boost level (0-5, 0 = off)")
    async def bassboost(self, interaction: discord.Interaction, level: int = 3) -> None:
        """Apply bass boost filter."""
        player = await self._check_player(interaction)
        if not player:
            return

        if not 0 <= level <= 5:
            return await interaction.response.send_message(
                "❌ Level must be between 0 and 5!", ephemeral=True
            )

        filters = player.filters

        if level == 0:
            filters.equalizer.reset()
            await player.set_filters(filters)
            return await interaction.response.send_message("🔊 Bass boost disabled!")

        # Apply bass boost EQ
        bands = [
            {"band": 0, "gain": 0.2 * level},
            {"band": 1, "gain": 0.15 * level},
            {"band": 2, "gain": 0.1 * level},
            {"band": 3, "gain": 0.05 * level},
            {"band": 4, "gain": 0.0},
        ]
        filters.equalizer.set(bands=bands)
        await player.set_filters(filters)

        await interaction.response.send_message(f"🔊 Bass boost set to level **{level}**!")

    @app_commands.command(name="nightcore", description="Toggle nightcore filter")
    async def nightcore(self, interaction: discord.Interaction) -> None:
        """Apply nightcore filter (faster + higher pitch)."""
        player = await self._check_player(interaction)
        if not player:
            return

        filters = player.filters

        # Check if already applied
        if filters.timescale.speed == 1.25:
            filters.timescale.reset()
            await player.set_filters(filters)
            return await interaction.response.send_message("🌙 Nightcore disabled!")

        filters.timescale.set(speed=1.25, pitch=1.25, rate=1.0)
        await player.set_filters(filters)
        await interaction.response.send_message("🌙 Nightcore enabled!")

    @app_commands.command(name="vaporwave", description="Toggle vaporwave filter")
    async def vaporwave(self, interaction: discord.Interaction) -> None:
        """Apply vaporwave filter (slower + lower pitch)."""
        player = await self._check_player(interaction)
        if not player:
            return

        filters = player.filters

        # Check if already applied
        if filters.timescale.speed == 0.8:
            filters.timescale.reset()
            await player.set_filters(filters)
            return await interaction.response.send_message("🌊 Vaporwave disabled!")

        filters.timescale.set(speed=0.8, pitch=0.8, rate=1.0)
        await player.set_filters(filters)
        await interaction.response.send_message("🌊 Vaporwave enabled!")

    @app_commands.command(name="karaoke", description="Toggle karaoke filter")
    async def karaoke(self, interaction: discord.Interaction) -> None:
        """Apply karaoke filter (reduces vocals)."""
        player = await self._check_player(interaction)
        if not player:
            return

        filters = player.filters

        # Check if already applied
        if filters.karaoke.level == 1.0:
            filters.karaoke.reset()
            await player.set_filters(filters)
            return await interaction.response.send_message("🎤 Karaoke disabled!")

        filters.karaoke.set(level=1.0, mono_level=1.0, filter_band=220.0, filter_width=100.0)
        await player.set_filters(filters)
        await interaction.response.send_message("🎤 Karaoke enabled! (vocals reduced)")

    @app_commands.command(name="tremolo", description="Toggle tremolo filter")
    @app_commands.describe(
        frequency="Tremolo frequency (0.1-14.0)",
        depth="Tremolo depth (0.0-1.0)"
    )
    async def tremolo(
        self,
        interaction: discord.Interaction,
        frequency: float = 4.0,
        depth: float = 0.5
    ) -> None:
        """Apply tremolo filter (wavering volume)."""
        player = await self._check_player(interaction)
        if not player:
            return

        if not 0.1 <= frequency <= 14.0:
            return await interaction.response.send_message(
                "❌ Frequency must be between 0.1 and 14.0!", ephemeral=True
            )
        if not 0.0 <= depth <= 1.0:
            return await interaction.response.send_message(
                "❌ Depth must be between 0.0 and 1.0!", ephemeral=True
            )

        filters = player.filters

        if frequency == 0.1 and depth == 0.0:
            filters.tremolo.reset()
            await player.set_filters(filters)
            return await interaction.response.send_message("〰️ Tremolo disabled!")

        filters.tremolo.set(frequency=frequency, depth=depth)
        await player.set_filters(filters)
        await interaction.response.send_message(
            f"〰️ Tremolo enabled! (freq: {frequency}, depth: {depth})"
        )

    @app_commands.command(name="vibrato", description="Toggle vibrato filter")
    @app_commands.describe(
        frequency="Vibrato frequency (0.1-14.0)",
        depth="Vibrato depth (0.0-1.0)"
    )
    async def vibrato(
        self,
        interaction: discord.Interaction,
        frequency: float = 4.0,
        depth: float = 0.5
    ) -> None:
        """Apply vibrato filter (wavering pitch)."""
        player = await self._check_player(interaction)
        if not player:
            return

        if not 0.1 <= frequency <= 14.0:
            return await interaction.response.send_message(
                "❌ Frequency must be between 0.1 and 14.0!", ephemeral=True
            )
        if not 0.0 <= depth <= 1.0:
            return await interaction.response.send_message(
                "❌ Depth must be between 0.0 and 1.0!", ephemeral=True
            )

        filters = player.filters

        if frequency == 0.1 and depth == 0.0:
            filters.vibrato.reset()
            await player.set_filters(filters)
            return await interaction.response.send_message("🎵 Vibrato disabled!")

        filters.vibrato.set(frequency=frequency, depth=depth)
        await player.set_filters(filters)
        await interaction.response.send_message(
            f"🎵 Vibrato enabled! (freq: {frequency}, depth: {depth})"
        )

    @app_commands.command(name="rotation", description="Toggle 8D/rotation filter")
    @app_commands.describe(speed="Rotation speed in Hz (0 to disable)")
    async def rotation(self, interaction: discord.Interaction, speed: float = 0.2) -> None:
        """Apply 8D/rotation filter (audio rotates around your head)."""
        player = await self._check_player(interaction)
        if not player:
            return

        filters = player.filters

        if speed == 0:
            filters.rotation.reset()
            await player.set_filters(filters)
            return await interaction.response.send_message("🔄 Rotation/8D disabled!")

        filters.rotation.set(rotation_hz=speed)
        await player.set_filters(filters)
        await interaction.response.send_message(f"🔄 8D rotation enabled! (speed: {speed} Hz)")

    @app_commands.command(name="lowpass", description="Toggle low pass filter")
    @app_commands.describe(smoothing="Smoothing level (1.0-100.0, higher = more muffled)")
    async def lowpass(self, interaction: discord.Interaction, smoothing: float = 20.0) -> None:
        """Apply low pass filter (muffled sound)."""
        player = await self._check_player(interaction)
        if not player:
            return

        if not 1.0 <= smoothing <= 100.0:
            return await interaction.response.send_message(
                "❌ Smoothing must be between 1.0 and 100.0!", ephemeral=True
            )

        filters = player.filters

        if smoothing == 1.0:
            filters.low_pass.reset()
            await player.set_filters(filters)
            return await interaction.response.send_message("🔉 Low pass disabled!")

        filters.low_pass.set(smoothing=smoothing)
        await player.set_filters(filters)
        await interaction.response.send_message(f"🔉 Low pass enabled! (smoothing: {smoothing})")

    @app_commands.command(name="speed", description="Set playback speed")
    @app_commands.describe(speed="Playback speed (0.5-2.0)")
    async def speed(self, interaction: discord.Interaction, speed: float = 1.0) -> None:
        """Set playback speed."""
        player = await self._check_player(interaction)
        if not player:
            return

        if not 0.5 <= speed <= 2.0:
            return await interaction.response.send_message(
                "❌ Speed must be between 0.5 and 2.0!", ephemeral=True
            )

        filters = player.filters
        filters.timescale.set(speed=speed)
        await player.set_filters(filters)

        emoji = "⏩" if speed > 1 else "⏪" if speed < 1 else "▶️"
        await interaction.response.send_message(f"{emoji} Playback speed set to **{speed}x**!")

    @app_commands.command(name="pitch", description="Set audio pitch")
    @app_commands.describe(pitch="Pitch multiplier (0.5-2.0)")
    async def pitch(self, interaction: discord.Interaction, pitch: float = 1.0) -> None:
        """Set audio pitch."""
        player = await self._check_player(interaction)
        if not player:
            return

        if not 0.5 <= pitch <= 2.0:
            return await interaction.response.send_message(
                "❌ Pitch must be between 0.5 and 2.0!", ephemeral=True
            )

        filters = player.filters
        filters.timescale.set(pitch=pitch)
        await player.set_filters(filters)

        emoji = "🔼" if pitch > 1 else "🔽" if pitch < 1 else "🎵"
        await interaction.response.send_message(f"{emoji} Pitch set to **{pitch}x**!")

    @app_commands.command(name="resetfilters", description="Reset all audio filters")
    async def resetfilters(self, interaction: discord.Interaction) -> None:
        """Reset all audio filters."""
        player = await self._check_player(interaction)
        if not player:
            return

        filters = player.filters
        filters.reset()
        await player.set_filters(filters)

        await interaction.response.send_message("🔄 All filters have been reset!")

    @app_commands.command(name="filters", description="View current active filters")
    async def filters(self, interaction: discord.Interaction) -> None:
        """View current active filters."""
        player = self._get_player(interaction)
        if not player:
            return await interaction.response.send_message("❌ No active player!", ephemeral=True)

        filters = player.filters
        active_filters = []

        # Check each filter
        if filters.equalizer._payload:
            active_filters.append("🔊 **Equalizer/Bass Boost**")

        if filters.timescale.speed != 1.0:
            active_filters.append(f"⏩ **Speed**: {filters.timescale.speed}x")
        if filters.timescale.pitch != 1.0:
            active_filters.append(f"🎵 **Pitch**: {filters.timescale.pitch}x")

        if filters.karaoke.level:
            active_filters.append("🎤 **Karaoke**")

        if filters.tremolo.frequency:
            active_filters.append(f"〰️ **Tremolo**: freq={filters.tremolo.frequency}")

        if filters.vibrato.frequency:
            active_filters.append(f"🎵 **Vibrato**: freq={filters.vibrato.frequency}")

        if filters.rotation.rotation_hz:
            active_filters.append(f"🔄 **8D Rotation**: {filters.rotation.rotation_hz} Hz")

        if filters.low_pass.smoothing:
            active_filters.append(f"🔉 **Low Pass**: smoothing={filters.low_pass.smoothing}")

        embed = discord.Embed(
            title="🎛️ Active Filters",
            color=self.bot.config.color["main"]
        )

        if active_filters:
            embed.description = "\n".join(active_filters)
        else:
            embed.description = "*No filters are currently active.*"

        embed.set_footer(text="Use /resetfilters to clear all filters")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Setup function for the cog."""
    await bot.add_cog(Filters(bot))
