# 🚀 Click Leads – Landing Page Oficial (2025)
Landing page institucional do **Click Leads**, criada para apresentar a solução de captação e entrega de leads em tempo real, destacando tecnologia, velocidade e o storytelling oficial da família do Grupo Garcia.

Esta é a **versão 2025**, inspirada no layout ilustrado utilizado nas peças do Click Leads, com foco em performance, credibilidade e identidade visual própria.

---

## 📌 Tecnologias utilizadas

- **HTML5** (sem dependências externas)
- **CSS3** com layout responsivo
- **Grid Layout + Flexbox**
- **Imagens otimizadas** em /img
- **Arquitetura de página estática** pronta para Vercel

Nenhum framework, nenhum build.  
**É só subir e publicar.**

---

## 📂 Estrutura do Projeto

```bash
.
├── index.html
├── sections.html
├── README.md
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

