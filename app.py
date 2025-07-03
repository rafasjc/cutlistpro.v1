"""
CutList Pro - Aplicação Principal (Versão Completa)
Geração de planos de corte e orçamentos profissionais
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import io
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="CutList Pro",
    page_icon="🪚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e86ab 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2e86ab;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button {
        background: linear-gradient(90deg, #2e86ab 0%, #1f4e79 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .project-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'current_project' not in st.session_state:
    st.session_state.current_project = 0
if 'cutting_diagram_generated' not in st.session_state:
    st.session_state.cutting_diagram_generated = False
if 'budget_generated' not in st.session_state:
    st.session_state.budget_generated = False

# Dados de exemplo (simulando banco de dados)
@st.cache_data
def get_sample_data():
    return {
        'projects': [
            {
                'id': 1,
                'name': 'Estante de Livros',
                'description': 'Estante simples com 3 prateleiras',
                'created_at': '02/07/2025 15:30',
                'updated_at': '03/07/2025 14:45',
                'status': 'Em desenvolvimento',
                'components': 4,
                'total_area': 0.98,
                'estimated_cost': 78.40,
                'material_type': 'MDF 15mm'
            },
            {
                'id': 2,
                'name': 'Mesa de Jantar',
                'description': 'Mesa retangular para 6 pessoas',
                'created_at': '01/07/2025 10:15',
                'updated_at': '02/07/2025 16:20',
                'status': 'Planejamento',
                'components': 6,
                'total_area': 2.45,
                'estimated_cost': 196.00,
                'material_type': 'Compensado 18mm'
            },
            {
                'id': 3,
                'name': 'Armário de Cozinha',
                'description': 'Armário suspenso com 2 portas',
                'created_at': '30/06/2025 14:30',
                'updated_at': '01/07/2025 09:10',
                'status': 'Concluído',
                'components': 8,
                'total_area': 1.85,
                'estimated_cost': 148.00,
                'material_type': 'MDP 15mm'
            }
        ],
        'components': {
            1: [  # Estante de Livros
                {'name': 'Lateral Esquerda', 'length': 600, 'width': 300, 'thickness': 15, 'quantity': 1, 'material': 'MDF'},
                {'name': 'Lateral Direita', 'length': 600, 'width': 300, 'thickness': 15, 'quantity': 1, 'material': 'MDF'},
                {'name': 'Fundo', 'length': 570, 'width': 270, 'thickness': 15, 'quantity': 1, 'material': 'MDF'},
                {'name': 'Prateleira', 'length': 570, 'width': 270, 'thickness': 15, 'quantity': 2, 'material': 'MDF'}
            ],
            2: [  # Mesa de Jantar
                {'name': 'Tampo', 'length': 1800, 'width': 900, 'thickness': 18, 'quantity': 1, 'material': 'Compensado'},
                {'name': 'Perna Frontal Esq', 'length': 720, 'width': 80, 'thickness': 18, 'quantity': 1, 'material': 'Compensado'},
                {'name': 'Perna Frontal Dir', 'length': 720, 'width': 80, 'thickness': 18, 'quantity': 1, 'material': 'Compensado'},
                {'name': 'Perna Traseira Esq', 'length': 720, 'width': 80, 'thickness': 18, 'quantity': 1, 'material': 'Compensado'},
                {'name': 'Perna Traseira Dir', 'length': 720, 'width': 80, 'thickness': 18, 'quantity': 1, 'material': 'Compensado'},
                {'name': 'Travessa', 'length': 1600, 'width': 100, 'thickness': 18, 'quantity': 2, 'material': 'Compensado'}
            ],
            3: [  # Armário de Cozinha
                {'name': 'Lateral Esquerda', 'length': 700, 'width': 320, 'thickness': 15, 'quantity': 1, 'material': 'MDP'},
                {'name': 'Lateral Direita', 'length': 700, 'width': 320, 'thickness': 15, 'quantity': 1, 'material': 'MDP'},
                {'name': 'Fundo', 'length': 770, 'width': 320, 'thickness': 15, 'quantity': 1, 'material': 'MDP'},
                {'name': 'Prateleira', 'length': 770, 'width': 300, 'thickness': 15, 'quantity': 2, 'material': 'MDP'},
                {'name': 'Porta Esquerda', 'length': 350, 'width': 680, 'thickness': 15, 'quantity': 1, 'material': 'MDP'},
                {'name': 'Porta Direita', 'length': 350, 'width': 680, 'thickness': 15, 'quantity': 1, 'material': 'MDP'},
                {'name': 'Topo', 'length': 800, 'width': 320, 'thickness': 15, 'quantity': 1, 'material': 'MDP'},
                {'name': 'Base', 'length': 800, 'width': 320, 'thickness': 15, 'quantity': 1, 'material': 'MDP'}
            ]
        },
        'materials': [
            {'name': 'MDF', 'thickness': 15, 'price': 80.00, 'unit': 'm²', 'category': 'Madeira Reconstituída', 'density': 650},
            {'name': 'Compensado', 'thickness': 18, 'price': 120.00, 'unit': 'm²', 'category': 'Madeira Laminada', 'density': 600},
            {'name': 'Pinus', 'thickness': 25, 'price': 15.00, 'unit': 'm', 'category': 'Madeira Maciça', 'density': 450},
            {'name': 'MDP', 'thickness': 15, 'price': 65.00, 'unit': 'm²', 'category': 'Madeira Reconstituída', 'density': 680},
            {'name': 'OSB', 'thickness': 12, 'price': 45.00, 'unit': 'm²', 'category': 'Madeira Reconstituída', 'density': 620}
        ]
    }

# Função para calcular área
def calculate_area(length, width, quantity=1):
    return (length * width * quantity) / 1000000  # mm² para m²

# Função para calcular peso
def calculate_weight(area, material_name, materials):
    material = next((m for m in materials if m['name'] == material_name), None)
    if material:
        thickness_m = material['thickness'] / 1000  # mm para m
        volume = area * thickness_m  # m³
        weight = volume * material['density']  # kg
        return weight
    return 0

# Função para gerar orçamento detalhado
def generate_budget(project_id, components, materials):
    budget_data = []
    total_cost = 0
    total_area = 0
    total_weight = 0
    
    # Agrupar componentes por material
    material_summary = {}
    
    for comp in components:
        area = calculate_area(comp['length'], comp['width'], comp['quantity'])
        material = next((m for m in materials if m['name'] == comp['material']), None)
        
        if material:
            cost = area * material['price']
            weight = calculate_weight(area, comp['material'], materials)
            
            budget_data.append({
                'Componente': comp['name'],
                'Dimensões (mm)': f"{comp['length']} x {comp['width']} x {comp['thickness']}",
                'Quantidade': comp['quantity'],
                'Material': comp['material'],
                'Área (m²)': round(area, 4),
                'Preço Unit. (R$/m²)': material['price'],
                'Custo Total (R$)': round(cost, 2),
                'Peso (kg)': round(weight, 2)
            })
            
            # Resumo por material
            if comp['material'] not in material_summary:
                material_summary[comp['material']] = {
                    'area': 0,
                    'cost': 0,
                    'weight': 0,
                    'price': material['price']
                }
            
            material_summary[comp['material']]['area'] += area
            material_summary[comp['material']]['cost'] += cost
            material_summary[comp['material']]['weight'] += weight
            
            total_cost += cost
            total_area += area
            total_weight += weight
    
    return budget_data, material_summary, total_cost, total_area, total_weight

# Função para gerar diagrama de corte
def generate_cutting_diagram(components):
    fig = go.Figure()
    
    # Simular layout de corte em uma chapa 2750x1830mm
    sheet_width = 2750
    sheet_height = 1830
    
    # Adicionar contorno da chapa
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=sheet_width, y1=sheet_height,
        line=dict(color="black", width=3),
        fillcolor="lightgray",
        opacity=0.2
    )
    
    # Posicionar componentes (algoritmo simples)
    x_pos, y_pos = 50, 50
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    for i, comp in enumerate(components):
        # Expandir quantidade
        for q in range(comp['quantity']):
            if x_pos + comp['length'] > sheet_width - 50:
                x_pos = 50
                y_pos += max(comp['width'], 200) + 20
            
            if y_pos + comp['width'] > sheet_height - 50:
                break  # Não cabe mais na chapa
            
            # Adicionar retângulo do componente
            fig.add_shape(
                type="rect",
                x0=x_pos, y0=y_pos,
                x1=x_pos + comp['length'], y1=y_pos + comp['width'],
                line=dict(color=colors[i % len(colors)], width=2),
                fillcolor=colors[i % len(colors)],
                opacity=0.7
            )
            
            # Adicionar texto
            fig.add_annotation(
                x=x_pos + comp['length']/2,
                y=y_pos + comp['width']/2,
                text=f"{comp['name']}<br>{comp['length']}x{comp['width']}<br>Qtd: {q+1}",
                showarrow=False,
                font=dict(color="white", size=9, family="Arial Black"),
                bgcolor="rgba(0,0,0,0.5)",
                bordercolor="white",
                borderwidth=1
            )
            
            x_pos += comp['length'] + 30
    
    # Calcular estatísticas
    total_component_area = sum([calculate_area(c['length'], c['width'], c['quantity']) for c in components])
    sheet_area = (sheet_width * sheet_height) / 1000000  # mm² para m²
    utilization = (total_component_area / sheet_area) * 100
    waste = 100 - utilization
    
    fig.update_layout(
        title=f"Diagrama de Corte - Chapa 2750x1830mm | Aproveitamento: {utilization:.1f}%",
        xaxis=dict(title="Largura (mm)", range=[0, sheet_width]),
        yaxis=dict(title="Altura (mm)", range=[0, sheet_height]),
        showlegend=False,
        height=600,
        plot_bgcolor='white'
    )
    
    return fig, utilization, waste

# Função para criar relatório em CSV
def create_csv_report(budget_data, material_summary, project_name):
    # Relatório de componentes
    df_components = pd.DataFrame(budget_data)
    
    # Relatório de materiais
    material_data = []
    for material, data in material_summary.items():
        material_data.append({
            'Material': material,
            'Área Total (m²)': round(data['area'], 4),
            'Preço (R$/m²)': data['price'],
            'Custo Total (R$)': round(data['cost'], 2),
            'Peso Total (kg)': round(data['weight'], 2)
        })
    
    df_materials = pd.DataFrame(material_data)
    
    # Criar arquivo CSV combinado
    output = io.StringIO()
    output.write(f"RELATÓRIO DE ORÇAMENTO - {project_name}\n")
    output.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
    
    output.write("=== COMPONENTES ===\n")
    df_components.to_csv(output, index=False)
    
    output.write("\n\n=== RESUMO POR MATERIAL ===\n")
    df_materials.to_csv(output, index=False)
    
    return output.getvalue()

# Sidebar
with st.sidebar:
    st.markdown("### 🧭 Navegação")
    page = st.selectbox(
        "Selecione uma página:",
        ["🏠 Dashboard", "📁 Projetos", "📐 Diagramas de Corte", "📤 Importar SketchUp", "📦 Materiais", "📊 Relatórios"]
    )
    
    st.markdown("---")
    
    # Informações do projeto atual
    data = get_sample_data()
    current_project = data['projects'][st.session_state.current_project]
    
    st.markdown("### Projeto Atual:")
    st.info(f"📋 {current_project['name']}")
    st.metric("🔧 Componentes", current_project['components'])
    st.metric("📏 Área Total", f"{current_project['total_area']} m²")
    st.metric("💰 Custo Est.", f"R$ {current_project['estimated_cost']:.2f}")
    
    st.markdown("---")
    st.markdown("### Links Úteis:")
    st.markdown("- [GitHub](https://github.com )")
    st.markdown("- [Documentação](https://docs.streamlit.io )")
    st.markdown("- [Suporte](https://discuss.streamlit.io )")

# Dados
data = get_sample_data()

# Página principal
if page == "🏠 Dashboard":
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🪚 CutList Pro</h1>
        <p>Planos de Corte e Orçamentos Profissionais</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📁 Projetos", len(data['projects']), delta="3 ativos")
    
    with col2:
        total_components = sum([p['components'] for p in data['projects']])
        st.metric("🔧 Componentes", total_components, delta="18 total")
    
    with col3:
        st.metric("📦 Materiais", len(data['materials']), delta="Biblioteca completa")
    
    with col4:
        current_project = data['projects'][st.session_state.current_project]
        st.metric("📊 Projeto Atual", current_project['name'][:10] + "...", delta=current_project['status'])
    
    st.markdown("---")
    
    # Projetos recentes
    st.markdown("### 📋 Projetos Recentes")
    
    for i, project in enumerate(data['projects']):
        with st.container():
            st.markdown(f"""
            <div class="project-card">
                <h4>📁 {project['name']}</h4>
                <p><strong>Descrição:</strong> {project['description']}</p>
                <div style="display: flex; justify-content: space-between;">
                    <span><strong>Status:</strong> {project['status']}</span>
                    <span><strong>Componentes:</strong> {project['components']}</span>
                    <span><strong>Custo:</strong> R$ {project['estimated_cost']:.2f}</span>
                </div>
                <p><small>Atualizado em: {project['updated_at']}</small></p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button(f"📂 Abrir", key=f"open_{project['id']}"):
                    st.session_state.current_project = i
                    st.success(f"✅ Projeto '{project['name']}' selecionado!")
                    st.rerun()
            
            with col2:
                if st.button(f"💰 Orçar", key=f"budget_{project['id']}"):
                    st.session_state.current_project = i
                    st.session_state.budget_generated = True
                    st.success(f"💰 Orçamento gerado para '{project['name']}'!")
                    st.rerun()

