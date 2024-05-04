import streamlit as st
from typing import Generator
from groq import Groq



# Definindo uma função para exibir ícones em estilo grande, similar ao Notion
def icon(emoji: str):
    """Mostra um emoji como ícone de página no estilo Notion."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

# Configurações iniciais da página Streamlit
st.set_page_config(page_icon="💬", layout="wide", page_title="Geomaker Chat Interface")

# Exibe um ícone de carro de corrida
icon("🏎️")

# Adiciona um subtítulo à página
st.subheader("Geomaker Chat Streamlit App")

# Verifica se a chave API está configurada em st.secrets e inicializa o cliente API
if "GROQ_API_KEY" in st.secrets:
    from groq import Groq  # Importa a biblioteca Groq assumindo sua existência
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("API Key not configured in st.secrets!", icon="🚨")

# Inicialização do histórico de chat e modelo selecionado no estado de sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# Dicionário com detalhes dos modelos disponíveis
models = {
    "llama3-70b-8192": {"name": "LLaMA3-70b-Instruct", "tokens": 8192, "developer": "Facebook"},
    "llama2-70b-4096": {"name": "LLaMA2-70b-chat", "tokens": 4096, "developer": "Meta"},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
    "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"}
}

# Interface para seleção do modelo
model_option = st.selectbox(
    "Choose a model:",
    options=list(models.keys()),
    format_func=lambda x: models[x]["name"],
    index=0  # Default to the first model in the list
)

# Atualiza o modelo selecionado e limpa o histórico se o modelo mudar
if st.session_state.selected_model != model_option:
    st.session_state.messages = []
    st.session_state.selected_model = model_option

# Interface para ajuste do número máximo de tokens
max_tokens_range = models[model_option]["tokens"]
max_tokens = st.slider(
    "Max Tokens:",
    min_value=512,
    max_value=max_tokens_range,
    value=min(32768, max_tokens_range),
    step=512,
    help=f"Adjust the maximum number of tokens (words) for the model's response. Max for selected model: {max_tokens_range}",
)

# Função para gerar respostas de chat da API
def generate_chat_responses(chat_completion):
    """Gera conteúdo de resposta do chat a partir da resposta da API do Groq."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Interface de entrada de chat
if prompt := st.text_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Processa a entrada do usuário e busca respostas da API
    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            max_tokens=max_tokens,
            stream=True,
        )

        chat_responses_generator = generate_chat_responses(chat_completion)
        full_response = "".join(list(chat_responses_generator))
        if full_response:
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
    except Exception as e:
        st.error(f"Error: {e}", icon="🚨")

# Mostra mensagens de chat
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👨‍💻"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
