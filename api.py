#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shopping Agent SAC API
Integrates with OpenAI's Assistants API using File Search
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def _load_openai_key():
    """Load OpenAI API key with fallback for legacy env var name."""
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")
    if api_key:
        api_key = api_key.strip()
    return api_key

def _load_assistant_id():
    """Load Assistant ID with fallback for common typos."""
    assistant_id = (
        os.environ.get("ASSISTANT_ID_OPENAI") or
        os.environ.get("ASSISTENT_ID_OPENAI") or
        os.environ.get("OPENAI_ASSISTANT_ID")
    )
    
    # Log warning if typo variant is used
    if not os.environ.get("ASSISTANT_ID_OPENAI") and os.environ.get("ASSISTENT_ID_OPENAI"):
        app.logger.warning(
            "[ASSISTANT_ID_TYPO] Using ASSISTENT_ID_OPENAI (typo). "
            "Please rename to ASSISTANT_ID_OPENAI in environment."
        )
    
    if assistant_id:
        assistant_id = assistant_id.strip()
    return assistant_id

def _load_openai_client():
    """Return an OpenAI client only when OPENAI_API_KEY is valid."""
    api_key = _load_openai_key()
    if not api_key or api_key == "local-dev-placeholder":
        app.logger.error(
            "[OPENAI_ENV_MISSING] OPENAI_API_KEY is missing or invalid. "
            "Set a real key via environment variable."
        )
        return None

    return OpenAI(api_key=api_key)


client = _load_openai_client()
assistant_id = _load_assistant_id()

# Configuration
VECTOR_STORE_ID = os.environ.get(
    "VECTOR_STORE_ID",
    "vs_69a983fd9a1c819198605bb91633aa36"
)
if not VECTOR_STORE_ID:
    raise ValueError(
        "VECTOR_STORE_ID environment variable is not set. "
        "Provide it via VECTOR_STORE_ID env var or use the default."
    )
MODEL = "gpt-4o-mini"
MAX_MESSAGE_LENGTH = 1500


