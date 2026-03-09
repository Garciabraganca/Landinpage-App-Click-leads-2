# 🚀 Click Leads – Landing Page Oficial (2025)
Landing page institucional do **Click Leads**, criada para apresentar a solução de captação e entrega de leads em tempo real, destacando tecnologia, velocidade e o storytelling oficial da família do Grupo Garcia.

Esta é a **versão 2025**, inspirada no layout ilustrado utilizado nas peças do Click Leads, com foco em performance, credibilidade e identidade visual própria.

---

## 📌 Tecnologias utilizadas

- **HTML5** (sem dependências externas para frontend)
- **CSS3** com layout responsivo
- **Grid Layout + Flexbox**
- **Imagens otimizadas** em /img
- **Python/Flask** (para Shopping Agent API)
- **OpenAI API** (Assistants com File Search)
- **Arquitetura de página estática + API backend** pronta para Vercel

---

## 📂 Estrutura do Projeto

```bash
.
├── index.html                 # Landing page principal
├── sections.html              # Seções reutilizáveis
├── api.py                     # Shopping Agent API (Flask)
├── README.md
├── requirements.txt           # Dependências Python
└── .vscode/tasks.json
```

---

## 🤖 Shopping Agent SAC (Novidade!)

A landing possui um **Agente de Atendimento (SAC)** que responde perguntas sobre as plataformas do Shopping das Plataformas.

### Features

- ✅ Chat interativo com histórico
- ✅ 8 perguntas pré-configuradas (chips/botões)
- ✅ Integração com **OpenAI Assistants API** (File Search)
- ✅ Responsivo (desktop + mobile)
- ✅ Rate-limit básico e validação de entrada
- ✅ Loading state e error handling

### Setup Local

1. **Instalar dependências Python:**
```bash
pip install -r requirements.txt
```

2. **Configurar variável de ambiente:**
```bash
export OPENAI_API_KEY="sua-chave-aqui"
# ou no Windows:
set OPENAI_API_KEY=sua-chave-aqui
```

3. **Rodar o servidor Flask (local):**
```bash
python api.py
# Roda em http://localhost:5501 por padrão
```

4. **Rodar o servidor HTTP da landing (em outro terminal):**
```bash
python -m http.server 5500
# Acesse em http://localhost:5500
```

5. **Testar no navegador:**
Vá para `http://localhost:5500` e procure pela seção "Tire suas dúvidas agora"

### Deployment (Vercel)

1. **Variáveis de ambiente:**
   - `OPENAI_API_KEY` (já configurada)
   - `PORT` (opcional, padrão 5501)

2. **Vector Store ID:**
   - `vs_69a983fd9a1c819198605bb91633aa36` (hardcoded no `api.py`)

3. **Notas:**
   - O arquivo da base de conhecimento está associado ao Vector Store ID
   - O modelo usado é `gpt-4o-mini`
   - System prompt está em português brasileiro

---

## ⚙️ Configuração da API (cadastro por URL de perfil)

Esta landing envia o cadastro para:

`POST ${BACKEND_BASE_URL}/api/broker-applications`

No `index.html`, a base da API é resolvida assim:

1. `window.NEXT_PUBLIC_CRM_API_BASE_URL` (preferencial)
2. `window.CRM_API_BASE_URL`
3. fallback local: `http://localhost:3000`

Exemplo para definir antes do script principal da landing:

```html
<script>
	window.NEXT_PUBLIC_CRM_API_BASE_URL = 'https://seu-backend.com';
</script>
```

Payload enviado:

```json
{
	"profileUrl": "https://linkedin.com/in/exemplo",
	"tenantSlug": "default",
	"utm": {
		"source": "",
		"campaign": "",
		"medium": "",
		"content": ""
	},
	"pageUrl": "https://dominio-da-landing"
}
```

## Analytics e broker applications


- Variável de Assistant suportada:
  - `ASSISTANT_ID_OPENAI` (canônica)
  - `OPENAI_ASSISTANT_ID` (legado)

- Fallback local do frontend: `http://localhost:5501`
- Fallback sem variavel explicita em preview/producao: `window.location.origin`
- Eventos GA4 implementados:
  - `view_profile_submission_step`
  - `select_store`
  - `select_profile_type`
  - `click_profile_submit`
  - `profile_submission_success`
  - `profile_submission_error`
- UTMs persistidas na sessao: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`
- Proxy opcional do backend:
  - `BROKER_APPLICATIONS_TARGET_URL=https://seu-backend.com/api/broker-applications`
  - `BROKER_APPLICATIONS_DESTINATION_URLS=https://destino-1.com/hook,https://destino-2.com/hook`
  - `BROKER_APPLICATIONS_TIMEOUT_MS=10000`
- Regra de sucesso:
  - com destino configurado, todos os destinos precisam retornar sucesso
  - sem destino configurado, `local` e `preview` aceitam apenas para teste com `destination_channel: "local_log"`
  - sem destino configurado em `production`, a rota retorna `503` para evitar falso positivo (pode ser sobrescrito com `BROKER_APPLICATIONS_ALLOW_UNCONFIGURED=true` em cenários controlados)

