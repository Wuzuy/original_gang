import discord
from discord.ext import commands
import sqlite3
from utils.checks import has_admin_role
from database.database_manager import DB_FILE

class Aniversarios(commands.Cog):
    """
    Cog para gerenciar a mensagem de aniversários.
    """
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="aniversarios", aliases=['birthdays'], help="Cria a mensagem de aniversários em um canal.")
    @commands.check(has_admin_role)
    async def aniversarios(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """
        Cria ou atualiza a mensagem de aniversários em um canal específico.
        Se nenhum canal for fornecido, usa o canal atual.
        """
        await self.client.delete_message_user(ctx)
        
        target_channel = channel or ctx.channel

        # 1. Gerar o embed de aniversários usando a função do core
        fields = await self.client._get_birthday_embed_fields(ctx.guild.id)
        
        embed = self.client.create_embed("Aniversários do Servidor", "", color=2326507, guild_id=ctx.guild.id)

        if fields:
            for field in fields:
                embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
        else:
            embed.description = "Nenhum aniversário registrado ainda. Use o botão abaixo para ser o primeiro!"

        # 2. Criar a view com o botão de registro
        view = self.client.BirthdayRegisterView()

        # 3. Enviar a mensagem
        try:
            birthday_message = await target_channel.send(embed=embed, view=view)
        except discord.Forbidden:
            await ctx.send(f"Eu não tenho permissão para enviar mensagens no canal {target_channel.mention}.", delete_after=15)
            return
        except Exception as e:
            await ctx.send(f"Ocorreu um erro ao enviar a mensagem: {e}", delete_after=15)
            return

        # 4. Salvar no banco de dados
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO server_configs (guild_id) VALUES (?)", (ctx.guild.id,))
            cursor.execute("UPDATE server_configs SET birthday_channel_id = ?, birthday_message_id = ? WHERE guild_id = ?",
                           (birthday_message.channel.id, birthday_message.id, ctx.guild.id))
            conn.commit()

        await ctx.send(f"✅ A mensagem de aniversários foi criada com sucesso em {birthday_message.channel.mention}!", delete_after=15)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Aniversarios(client))