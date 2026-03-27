"""
Settings Cog - Server configuration.
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

logger = logging.getLogger(__name__)


class Settings(commands.Cog):
    """Server configuration commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # ============== Prefix Commands ==============

    @app_commands.command(name="prefix", description="Set the command prefix for this server")
    @app_commands.describe(prefix="New prefix (1-5 characters)")
    @app_commands.default_permissions(manage_guild=True)
    async def prefix(self, interaction: discord.Interaction, prefix: str) -> None:
        """Set the server prefix."""
        if len(prefix) > 5:
            return await interaction.response.send_message(
                "❌ Prefix must be 5 characters or less!",
                ephemeral=True
            )

        await self.bot.db.set_prefix(interaction.guild.id, prefix)
        await interaction.response.send_message(
            f"✅ Prefix set to `{prefix}`\n"
            f"You can also always use slash commands or mention the bot!"
        )

    # ============== Language Commands ==============

    @app_commands.command(name="language", description="Set the bot language for this server")
    @app_commands.describe(language="Language code")
    @app_commands.choices(language=[
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="Spanish", value="es"),
        app_commands.Choice(name="French", value="fr"),
        app_commands.Choice(name="German", value="de"),
        app_commands.Choice(name="Portuguese", value="pt"),
        app_commands.Choice(name="Japanese", value="ja"),
        app_commands.Choice(name="Korean", value="ko"),
        app_commands.Choice(name="Chinese", value="zh"),
    ])
    @app_commands.default_permissions(manage_guild=True)
    async def language(self, interaction: discord.Interaction, language: str) -> None:
        """Set the server language."""
        await self.bot.db.set_language(interaction.guild.id, language)

        language_names = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "pt": "Portuguese",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese"
        }

        await interaction.response.send_message(
            f"✅ Language set to **{language_names.get(language, language)}**!"
        )

    # ============== DJ Role Commands ==============

    dj_group = app_commands.Group(name="dj", description="DJ role management")

    @dj_group.command(name="add", description="Add a DJ role")
    @app_commands.describe(role="Role to add as DJ")
    @app_commands.default_permissions(manage_guild=True)
    async def dj_add(self, interaction: discord.Interaction, role: discord.Role) -> None:
        """Add a DJ role."""
        success = await self.bot.db.add_dj_role(interaction.guild.id, role.id)

        if success:
            await interaction.response.send_message(
                f"✅ Added {role.mention} as a DJ role!"
            )
        else:
            await interaction.response.send_message(
                f"❌ {role.mention} is already a DJ role!",
                ephemeral=True
            )

    @dj_group.command(name="remove", description="Remove a DJ role")
    @app_commands.describe(role="Role to remove from DJ")
    @app_commands.default_permissions(manage_guild=True)
    async def dj_remove(self, interaction: discord.Interaction, role: discord.Role) -> None:
        """Remove a DJ role."""
        success = await self.bot.db.remove_dj_role(interaction.guild.id, role.id)

        if success:
            await interaction.response.send_message(
                f"✅ Removed {role.mention} from DJ roles!"
            )
        else:
            await interaction.response.send_message(
                f"❌ {role.mention} is not a DJ role!",
                ephemeral=True
            )

    @dj_group.command(name="list", description="List all DJ roles")
    async def dj_list(self, interaction: discord.Interaction) -> None:
        """List all DJ roles."""
        role_ids = await self.bot.db.get_dj_roles(interaction.guild.id)

        if not role_ids:
            return await interaction.response.send_message(
                "📋 No DJ roles configured.\n"
                "Use `/dj add @role` to add DJ roles.",
                ephemeral=True
            )

        roles = []
        for role_id in role_ids:
            role = interaction.guild.get_role(role_id)
            if role:
                roles.append(role.mention)

        embed = discord.Embed(
            title="🎧 DJ Roles",
            description="\n".join(roles) if roles else "*No valid DJ roles found.*",
            color=self.bot.config.color["main"]
        )

        await interaction.response.send_message(embed=embed)

    @dj_group.command(name="only", description="Toggle DJ-only mode")
    @app_commands.describe(enabled="Enable or disable DJ-only mode")
    @app_commands.default_permissions(manage_guild=True)
    async def dj_only(self, interaction: discord.Interaction, enabled: bool) -> None:
        """Toggle DJ-only mode."""
        await self.bot.db.set_dj_only(interaction.guild.id, enabled)

        if enabled:
            await interaction.response.send_message(
                "✅ DJ-only mode **enabled**!\n"
                "Only users with DJ roles can use music commands."
            )
        else:
            await interaction.response.send_message(
                "✅ DJ-only mode **disabled**!\n"
                "Everyone can use music commands."
            )

    # ============== 24/7 Mode ==============

    @app_commands.command(name="247", description="Toggle 24/7 mode (stay connected)")
    @app_commands.default_permissions(manage_guild=True)
    async def stay_connected(self, interaction: discord.Interaction) -> None:
        """Toggle 24/7 mode."""
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        current = settings.stay_connected if settings else False
        new_value = not current

        await self.bot.db.set_stay_connected(interaction.guild.id, new_value)

        if new_value:
            await interaction.response.send_message(
                "✅ 24/7 mode **enabled**!\n"
                "I'll stay connected to voice even when alone."
            )
        else:
            await interaction.response.send_message(
                "✅ 24/7 mode **disabled**!\n"
                "I'll disconnect when left alone."
            )

    # ============== Default Volume ==============

    @app_commands.command(name="defaultvolume", description="Set the default volume for this server")
    @app_commands.describe(volume="Default volume level (1-100)")
    @app_commands.default_permissions(manage_guild=True)
    async def default_volume(self, interaction: discord.Interaction, volume: int) -> None:
        """Set default volume."""
        if not 1 <= volume <= 100:
            return await interaction.response.send_message(
                "❌ Volume must be between 1 and 100!",
                ephemeral=True
            )

        await self.bot.db.set_default_volume(interaction.guild.id, volume)
        await interaction.response.send_message(
            f"🔊 Default volume set to **{volume}%**!"
        )

    # ============== View Settings ==============

    @app_commands.command(name="settings", description="View current server settings")
    async def settings(self, interaction: discord.Interaction) -> None:
        """View current server settings."""
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        dj_roles = await self.bot.db.get_dj_roles(interaction.guild.id)

        embed = discord.Embed(
            title="⚙️ Server Settings",
            color=self.bot.config.color["main"]
        )

        if settings:
            embed.add_field(
                name="Prefix",
                value=f"`{settings.prefix}`",
                inline=True
            )
            embed.add_field(
                name="Language",
                value=settings.language.upper(),
                inline=True
            )
            embed.add_field(
                name="Default Volume",
                value=f"{settings.default_volume}%",
                inline=True
            )
            embed.add_field(
                name="24/7 Mode",
                value="✅ Enabled" if settings.stay_connected else "❌ Disabled",
                inline=True
            )
            embed.add_field(
                name="DJ Only",
                value="✅ Enabled" if settings.dj_only else "❌ Disabled",
                inline=True
            )
            embed.add_field(
                name="Announce Songs",
                value="✅ Enabled" if settings.announce_songs else "❌ Disabled",
                inline=True
            )
        else:
            embed.description = "*Using default settings*"
            embed.add_field(name="Prefix", value=f"`{self.bot.config.default_prefix}`", inline=True)
            embed.add_field(name="Language", value="EN", inline=True)
            embed.add_field(name="Default Volume", value="100%", inline=True)

        # DJ Roles
        if dj_roles:
            roles = [f"<@&{role_id}>" for role_id in dj_roles]
            embed.add_field(
                name=f"DJ Roles ({len(dj_roles)})",
                value=", ".join(roles[:5]) + ("..." if len(roles) > 5 else ""),
                inline=False
            )

        embed.set_footer(text="Use /prefix, /language, /247, /dj to configure")

        await interaction.response.send_message(embed=embed)

    # ============== Reset Settings ==============

    @app_commands.command(name="reset", description="Reset all server settings to default")
    @app_commands.default_permissions(administrator=True)
    async def reset(self, interaction: discord.Interaction) -> None:
        """Reset all server settings."""
        # Confirmation view
        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.value = None

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.value = True
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.value = False
                self.stop()

        view = ConfirmView()
        await interaction.response.send_message(
            "⚠️ Are you sure you want to reset all settings?\n"
            "This will reset prefix, DJ roles, 24/7 mode, and all other settings.",
            view=view
        )

        await view.wait()

        if view.value:
            # Reset by recreating the guild entry
            await self.bot.db.create_guild(interaction.guild.id)
            await interaction.edit_original_response(
                content="✅ All settings have been reset to default!",
                view=None
            )
        else:
            await interaction.edit_original_response(
                content="❌ Reset cancelled.",
                view=None
            )


async def setup(bot: commands.Bot) -> None:
    """Setup function for the cog."""
    await bot.add_cog(Settings(bot))
