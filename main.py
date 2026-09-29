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
            :root {
                --bg-color: var(--tg-theme-bg-color, #0f172a);
                --card-bg: var(--tg-theme-secondary-bg-color, #1e293b);
                --text-color: var(--tg-theme-text-color, #f8fafc);
                --hint-color: var(--tg-theme-hint-color, #94a3b8);
                --primary-color: var(--tg-theme-button-color, #3b82f6);
                --button-text: var(--tg-theme-button-text-color, #ffffff);
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                margin: 0;
                padding: 16px;
                padding-bottom: 80px;
            }
            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            h1 { font-size: 22px; margin: 0; }
            .badge {
                background: rgba(59, 130, 246, 0.15);
                color: var(--primary-color);
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }
            /* Navegação em abas */
            .tabs {
                display: flex;
                background: var(--card-bg);
                border-radius: 12px;
                padding: 4px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            }
            .tab-btn {
                flex: 1;
                background: none;
                border: none;
                color: var(--hint-color);
                padding: 10px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                border-radius: 8px;
                transition: all 0.3s ease;
            }
            .tab-btn.active {
                background: var(--primary-color);
                color: var(--button-text);
            }
            /* Seções */
            .section { display: none; }
            .section.active { display: block; }
            
            .card {
                background: var(--card-bg);
                padding: 16px;
                border-radius: 16px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
                margin-bottom: 16px;
                border: 1px solid rgba(255,255,255,0.05);
            }
            .card h3 { margin-top: 0; font-size: 16px; color: var(--primary-color); display: flex; align-items: center; gap: 8px; }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
                margin-bottom: 16px;
            }
            .metric-box {
                background: rgba(255,255,255,0.03);
                padding: 12px;
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.03);
            }
            .metric-box span { font-size: 12px; color: var(--hint-color); display: block; }
            .metric-box strong { font-size: 18px; margin-top: 4px; display: block; }

            /* Formulários */
            .form-group { margin-bottom: 14px; }
            label { display: block; font-size: 13px; color: var(--hint-color); margin-bottom: 6px; }
            input, select {
                width: 100%;
                padding: 12px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.1);
                background: rgba(0,0,0,0.2);
                color: var(--text-color);
                font-size: 14px;
                box-sizing: border-box;
            }
            input:focus, select:focus {
                outline: none;
                border-color: var(--primary-color);
            }
            .btn {
                background: var(--primary-color);
                color: var(--button-text);
                border: none;
                padding: 12px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                width: 100%;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }
            .btn:active { transform: scale(0.98); }
            
            .info-box {
                font-size: 12px;
                color: var(--hint-color);
                background: rgba(59, 130, 246, 0.05);
                border-left: 3px solid var(--primary-color);
                padding: 10px;
                border-radius: 0 8px 8px 0;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>

        <header>
            <div>
                <h1>Painel de Controle</h1>
                <span id="username-display" style="font-size: 12px; color: var(--hint-color);">Carregando usuário...</span>
            </div>
            <div class="badge">SaaS Ativo 🚀</div>
        </header>

        <!-- Abas de Navegação -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('dashboard')">📊 Visão Geral</button>
            <button class="tab-btn" onclick="switchTab('bots')">🤖 Meus Bots</button>
            <button class="tab-btn" onclick="switchTab('gateway')">💳 Gateways</button>
        </div>

        <!-- ABA 1: DASHBOARD -->
        <div id="dashboard" class="section active">
            <div class="metrics-grid">
                <div class="metric-box">
                    <span>Faturamento (Mês)</span>
                    <strong style="color: #10b981;">R$ 0,00</strong>
                </div>
                <div class="metric-box">
                    <span>Assinantes Ativos</span>
                    <strong style="color: #3b82f6;">0</strong>
                </div>
            </div>

            <div class="card">
                <h3>📈 Extrato de Taxas de Serviço</h3>
                <p style="font-size: 13px; color: var(--hint-color); margin-bottom: 10px;">
                    Modelo transparente: Cobramos apenas <strong>2.8% + R$ 1,00</strong> por venda realizada para manter a infraestrutura e segurança.
                </p>
                <div style="display: flex; justify-content: space-between; font-size: 14px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <span>Total de Vendas Processadas:</span>
                    <strong>R$ 0,00</strong>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 14px; padding: 8px 0;">
                    <span>Taxas Retidas pelo Sistema:</span>
                    <strong style="color: #ef4444;">R$ 0,00</strong>
                </div>
            </div>
        </div>

        <!-- ABA 2: MEUS BOTS -->
        <div id="bots" class="section">
            <div class="card">
                <h3>🤖 Gerenciar Bot do Telegram</h3>
                <form onsubmit="salvarBot(event)">
                    <div class="form-group">
                        <label>Token do BotFather (@BotFather)</label>
                        <input type="text" id="bot-token" placeholder="Ex: 123456789:ABCdefGhIJK..." required>
                    </div>
                    <button type="submit" class="btn">Conectar e Validar Bot</button>
                </form>
                <div class="info-box">
                    💡 Vá até o @BotFather no Telegram, crie um bot com o comando /newbot e cole o token gerado acima.
                </div>
            </div>
        </div>

        <!-- ABA 3: GATEWAYS DE PAGAMENTO -->
        <div id="gateway" class="section">
            <div class="card">
                <h3>💳 Configurar Recebimento</h3>
                <form onsubmit="salvarGateway(event)">
                    <div class="form-group">
                        <label>Selecione o Gateway</label>
                        <select id="gateway-type" onchange="mudarCamposGateway()">
                            <option value="mercadopago">Mercado Pago (Cartão / Pix)</option>
                            <option value="pushinpay">Pushin Pay (Pix R$ 0,35 fixo)</option>
                        </select>
                    </div>

                    <div id="campos-mercadopago">
                        <div class="form-group">
                            <label>Access Token do Mercado Pago</label>
                            <input type="password" id="mp-token" placeholder="APP_USR-xxxxxx...">
                        </div>
                    </div>

                    <div id="campos-pushinpay" style="display: none;">
                        <div class="form-group">
                            <label>Token da API Pushin Pay</label>
                            <input type="password" id="pushin-token" placeholder="Bearer Token...">
                        </div>
                    </div>

                    <button type="submit" class="btn">Salvar Credenciais</button>
                </form>
                <div class="info-box">
                    🔒 Suas chaves de API são criptografadas e usadas exclusivamente para processar as vendas dos seus clientes.
                </div>
            </div>
        </div>

        <script>
            let tg = window.Telegram.WebApp;
            tg.expand();

            // Identificar o usuário logado via Telegram WebApp
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                let user = tg.initDataUnsafe.user;
                document.getElementById('username-display').innerText = `Olá, ${user.first_name} (@${user.username || 'sem_user'})`;
            }

            // Alternar Abas
            function switchTab(tabId) {
                document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                
                document.getElementById(tabId).classList.add('active');
                event.currentTarget.classList.add('active');
            }

            // Alternar campos do gateway dinamicamente
            function mudarCamposGateway() {
                let tipo = document.getElementById('gateway-type').value;
                if (tipo === 'mercadopago') {
                    document.getElementById('campos-mercadopago').style.display = 'block';
                    document.getElementById('campos-pushinpay').style.display = 'none';
                } else {
                    document.getElementById('campos-mercadopago').style.display = 'none';
                    document.getElementById('campos-pushinpay').style.display = 'block';
                }
            }

            function salvarBot(event) {
                event.preventDefault();
                let token = document.getElementById('bot-token').value;
                tg.showAlert("Bot cadastrado com sucesso! Iniciando instâncias...");
                // Aqui você integrará com a rota POST do seu backend Python para salvar no banco
            }

            function salvarGateway(event) {
                event.preventDefault();
                tg.showAlert("Credenciais de pagamento salvas com segurança!");
                // Enviar via AJAX/Fetch para o FastAPI salvar as chaves
            }
        </script>
    </body>
    </html>
    """

# --- INICIALIZAÇÃO SIMULTÂNEA (WEB + BOT) ---
@app.on_event("startup")
async def startup_event():
    # Inicia o polling do bot em segundo plano junto com o FastAPI
    asyncio.create_task(dp.start_polling(bot))
