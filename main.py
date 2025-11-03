import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Inicializa colorama para logs coloridos
init(autoreset=True)

# Cargar variables del archivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configurar Intents (permisos del bot)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # necesario para manejar jugadores

# Crear la instancia del bot
bot = commands.Bot(
    command_prefix="!",  # aún se pueden usar comandos clásicos si querés
    intents=intents,
    help_command=None
)

# EVENTOS PRINCIPALES
@bot.event
async def on_ready():
    print(f"{Fore.GREEN}✅ Bot conectado como {bot.user}")
    print(f"{Fore.CYAN}🌐 Conectado a {len(bot.guilds)} servidores.")

    # Sincronizar slash commands después de cargar cogs y estar listo
    try:
        synced = await bot.tree.sync()
        print(f"{Fore.GREEN}✅ {len(synced)} comandos slash sincronizados.")
    except Exception as e:
        print(f"{Fore.RED}❌ Error al sincronizar comandos: {e}")

    print(f"{Fore.MAGENTA}🚀 Listo para jugar Mafia!")

@bot.event
async def on_command_error(ctx, error):
    """Captura errores de comandos clásicos (!comando)"""
    await ctx.send(f"❌ Error: {error}")

# CARGA AUTOMÁTICA DE COGS
async def load_cogs():
    """Carga automática de todos los módulos del directorio /cogs"""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"{Fore.BLUE}🔹 Cargado módulo: {filename}")
            except Exception as e:
                print(f"{Fore.RED}❌ Error al cargar {filename}: {e}")

# EJECUCIÓN DEL BOT
async def main():
    async with bot:
        # Primero cargamos todos los cogs
        await load_cogs()
        # Finalmente iniciamos el bot
        try:
            await bot.start(TOKEN)
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}🔴 Bot detenido por el usuario.")

if __name__ == "__main__":
    asyncio.run(main())
