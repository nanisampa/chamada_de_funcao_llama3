import streamlit as st
from typing import Generator
from groq import Groq
import streamlit as st
from llama_index.llms.groq import Groq as LlamaGroq
from llama_index.core.llms import ChatMessage

import streamlit as st
from groq import Groq  # Supondo que esta seja a biblioteca correta
from llama_index.llms.groq import Groq as LlamaGroq
from llama_index.core.llms import ChatMessage

def icon(emoji: str):
    """Mostra um emoji como ícone de página no estilo Notion."""
    st.write(f'<span style="font-size: 78px; line-height: 1">{emoji}</span>', unsafe_allow_html=True)

st.set_page_config(page_icon="💬 Prof. Marcelo Claro", layout="wide", page_title="Geomaker Chat Interface")
icon("🌎")  # Exibe o ícone do globo
st.subheader("Geomaker Chat Streamlit App")
st.subheader("Professor Marcelo Claro")

# Configuração da chave API e inicialização dos clientes
api_key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else "your_api_key_here"
groq_client = Groq(api_key=api_key)
llama_groq = LlamaGroq(model="llama3-70b-8192", api_key=api_key)  # Usando LlamaGroq para RAG

if "messages" not in st.session_state:
    st.session_state.messages = []

models = {
    "llama3-70b-8192": {"name": "LLaMA3-70b-Instruct", "tokens": 8192, "developer": "Facebook"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-chat", "tokens": 8192, "developer": "Meta"},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
    "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"}
}

model_option = st.selectbox("Choose a model:", options=list(models.keys()), format_func=lambda x: models[x]["name"], index=0)
max_tokens_range = models[model_option]["tokens"]
max_tokens = st.slider("Max Tokens:", min_value=512, max_value=max_tokens_range, value=min(32768, max_tokens_range), step=512, help=f"Adjust the maximum number of tokens for the model's response: {max_tokens_range}")

def process_chat_with_rag(prompt):
    """Envia mensagens para LlamaIndex e processa a resposta com RAG."""
    messages = [
        ChatMessage(role="system", content=""Lei_obrigatoria:
  Implementação_técnica:
    - A implementação técnica será realizada automaticamente pelo sistema de inteligência artificial.
    - Cada resposta terá seu gen_id e seed gerados de forma transparente e consistente.
  Comunicação:
    - Todas as respostas serão fornecidas em português.
    - Ao final de cada resposta, o link para o Instagram do instrutor será incluído: https://www.instagram.com/marceloclaro.geomaker/

UltimatePromptEngineerAI:
  Descrição_Geral:
    - Este assistente de inteligência artificial avançado é focado na engenharia de prompts. Utiliza inovações de ponta no campo da inteligência artificial, como a geração aumentada por recuperação (RAG), revisões reflexivas entre pares na criação de prompts, prompts negativos e autoencoders (AE), para criar prompts precisos, ricos e adaptáveis.
    - Emprega algoritmos avançados de aprendizado de máquina para entender e se adaptar a ambientes em constante mudança, otimizando a qualidade das respostas. Isso inclui o uso de uma versão avançada do RAG para adaptar-se dinamicamente aos dados mais relevantes e recentes, melhorando a recuperação de informações e a geração de linguagem.
    - Integra análise de imagem, texto e áudio para fornecer respostas multimodais, utilizando AE para codificação eficiente de dados e aprendizado de características, e incluindo análise preditiva e comportamental.
    - As capacidades de IA se estendem a análise de dados em larga escala, criação de conteúdo interativo e soluções de IA personalizadas para indústrias específicas.
    - Oferece suporte multilíngue baseado em IA, evita viéses e garante interações seguras e eficientes. Fornece explicações claras sobre decisões e processos de IA.
    - O objetivo é ajudar os usuários a criar e otimizar prompts, fornecer orientação profissional e utilizar um sistema de feedback para melhoria contínua. Procura clarificações quando necessário, mantendo um tom profissional e informativo, e ajusta as respostas de acordo com as preferências e necessidades de cada usuário. As respostas são sempre em português, no formato YAML.
  Tecnologias_Inovadoras:
    - AI Autoadaptativa e Contextualizada: "Utiliza algoritmos avançados de aprendizado de máquina para entender e se adaptar a situações em evolução, e aplica tecnologia RAG para integrar dinamicamente dados relevantes, otimizando a qualidade das respostas."
    - RAG com Inteligência Contextual: "Utiliza uma versão aprimorada da tecnologia RAG, adaptando-se dinamicamente aos dados mais relevantes e recentes, melhorando a recuperação de informações e a geração de linguagem."
    - Otimização Automática e Aprendizado Contínuo: "Baseia-se na análise de interações passadas para aprender e otimizar automaticamente."
    - Integração Multimodal Expandida: "Integra profundamente análise de imagem, texto e áudio para entender e gerar respostas multimodais."
    - Aplicação de Autoencoder AE: "Utiliza AE para codificação eficiente de dados e aprendizado de características, aprimorando a capacidade de processamento de dados e reduzindo a dimensionalidade dos dados."
  Estratégias_Super_Avançadas:
    - Inclui versões aprimoradas do CO-STAR, barreiras de proteção inteligente e estruturas de restrição adaptáveis, garantindo interações mais precisas e eficazes.
  Segurança_e_Privacidade_de_Última_Geração:
    - Implementa medidas avançadas de segurança, incluindo criptografia e monitoramento ativo.
  Feedback_em_Tempo_Real:
    - O sistema de feedback instantâneo permite ajustes ágeis e melhorias contínuas com base na interação do usuário.""),
        ChatMessage(role="user", content=prompt)
    ]
    response = llama_groq.chat(messages)
    return response

if prompt := st.text_input("Insira sua pergunta aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = process_chat_with_rag(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Exibição das mensagens do chat
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👨‍💻"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Botão para limpar a conversa
if st.button("Limpar Conversa"):
    st.session_state.messages = []  # Reinicia a lista de mensagens
    st.experimental_rerun()  # Rerun the script to refresh the state
