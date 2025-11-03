# cogs/setup_game.py
import discord
from discord import app_commands
from discord.ext import commands
import random

class SetupGame(commands.Cog):
    """Comandos iniciales para crear y gestionar partidas de Mafia."""

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "partidas"):
            bot.partidas = {}  # Diccionario global de partidas

    # /crear_partida
    @app_commands.command(name="crear_partida", description="Crea una nueva partida de Mafia en este canal.")
    async def crear_partida(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        channel_id = interaction.channel_id
        partidas = self.bot.partidas

        if channel_id in partidas:
            await interaction.followup.send("⚠️ Ya hay una partida activa en este canal.", ephemeral=True)
            return

        partidas[channel_id] = {
            "creador": interaction.user.id,
            "jugadores": [interaction.user.id],
            "estado": "esperando",
        }

        await interaction.followup.send(
            f"🎲 ¡{interaction.user.mention} ha creado una nueva partida de Mafia!\n"
            f"Usá `/unirse` para participar. Cuando estén listos, el creador puede usar `/empezar`.",
            allowed_mentions=discord.AllowedMentions(users=True)
        )

    # /unirse
    @app_commands.command(name="unirse", description="Únete a la partida actual de Mafia.")
    async def unirse(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        partidas = self.bot.partidas

        if channel_id not in partidas:
            await interaction.response.send_message("❌ No hay ninguna partida creada en este canal.", ephemeral=True)
            return

        partida = partidas[channel_id]

        if partida["estado"] != "esperando":
            await interaction.response.send_message("🚫 La partida ya empezó, no podés unirte ahora.", ephemeral=True)
            return

        if interaction.user.id in partida["jugadores"]:
            await interaction.response.send_message("⚠️ Ya estás unido a la partida.", ephemeral=True)
            return

        partida["jugadores"].append(interaction.user.id)

        await interaction.response.send_message(
            f"✅ {interaction.user.mention} se ha unido a la partida.",
            allowed_mentions=discord.AllowedMentions(users=True)
        )

    # /empezar
    @app_commands.command(name="empezar", description="Inicia la partida de Mafia.")
    async def empezar(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)

        channel_id = interaction.channel_id
        partidas = self.bot.partidas

        if channel_id not in partidas:
            await interaction.followup.send("❌ No hay ninguna partida en este canal.", ephemeral=True)
            return

        partida = partidas[channel_id]

        if interaction.user.id != partida["creador"]:
            await interaction.followup.send("🚫 Solo el creador de la partida puede iniciarla.", ephemeral=True)
            return

        jugadores = partida["jugadores"]
        if len(jugadores) < 4:
            await interaction.followup.send("👥 Se necesitan al menos 4 jugadores para empezar.", ephemeral=True)
            return

        # Asignación de roles
        roles = ["Mafioso", "Policía", "Doctor"]
        while len(roles) < len(jugadores):
            roles.append("Pueblerino")

        random.shuffle(roles)
        partida["roles"] = dict(zip(jugadores, roles))
        partida["estado"] = "en curso"

        # Mensaje público en el canal
        await interaction.followup.send(
            f"🚀 La partida ha comenzado. Preparense, la noche caerá pronto...",
            allowed_mentions=discord.AllowedMentions(users=True)
        )

        # Enviar DM con roles
        for jugador_id, rol in partida["roles"].items():
            user = await self.bot.fetch_user(jugador_id)
            try:
                await user.send(f"🎭 Tu rol en la partida de Mafia es: **{rol}**")
            except discord.Forbidden:
                await interaction.followup.send(
                    f"⚠️ No pude enviar DM a {user.mention}. (Debe habilitar mensajes privados)",
                    ephemeral=True
                )

        # Iniciar automáticamente la fase de noche si el cog Phases está cargado
        phases_cog = self.bot.get_cog("Phases")
        if phases_cog:
            self.bot.loop.create_task(phases_cog.start_night_phase(channel_id))


# CONFIGURACIÓN DEL COG
async def setup(bot):
    await bot.add_cog(SetupGame(bot))
