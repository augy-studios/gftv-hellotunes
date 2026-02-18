"""Script to clear synced slash commands (global, guild, or both)."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


async def clear():
    client = commands.Bot(command_prefix="!", intents=discord.Intents.default())

    async with client:
        await client.login(os.getenv("TOKEN"))

        # Clear global commands
        client.tree.clear_commands(guild=None)
        await client.tree.sync()
        print("Global commands cleared.")

        # Clear guild commands if GUILD_ID is set
        guild_id = os.getenv("GUILD_ID", "")
        if guild_id.strip():
            guild = discord.Object(id=int(guild_id))
            client.tree.clear_commands(guild=guild)
            await client.tree.sync(guild=guild)
            print(f"Guild commands cleared for {guild_id}.")

        print("Done.")


asyncio.run(clear())
