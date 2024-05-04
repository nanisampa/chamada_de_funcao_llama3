# Importa as bibliotecas necessárias
from langchain_groq import ChatGroq
import os
import yfinance as yf
import pandas as pd
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from datetime import date
import plotly.graph_objects as go
import streamlit as st

# Define a função para obter informações detalhadas sobre uma ação específica
@tool
def get_stock_info(symbol, key):
    """
    Retorna informações detalhadas sobre a ação especificada pelo símbolo e chave.
    """
    data = yf.Ticker(symbol)  # Cria um objeto Ticker para o símbolo especificado
    stock_info = data.info  # Obtém todas as informações disponíveis sobre a ação
    return stock_info[key]  # Retorna o valor para a chave especificada

# Define a função para obter os preços históricos de uma ação
@tool
def get_historical_price(symbol, start_date, end_date):
    """
    Retorna os preços históricos de uma ação entre as datas especificadas.
    """
    data = yf.Ticker(symbol)  # Cria um objeto Ticker para o símbolo especificado
    hist = data.history(start=start_date, end=end_date)  # Obtém o histórico de preços
    hist = hist.reset_index()  # Reseta o índice para fazer a data uma coluna normal
    hist[symbol] = hist['Close']  # Cria uma coluna com o preço de fechamento
    return hist[['Date', symbol]]  # Retorna um DataFrame com data e preço de fechamento

# Função para criar gráficos dos preços das ações ao longo do tempo
def plot_price_over_time(historical_price_dfs):
    """
    Cria um gráfico dos preços das ações ao longo do tempo com os dados fornecidos.
    """
    full_df = pd.DataFrame(columns=['Date'])  # Inicializa um DataFrame vazio
    for df in historical_price_dfs:
        full_df = full_df.merge(df, on='Date', how='outer')  # Mescla os DataFrames pelo campo 'Date'

    fig = go.Figure()  # Cria uma figura Plotly
    for column in full_df.columns[1:]:  # Adiciona uma linha para cada coluna de ações no DataFrame
        fig.add_trace(go.Scatter(x=full_df['Date'], y=full_df[column], mode='lines+markers', name=column))

    # Configura o layout do gráfico
    fig.update_layout(
        title='Preço das Ações ao Longo do Tempo',
        xaxis_title='Data',
        yaxis_title='Preço da Ação (USD)',
        yaxis_tickprefix='$',
        yaxis_tickformat=',.2f',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)  # Exibe o gráfico no Streamlit

# Função que coordena a obtenção de informações e gráficos baseados no prompt do usuário
def call_functions(llm_with_tools, user_prompt):
    """
    Coordena as funções de obtenção de informações e gráficos de ações com base no prompt do usuário.
    """
    system_prompt = f'Você é um assistente financeiro útil que analisa ações e preços de ações. Hoje é {date.today()}'
    messages = [SystemMessage(system_prompt), HumanMessage(user_prompt)]
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)
    historical_price_dfs = []
    symbols = []

    for tool_call in ai_msg.tool_calls:
        selected_tool = {"get_stock_info": get_stock_info, "get_historical_price": get_historical_price}[tool_call["name"].lower()]
        tool_output = selected_tool.invoke(tool_call["args"])
        if tool_call['name'] == 'get_historical_price':
            historical_price_dfs.append(tool_output)
            symbols.append(tool_output.columns[1])
        else:
            messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))

    if len(historical_price_dfs) > 0:
        plot_price_over_time(historical_price_dfs)
        symbols = ' e '.join(symbols)
        messages.append(ToolMessage(f'Um gráfico de preços históricos para {symbols} foi gerado.', tool_call_id=0))

    return llm_with_tools.invoke(messages).content

# Função principal que executa a aplicação Streamlit
def main():
    """
    Função principal para executar a aplicação Streamlit.
    """
    api_key = "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"  # Substitua com sua chave real de API
    llm = ChatGroq(groq_api_key=api_key, model='llama3-70b-8192')
    tools = [get_stock_info, get_historical_price]
    llm_with_tools = llm.bind_tools(tools)

    st.title("Análise do Mercado de Ações com Llama 3")
    user_question = st.text_input("Faça uma pergunta sobre preços de ações ou empresas:")

    if user_question:
        response = call_functions(llm_with_tools, user_question)
        st.write(response)

# Verifica se o script é o módulo principal e executa a função main
if __name__ == "__main__":
    main()
