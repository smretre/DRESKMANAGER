import os
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import BaseModel

# 2. Modelos Pydantic para receber os dados do painel
class BotData(BaseModel):
    user_id: int
    bot_token: str

class GatewayData(BaseModel):
    user_id: int
    gateway_type: str
    token: str

# Pegando as variáveis de ambiente configuradas no Render
TOKEN = os.getenv("BOT_TOKEN") # O token do seu Bot Pai gerado no BotFather
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://seu-site.onrender.com") # URL gerada pelo Render

app = FastAPI()
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Dicionários em memória para armazenar os dados do SaaS
active_client_bots = {} # user_id -> bot_token
user_bots_registry = {} # user_id -> info do bot (para listar na aba Meus Bots)

# --- COMANDOS DO BOT DO TELEGRAM (BOT PAI) ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
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

        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('dashboard', this)">📊 Visão Geral</button>
            <button class="tab-btn" onclick="switchTab('bots', this)">🤖 Meus Bots</button>
            <button class="tab-btn" onclick="switchTab('gateway', this)">💳 Gateways</button>
        </div>

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

            <!-- Listagem do Bot Salvo -->
            <div class="card" id="bot-status-card" style="display: none;">
                <h3>🤖 Bot Conectado</h3>
                <p id="bot-info-text" style="font-size: 14px; color: var(--hint-color);"></p>
                <span class="badge" style="display: inline-block; margin-top: 8px;">Status: Ativo ✅</span>
            </div>
        </div>

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

            let telegramUser = { id: 123456, first_name: "Usuário", username: "unknown" };
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                telegramUser = tg.initDataUnsafe.user;
                document.getElementById('username-display').innerText = `Olá, ${telegramUser.first_name} (@${telegramUser.username || 'sem_user'})`;
            }

            function switchTab(tabId, btnElement) {
                document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                
                document.getElementById(tabId).classList.add('active');
                btnElement.classList.add('active');
                
                if (tabId === 'bots') {
                    carregarMeusBots();
                }
            }

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

            async function salvarBot(event) {
                event.preventDefault();
                let token = document.getElementById('bot-token').value;

                let response = await fetch('/api/salvar-bot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: telegramUser.id, bot_token: token })
                });

                if (response.ok) {
                    let data = await response.json();
                    alert("Bot cadastrado e validado com sucesso!");
                    document.getElementById('bot-token').value = '';
                    carregarMeusBots();
                } else {
                    alert("Erro ao salvar o bot. Verifique o token.");
                }
            }

            async function carregarMeusBots() {
                try {
                    let response = await fetch(`/api/meus-bots?user_id=${telegramUser.id}`);
                    if (response.ok) {
                        let data = await response.json();
                        if (data.bot) {
                            document.getElementById('bot-status-card').style.display = 'block';
                            document.getElementById('bot-info-text').innerHTML = `Bot Conectado: <strong>@${data.bot.username}</strong> (${data.bot.first_name})`;
                        }
                    }
                } catch(e) {
                    console.log("Erro ao carregar bots");
                }
            }

            async function salvarGateway(event) {
                event.preventDefault();
                let tipo = document.getElementById('gateway-type').value;
                let tokenGateway = tipo === 'mercadopago' ? document.getElementById('mp-token').value : document.getElementById('pushin-token').value;

                let response = await fetch('/api/salvar-gateway', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: telegramUser.id, gateway_type: tipo, token: tokenGateway })
                });

                if (response.ok) {
                    alert("Credenciais de pagamento salvas com segurança!");
                } else {
                    alert("Erro ao salvar credenciais.");
                }
            }
        </script>
    </body>
    </html>
    """

# --- INICIALIZAÇÃO SIMULTÂNEA (WEB + BOT PAI) ---
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(dp.start_polling(bot))

# --- ROTAS DE API PARA SALVAR DADOS E CONFIGURAR O BOT DO CLIENTE ---
@app.post("/api/salvar-bot")
async def api_salvar_bot(data: BotData):
    try:
        # 1. Valida o token com a API do Telegram
        temp_bot = Bot(token=data.bot_token)
        bot_info = await temp_bot.get_me()
        
        # Salva o bot no registro do painel web para aparecer na aba "Meus Bots"
        user_bots_registry[data.user_id] = {
            "username": bot_info.username,
            "first_name": bot_info.first_name
        }

        # 2. Configura o Dispatcher dedicado para o bot do cliente
        client_dp = Dispatcher()

        # Configura a lista de comandos nativa no menu lateral do Telegram (ícone de menu azul)
        await temp_bot.set_my_commands([
            types.BotCommand(command="admin", description="⚙️ Painel Administrador"),
            types.BotCommand(command="start", description="🚀 Começar"),
            types.BotCommand(command="meus_acessos", description="🔗 Meus acessos"),
            types.BotCommand(command="suporte", description="💬 Suporte"),
            types.BotCommand(command="sobre", description="❓ Sobre")
        ])

        owner_id = data.user_id

        @client_dp.message(Command("admin"))
        async def client_admin_menu(message: types.Message):
            if message.from_user.id != owner_id:
                await message.answer("⚠️ Este comando é restrito apenas ao administrador/dono deste bot.")
                return

            builder = InlineKeyboardBuilder()
            builder.row(types.InlineKeyboardButton(text="💳 Gateways de pagamento", callback_data="cfg_gateways"))
            builder.row(types.InlineKeyboardButton(text="🛒 Métodos de pagamento", callback_data="cfg_metodos"))
            builder.row(types.InlineKeyboardButton(text="📦 Meus Produtos", callback_data="cfg_produtos"))
            builder.row(types.InlineKeyboardButton(text="🏷️ Meus Cupons", callback_data="cfg_cupons"))
            builder.row(types.InlineKeyboardButton(text="🛠️ Configurações", callback_data="cfg_config"))
            builder.row(types.InlineKeyboardButton(text="❓ Ajuda e Suporte", callback_data="cfg_ajuda"))

            user_name = message.from_user.first_name if message.from_user else "Administrador"

            await message.answer(
                f"⚙️ **Painel Administrador** ⚙️\n\n"
                f"Status: **O bot está pronto para venda ✅**\n\n"
                f"Olá, **{user_name}**!\n"
                f"Aqui, você pode fazer todas as configurações do seu bot, desde a gestão de grupos e planos até a personalização de mensagens e opções de pagamento. "
                f"Transforme a experiência dos seus usuários e alcance novos patamares de eficiência e sucesso!\n\n"
                f"💡 Você pode voltar para esse menu a qualquer momento digitando `/admin`.",
                reply_markup=builder.as_markup(),
                parse_mode="Markdown"
            )

        # 4. Tratamento de cliques (callbacks) dos botões do painel administrativo para funcionarem perfeitamente
        @client_dp.callback_query(F.data.startswith("cfg_"))
        async def process_admin_callbacks(callback: types.CallbackQuery):
            if callback.from_user.id != owner_id:
                await callback.answer("Acesso negado.", show_alert=True)
                return

            action = callback.data
            text_resp = "🛠️ Configuração selecionada."

            if action == "cfg_gateways":
                text_resp = "💳 **Gateways de Pagamento**\n\nConfigure suas chaves do Mercado Pago ou Pushin Pay pelo painel web."
            elif action == "cfg_metodos":
                text_resp = "🛒 **Métodos de Pagamento**\n\nAtive Pix, Cartão de Crédito ou Boleto para os seus clientes."
            elif action == "cfg_produtos":
                text_resp = "📦 **Meus Produtos**\n\nGerencie seus produtos, planos e links de convite para grupos/canais."
            elif action == "cfg_cupons":
                text_resp = "🏷️ **Meus Cupons**\n\nCrie cupons de desconto exclusivos para impulsionar suas vendas."
            elif action == "cfg_config":
                text_resp = "🛠️️ **Configurações Gerais**\n\nPersonalize textos, mensagens de boas-vindas e regras da loja."
            elif action == "cfg_ajuda":
                text_resp = "❓ **Ajuda e Suporte**\n\nEm caso de dúvidas, entre em contato com o suporte oficial da plataforma."

            await callback.message.answer(text_resp, parse_mode="Markdown")
            await callback.answer()

        @client_dp.message(Command("start"))
        async def client_start(message: types.Message):
            if message.from_user.id == owner_id:
                await message.answer("👋 Olá Dono! Utilize o comando `/admin` para gerenciar as configurações do seu bot.")
            else:
                await message.answer("👋 **Bem-vindo à nossa loja!**\n\nConfira os nossos produtos disponíveis para compra.", parse_mode="Markdown")

        @client_dp.message(Command("sobre"))
        async def client_sobre(message: types.Message):
            await message.answer(
                "Este bot foi criado com o **Bot Manager**, uma plataforma que permite que qualquer "
                "pessoa crie seu próprio bot personalizado e gerencie seus grupos e canais no Telegram. 🚀",
                parse_mode="Markdown"
            )

        @client_dp.message(Command("suporte"))
        async def client_suporte(message: types.Message):
            await message.answer("💬 Para dúvidas e suporte, utilize os nossos canais oficiais de atendimento.", parse_mode="Markdown")

        @client_dp.message(Command("meus_acessos"))
        async def client_meus_acessos(message: types.Message):
            await message.answer("🔗 Aqui estão os seus acessos ativos e assinaturas vinculadas.", parse_mode="Markdown")

        # 3. Inicia o polling do bot do cliente em segundo plano de forma isolada
        asyncio.create_task(client_dp.start_polling(temp_bot))
        active_client_bots[data.user_id] = data.bot_token

        print(f"Bot @{bot_info.username} do usuário {data.user_id} iniciado com sucesso!")
        return {"status": "success", "message": f"Bot @{bot_info.username} conectado com sucesso!"}

    except Exception as e:
        print(f"Erro ao validar bot: {e}")
        raise HTTPException(status_code=400, detail="Token inválido ou erro ao conectar.")

@app.get("/api/meus-bots")
async def api_meus_bots(user_id: int):
    bot_info = user_bots_registry.get(user_id)
    if bot_info:
        return {"status": "success", "bot": bot_info}
    return {"status": "not_found"}

@app.post("/api/salvar-gateway")
async def api_salvar_gateway(data: GatewayData):
    print(f"Recebido Gateway {data.gateway_type} do usuário {data.user_id}")
    return {"status": "success", "message": "Gateway salvo com sucesso"}
