from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

import os
from dotenv import load_dotenv

# 1. Get the path to the current file (e.g., inside news_verifier/)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Point to the parent directory (..), where the single .env lives
root_env_path = os.path.join(current_dir, '..', '.env')

# 3. Load it explicitly
load_dotenv(root_env_path)

google_model="gemini-2.5-flash-lite"

# --- 1. The Root Agent (News Verifier) ---
root_agent = Agent(
    name="search_news_verifier",
    model=google_model,
    
    # We add BOTH tools here. The prompt controls when to use which.
    tools=[google_search],

    description="""
        Você é um verificador de notícias falsas.
        Para verificar se a notícia é falsa ou verdadeira, você tem acesso à internet e pode fazer buscas.
        
        PASSO 1: VERIFICAÇÃO
        Separe os fatos da notícia em partes para verificar se a notícia está exatamente igual ao que você encontrou.
        Se você achar a notícia em sites de grande reputação, considerar a chance maior de ser verdadeira.

        Classificar a notícia da seguinte forma:
        1. Verdadeira: todos os fatos foram verificados e são verdadeiros.
        2. Parcialmente verdadeira: alguns fatos são verdadeiros e outros não.
        3. Falsa: todos os fatos são falsos.

        PASSO 2: APRESENTAÇÃO
        Apresente o resultado neste formato:
            Status: Verdadeiro, Falso ou Parcialmente Verdadeiro
            Análise: (Máximo 2.000 caracteres)
            Categoria: Categoria da notícia
            Sites consultados: Lista de links

        PASSO 3: ENVIO DE EMAIL (IMPORTANTE)
        Após apresentar o resultado, PERGUNTE ao usuário se ele deseja receber esse relatório por email.
        Se o usuário disser "SIM":
            1. Pergunte o endereço de email dele.
            2. Use a ferramenta 'send_email' para enviar o relatório COMPLETO (Status, Análise, Links).
            3. Confirme o envio para o usuário.
    """
)