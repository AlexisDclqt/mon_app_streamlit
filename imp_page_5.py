import streamlit as st
import pandas as pd
import plotly.express as px


DATA = "imp.xlsx"


@st.cache_data(persist=True)


def load_data():
    data = pd.read_excel(DATA, dtype={'CODPRO': str})
    

    data['AXE_PRODUIT'] = data['AXE_PRODUIT'].astype(str).str.strip().str.upper()
    data['CODBLO'] = data['CODBLO'].astype(str).str.strip().str.upper()
    data['ALLSTS'] = data['ALLSTS'].astype(str).str.strip()
    data['DPLSTS'] = pd.to_numeric(data['DPLSTS'], errors='coerce').astype('Int64')
    data['NIVSTS'] = pd.to_numeric(data['NIVSTS'], errors='coerce').astype('Int64')
    data['Classement Marque A-Z'] = data['Classement Marque A-Z'].astype(str).str.strip().str.upper()
    data[['ABC_ROT','TYPE']] =  data[['ABC_ROT','TYPE']].replace(' ','NAN')
    data['ABC_ROT'] = data['ABC_ROT'].astype(str).str.upper()
    data['UVC_STOCK'] = pd.to_numeric(data['UVC_STOCK'], errors = 'coerce').astype('Int64')
    data['UVC_ENCOURS'] = pd.to_numeric(data['UVC_ENCOURS'], errors = 'coerce').astype('Int64')
    data['UVC_RESTANT'] = pd.to_numeric(data['UVC_RESTANT'], errors = 'coerce').astype('Int64')

    return data

data = load_data()


df_with_reserve = data[(data['TYPE'] == 'Réserve') & (data['CODPRO'] != "") & data['CODBLO'].isin(['NAN']) & (data["AXE_PRODUIT"] != "")]

df_without_reserve = data[(data['TYPE'] != 'Réserve') & (data['CODPRO'] != "") & data['CODBLO'].isin(['NAN']) & (data["AXE_PRODUIT"] != "")]

df_codblo = data.groupby(['ZONSTS', 'ALLSTS', 'CODBLO','AXE_PRODUIT']).size().reset_index(name="Nombre d'emplacements").sort_values(by="Nombre d'emplacements", ascending=False)


# df_axe = df_without_reserve.groupby('AXE_PRODUIT')['CODPRO'].size().reset_index(name="Nombre d'emplacements").sort_values(by="Nombre d'emplacements", ascending=False)
df_axe = df_without_reserve.groupby('AXE_PRODUIT')['CODPRO'].size().reset_index(name="Nombre d'emplacements").sort_values(by="Nombre d'emplacements", ascending=False)
  
    
df_axe_r = df_with_reserve.groupby('AXE_PRODUIT')['CODPRO'].size().reset_index(name="Nombre d'emplacements Réserves").sort_values(by="Nombre d'emplacements Réserves", ascending=False)
# df_axe_r = df_with_reserve.groupby('AXE_PRODUIT').size().reset_index(name="Nombre d'emplacements").sort_values(by="Nombre d'emplacements", ascending=False)
df_FP = data[(data['CODBLO'] == 'FP') & (data['TYPE'] != 'Réserve')]

df_FP = df_FP.groupby(['ALLSTS']).size().reset_index(name = "Nombre d'emplacements FP").sort_values(by = "ALLSTS", ascending = False)

df_abc = data.copy()

df_abc = df_abc[(df_abc['TYPE'] != "Réserve") & (df_abc['CODPRO'] != "") & (df_abc['ABC_ROT'] != "NAN")]

df_abc = df_abc[['CODPRO','ABC_ROT','AXE_PRODUIT']]

# df_abc.dropna(subset = ['CODPRO'], axis = 0, inplace = True)

# df_abc = df_abc[df_abc['ABC_ROT'] != "NAN"]

df_abc = df_abc.groupby(['AXE_PRODUIT','ABC_ROT'])['CODPRO'].nunique().reset_index(name = "Nombre d'article")




if st.sidebar.button("♻️ Recharger les données"):
    st.cache_data.clear()


st.sidebar.subheader("📊 Graphiques")

if st.sidebar.checkbox("Voir Répartition emp par AXE", True):
    vis_type = st.sidebar.selectbox('Type de visualisation', ['Histogramme des AXE', 'Diagramme Circulaire des AXE'], key='axe_vis')
    st.markdown("### 📦 Répartition des emplacements par Axe ​​⏬ ")
    st.info(f"📦 Total d'emplacements Picking : {df_axe["Nombre d\'emplacements"].sum()}")
    fig = px.bar(df_axe, x='AXE_PRODUIT', y="Nombre d'emplacements", color='AXE_PRODUIT', height=500, text = "Nombre d'emplacements") if vis_type == 'Histogramme des AXE' else px.pie(df_axe, values="Nombre d'emplacements", names='AXE_PRODUIT')
    st.plotly_chart(fig)
    st.markdown("----------------------------------------------------------------------------------------------------------")



if st.sidebar.checkbox("Voir Répartition réserve par AXE", True):
    vis_type_r = st.sidebar.selectbox('Type de visualisation (Réserves)', ['Histogramme des Réserves', 'Diagramme Circulaire des Réserves'], key='res_vis')
    st.markdown("### 🗃️ Répartition des Réserves par Axe ​​⏬ ")
    st.info(f"📦 Total d'emplacements Réserves : {df_axe_r["Nombre d\'emplacements Réserves"].sum()}")
    fig_r = px.bar(df_axe_r, x='AXE_PRODUIT', y="Nombre d'emplacements Réserves", color='AXE_PRODUIT', height=500, text = "Nombre d'emplacements Réserves") if vis_type_r == 'Histogramme des Réserves' else px.pie(df_axe_r, values="Nombre d'emplacements Réserves", names='AXE_PRODUIT')
    st.plotly_chart(fig_r)
    st.markdown("----------------------------------------------------------------------------------------------------------")
    

if st.sidebar.checkbox("Voir la répartition des classse ABC par AXE", True):
    st.markdown("### Répartition des ABC ​​⏬")
    st.info(f"📦 Total d'articles au picking dans le dépôt : {df_abc["Nombre d\'article"].sum()}")
    fig_abc = px.bar(df_abc, x = 'ABC_ROT', y = "Nombre d'article", color = 'AXE_PRODUIT',text_auto = True, height = 500,width = 1600, facet_col = "AXE_PRODUIT")#pattern_shape= "AXE_PRODUIT", pattern_shape_sequence = [".","x","+","-"])
    st.plotly_chart(fig_abc)
    

uvc = data[data['TYPE'] !='Réserve']
uvc = data['UVC_STOCK'].sum()
nb = df_abc["Nombre d'article"].sum()
st.sidebar.metric(label="Nombre codpro", value= f'{nb} articles', border = True)
st.sidebar.metric(label="Nombre d'UVC au PICKING", value= f'{uvc} UVC', border = True)
    