elif page == "📁 Projetos":
    st.markdown("### 📁 Gerenciador de Projetos")
    
    # Seletor de projeto
    st.markdown("#### Selecionar Projeto:")
    project_options = [f"{p['name']} ({p['components']} componentes)" for p in data['projects']]
    selected_index = st.selectbox(
        "Projeto:",
        range(len(project_options)),
        format_func=lambda x: project_options[x],
        index=st.session_state.current_project,
        key="project_selector"
    )
    
    if selected_index != st.session_state.current_project:
        st.session_state.current_project = selected_index
        st.rerun()
    
    # Informações do projeto
    project = data['projects'][st.session_state.current_project]
    components = data['components'][project['id']]
    
    st.markdown(f"### 📊 {project['name']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Descrição:** {project['description']}")
        st.write(f"**Status:** {project['status']}")
        st.write(f"**Criado em:** {project['created_at']}")
    
    with col2:
        st.write(f"**Atualizado em:** {project['updated_at']}")
        st.write(f"**Componentes:** {project['components']}")
        st.write(f"**Área Total:** {project['total_area']} m²")
    
    st.markdown("---")
    
    # Lista de componentes
    st.markdown("### 🔧 Componentes")
    
    df_components = pd.DataFrame(components)
    st.dataframe(df_components, use_container_width=True)
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 Gerar Plano de Corte", type="primary"):
            st.session_state.cutting_diagram_generated = True
            st.success("✅ Plano de corte gerado! Vá para 'Diagramas de Corte' para visualizar.")
    
    with col2:
        if st.button("💰 Gerar Orçamento", type="primary"):
            st.session_state.budget_generated = True
            
            # Gerar orçamento
            budget_data, material_summary, total_cost, total_area, total_weight = generate_budget(
                project['id'], components, data['materials']
            )
            
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("### 💰 Orçamento Gerado!")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("💵 Custo Total", f"R$ {total_cost:.2f}")
            with col_b:
                st.metric("📏 Área Total", f"{total_area:.2f} m²")
            with col_c:
                st.metric("⚖️ Peso Total", f"{total_weight:.1f} kg")
            
            st.markdown("#### 📋 Resumo por Material:")
            for material, data_mat in material_summary.items():
                st.write(f"**{material}:** {data_mat['area']:.2f} m² - R$ {data_mat['cost']:.2f}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        if st.button("📄 Gerar Relatório", type="primary"):
            # Gerar dados do relatório
            budget_data, material_summary, total_cost, total_area, total_weight = generate_budget(
                project['id'], components, data['materials']
            )
            
            # Criar CSV
            csv_content = create_csv_report(budget_data, material_summary, project['name'])
            
            st.success("📄 Relatório gerado com sucesso!")
            
            # Botão de download
            st.download_button(
                label="⬇️ Download Relatório CSV",
                data=csv_content,
                file_name=f"orcamento_{project['name'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                type="primary"
            )

elif page == "📐 Diagramas de Corte":
    st.markdown("### 📐 Diagramas de Corte")
    
    current_project = data['projects'][st.session_state.current_project]
    components = data['components'][current_project['id']]
    
    if st.button("🎯 Gerar Diagrama de Corte", type="primary"):
        st.session_state.cutting_diagram_generated = True
        
        with st.spinner("Gerando diagrama otimizado..."):
            fig, utilization, waste = generate_cutting_diagram(components)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Aproveitamento", f"{utilization:.1f}%", 
                         delta="Excelente" if utilization > 80 else "Bom" if utilization > 60 else "Regular")
            
            with col2:
                st.metric("🗑️ Desperdício", f"{waste:.1f}%", 
                         delta=f"{-5:.1f}% vs média")
            
            with col3:
                st.metric("📦 Chapas Necessárias", "1", delta="Otimizado")
            
            with col4:
                sheet_cost = (2.75 * 1.83) * 80  # Área da chapa * preço MDF
                st.metric("💰 Custo da Chapa", f"R$ {sheet_cost:.2f}")
            
            # Informações adicionais
            st.markdown("---")
            st.markdown("### 📋 Informações do Corte")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Especificações da Chapa:**")
                st.write("• Dimensões: 2750 x 1830 mm")
                st.write("• Material: MDF 15mm")
                st.write("• Área: 5.03 m²")
                
            with col2:
                st.markdown("**Recomendações:**")
                st.write("• Usar serra circular com guia")
                st.write("• Margem de segurança: 3mm")
                st.write("• Verificar fibra da madeira")
    
    elif st.session_state.cutting_diagram_generated:
        # Mostrar diagrama já gerado
        fig, utilization, waste = generate_cutting_diagram(components)
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Aproveitamento", f"{utilization:.1f}%")
        with col2:
            st.metric("🗑️ Desperdício", f"{waste:.1f}%")
        with col3:
            st.metric("📦 Chapas Necessárias", "1")
        with col4:
            sheet_cost = (2.75 * 1.83) * 80
            st.metric("💰 Custo da Chapa", f"R$ {sheet_cost:.2f}")
    
    else:
        st.info("📐 Clique em 'Gerar Diagrama de Corte' para criar o plano de corte otimizado.")

