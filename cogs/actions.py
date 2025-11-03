from discord.ext import commands
from discord import app_commands
import discord

class Actions(commands.Cog):
    """Gestión de acciones de roles durante la noche."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="accion", description="Realiza tu acción nocturna sobre otro jugador")
    @app_commands.describe(objetivo="Jugador sobre el que aplicar la acción")
    async def accion(self, interaction: discord.Interaction, objetivo: discord.User):
        await interaction.response.defer(ephemeral=True)

        channel_id = interaction.channel_id
        jugador_id = interaction.user.id
        partidas = self.bot.partidas

        if channel_id not in partidas:
            await interaction.followup.send("❌ No hay ninguna partida en este canal.", ephemeral=True)
            return

        partida = partidas[channel_id]

        if partida["estado"] != "en curso":
            await interaction.followup.send("🚫 La partida no está en curso.", ephemeral=True)
            return

        if jugador_id not in partida["roles"]:
            await interaction.followup.send("❌ No estás participando en esta partida.", ephemeral=True)
            return

        rol = partida["roles"][jugador_id]

        # Creamos un diccionario temporal de acciones de la noche si no existe
        if "acciones_noche" not in partida:
            partida["acciones_noche"] = {}

        # Registrar la acción según el rol
        if rol == "Mafioso":
            partida["acciones_noche"][jugador_id] = {"tipo": "matar", "objetivo": objetivo.id}
            await interaction.followup.send(f"🔪 Has decidido atacar a {objetivo.mention}.", ephemeral=True)

        elif rol == "Doctor":
            partida["acciones_noche"][jugador_id] = {"tipo": "proteger", "objetivo": objetivo.id}
            await interaction.followup.send(f"🩺 Has decidido proteger a {objetivo.mention}.", ephemeral=True)

        elif rol == "Policía":
            partida["acciones_noche"][jugador_id] = {"tipo": "investigar", "objetivo": objetivo.id}
            await interaction.followup.send(f"🕵️ Has decidido investigar a {objetivo.mention}.", ephemeral=True)

        else:
            await interaction.followup.send("⚠️ Tu rol no tiene acción nocturna.", ephemeral=True)


# CONFIGURACIÓN DEL COG
async def setup(bot):
    await bot.add_cog(Actions(bot))
