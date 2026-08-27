# Original Gang — Discord Community Bot

Bot de comunidade para servidores Discord, desenvolvido em Python com `discord.py`. Focado em gestão de comunidades, oferece sistema de aniversários, painel administrativo, envio agendado de mensagens, personalização de aparência dos embeds e logs de eventos.

## Funcionalidades

- **Aniversários** — registro e mensagens automáticas de aniversário por servidor
- **Painel administrativo** — interface de gestão do servidor via botões
- **Mensagens agendadas** — envio de DMs agendadas por cargo e para todos
- **Logs de eventos** — logs de canais, mensagens, cargos, entrada/saída e moderação
- **Personalização** — cor, imagem e thumbnail dos embeds configuráveis por servidor
- **Comandos de moderação** — ban e outros, com checks de permissão

## Tecnologias

- Python 3.10+
- [discord.py](https://github.com/Rapptz/discord-py)
- SQLite

## Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/Wuzuy/original_gang.git
   cd original_gang
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Crie um arquivo `.env` na raiz:
   ```env
   DISCORD_TOKEN=seu_token_aqui
   SUPER_ADMIN_IDS=id1,id2,id3
   ```

4. Inicie o bot:
   ```bash
   python bot.py
   ```

## Licença

Distribuído sob a licença MIT.