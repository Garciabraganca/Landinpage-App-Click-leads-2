#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shopping Agent SAC API
Integrates with OpenAI's Assistants API using File Search
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY environment variable is not set. "
        "Ensure it's configured in Vercel or locally in .env file."
    )

client = OpenAI(api_key=api_key)

# Configuration
VECTOR_STORE_ID = "vs_69a983fd9a1c819198605bb91633aa36"
MODEL = "gpt-4o-mini"
MAX_MESSAGE_LENGTH = 1500


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
        
        # Extract the assistant's response
        assistant_message = ""
        for block in response.content:
            if hasattr(block, "text"):
                assistant_message += block.text
        
        if not assistant_message:
            return jsonify({
                "success": False,
                "error": "Não consegui gerar uma resposta. Tente novamente."
            }), 500
        
        return jsonify({
            "success": True,
            "response": assistant_message
        }), 200
    
    except Exception as e:
        print(f"Error in shopping_agent: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Desculpe, houve um erro ao processar sua mensagem. Tente novamente."
        }), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5501))
    app.run(debug=False, host="0.0.0.0", port=port)
