
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from collections import Counter
import re
import os

# Configuração da página
st.set_page_config(
    page_title="Análise Grupo de Estudos AWS re/Start",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar e processar dados
@st.cache_data
def load_data():
    """Carrega e processa os dados dos três arquivos CSV"""
    try:
        # Obter o caminho do diretório do script
        script_dir = os.path.dirname(__file__)
        
        # Carregar os três arquivos
        nivelamento = pd.read_csv(os.path.join(script_dir, 'Start - BRSAO 202 AWS - NIVELAMENTO.csv'))
        aula01 = pd.read_csv(os.path.join(script_dir, 'Start - BRSAO 202 AWS - AULA 01.csv'))
        aula02 = pd.read_csv(os.path.join(script_dir, 'Start - BRSAO 202 AWS - AULA 02.csv'))
        
        # Adicionar coluna de origem
        nivelamento['Origem'] = 'Nivelamento'
        aula01['Origem'] = 'Aula 01'
        aula02['Origem'] = 'Aula 02'
        
        # Combinar todos os dados
        dados_completos = pd.concat([nivelamento, aula01, aula02], ignore_index=True)
        
        return dados_completos, nivelamento, aula01, aula02
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None, None, None

# Função para processar dias da semana
def processar_dias_semana(dados):
    """Processa e conta os dias da semana mais escolhidos"""
    todos_dias = []
    for dias_str in dados['Quais dias da semana você tem disponibilidade para estudar? '].dropna():
        dias = [dia.strip() for dia in str(dias_str).split(';')]
        todos_dias.extend(dias)
    
    contador_dias = Counter(todos_dias)
    return contador_dias

# Função para processar horários
def processar_horarios(dados):
    """Processa e conta os horários mais escolhidos"""
    todos_horarios = []
    for horario_str in dados['Quais horários você pode estudar? '].dropna():
        horarios = [horario.strip() for horario in str(horario_str).split(';')]
        todos_horarios.extend(horarios)
    
    contador_horarios = Counter(todos_horarios)
    return contador_horarios

# Função para processar temas
def processar_temas(dados):
    """Processa e conta os temas mais solicitados"""
    todos_temas = []
    for tema_str in dados['Quais temas da aula você gostaria de revisar no grupo de estudos? '].dropna():
        # Limpar e dividir temas
        temas = [tema.strip() for tema in str(tema_str).split(';') if tema.strip()]
        todos_temas.extend(temas)
    
    contador_temas = Counter(todos_temas)
    return contador_temas

# Função para processar formas de estudo
def processar_formas_estudo(dados):
    """Processa e conta as formas de estudo preferidas"""
    todas_formas = []
    for forma_str in dados['Você prefere revisar conteúdo em grupo de estudo através de: '].dropna():
        formas = [forma.strip() for forma in str(forma_str).split(';')]
        todas_formas.extend(formas)
    
    contador_formas = Counter(todas_formas)
    return contador_formas

def criar_termometro_dificuldade(dados):
    """Cria um gráfico de termômetro para a dificuldade percebida."""
    coluna_dificuldade = 'Como você avalia sua facilidade/dificuldade com os temas da aula? '
    if coluna_dificuldade not in dados.columns or dados[coluna_dificuldade].dropna().empty:
        return None
    
    media_dificuldade = dados[coluna_dificuldade].mean()
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = media_dificuldade,
        title = {'text': "Nível de Dificuldade (1=Fácil, 5=Difícil)"},
        gauge = {
            'axis': {'range': [1, 5], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "rgba(0,0,0,0)"},
            'steps' : [
                {'range': [1, 2.5], 'color': 'lightgreen'},
                {'range': [2.5, 3.5], 'color': 'yellow'},
                {'range': [3.5, 5], 'color': 'red'}],
            'threshold' : {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': media_dificuldade
            }
        }
    ))
    fig.update_layout(height=400)
    return fig

