from discord.ext import commands

class Roles(commands.Cog):
    """Define roles y sus características para el juego de Mafia."""

    def __init__(self, bot):
        self.bot = bot

        # Diccionario con roles
        # Cada rol tiene un nombre, descripción y habilidad
        self.roles = {
            "Mafioso": {
                "descripcion": "Miembro de la mafia. Se elimina a un jugador cada noche.",
                "habilidad": "Elegir una víctima durante la noche."
            },
            "Policía": {
                "descripcion": "Detecta si un jugador es mafioso.",
                "habilidad": "Investigar a un jugador cada noche."
            },
            "Doctor": {
                "descripcion": "Protege a un jugador de ser eliminado.",
                "habilidad": "Salvar a un jugador durante la noche."
            },
            "Pueblerino": {
                "descripcion": "No tiene habilidades especiales.",
                "habilidad": "Votar durante el día para eliminar sospechosos."
            }
        }

    def get_roles_list(self):
        """Devuelve la lista de roles disponibles."""
        return list(self.roles.keys())

    def get_role_info(self, role_name):
        """Devuelve la info de un rol dado su nombre."""
        return self.roles.get(role_name, None)

# CONFIGURACIÓN DEL COG
async def setup(bot):
    await bot.add_cog(Roles(bot))
