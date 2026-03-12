# 🚀 Click Leads – Landing Page Oficial (2025)
Landing page institucional do **Click Leads**, criada para apresentar a solução de captação e entrega de leads em tempo real, destacando tecnologia, velocidade e o storytelling oficial da família do Grupo Garcia.

Esta é a **versão 2025**, inspirada no layout ilustrado utilizado nas peças do Click Leads, com foco em performance, credibilidade e identidade visual própria.

---

## 📌 Tecnologias utilizadas

- **HTML5** (sem dependências externas para frontend)
- **CSS3** com layout responsivo
- **Grid Layout + Flexbox**
- **Imagens otimizadas** em /img
- **Python/Flask** (API de envio para CRM)
- **Arquitetura de página estática + API backend** pronta para Vercel

---

## 📂 Estrutura do Projeto

```bash
.
├── index.html                 # Landing page principal
├── sections.html              # Seções reutilizáveis
├── api.py                     # API de broker applications (Flask)
├── README.md
├── requirements.txt           # Dependências Python
└── .vscode/tasks.json
```

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
  - `BROKER_APPLICATIONS_TARGET_URL=https://clickleads.grupogarciaseguradoras.com.br/api/broker-applications`
  - `BROKER_APPLICATIONS_DESTINATION_URLS=https://destino-1.com/hook,https://destino-2.com/hook`
  - aliases aceitos: `SUPERVISOR_DESTINATION_URL` e `SUPERVISOR_DESTINATION_URLS`
  - overrides por tenant/profile (precedencia: `<TENANT>_<PROFILE_TYPE>` > `<TENANT>` > `<PROFILE_TYPE>` > global):
    - `BROKER_APPLICATIONS_DESTINATION_URLS_DEFAULT_INSTAGRAM=https://seu-backend.com/api/broker-applications/instagram`
  - `BROKER_APPLICATIONS_TIMEOUT_MS=10000`
- Regra de sucesso:
  - com destino configurado, todos os destinos precisam retornar sucesso
  - sem destino configurado, `local` e `preview` aceitam apenas para teste com `destination_channel: "local_log"`
  - sem destino configurado em `production`, a rota retorna `503` para evitar falso positivo (pode ser sobrescrito com `BROKER_APPLICATIONS_ALLOW_UNCONFIGURED=true` em cenários controlados)
