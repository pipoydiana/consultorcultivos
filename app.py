import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Consulta Agrícola",
    page_icon="🌱",
    layout="wide"
)

def main():
    st.title("🌱 Sistema de Consulta Agrícola (2019-2024)")
    st.markdown("""
    Esta aplicación permite analizar la evolución de los cultivos por departamento.
    Sube tu archivo Excel para comenzar el análisis.
    """)

    # --- CARGA DE ARCHIVO ---
    st.sidebar.header("Configuración de Datos")
    uploaded_file = st.sidebar.file_uploader("Cargar archivo Excel (.xlsx)", type=["xlsx"])

    if uploaded_file is not None:
        try:
            # Cargar datos
            df = pd.read_excel(uploaded_file)
            
            # Limpieza de nombres de columnas
            df.columns = df.columns.str.strip()
            
            # Verificar columnas necesarias
            required_cols = ['Departamento', 'Cultivo', 'Año', 'Área sembrada (ha)', 
                             'Área cosechada (ha)', 'Producción (t)', 'Rendimiento (t/ha)']
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                st.error(f"El archivo no contiene las columnas necesarias: {', '.join(missing_cols)}")
                return

            # --- FILTROS ---
            st.sidebar.subheader("Filtros de Búsqueda")
            
            # Selector de Departamento
            departamentos = sorted(df['Departamento'].unique())
            dept_seleccionado = st.sidebar.selectbox("Seleccione el Departamento", departamentos)
            
            # Filtrar por departamento para el siguiente selector
            df_dept = df[df['Departamento'] == dept_seleccionado]
            
            # Selector de Cultivo
            cultivos = sorted(df_dept['Cultivo'].unique())
            cult_seleccionado = st.sidebar.selectbox(f"Seleccione el Cultivo en {dept_seleccionado}", cultivos)
            
            # Filtrar datos finales
            resultado = df_dept[df_dept['Cultivo'] == cult_seleccionado]

            # --- VISUALIZACIÓN ---
            if not resultado.empty:
                st.header(f"Resumen: {cult_seleccionado} en {dept_seleccionado}")
                
                # Agrupación por año
                resumen_anual = resultado.groupby('Año').agg({
                    'Área sembrada (ha)': 'sum',
                    'Área cosechada (ha)': 'sum',
                    'Producción (t)': 'sum',
                    'Rendimiento (t/ha)': 'mean'
                }).reset_index()

                # Métricas Principales (Totales Históricos)
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_prod = resultado['Producción (t)'].sum()
                    st.metric("Producción Total (t)", f"{total_prod:,.2f}")
                with col2:
                    rend_max = resultado['Rendimiento (t/ha)'].max()
                    st.metric("Rendimiento Máximo (t/ha)", f"{rend_max:,.2f}")
                with col3:
                    area_total = resultado['Área sembrada (ha)'].sum()
                    st.metric("Total Área Sembrada (ha)", f"{area_total:,.2f}")

                # Gráficos
                tab1, tab2, tab3 = st.tabs(["📊 Producción y Área", "📈 Rendimiento", "📄 Datos Detallados"])
                
                with tab1:
                    fig_prod = px.bar(resumen_anual, x='Año', y='Producción (t)', 
                                     title=f"Evolución de la Producción de {cult_seleccionado}",
                                     labels={'Producción (t)': 'Toneladas'},
                                     color_discrete_sequence=['#2ecc71'])
                    st.plotly_chart(fig_prod, use_container_width=True)
                    
                    fig_area = px.line(resumen_anual, x='Año', y=['Área sembrada (ha)', 'Área cosechada (ha)'],
                                      title="Comparativa de Áreas",
                                      markers=True)
                    st.plotly_chart(fig_area, use_container_width=True)

                with tab2:
                    fig_rend = px.area(resumen_anual, x='Año', y='Rendimiento (t/ha)',
                                      title="Rendimiento Promedio por Año",
                                      color_discrete_sequence=['#f1c40f'])
                    st.plotly_chart(fig_rend, use_container_width=True)

                with tab3:
                    st.subheader("Tabla de datos anuales")
                    st.dataframe(resumen_anual.style.format({
                        'Área sembrada (ha)': '{:,.2f}',
                        'Área cosechada (ha)': '{:,.2f}',
                        'Producción (t)': '{:,.2f}',
                        'Rendimiento (t/ha)': '{:,.2f}'
                    }), use_container_width=True)
            else:
                st.warning("No se encontraron registros para los criterios seleccionados.")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    else:
        # Estado inicial cuando no hay archivo
        st.info("👋 Por favor, carga el archivo Excel en el panel de la izquierda para comenzar.")
        
        # Opcional: Mostrar una previsualización de cómo debe ser el Excel
        with st.expander("Ver formato de archivo requerido"):
            st.write("El archivo debe contener al menos las siguientes columnas:")
            st.markdown("- Departamento\n- Cultivo\n- Año\n- Área sembrada (ha)\n- Área cosechada (ha)\n- Producción (t)\n- Rendimiento (t/ha)")

if __name__ == "__main__":
    main()