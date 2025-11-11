import discord
from discord.ext import commands
import sqlite3
from database.database_manager import DB_FILE
from utils.checks import is_super_admin
from ui.base_view import BaseView

def create_main_panel_view(author: discord.User, bot_instance: commands.Bot, guild: discord.Guild):
    """
    Função auxiliar para evitar importação circular.
    Cria e retorna uma instância da MainPanelView.
    """
    # Importação local para evitar dependência circular
    from commands.admin.painel import MainPanelView
    return MainPanelView(author=author, bot_instance=bot_instance, guild=guild)

PERM_TYPES = {
    "admin": {"name": "Admin", "table": "perm_roles", "description": "Cargos com acesso a comandos administrativos."},
    "moderador": {"name": "Moderador", "table": "mod_roles", "description": "Cargos com acesso a comandos de moderação (ban, kick, etc.)."}
}

class ConfigPermView(BaseView):
    def __init__(self, author: discord.User, bot_instance, guild: discord.Guild):
        super().__init__(author=author, timeout=900.0)
        self.bot_instance = bot_instance
        self.guild = guild
        self.add_item(self.PermTypeSelect())
        self.add_item(self.BackButton())

    async def generate_embed(self) -> discord.Embed:
        embed = self.bot_instance.create_user_embed(self.author, self.guild, "Configure os cargos de permissão do bot.", title="Painel de Configuração de Permissões")

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            for key, perm_info in PERM_TYPES.items():
                cursor.execute(f"SELECT role_id FROM {perm_info['table']} WHERE guild_id = ?", (self.guild.id,))
                role_ids = {row[0] for row in cursor.fetchall()}
                
                roles = [self.guild.get_role(rid) for rid in role_ids]
                value = " ".join([r.mention for r in roles if r]) or "`Nenhum cargo definido`"
                embed.add_field(name=f"**{perm_info['name']}**", value=value, inline=False)
        
        return embed

    async def update_message(self, interaction: discord.Interaction):
        embed = await self.generate_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    class BackButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="Voltar ao Painel", style=discord.ButtonStyle.danger, row=4)

        async def callback(self, interaction: discord.Interaction):
            view: 'ConfigPermView' = self.view # type: ignore
            main_view = create_main_panel_view(author=interaction.user, bot_instance=view.bot_instance, guild=view.guild)
            attachments = []
            if main_view.original_file:
                attachments.append(main_view.original_file)
            await interaction.response.edit_message(embed=main_view.original_embed, view=main_view, attachments=attachments)

    class PermTypeSelect(discord.ui.Select):
        def __init__(self):
            options = [discord.SelectOption(label=info["name"], value=key, description=info["description"]) for key, info in PERM_TYPES.items()]
            super().__init__(placeholder="Selecione o tipo de permissão para configurar...", options=options)

        async def callback(self, interaction: discord.Interaction):
            view: 'ConfigPermView' = self.view
            perm_type_key = self.values[0]

            # Remove o seletor de cargos antigo, se houver
            for item in view.children:
                if isinstance(item, view.RoleMultiSelect):
                    view.remove_item(item)

            view.add_item(view.RoleMultiSelect(perm_type_key))
            await interaction.response.edit_message(view=view) # Apenas atualiza a view com o novo seletor

    class RoleMultiSelect(discord.ui.RoleSelect):
        def __init__(self, perm_type_key: str):
            self.perm_type_key = perm_type_key
            self.table_name = PERM_TYPES[perm_type_key]["table"]
            super().__init__(placeholder=f"Gerenciar cargos de '{PERM_TYPES[perm_type_key]['name']}'...", min_values=0, max_values=25)

        async def callback(self, interaction: discord.Interaction):
            view: 'ConfigPermView' = self.view
            selected_role_ids = {role.id for role in self.values}

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                # Remove todos os cargos para este tipo de permissão e guild
                cursor.execute(f"DELETE FROM {self.table_name} WHERE guild_id = ?", (view.guild.id,))
                # Insere os cargos que foram selecionados na view
                if selected_role_ids:
                    cursor.executemany(f"INSERT INTO {self.table_name} (guild_id, role_id) VALUES (?, ?)", [(view.guild.id, role_id) for role_id in selected_role_ids])
                conn.commit()

            await view.update_message(interaction)

class ConfigPerm(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="configperm", help="Abre um painel para configurar os cargos de permissão do bot.")
    @commands.check(is_super_admin)
    async def configperm(self, ctx: commands.Context):
        """Abre um painel para configurar os cargos de Admin e Moderador do bot."""
        await self.client.delete_message_user(ctx)

        view = ConfigPermView(author=ctx.author, bot_instance=self.client, guild=ctx.guild)
        initial_embed = await view.generate_embed()
        await ctx.send(embed=initial_embed, view=view, delete_after=900) # Apaga após 15 minutos

    @configperm.error
    async def configperm_error(self, ctx: commands.Context, error):
        """Trata erros para o comando configperm."""
        await self.client.delete_message_user(ctx)
        
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                f"{ctx.author.mention}, apenas Super Admins podem usar este comando.",
                delete_after=10
            )
        else:
            print(f"Erro inesperado no comando configperm: {error}")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(ConfigPerm(client))