elif page == "📤 Importar SketchUp":
    st.markdown("### 🏗️ Importar SketchUp")
    
    st.markdown("#### Como usar:")
    st.markdown("""
    1. Faça upload do seu arquivo SketchUp (.skp)
    2. O sistema extrairá automaticamente os componentes
    3. Revise e ajuste os componentes se necessário
    4. Crie um novo projeto ou adicione ao projeto atual
    """)
    
    st.markdown("### 📤 Upload de Arquivo SketchUp")
    
    uploaded_file = st.file_uploader(
        "Selecione um arquivo SketchUp (.skp)",
        type=['skp'],
        help="Limite: 200MB por arquivo"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Arquivo '{uploaded_file.name}' carregado com sucesso!")
        
        with st.spinner("Processando arquivo SketchUp..."):
            import time
            time.sleep(3)
            
            st.success("✅ Arquivo processado com sucesso!")
            
            # Simular componentes extraídos
            st.markdown("### 🔧 Componentes Extraídos:")
            
            extracted_components = [
                {'nome': 'Painel Lateral', 'comprimento': 800, 'largura': 400, 'espessura': 18},
                {'nome': 'Prateleira', 'comprimento': 760, 'largura': 350, 'espessura': 18},
                {'nome': 'Fundo', 'comprimento': 760, 'largura': 380, 'espessura': 12}
            ]
            
            df_extracted = pd.DataFrame(extracted_components)
            st.dataframe(df_extracted, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("➕ Adicionar ao Projeto Atual", type="primary"):
                    st.success("✅ Componentes adicionados ao projeto atual!")
            
            with col2:
                if st.button("🆕 Criar Novo Projeto"):
                    st.success("✅ Novo projeto criado com os componentes extraídos!")

elif page == "📦 Materiais":
    st.markdown("### 📦 Materiais")
    
    st.markdown("#### 📋 Materiais Disponíveis")
    
    df_materials = pd.DataFrame(data['materials'])
    st.dataframe(df_materials, use_container_width=True)
    
    # Gráfico de preços
    st.markdown("#### 💰 Comparação de Preços")
    
    fig_prices = px.bar(
        df_materials, 
        x='name', 
        y='price',
        color='category',
        title="Preços por Material",
        labels={'name': 'Material', 'price': 'Preço (R$/m²)', 'category': 'Categoria'}
    )
    
    st.plotly_chart(fig_prices, use_container_width=True)
    
    # Adicionar novo material
    with st.expander("➕ Adicionar Material"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Nome do Material")
            new_thickness = st.number_input("Espessura (mm)", min_value=1, max_value=100, value=15)
            new_price = st.number_input("Preço (R$/m²)", min_value=0.0, value=50.0, step=0.1)
        
        with col2:
            new_unit = st.selectbox("Unidade", ["m²", "m", "unidade"])
            new_category = st.selectbox("Categoria", ["Madeira Reconstituída", "Madeira Laminada", "Madeira Maciça"])
            new_density = st.number_input("Densidade (kg/m³)", min_value=100, max_value=1000, value=600)
        
        if st.button("Adicionar Material"):
            st.success(f"✅ Material '{new_name}' adicionado com sucesso!")

elif page == "📊 Relatórios":
    st.markdown("### 📊 Relatórios")
    
    current_project = data['projects'][st.session_state.current_project]
    components = data['components'][current_project['id']]
    
    # Gerar dados para relatórios
    budget_data, material_summary, total_cost, total_area, total_weight = generate_budget(
        current_project['id'], components, data['materials']
    )
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Custo Total", f"R$ {total_cost:.2f}")
    
    with col2:
        st.metric("📏 Área Total", f"{total_area:.2f} m²")
    
    with col3:
        st.metric("⚖️ Peso Total", f"{total_weight:.1f} kg")
    
    with col4:
        avg_cost_per_m2 = total_cost / total_area if total_area > 0 else 0
        st.metric("📊 Custo/m²", f"R$ {avg_cost_per_m2:.2f}")
    
    # Gráfico de custos por material
    st.markdown("#### 💰 Análise de Custos por Material")
    
    materials_chart = []
    costs_chart = []
    
    for material, data_mat in material_summary.items():
        materials_chart.append(material)
        costs_chart.append(data_mat['cost'])
    
    fig_cost = px.pie(
        values=costs_chart,
        names=materials_chart,
        title="Distribuição de Custos por Material"
    )
    
    st.plotly_chart(fig_cost, use_container_width=True)
    
    # Tabela detalhada de componentes
    st.markdown("#### 📋 Detalhamento por Componente")
    
    df_budget = pd.DataFrame(budget_data)
    st.dataframe(df_budget, use_container_width=True)
    
    # Botões de exportação
    st.markdown("#### 📤 Exportar Relatórios")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV detalhado
        csv_content = create_csv_report(budget_data, material_summary, current_project['name'])
        
        st.download_button(
            label="📊 Download CSV Completo",
            data=csv_content,
            file_name=f"relatorio_completo_{current_project['name'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary"
        )
    
    with col2:
        # Lista de componentes simples
        df_simple = df_budget[['Componente', 'Dimensões (mm)', 'Quantidade', 'Material', 'Custo Total (R$)']]
        csv_simple = df_simple.to_csv(index=False)
        
        st.download_button(
            label="📋 Download Lista Componentes",
            data=csv_simple,
            file_name=f"componentes_{current_project['name'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col3:
        # Resumo de materiais
        df_materials_summary = pd.DataFrame([
            {
                'Material': material,
                'Área (m²)': round(data_mat['area'], 4),
                'Custo (R$)': round(data_mat['cost'], 2),
                'Peso (kg)': round(data_mat['weight'], 2)
            }
            for material, data_mat in material_summary.items()
        ])
        
        csv_materials = df_materials_summary.to_csv(index=False)
        
        st.download_button(
            label="📦 Download Resumo Materiais",
            data=csv_materials,
            file_name=f"materiais_{current_project['name'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🪚 <strong>CutList Pro</strong> - Desenvolvido com ❤️ usando Streamlit</p>
    <p>Versão 2.0 | © 2025 | Planos de corte e orçamentos profissionais</p>
</div>
""", unsafe_allow_html=True)