# Função principal
def main():
    # Título principal
    st.title("Análise do Grupo de Estudos AWS re/Start")
    st.markdown("[Acesse o nosso discord](https://discord.gg/NTAtHGXy) | [Acesse a planilha oficial](https://escoladanuvem.sharepoint.com/:x:/s/pedagogico/EaaqSNzKuoNPuRvNTXzShd4BnbR7tl2pz_I-YmK8AWdaTw?rtime=9MCy6zXg3Ug)")
    st.markdown("---")
    
    # Carregar dados
    dados_completos, nivelamento, aula01, aula02 = load_data()
    
    if dados_completos is None:
        st.error("Não foi possível carregar os dados. Verifique se os arquivos CSV estão no diretório correto.")
        return

    # Exibir lista de participantes no início
    with st.expander("Ver lista de todos os participantes"):
        nomes_unicos = dados_completos['Nome Completo '].dropna().unique()
        for nome in sorted(nomes_unicos):
            st.markdown(f"- {nome.strip()}")
    
    # Sidebar com filtros
    st.sidebar.header("Filtros")
    origem_selecionada = st.sidebar.multiselect(
        "Selecione as origens dos dados:",
        options=['Nivelamento', 'Aula 01', 'Aula 02'],
        default=['Nivelamento', 'Aula 01', 'Aula 02']
    )
    
    # Filtrar dados baseado na seleção
    dados_filtrados = dados_completos[dados_completos['Origem'].isin(origem_selecionada)]
    
    # Métricas gerais
    st.subheader("Visão Geral")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Formulários Respondidos", len(dados_filtrados))
    
    with col2:
        participantes_unicos = dados_filtrados['E-mail '].nunique()
        st.metric("Participantes Únicos", participantes_unicos)
    
    st.markdown("---")
    
    # Análise de Dias e Horários
    st.header("Disponibilidade para Estudos")
    col1, col2 = st.columns(2)

    with col1:
        contador_dias = processar_dias_semana(dados_filtrados)
        if contador_dias:
            dias_df = pd.DataFrame(list(contador_dias.items()), columns=['Dia', 'Votos'])
            dias_df = dias_df.sort_values('Votos', ascending=False)
            fig_dias = px.bar(
                dias_df, 
                x='Dia', 
                y='Votos',
                title='Disponibilidade por Dia da Semana',
                color='Votos',
                color_continuous_scale='Blues'
            )
            fig_dias.update_layout(height=400)
            st.plotly_chart(fig_dias, use_container_width=True)

    with col2:
        contador_horarios = processar_horarios(dados_filtrados)
        if contador_horarios:
            horarios_df = pd.DataFrame(list(contador_horarios.items()), columns=['Horário', 'Votos'])
            horarios_df = horarios_df.sort_values('Votos', ascending=False)
            fig_horarios = px.pie(
                horarios_df, 
                values='Votos', 
                names='Horário',
                title='Distribuição de Horários Preferidos',
                hole=0.4
            )
            fig_horarios.update_layout(height=400)
            st.plotly_chart(fig_horarios, use_container_width=True)

    if contador_dias:
        st.subheader("Top 5 Dias Mais Votados")
        dias_df_top5 = pd.DataFrame(list(contador_dias.items()), columns=['Dia', 'Votos']).sort_values('Votos', ascending=False).head(5)
        st.table(dias_df_top5)

    st.markdown("---")
    
    # Análise de Temas
    st.header("Temas Mais Solicitados para Revisão")
    contador_temas = processar_temas(dados_filtrados)
    if contador_temas:
        temas_filtrados = {tema: votos for tema, votos in contador_temas.items() if votos > 0}
        temas_df = pd.DataFrame(list(temas_filtrados.items()), columns=['Tema', 'Votos'])
        temas_df = temas_df.sort_values('Votos', ascending=True)
        
        fig_temas = px.bar(
            temas_df.tail(15), 
            x='Votos', 
            y='Tema',
            title='Top 15 Temas Mais Solicitados',
            orientation='h',
            color='Votos',
            color_continuous_scale='Viridis'
        )
        fig_temas.update_layout(height=500)
        st.plotly_chart(fig_temas, use_container_width=True)
        
        with st.expander("Ver todos os temas solicitados"):
            temas_completos_df = pd.DataFrame(list(contador_temas.items()), columns=['Tema', 'Votos'])
            temas_completos_df = temas_completos_df.sort_values('Votos', ascending=False)
            st.dataframe(temas_completos_df, use_container_width=True)
    
    st.markdown("---")
    
    # Análise de Formas de Estudo e Mentoria
    st.header("Metodologia e Mentoria")
    col1, col2 = st.columns(2)

    with col1:
        contador_formas = processar_formas_estudo(dados_filtrados)
        if contador_formas:
            formas_df = pd.DataFrame(list(contador_formas.items()), columns=['Forma de Estudo', 'Votos'])
            formas_df = formas_df.sort_values('Votos', ascending=False)
            fig_formas = px.bar(
                formas_df, 
                x='Forma de Estudo', 
                y='Votos',
                title='Preferências de Metodologia de Estudo',
                color='Votos',
                color_continuous_scale='Oranges'
            )
            fig_formas.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig_formas, use_container_width=True)

    with col2:
        mentoria_counts = dados_filtrados['Você gostaria de ser mentor/líder em algum encontro de grupo (explicar um tema que você domina)? '].value_counts()
        fig_mentoria = px.pie(
            values=mentoria_counts.values, 
            names=mentoria_counts.index,
            title='Disponibilidade para Mentoria',
            hole=0.4
        )
        st.plotly_chart(fig_mentoria, use_container_width=True)
        
        mentores = dados_filtrados[dados_filtrados['Você gostaria de ser mentor/líder em algum encontro de grupo (explicar um tema que você domina)? '] == 'Sim']['Nome Completo '].unique()
        if len(mentores) > 0:
            with st.expander(f"Ver os {len(mentores)} mentores disponíveis"):
                for mentor in mentores:
                    st.markdown(f"- {mentor}")

    st.markdown("---")

    # Termômetro de Dificuldade
    st.header("Nível de Dificuldade Percebido")
    fig_termometro = criar_termometro_dificuldade(dados_filtrados)
    if fig_termometro:
        st.plotly_chart(fig_termometro, use_container_width=True)
    else:
        st.info("Não há dados de dificuldade para os filtros selecionados.")

    st.markdown("---")
    
    # Análise de Confiança
    st.header("Nível de Confiança dos Participantes")
    confianca_counts = dados_filtrados['Você se sente confiante para aplicar os conceitos desta aula em exercícios/laboratórios? '].value_counts()
    fig_confianca = px.bar(
        x=confianca_counts.index, 
        y=confianca_counts.values,
        title='Distribuição do Nível de Confiança',
        labels={'x': 'Nível de Confiança', 'y': 'Número de Pessoas'},
        color=confianca_counts.values,
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig_confianca, use_container_width=True)
    
    st.markdown("---")
    
    # Resumo
    st.header("Resumo dos Principais Insights")
    if contador_dias:
        melhor_dia = max(contador_dias, key=contador_dias.get)
        st.write(f"- **Melhor dia**: {melhor_dia} ({contador_dias[melhor_dia]} votos)")
    if contador_horarios:
        melhor_horario = max(contador_horarios, key=contador_horarios.get)
        st.write(f"- **Melhor horário**: {melhor_horario} ({contador_horarios[melhor_horario]} votos)")
    if contador_formas:
        melhor_forma = max(contador_formas, key=contador_formas.get)
        st.write(f"- **Forma de estudo preferida**: {melhor_forma} ({contador_formas[melhor_forma]} votos)")
    total_respostas = len(dados_filtrados)
    mentores_sim = mentoria_counts.get('Sim', 0)
    percentual_mentores = (mentores_sim / total_respostas * 100) if total_respostas > 0 else 0
    st.write(f"- **Mentores disponíveis**: {percentual_mentores:.1f}% dos participantes")
    
    with st.expander("Ver dados brutos"):
        st.dataframe(dados_filtrados, use_container_width=True)

if __name__ == "__main__":
    main()
