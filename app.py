from langchain_groq import ChatGroq
import os
import yfinance as yf
import pandas as pd
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from datetime import date
import plotly.graph_objects as go
import streamlit as st

@tool
def get_stock_info(symbol, key):
    """
    Retorna informações detalhadas sobre a ação especificada pelo símbolo e chave.
    """
    data = yf.Ticker(symbol)
    stock_info = data.info
    return stock_info[key]

@tool
def get_historical_price(symbol, start_date, end_date):
    """
    Retorna os preços históricos de uma ação entre as datas especificadas.
    """
    data = yf.Ticker(symbol)
    hist = data.history(start=start_date, end=end_date)
    hist = hist.reset_index()
    hist[symbol] = hist['Close']
    return hist[['Date', symbol]]

def plot_price_over_time(historical_price_dfs):
    """
    Cria um gráfico dos preços das ações ao longo do tempo com os dados fornecidos.
    """
    full_df = pd.DataFrame(columns=['Date'])
    for df in historical_price_dfs:
        full_df = full_df.merge(df, on='Date', how='outer')

    fig = go.Figure()
    for column in full_df.columns[1:]:
        fig.add_trace(go.Scatter(x=full_df['Date'], y=full_df[column], mode='lines+markers', name=column))

    fig.update_layout(
        title='Stock Price Over Time',
        xaxis_title='Date',
        yaxis_title='Stock Price (USD)',
        yaxis_tickprefix='$',
        yaxis_tickformat=',.2f',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)

def call_functions(llm_with_tools, user_prompt):
    """
    Coordena as funções de obtenção de informações e gráficos de ações com base no prompt do usuário.
    """
    system_prompt = f'You are a helpful finance assistant that analyzes stocks and stock prices. Today is {date.today()}'
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
        symbols = ' and '.join(symbols)
        messages.append(ToolMessage(f'A historical stock price chart for {symbols} has been generated.', tool_call_id=0))

    return llm_with_tools.invoke(messages).content

def main():
    """
    Função principal para executar a aplicação Streamlit.
    """
    api_key = "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"
    llm = ChatGroq(groq_api_key=api_key, model='llama3-70b-8192')
    tools = [get_stock_info, get_historical_price]
    llm_with_tools = llm.bind_tools(tools)

    st.title("Stock Market Analysis with Llama 3")
    user_question = st.text_input("Ask a question about stock prices or companies:")

    if user_question:
        response = call_functions(llm_with_tools, user_question)
        st.write(response)

if __name__ == "__main__":
    main()
