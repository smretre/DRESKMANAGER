import os
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import BaseModel

# --- MODELOS PYDANTIC ---
class BotData(BaseModel):
    user_id: int
    bot_token: str

class GatewayData(BaseModel):
    user_id: int
    gateway_type: str
    token: str

class MetodoData(BaseModel):
    user_id: int
    metodos: list

class ProdutoData(BaseModel):
    user_id: int
    nome: str
    descricao: str
    tipo_plano: str # diario, semanal, mensal, vitalicio
    preco: float

class CupomData(BaseModel):
    user_id: int
    codigo: str
    desconto: float

class ConfigData(BaseModel):
    user_id: int
    imagem_url: str
    mensagem_remarketing: str
    suporte_link: str

# Variáveis de Ambiente
TOKEN = os.getenv("BOT_TOKEN") 
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://seu-site.onrender.com") 

app = FastAPI()
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Armazenamento em memória do SaaS
active_client_bots = {} 
user_bots_registry = {} 
user_gateways = {}
user_metodos = {}
user_produtos = {}
user_cupons = {}
user_configs = {}

# --- BOT PAI (PRINCIPAL) ---
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

# --- PAINEL WEB COMPLETO ---
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
                padding: 12px;
                padding-bottom: 80px;
            }
            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            h1 { font-size: 20px; margin: 0; }
            .badge {
                background: rgba(59, 130, 246, 0.15);
                color: var(--primary-color);
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: bold;
            }
            .menu-scroll {
                display: flex;
                gap: 6px;
                overflow-x: auto;
                padding-bottom: 8px;
                margin-bottom: 15px;
                scrollbar-width: none;
            }
            .menu-scroll::-webkit-scrollbar { display: none; }
            .tab-btn {
                background: var(--card-bg);
                border: 1px solid rgba(255,255,255,0.05);
                color: var(--hint-color);
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
                border-radius: 8px;
                white-space: nowrap;
                transition: all 0.3s ease;
            }
            .tab-btn.active {
                background: var(--primary-color);
                color: var(--button-text);
                border-color: transparent;
            }
            .section { display: none; }
            .section.active { display: block; }
            
            .card {
                background: var(--card-bg);
                padding: 14px;
                border-radius: 14px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
                margin-bottom: 14px;
                border: 1px solid rgba(255,255,255,0.05);
            }
            .card h3 { margin-top: 0; font-size: 15px; color: var(--primary-color); }
            
            .form-group { margin-bottom: 12px; }
            label { display: block; font-size: 12px; color: var(--hint-color); margin-bottom: 4px; }
            input, select, textarea {
                width: 100%;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.1);
                background: rgba(0,0,0,0.2);
                color: var(--text-color);
                font-size: 13px;
                box-sizing: border-box;
            }
            textarea { resize: vertical; height: 70px; }
            input:focus, select:focus, textarea:focus {
                outline: none;
                border-color: var(--primary-color);
            }
            .checkbox-group {
                display: flex;
                gap: 15px;
                align-items: center;
                font-size: 13px;
                margin-top: 5px;
            }
            .checkbox-group label { display: inline; color: var(--text-color); margin-bottom: 0; cursor: pointer; }
            
            .btn {
                background: var(--primary-color);
                color: var(--button-text);
                border: none;
                padding: 11px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                width: 100%;
                cursor: pointer;
            }
            .btn:active { transform: scale(0.98); }
            .info-box {
                font-size: 11px;
                color: var(--hint-color);
                background: rgba(59, 130, 246, 0.05);
                border-left: 3px solid var(--primary-color);
                padding: 8px;
                border-radius: 0 6px 6px 0;
                margin-top: 8px;
            }
        </style>
    </head>
    <body>

        <header>
            <div>
                <h1>Painel de Controle</h1>
                <span id="username-display" style="font-size: 11px; color: var(--hint-color);">Carregando usuário...</span>
            </div>
            <div class="badge">SaaS Ativo 🚀</div>
        </header>

        <!-- Menu de Abas Deslizante -->
        <div class="menu-scroll">
            <button class="tab-btn active" onclick="switchTab('dashboard', this)">📊 Geral</button>
            <button class="tab-btn" onclick="switchTab('bots', this)">🤖 Meus Bots</button>
            <button class="tab-btn" onclick="switchTab('gateway', this)">💳 Gateway</button>
            <button class="tab-btn" onclick="switchTab('metodos', this)">🛒 Métodos</button>
            <button class="tab-btn" onclick="switchTab('produtos', this)">📦 Produtos</button>
            <button class="tab-btn" onclick="switchTab('cupons', this)">🏷️ Cupons</button>
            <button class="tab-btn" onclick="switchTab('configs', this)">⚙️ Configs</button>
            <button class="tab-btn" onclick="switchTab('suporte', this)">❓ Suporte</button>
        </div>

        <!-- 1. DASHBOARD -->
        <div id="dashboard" class="section active">
            <div class="card">
                <h3>📊 Visão Geral</h3>
                <p style="font-size: 12px; color: var(--hint-color);">Acompanhe o rendimento e o status geral das suas automações de vendas pelo bot.</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;">
                    <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;">
                        <span style="font-size: 11px; color: var(--hint-color);">Faturamento</span>
                        <strong style="font-size: 16px; color: #10b981; display: block; margin-top: 4px;">R$ 0,00</strong>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px;">
                        <span style="font-size: 11px; color: var(--hint-color);">Assinantes</span>
                        <strong style="font-size: 16px; color: #3b82f6; display: block; margin-top: 4px;">0</strong>
                    </div>
                </div>
            </div>
        </div>

        <!-- 2. MEUS BOTS -->
        <div id="bots" class="section">
            <div class="card">
                <h3>🤖 Conectar Novo Bot</h3>
                <form onsubmit="salvarBot(event)">
                    <div class="form-group">
                        <label>Token do BotFather (@BotFather)</label>
                        <input type="text" id="bot-token" placeholder="Ex: 123456789:ABCdef..." required>
                    </div>
                    <button type="submit" class="btn">Conectar Bot</button>
                </form>
            </div>
            <div class="card" id="bot-status-card" style="display: none;">
                <h3>🤖 Bot Ativo no Sistema</h3>
                <p id="bot-info-text" style="font-size: 13px; color: var(--hint-color);"></p>
                <span class="badge" style="display: inline-block; margin-top: 6px;">Conectado ✅</span>
            </div>
        </div>

        <!-- 3. GATEWAY DE PAGAMENTO -->
        <div id="gateway" class="section">
            <div class="card">
                <h3>💳 Gateway de Pagamento</h3>
                <form onsubmit="salvarGateway(event)">
                    <div class="form-group">
                        <label>Selecionar Gateway</label>
                        <select id="gateway-type" onchange="mudarCamposGateway()">
                            <option value="mercadopago">Mercado Pago</option>
                            <option value="pushinpay">Pushin Pay (Pix)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Token / Chave de Acesso</label>
                        <input type="password" id="gateway-token" placeholder="Cole sua credencial aqui..." required>
                    </div>
                    <button type="submit" class="btn">Salvar Gateway</button>
                </form>
                <div class="info-box">Se já houver uma chave configurada, ela será atualizada com a nova inserção.</div>
            </div>
        </div>

        <!-- 4. MÉTODOS DE PAGAMENTO -->
        <div id="metodos" class="section">
            <div class="card">
                <h3>🛒 Métodos de Pagamento Ativos</h3>
                <form onsubmit="salvarMetodos(event)">
                    <div class="checkbox-group"><input type="checkbox" id="metodo-pix" checked><label for="metodo-pix">Pix (Aprovação Instantânea)</label></div>
                    <div class="checkbox-group" style="margin-top: 8px;"><input type="checkbox" id="metodo-cartao"><label for="metodo-cartao">Cartão de Crédito</label></div>
                    <div class="checkbox-group" style="margin-top: 8px; margin-bottom: 12px;"><input type="checkbox" id="metodo-boleto"><label for="metodo-boleto">Boleto Bancário</label></div>
                    <button type="submit" class="btn">Salvar Métodos</button>
                </form>
            </div>
        </div>

        <!-- 5. MEUS PRODUTOS -->
        <div id="produtos" class="section">
            <div class="card">
                <h3>📦 Configurar Produtos e Planos</h3>
                <form onsubmit="salvarProduto(event)">
                    <div class="form-group">
                        <label>Nome do Produto (Ex: Grupo VIP / Acesso Vídeo)</label>
                        <input type="text" id="prod-nome" placeholder="Nome do produto..." required>
                    </div>
                    <div class="form-group">
                        <label>Descrição e Mensagem de Boas-Vindas (/start)</label>
                        <textarea id="prod-desc" placeholder="Descreva os benefícios e planos..."></textarea>
                    </div>
                    <div class="form-group">
                        <label>Tipo de Duração do Plano</label>
                        <select id="prod-tipo">
                            <option value="diario">Diário (Aviso de renovação nas últimas 3h)</option>
                            <option value="semanal">Semanal (Aviso nós últimos 3 dias)</option>
                            <option value="mensal">Mensal (Aviso nós últimos 3 dias)</option>
                            <option value="vitalicio">Vitalício (Sem expiração)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Preço (R$)</label>
                        <input type="number" step="0.01" id="prod-preco" placeholder="Ex: 29.90" required>
                    </div>
                    <button type="submit" class="btn">Salvar Produto</button>
                </form>
            </div>
        </div>

        <!-- 6. MEUS CUPONS -->
        <div id="cupons" class="section">
            <div class="card">
                <h3>🏷️ Cupons de Desconto</h3>
                <form onsubmit="salvarCupom(event)">
                    <div class="form-group">
                        <label>Código do Cupom</label>
                        <input type="text" id="cupom-codigo" placeholder="Ex: DESCONTO5" required>
                    </div>
                    <div class="form-group">
                        <label>Porcentagem de Desconto (%)</label>
                        <input type="number" step="0.1" id="cupom-desconto" placeholder="Ex: 5.0" required>
                    </div>
                    <button type="submit" class="btn">Criar Cupom</button>
                </form>
            </div>
        </div>

        <!-- 7. CONFIGURAÇÕES -->
        <div id="configs" class="section">
            <div class="card">
                <h3>⚙️ Configurações Iniciais e Remarketing</h3>
                <form onsubmit="salvarConfigs(event)">
                    <div class="form-group">
                        <label>URL da Imagem de Início (/start)</label>
                        <input type="text" id="cfg-imagem" placeholder="https://exemplo.com/imagem.jpg">
                    </div>
                    <div class="form-group">
                        <label>Mensagem de Remarketing (Carrinho Abandonado / Expiração)</label>
                        <textarea id="cfg-remarketing" placeholder="Mensagem enviada para reengajar o usuário..."></textarea>
                    </div>
                    <button type="submit" class="btn">Salvar Configurações</button>
                </form>
            </div>
        </div>

        <!-- 8. AJUDA E SUPORTE -->
        <div id="suporte" class="section">
            <div class="card">
                <h3>❓ Ajuda e Suporte</h3>
                <form onsubmit="salvarSuporte(event)">
                    <div class="form-group">
                        <label>Link do Grupo ou Atendente de Suporte</label>
                        <input type="text" id="cfg-suporte" placeholder="https://t.me/seu_grupo_suporte" required>
                    </div>
                    <button type="submit" class="btn">Salvar Suporte</button>
                </form>
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
                
                if (tabId === 'bots') carregarMeusBots();
            }

            async function salvarBot(event) {
                event.preventDefault();
                let token = document.getElementById('bot-token').value;
                let res = await fetch('/api/salvar-bot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: telegramUser.id, bot_token: token })
                });
                if (res.ok) { alert("Bot conectado com sucesso!"); carregarMeusBots(); }
                else { alert("Token inválido."); }
            }

            async function carregarMeusBots() {
                let res = await fetch(`/api/meus-bots?user_id=${telegramUser.id}`);
                if (res.ok) {
                    let data = await res.json();
                    if (data.bot) {
                        document.getElementById('bot-status-card').style.display = 'block';
                        document.getElementById('bot-info-text').innerHTML = `Bot: <strong>@${data.bot.username}</strong>`;
                    }
                }
            }

            async function salvarGateway(event) {
                event.preventDefault();
                let tipo = document.getElementById('gateway-type').value;
                let token = document.getElementById('gateway-token').value;
                let res = await fetch('/api/salvar-gateway', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: telegramUser.id, gateway_type: tipo, token: token })
                });
                if (res.ok) alert("Gateway salvo!");
            }

            async function salvarMetodos(event) {
                event.preventDefault();
                let metodos = [];
                if(document.getElementById('metodo-pix').checked) metodos.push('pix');
                if(document.getElementById('metodo-cartao').checked) metodos.push('cartao');
                if(document.getElementById('metodo-boleto').checked) metodos.push('boleto');
                
                let res = await fetch('/api/salvar-metodos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: telegramUser.id, metodos: metodos })
                });
                if(res.ok) alert("Métodos salvos!");
            }

            async function salvarProduto(event) {
                event.preventDefault();
                let data = {
                    user_id: telegramUser.id,
                    nome: document.getElementById('prod-nome').value,
                    descricao: document.getElementById('prod-desc').value,
                    tipo_plano: document.getElementById('prod-tipo').value,
                    preco: parseFloat(document.getElementById('prod-preco').value)
                };
                let res = await fetch('/api/salvar-produto', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if(res.ok) alert("Produto salvo com sucesso!");
            }

            async function salvarCupom(event) {
                event.preventDefault();
                let data = {
                    user_id: telegramUser.id,
                    codigo: document.getElementById('cupom-codigo').value,
                    desconto: parseFloat(document.getElementById('cupom-desconto').value)
                };
                let res = await fetch('/api/salvar-cupom', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if(res.ok) alert("Cupom criado!");
            }

            async function salvarConfigs(event) {
                event.preventDefault();
                let data = {
                    user_id: telegramUser.id,
                    imagem_url: document.getElementById('cfg-imagem').value,
                    mensagem_remarketing: document.getElementById('cfg-remarketing').value,
                    suporte_link: ""
                };
                let res = await fetch('/api/salvar-configs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if(res.ok) alert("Configurações salvas!");
            }

            async function salvarSuporte(event) {
                event.preventDefault();
                let suporte = document.getElementById('cfg-suporte').value;
                let res = await fetch('/api/salvar-suporte', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: telegramUser.id, suporte_link: suporte })
                });
                if(res.ok) alert("Link de suporte salvo!");
            }
        </script>
    </body>
    </html>
    """

# --- INICIALIZAÇÃO DO BOT PAI ---
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(dp.start_polling(bot))

# --- ROTAS DE API PARA PROCESSAMENTO DOS DADOS ---
@app.post("/api/salvar-bot")
async def api_salvar_bot(data: BotData):
    try:
        temp_bot = Bot(token=data.bot_token)
        bot_info = await temp_bot.get_me()
        
        user_bots_registry[data.user_id] = {
            "username": bot_info.username,
            "first_name": bot_info.first_name
        }

        client_dp = Dispatcher()

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
                await message.answer("⚠️ Comando restrito ao administrador do bot.")
                return

            builder = InlineKeyboardBuilder()
            builder.row(types.InlineKeyboardButton(text="💳 Gateways de pagamento", callback_data="cfg_gateways"))
            builder.row(types.InlineKeyboardButton(text="🛒 Métodos de pagamento", callback_data="cfg_metodos"))
            builder.row(types.InlineKeyboardButton(text="📦 Meus Produtos", callback_data="cfg_produtos"))
            builder.row(types.InlineKeyboardButton(text="🏷️ Meus Cupons", callback_data="cfg_cupons"))
            builder.row(types.InlineKeyboardButton(text="🛠️ Configurações", callback_data="cfg_config"))
            builder.row(types.InlineKeyboardButton(text="❓ Ajuda e Suporte", callback_data="cfg_ajuda"))

            await message.answer(
                "⚙️ **Painel Administrador** ⚙️\n\n"
                "Status: **O bot está pronto para venda ✅**\n\n"
                "Gerencie suas opções abaixo ou utilize o Web App de controle.",
                reply_markup=builder.as_markup(),
                parse_mode="Markdown"
            )

        @client_dp.callback_query(F.data.startswith("cfg_"))
        async def process_admin_callbacks(callback: types.CallbackQuery):
            if callback.from_user.id != owner_id:
                await callback.answer("Acesso negado.", show_alert=True)
                return
            
            action = callback.data
            texts = {
                "cfg_gateways": "💳 **Gateways:** Configure suas chaves no painel web.",
                "cfg_metodos": "🛒 **Métodos:** Pix, Cartão ou Boleto ativos.",
                "cfg_produtos": "📦 **Produtos:** Gerencie seus planos diários, semanais, mensais ou vitalícios.",
                "cfg_cupons": "🏷️ **Cupons:** Configure descontos especiais.",
                "cfg_config": "🛠️ **Configurações:** Imagem de boas-vindas e remarketing.",
                "cfg_ajuda": "❓ **Suporte:** Canais de atendimento configurados."
            }
            await callback.message.answer(texts.get(action, "Configuração"), parse_mode="Markdown")
            await callback.answer()

        @client_dp.message(Command("start"))
        async def client_start(message: types.Message):
            if message.from_user.id == owner_id:
                await message.answer("👋 Olá Dono! Utilize `/admin` para gerenciar as configurações.")
            else:
                cfg = user_configs.get(owner_id, {})
                prod = user_produtos.get(owner_id, {})
                
                texto_inicio = prod.get("descricao", "👋 **Bem-vindo à nossa loja!**\n\nConfira nossos planos disponíveis.")
                imagem = cfg.get("imagem_url")

                if imagem:
                    await message.answer_photo(photo=imagem, caption=texto_inicio, parse_mode="Markdown")
                else:
                    await message.answer(texto_inicio, parse_mode="Markdown")

        @client_dp.message(Command("suporte"))
        async def client_suporte(message: types.Message):
            suporte_info = user_configs.get(owner_id, {}).get("suporte_link", "Canal padrão de atendimento.")
            await message.answer(f"💬 **Suporte ao Cliente**\n\nAcesse: {suporte_info}", parse_mode="Markdown")

        @client_dp.message(Command("meus_acessos"))
        async def client_meus_acessos(message: types.Message):
            await message.answer("🔗 Aqui estão os seus acessos ativos.", parse_mode="Markdown")

        asyncio.create_task(client_dp.start_polling(temp_bot))
        active_client_bots[data.user_id] = data.bot_token
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/meus-bots")
async def api_meus_bots(user_id: int):
    return {"status": "success", "bot": user_bots_registry.get(user_id)}

@app.post("/api/salvar-gateway")
async def api_salvar_gateway(data: GatewayData):
    user_gateways[data.user_id] = {"type": data.gateway_type, "token": data.token}
    return {"status": "success"}

@app.post("/api/salvar-metodos")
async def api_salvar_metodos(data: MetodoData):
    user_metodos[data.user_id] = data.metodos
    return {"status": "success"}

@app.post("/api/salvar-produto")
async def api_salvar_produto(data: ProdutoData):
    user_produtos[data.user_id] = data.dict()
    return {"status": "success"}

@app.post("/api/salvar-cupom")
async def api_salvar_cupom(data: CupomData):
    user_cupons[data.user_id] = {"codigo": data.codigo, "desconto": data.desconto}
    return {"status": "success"}

@app.post("/api/salvar-configs")
async def api_salvar_configs(data: ConfigData):
    if data.user_id not in user_configs: user_configs[data.user_id] = {}
    user_configs[data.user_id]["imagem_url"] = data.imagem_url
    user_configs[data.user_id]["mensagem_remarketing"] = data.mensagem_remarketing
    return {"status": "success"}

@app.post("/api/salvar-suporte")
async def api_salvar_suporte(data: Request):
    body = await data.json()
    user_id = body.get("user_id")
    suporte = body.get("suporte_link")
    if user_id not in user_configs: user_configs[user_id] = {}
    user_configs[user_id]["suporte_link"] = suporte
    return {"status": "success"}