@app.route("/api/broker-applications", methods=["POST"])
def broker_applications():
    """
    Recebe candidaturas de corretores enviadas pelos cards das lojas.

    Request JSON:
    {
        "event_type": "broker_application",
        "store_slug": "string",
        "store_name": "string",
        "profile_url": "string",
        "submitted_at": "ISO8601",
        "page": "string",
        "tenantSlug": "string",
        "utm": { ... },
        "pageUrl": "string"
    }

    Response JSON:
    { "success": true, "message": "Candidatura recebida." }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "JSON inválido."}), 400

        store_slug = (data.get("store_slug") or "").strip()
        store_name = (data.get("store_name") or "").strip()
        profile_url = (data.get("profile_url") or "").strip()

        if not store_slug or not store_name:
            return jsonify({"success": False, "error": "Loja inválida."}), 400

        if not profile_url:
            return jsonify({"success": False, "error": "Link de perfil obrigatório."}), 400

        # Log estruturado da candidatura para rastreio no servidor
        app.logger.info(
            "[BROKER_APPLICATION] store=%s | name=%s | profile=%s | page=%s | tenant=%s | pageUrl=%s",
            store_slug,
            store_name,
            profile_url,
            data.get("page", ""),
            data.get("tenantSlug", ""),
            data.get("pageUrl", ""),
        )

        # Se um webhook externo estiver configurado, encaminhar a candidatura
        webhook_url = os.environ.get("BROKER_WEBHOOK_URL", "").strip()
        if webhook_url:
            import urllib.request
            import json as _json

            req = urllib.request.Request(
                webhook_url,
                data=_json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=5):
                    pass
            except Exception as webhook_err:
                app.logger.warning("[BROKER_WEBHOOK_FAILED] %s", str(webhook_err))

        return jsonify({
            "success": True,
            "message": "Candidatura recebida. O supervisor da loja será notificado."
        }), 200

    except Exception as e:
        app.logger.error("[BROKER_APPLICATION_ERROR] %s", str(e))
        return jsonify({"success": False, "error": "Erro interno. Tente novamente."}), 500


@app.route("/api/shopping-agent", methods=["POST"])
def shopping_agent():
    """
    Handle chat messages for the Shopping Agent.
    
    Request JSON:
    {
        "message": "string",
        "history": [{"role": "user|assistant", "content": "string"}]
    }
    
    Response JSON:
    {
        "success": true,
        "response": "assistant's response text"
    }
    """
    try:
        if client is None:
            app.logger.error("[OPENAI_ENV_MISSING] Shopping Agent called without valid OpenAI client")
            return jsonify({
                "success": False,
                "error": "Shopping Agent indisponivel: OPENAI_API_KEY ausente ou invalida."
            }), 500

        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON"}), 400
        
        message = data.get("message", "").strip()
        history = data.get("history", [])
        
        # Validate message
        if not message:
            return jsonify({"success": False, "error": "Message cannot be empty"}), 400
        
        if len(message) > MAX_MESSAGE_LENGTH:
            return (
                jsonify({
                    "success": False,
                    "error": f"Message too long (max {MAX_MESSAGE_LENGTH} characters)"
                }),
                400
            )
        
        # System instruction for the Shopping Agent
        system_instruction = (
            "Você é o consultor do Shopping das Plataformas. "
            "Responda em português brasileiro, sendo consultivo e direto. "
            "Use o File Search para consultar a base de conhecimento sobre as plataformas. "
            "Não invente informações que não estejam na base. "
            "Se não souber algo, diga que vai pesquisar ou recomende contato com o suporte. "
            "Seja amigável e sempre ofereça valor."
        )
        
        # Build messages for the API
        messages = []
        
        # Add history if provided
        if history:
            messages.extend(history)
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Call OpenAI API with File Search
        response = client.beta.chat.completions.create(
            model=MODEL,
            messages=messages,
            system=system_instruction,
            tools=[{
                "type": "file_search",
                "file_search": {
                    "max_num_results": 5
                }
            }],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [VECTOR_STORE_ID]
                }
            }
        )
        
        # Extract the assistant's response with multiple fallback strategies
        assistant_message = ""
        
        # Strategy 1: Try response.content (current structure)
        if hasattr(response, "content"):
            for block in response.content:
                if hasattr(block, "text"):
                    assistant_message += block.text
        
        # Strategy 2: Try response.choices[0].message.content
        if not assistant_message and hasattr(response, "choices"):
            try:
                content = response.choices[0].message.content
                if isinstance(content, str):
                    assistant_message = content
                elif isinstance(content, list):
                    assistant_message = "".join(
                        item.text if hasattr(item, "text") else str(item)
                        for item in content
                    )
            except (IndexError, AttributeError):
                pass
        
        if not assistant_message:
            # Log the raw response for debugging
            app.logger.error(
                f"[OPENAI_RESPONSE_PARSE_FAILED] Could not extract assistant message. "
                f"Response type: {type(response).__name__}"
            )
            
            return jsonify({
                "success": False,
                "error": "Não consegui gerar uma resposta. Tente novamente."
            }), 500
        
        return jsonify({
            "success": True,
            "response": assistant_message
        }), 200
    
    except Exception as e:
        app.logger.error(f"[OPENAI_CALL_FAILED] Error in shopping_agent: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Desculpe, houve um erro ao processar sua mensagem. Tente novamente."
        }), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


@app.route("/api/health/openai", methods=["GET"])
def health_openai():
    """OpenAI configuration health check endpoint"""
    api_key = _load_openai_key()
    assistant = _load_assistant_id()
    
    has_key = bool(api_key and api_key != "local-dev-placeholder")
    has_assistant = bool(assistant)
    
    return jsonify({
        "ok": has_key and client is not None,
        "hasOpenAIKey": has_key,
        "hasAssistantId": has_assistant,
        "keyPrefix": api_key[:7] if has_key else None,
        "assistantPrefix": assistant[:6] if has_assistant else None,
        "runtime": "python-flask"
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5501))
    app.run(debug=False, host="0.0.0.0", port=port)
