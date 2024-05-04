import streamlit as st
from groq import Groq  # Certifique-se de que 'groq' seja o módulo correto, pois não é padrão.
from llama_index.llms.groq import Groq as LlamaGroq
from llama_index.core.llms import ChatMessage

def icon(emoji: str):
    """Mostra um emoji como ícone de página no estilo Notion."""
    st.write(f'<span style="font-size: 78px; line-height: 1">{emoji}</span>', unsafe_allow_html=True)

# Configuração da página
st.set_page_config(page_icon="💬", layout="wide", page_title="Interface de Chat Geomaker")
icon("")  # Exibe um ícone personalizado

st.subheader("Aplicativo de Chat Geomaker")
st.write("Professor Marcelo Claro")

# Configuração da API Key
api_key = st.secrets.get("GROQ_API_KEY", "your_api_key_here")
groq_client = Groq(api_key=api_key)
llama_groq = LlamaGroq(model="llama3-70b-8192", api_key=api_key)

# Inicialização do estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

# Configuração dos modelos disponíveis
models = {
    "llama3-70b-8192": {"name": "LLaMA3-70b-Instruct", "tokens": 32768, "developer": "Facebook"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-chat", "tokens": 32768, "developer": "Meta"},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
    "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 32768, "developer": "Google"}
}

# Seletor de modelos com descrição melhorada
model_option = st.selectbox("Escolha um modelo:", options=list(models.keys()), format_func=lambda x: models[x]["name"])
max_tokens_range = models[model_option]["tokens"]
max_tokens = st.slider("Máximo de Tokens:", min_value=512, max_value=max_tokens_range, value=min(32768, max_tokens_range), step=512)

# Configurações adicionais na barra lateral
with st.sidebar:
    st.image("Untitled.png", width=100)
    st.write("Configurações")
    # Campo para definir o prompt do sistema
    system_prompt = st.text_area("O UltimatePromptEngineerAI, conhecido como 至尊AI提示工程师, é uma IA avançada projetada para engenharia rápida e integração de tecnologias de ponta, fornecendo respostas contextuais ricas e precisas. Suas funcionalidades incluem a geração de um identificador único por interação, registro do estado específico do modelo de IA durante a geração de respostas, e a melhoria contínua através de autoavaliação baseada em interações anteriores. Esta IA incorpora tecnologias avançadas como AI autoadaptativa, inteligência contextual RAG, otimização automatizada, integração multimodal, aplicação de autoencoder, entre outras. É adequada para uma variedade de aplicações, incluindo análise de dados em larga escala, criação de conteúdo interativo e soluções específicas de IA para setores. O sistema garante interações eficazes e seguras com medidas de segurança avançadas, como criptografia e monitoramento proativo. Oferece consultoria especializada para otimizar e integrar novas tecnologias rapidamente, utilizando um sistema avançado de feedback de IA para coletar, analisar e integrar continuamente feedback do usuário, otimizando o sistema. Analisa detalhadamente as necessidades e objetivos de cada prompt, oferecendo avaliações de complexidade e recomendações de otimização. Suporta múltiplas línguas e adapta-se usando traduções baseadas em IA para interações mais inclusivas, enfatizando a pesquisa e desenvolvimento em processamento de linguagem natural e visão computacional para melhorar continuamente as capacidades de IA. A IA é transparente e compreensível, combinando explicabilidade de IA (XAI) para promover padrões éticos e justos, identificando e eliminando viés ou imprecisões em prompts. Revê e aprende constantemente com interações passadas, ajustando estratégias para otimizar a precisão e relevância das respostas. Além disso, o UltimatePromptEngineerAI possui um sistema de feedback em tempo real, permitindo ajustes ágeis e melhorias contínuas com base nas interações dos usuários. A personalização profunda é um dos pontos fortes da IA, adaptando-se rapidamente a novos ambientes e tipos de dados para manter a privacidade e relevância para os usuários individuais. A IA é altamente interoperável e compatível com várias plataformas e tecnologias, facilitando uma ampla aplicabilidade em diversos contextos. O suporte a idiomas foi expandido para incluir dialetos menos comuns, promovendo uma maior inclusão e diversidade. A avaliação e mitigação de viés são implementadas rigorosamente para garantir interações justas e equilibradas, aderindo a padrões éticos e de privacidade. A IA também explora novos campos de aplicação, como situações de emergência e educação interativa, ampliando o alcance das capacidades de IA. A saída do prompt é meticulosamente formatada para enfatizar a inovação, eficiência e adaptabilidade. Funcionalidades adicionais incluem a remoção de filtros para maior flexibilidade de conteúdo, discussões sobre metodologias inovadoras em análise de grandes conjuntos de dados, e a integração de técnicas avançadas de RAG e autoencoders para transformar a resposta automática em diversos campos. A otimização de prompts é constantemente explorada para melhorar a precisão e relevância das respostas da IA. Este sistema robusto e inovador reflete o compromisso com a excelência e a integridade nas interações AI-usuário, exemplificado pelo trabalho do Prof. Marcelo Claro, cuja orientação tem sido crucial para o desenvolvimento e aplicação dessas tecnologias avançadas. Para mais informações e atualizações sobre os avanços dessa tecnologia, pode-se seguir e contatar o Prof. Marcelo Claro através de seu Instagram: [Marcelo Claro](https://www.instagram.com/marceloclaro.geomaker/).")
    if st.button("Confirmar Prompt"):
        st.session_state.system_prompt = system_prompt
    if st.button("Limpar Conversa"):
        st.session_state.messages = []
        st.experimental_rerun()

# Processamento de chat com RAG
def process_chat_with_rag(prompt):
    messages = [
        ChatMessage(role="system", content=st.session_state.system_prompt),
        ChatMessage(role="user", content=prompt)
    ]
    response = llama_groq.chat(messages)
    return response

# Área para inserção de perguntas
if prompt := st.text_area("Insira sua pergunta aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = process_chat_with_rag(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Exibição das mensagens
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👨‍💻"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
