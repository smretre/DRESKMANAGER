import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Pegando as variáveis de ambiente configuradas no Render
TOKEN = os.getenv("BOT_TOKEN") # O token do seu Bot Pai gerado no BotFather
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://seu-site.onrender.com") # URL gerada pelo Render

app = FastAPI()
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- COMANDOS DO BOT DO TELEGRAM ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Adiciona o botão que abre o Painel Web App dentro do Telegram
    builder.button(
        text="📊 Abrir Painel de Gestão", 
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    )
    
    await message.answer(
        "👋 **Bem-vindo ao Gerenciador de Bots!**\n\n"
        "Com este bot, você pode criar e gerenciar seus próprios bots de vendas, "
        "configurar pagamentos e acompanhar suas assinaturas.\n\n"
        "Clique no botão abaixo para abrir seu painel de controle:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

# --- ROTA WEB DO PAINEL (WEB APP) ---
@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    # Aqui é o código HTML/CSS do seu painel visual (Web App)
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Painel de Gestão - Bot Manager</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: var(--tg-theme-bg-color, #f4f4f9); color: var(--tg-theme-text-color, #333); margin: 0; padding: 20px; }
            .card { background: var(--tg-theme-secondary-bg-color, #fff); padding: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 15px; }
            h2 { margin-top: 0; font-size: 20px; color: var(--tg-theme-button-color, #2481cc); }
            button { background: var(--tg-theme-button-color, #2481cc); color: var(--tg-theme-button-text-color, #fff); border: none; padding: 10px 15px; border-radius: 8px; font-size: 16px; width: 100%; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Painel do Usuário 🚀</h1>
        <div class="card">
            <h2>Resumo de Vendas</h2>
            <p>Faturamento do Mês: <strong>R$ 0,00</strong></p>
            <p>Assinantes Ativos: <strong>0</strong></p>
        </div>
        <div class="card">
            <h2>Meus Bots</h2>
            <p>Nenhum bot conectado ainda.</p>
            <button onclick="alert('Aqui você abrirá o cadastro do Token do BotFather!')">Conectar Novo Bot</button>
        </div>
        <script>
            // Inicializa o Web App do Telegram
            let tg = window.Telegram.WebApp;
            tg.expand();
        </script>
    </body>
    </html>
    """

# --- INICIALIZAÇÃO SIMULTÂNEA (WEB + BOT) ---
@app.on_event("startup")
async def startup_event():
    # Inicia o polling do bot em segundo plano junto com o FastAPI
    asyncio.create_task(dp.start_polling(bot))
