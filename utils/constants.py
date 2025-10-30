"""
Arquivo para armazenar constantes e dicionários de configuração usados em todo o bot.
"""

LOG_TYPES = {
    "bot": {"name": "Log do Bot", "column": "log_bot_channel_id", "description": "Logs de comandos e ações do bot."},
    "canal": {"name": "Log de Canais", "column": "log_channel_channel_id", "description": "Criação, exclusão e edição de canais."},
    "mensagem": {"name": "Log de Mensagens", "column": "log_message_channel_id", "description": "Mensagens editadas e apagadas."},
    "cargos": {"name": "Log de Cargos", "column": "log_role_channel_id", "description": "Criação, exclusão e edição de cargos."},
    "entrada": {"name": "Log de Entrada", "column": "log_join_channel_id", "description": "Registra quando um membro entra no servidor."},
    "saida": {"name": "Log de Saída", "column": "log_leave_channel_id", "description": "Registra quando um membro sai do servidor."},
    "moderacao": {"name": "Log de Moderação", "column": "log_moderation_channel_id", "description": "Logs de ban, kick, mute, etc."}
}