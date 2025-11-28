from google.adk.agents.llm_agent import Agent
from duckduckgo_search import DDGS 
import smtplib
from email.mime.text import MIMEText

import os
from dotenv import load_dotenv

# 1. Get the path to the current file (e.g., inside news_verifier/)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Point to the parent directory (..), where the single .env lives
root_env_path = os.path.join(current_dir, '..', '.env')

# 3. Load it explicitly
load_dotenv(root_env_path)

google_model="gemini-2.5-flash-lite"

# ==========================================
# TOOL 1: WEB SEARCH (Python Implementation)
# ==========================================
def search_web(query: str) -> str:
    """
    Realiza uma busca na web para verificar fatos.
    Retorna títulos, links e resumos.
    """
    print(f"\n[🔍 ROOT AGENT] Searching for: {query}")
    try:
        results = DDGS().text(query, max_results=5)
        if not results: return "No results found."
        
        formatted = ""
        for r in results:
            formatted += f"Source: {r['title']}\nLink: {r['href']}\nSummary: {r['body']}\n\n"
        return formatted
    except Exception as e:
        return f"Search error: {e}"

# ==========================================
# TOOL 2: EMAIL SENDER (Python Implementation)
# ==========================================
def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Envia email via Gmail.
    """
    sender_email = os.getenv("GMAIL_USER")
    sender_password =  os.getenv("GMAIL_APP_PASSWORD")
    
    print(f"\n[📧 SUB-AGENT] Sending email to {recipient}...")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender_email, sender_password)
            smtp_server.sendmail(sender_email, recipient, msg.as_string())
        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {e}"

# ==========================================
# AGENT 1: THE EMAIL SPECIALIST (Sub-Agent)
# ==========================================
email_specialist = Agent(
    name="email_specialist",
    model=google_model,
    tools=[send_email], # Uses the Python tool
    description="""
    Você é um especialista em comunicação.
    Sua única função é formatar um email profissional e enviá-lo usando a ferramenta disponível.
    Não pergunte nada, apenas envie.
    """
)

# ==========================================
# AGENT 2: THE MANAGER (Root Agent)
# ==========================================
root_agent = Agent(
    name="search_news_verifier_emailer",
    model=google_model,
    
    # 1. Provide the Search Tool
    tools=[search_web], 
    
    # 2. Provide the Sub-Agent for delegation
    sub_agents=[email_specialist], 
    
    description="""
    Você é um verificador de notícias falsas.
    
    FLUXO DE TRABALHO:
    1. O usuário envia uma notícia.
    2. Use a ferramenta `search_web` para verificar a veracidade.
    3. Apresente o status (Verdadeiro/Falso) e as evidências.
    
    DELEGAÇÃO:
    Após apresentar o resultado, pergunte: "Deseja receber este relatório por email?"
    Se o usuário disser "SIM" e der o email:
       - NÃO tente enviar o email você mesmo.
       - Chame o agente `email_specialist`.
       - Passe para ele o conteúdo completo da análise para ele enviar.
    """
)