# cogs/phases.py
from discord.ext import commands
import asyncio

class Phases(commands.Cog):
    """Maneja las fases del juego: día, noche y resolución de acciones."""

    def __init__(self, bot):
        self.bot = bot
        self.day_duration = 60
        self.night_duration = 60

    async def start_night_phase(self, channel_id):
        partida = self.bot.partidas.get(channel_id)
        if not partida or partida["estado"] != "en curso":
            return

        canal = self.bot.get_channel(channel_id)
        await canal.send("🌙 **Comienza la noche. Todos cierren los ojos.**")

        # Identificar jugadores que tienen acción nocturna
        jugadores_con_accion = [
            jugador_id
            for jugador_id, rol in partida["roles"].items()
            if rol in ["Mafioso", "Policía", "Doctor"]
        ]

        if not jugadores_con_accion:
            await canal.send("🌙 Esta noche no hay acciones. Avanzando al día...")
            await self.start_day_phase(channel_id)
            return

        # Crear diccionario para registrar acciones si no existe
        if "acciones_noche" not in partida:
            partida["acciones_noche"] = {}

        # Notificar a los jugadores por DM
        for jugador_id in jugadores_con_accion:
            user = await self.bot.fetch_user(jugador_id)
            rol = partida["roles"][jugador_id]
            if rol == "Mafioso":
                await user.send("🌒 Es de noche. Usa `/accion @jugador` para elegir tu víctima.")
            elif rol == "Policía":
                await user.send("🌒 Es de noche. Usa `/accion @jugador` para investigar a un jugador.")
            elif rol == "Doctor":
                await user.send("🌒 Es de noche. Usa `/accion @jugador` para proteger a alguien.")

        # Espera activa: no duerme tiempo fijo, espera a que todos actúen
        while True:
            await asyncio.sleep(1)  # pequeña espera para no bloquear el loop
            if all(jugador_id in partida["acciones_noche"] for jugador_id in jugadores_con_accion):
                break

        # Resolver acciones
        await self.resolve_night_actions(channel_id)

        # Pasar al día
        await self.start_day_phase(channel_id)

    async def resolve_night_actions(self, channel_id):
        partida = self.bot.partidas.get(channel_id)
        if not partida or "acciones_noche" not in partida:
            return

        acciones = partida["acciones_noche"]
        muertes = []
        protegidos = set()

        # Primero, recopilar objetivos de Doctor
        for jugador_id, accion in acciones.items():
            if accion["tipo"] == "proteger":
                protegidos.add(accion["objetivo"])

        # Luego, resolver ataques de Mafioso
        for jugador_id, accion in acciones.items():
            if accion["tipo"] == "matar":
                objetivo_id = accion["objetivo"]
                if objetivo_id not in protegidos:
                    muertes.append(objetivo_id)

        # Notificar muertes en el canal
        canal = self.bot.get_channel(channel_id)
        if muertes:
            menciones = [f"<@{uid}>" for uid in muertes]
            await canal.send(f"💀 Durante la noche, los siguientes jugadores han sido eliminados: {', '.join(menciones)}")
            for uid in muertes:
                partida["roles"].pop(uid, None)
                partida["jugadores"].remove(uid)
        else:
            await canal.send("🌙 La noche ha pasado sin muertes.")

        # Notificar resultados de investigación de Policía
        for jugador_id, accion in acciones.items():
            if accion["tipo"] == "investigar":
                objetivo_id = accion["objetivo"]
                rol_objetivo = partida["roles"].get(objetivo_id)
                user = await self.bot.fetch_user(jugador_id)
                if rol_objetivo:
                    await user.send(f"🕵️ Resultado de tu investigación: {rol_objetivo}")
                else:
                    await user.send("🕵️ Tu objetivo ya no está en la partida.")

        # Limpiar acciones para la próxima ronda
        partida["acciones_noche"] = {}

    async def start_day_phase(self, channel_id):
        partida = self.bot.partidas.get(channel_id)
        if not partida or partida["estado"] != "en curso":
            return

        canal = self.bot.get_channel(channel_id)
        await canal.send("☀️ **Amanece! Discute y vota a un sospechoso.**")

        # Espera duración del día
        await asyncio.sleep(self.day_duration)

        # Vuelve a la noche automáticamente
        await self.start_night_phase(channel_id)

    # Comando para testing
    @commands.command(name="empezar_fases")
    async def empezar_fases(self, ctx):
        channel_id = ctx.channel.id
        if channel_id not in self.bot.partidas:
            await ctx.send("❌ No hay ninguna partida en este canal.")
            return
        await ctx.send("🚀 Iniciando ciclo día/noche...")
        await self.start_night_phase(channel_id)

async def setup(bot):
    await bot.add_cog(Phases(bot))
