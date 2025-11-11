import discord
from discord.ext import commands
import sqlite3
import re
from database.database_manager import DB_FILE
from utils.checks import has_admin_role
from ui.base_view import BaseView
from commands.admin.configLog import create_main_panel_view

URL_REGEX = re.compile(r"^(https?:\/\/[^\s\/$.?#].[^\s]*)$")

class ConfigAparenciaView(BaseView):
    def __init__(self, author: discord.User, bot_instance, guild: discord.Guild):
        super().__init__(author=author, timeout=900.0)
        self.bot_instance = bot_instance
        self.guild = guild

    async def generate_embed(self) -> discord.Embed:
        """Gera o embed que mostra as configurações atuais."""
        embed = self.bot_instance.create_user_embed(self.author, self.guild, "Gerencie a aparência dos embeds do bot neste servidor.", title="Painel de Aparência")

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT embed_color, embed_image_url, embed_thumbnail_url FROM server_configs WHERE guild_id = ?", (self.guild.id,))
            config = cursor.fetchone()

        color, image_url, thumb_url = config if config else (None, None, None)

        color_hex = f"#{color:06x}" if color else "Padrão do Bot"
        embed.add_field(name="Cor do Embed", value=f"`{color_hex}`", inline=False)
        embed.add_field(name="URL da Imagem", value=image_url or "`Não definida`", inline=False)
        embed.add_field(name="URL da Thumbnail", value=thumb_url or "`Não definida`", inline=False)

        # Atualiza a cor do próprio embed de preview
        if color:
            embed.color = color

        return embed

    async def update_message(self, interaction: discord.Interaction, is_modal_response: bool = False):
        embed = await self.generate_embed()
        if is_modal_response:
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)
        else:
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Definir Cor", style=discord.ButtonStyle.primary, emoji="🎨")
    async def set_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = self.ConfigModal(config_type="color", title="Definir Cor do Embed", label="Cor em Hexadecimal (ex: #FF0000)")
        modal.view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Definir Imagem", style=discord.ButtonStyle.primary, emoji="🖼️")
    async def set_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = self.ConfigModal(config_type="image_url", title="Definir Imagem do Embed", label="URL da Imagem (deve ser https://...)")
        modal.view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Definir Thumbnail", style=discord.ButtonStyle.primary, emoji="📌")
    async def set_thumbnail(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = self.ConfigModal(config_type="thumbnail_url", title="Definir Thumbnail do Embed", label="URL da Thumbnail (deve ser https://...)")
        modal.view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Resetar Aparência", style=discord.ButtonStyle.danger, row=1)
    async def reset_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE server_configs SET embed_color = NULL, embed_image_url = NULL, embed_thumbnail_url = NULL WHERE guild_id = ?", (self.guild.id,))
            conn.commit()
        await self.update_message(interaction)

    @discord.ui.button(label="Voltar ao Painel", style=discord.ButtonStyle.danger, row=2)
    async def go_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        main_view = create_main_panel_view(author=interaction.user, bot_instance=self.bot_instance, guild=self.guild)
        attachments = [main_view.original_file] if main_view.original_file else []
        await interaction.response.edit_message(embed=main_view.original_embed, view=main_view, attachments=attachments)

    class ConfigModal(discord.ui.Modal):
        def __init__(self, config_type: str, title: str, label: str):
            super().__init__(title=title)
            self.config_type = config_type
            self.value_input = discord.ui.TextInput(label=label, placeholder="Deixe em branco para remover.", required=False)
            self.add_item(self.value_input)

        async def on_submit(self, interaction: discord.Interaction):
            value = self.value_input.value.strip()
            db_column = f"embed_{self.config_type}"
            db_value = None

            if value:
                if self.config_type == "color":
                    value = value.lstrip('#')
                    try:
                        db_value = int(value, 16)
                    except ValueError:
                        await interaction.response.send_message("Cor inválida. Use o formato hexadecimal (ex: #FF0000).", ephemeral=True)
                        return
                else: # image_url ou thumbnail_url
                    if not URL_REGEX.match(value):
                        await interaction.response.send_message("URL inválida. Certifique-se de que começa com http:// ou https://.", ephemeral=True)
                        return
                    db_value = value

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO server_configs (guild_id) VALUES (?)", (interaction.guild_id,))
                cursor.execute(f"UPDATE server_configs SET {db_column} = ? WHERE guild_id = ?", (db_value, interaction.guild_id))
                conn.commit()

            await interaction.response.send_message("Configuração atualizada!", ephemeral=True, delete_after=3)
            await self.view.update_message(interaction, is_modal_response=True)

class ConfigAparencia(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="configaparencia", help="Abre o painel para configurar a aparência do bot.")
    @commands.check(has_admin_role)
    async def configaparencia(self, ctx: commands.Context):
        """Abre um painel interativo para configurar a aparência dos embeds."""
        await self.client.delete_message_user(ctx)
        view = ConfigAparenciaView(author=ctx.author, bot_instance=self.client, guild=ctx.guild)
        embed = await view.generate_embed()
        await ctx.send(embed=embed, view=view, delete_after=900)

    @configaparencia.error
    async def configaparencia_error(self, ctx: commands.Context, error):
        await self.client.delete_message_user(ctx)
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"{ctx.author.mention}, você não tem permissão para usar este comando.", delete_after=10)
        else:
            print(f"Erro em r.configaparencia: {error}")
            await ctx.send("Ocorreu um erro ao executar o comando.", delete_after=10)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(ConfigAparencia(client))


"""
IMPORTANTE: Adicione as seguintes colunas à sua tabela `server_configs` no arquivo de banco de dados.
Você pode fazer isso usando um gerenciador de SQLite ou via código uma única vez.

ALTER TABLE server_configs ADD COLUMN embed_color INTEGER;
ALTER TABLE server_configs ADD COLUMN embed_image_url TEXT;
ALTER TABLE server_configs ADD COLUMN embed_thumbnail_url TEXT;
"""