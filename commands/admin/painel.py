import discord
from discord.ext import commands
import sqlite3
import os
from utils.checks import has_admin_role
from database.database_manager import DB_FILE
from ui.base_view import BaseView

# Importa as views que serão usadas nos botões
from ui.birthday_views import AdminBirthdayManagementView
from commands.admin.configLog import ConfigLogView, create_main_panel_view
from commands.super_admin.configPerm import ConfigPermView
from commands.admin.configaparencia import ConfigAparenciaView

class MainPanelView(BaseView):
    """
    A View principal do painel de controle. Contém os botões para as principais
    funcionalidades administrativas.
    """
    def __init__(self, author: discord.User, bot_instance: commands.Bot, guild: discord.Guild):
        super().__init__(author=author, timeout=900.0)
        self.bot_instance = bot_instance
        self.guild = guild
        self.original_embed, self.original_file = self._create_initial_embed()

    def _create_initial_embed(self):
        """Cria o embed inicial com a imagem."""
        image_path = "images/og_painel.png"
        if not os.path.exists(image_path):
            print(f"Aviso: A imagem do painel não foi encontrada em '{image_path}'. O embed será criado sem imagem.")
            return self.bot_instance.create_user_embed(self.author, self.guild, "Bem-vindo ao centro de controle...", title="Painel de Controle"), None
        file = discord.File(image_path, filename="painel.png")
        embed = self.bot_instance.create_user_embed(
            self.author,
            self.guild,
            "Bem-vindo ao centro de controle do bot. Selecione uma opção abaixo para gerenciar as configurações do servidor.",
            title="Painel de Controle Administrativo"
        )
        embed.set_image(url="attachment://painel.png")
        return embed, file # file pode ser None

    @discord.ui.button(label="Aniversários", style=discord.ButtonStyle.primary, emoji="🎂")
    async def manage_birthdays(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Abre o painel de gerenciamento de aniversários."""
        view = AdminBirthdayManagementView(author=interaction.user, bot_instance=self.bot_instance, guild=self.guild)
        embed = self.bot_instance.create_user_embed(
            interaction.user, self.guild, "Adicione, remova ou altere os aniversários dos membros.", title="Gerenciamento de Aniversários"
        )
        await interaction.response.edit_message(embed=embed, view=view, attachments=[])

    @discord.ui.button(label="Logs", style=discord.ButtonStyle.secondary, emoji="📋")
    async def configure_logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Abre o painel de configuração de logs."""
        view = ConfigLogView(author=interaction.user, bot_instance=self.bot_instance, guild=self.guild)
        embed = await view.generate_embed()
        await interaction.response.edit_message(embed=embed, view=view, attachments=[])

    @discord.ui.button(label="Permissões", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def configure_perms(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Abre o painel de configuração de permissões de admin."""
        view = ConfigPermView(author=interaction.user, bot_instance=self.bot_instance, guild=self.guild)
        embed = await view.generate_embed()
        await interaction.response.edit_message(embed=embed, view=view, attachments=[])

    @discord.ui.button(label="Aparência", style=discord.ButtonStyle.secondary, emoji="🎨", row=1)
    async def configure_appearance(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Abre o painel de configuração de aparência."""
        view = ConfigAparenciaView(author=interaction.user, bot_instance=self.bot_instance, guild=self.guild)
        embed = await view.generate_embed()
        await interaction.response.edit_message(embed=embed, view=view, attachments=[])


class Painel(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="painel", help="Abre o painel de controle administrativo do bot.")
    @commands.check(has_admin_role)
    async def painel(self, ctx: commands.Context):
        """
        Abre um painel interativo para gerenciar várias configurações do bot
        no servidor, como logs, aniversários e permissões.
        """
        await self.client.delete_message_user(ctx)
        view = MainPanelView(author=ctx.author, bot_instance=self.client, guild=ctx.guild)
        kwargs = {'embed': view.original_embed, 'view': view, 'delete_after': 900}
        if view.original_file:
            kwargs['file'] = view.original_file
        
        await ctx.send(**kwargs)

    @painel.error
    async def painel_error(self, ctx: commands.Context, error):
        """Trata erros para o comando painel."""
        await self.client.delete_message_user(ctx)
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                f"{ctx.author.mention}, você não tem permissão para usar este comando.",
                delete_after=10
            )
        else:
            print(f"Erro no comando r.painel: {error}")
            await ctx.send(f"{ctx.author.mention}, ocorreu um erro ao executar o comando.", delete_after=10)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Painel(client))