import discord
from discord.ext import commands
import os

class Help(commands.Cog):
    """
    Cog para o comando de ajuda dinâmico.
    """
    def __init__(self, client: commands.Bot):
        self.client = client
        # Mapeia o nome da pasta para o nome da categoria no embed.
        self.category_mapping = {
            'admin': '👑 Comandos de Administrador',
            'super_admin': '⭐ Comandos de Super Admin',
            'moderation': '🛡️ Comandos de Moderação',
            'geral': '👤 Comandos Gerais',
        }

    @commands.command(name="help", aliases=['ajuda'])
    async def help_command(self, ctx: commands.Context):
        """Mostra uma mensagem de ajuda com os comandos que o usuário pode usar."""
        await self.client.delete_message_user(ctx)

        embed = self.client.create_user_embed(
            ctx.author,
            ctx.guild,
            "Aqui estão os comandos disponíveis para você, organizados por categoria.",
            title="Central de Ajuda"
        )
        embed.set_thumbnail(url=self.client.user.display_avatar.url)

        categorized_commands = {cat: [] for cat in self.category_mapping.values()}

        for cog_name, cog in self.client.cogs.items():
            # Determina a categoria pela pasta do cog
            module_path = cog.__module__.split('.')
            if len(module_path) > 2 and module_path[0] == 'commands':
                folder_name = module_path[1]
                category = self.category_mapping.get(folder_name)

                if category:
                    for command in cog.get_commands():
                        try:
                            if await command.can_run(ctx):
                                categorized_commands[category].append(f"`{command.name}`: {command.help or 'Sem descrição.'}")
                        except commands.CommandError:
                            continue

        for category, commands_list in categorized_commands.items():
            if commands_list:
                embed.add_field(name=category, value="\n".join(commands_list), inline=False)

        await ctx.send(embed=embed, delete_after=120)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Help(client))