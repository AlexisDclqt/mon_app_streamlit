import streamlit as st
import pandas as pd


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

    return data

data = load_data()


df_with_reserve = data[(data['TYPE'] == 'Réserve') & (data['CODPRO'])]
df_without_reserve = data[(data['TYPE'] != 'Réserve') & (data['CODPRO'])]

df_codblo = data.groupby(['ZONSTS', 'ALLSTS', 'CODBLO','AXE_PRODUIT']).size().reset_index(name="Nombre d'emplacements").sort_values(by="Nombre d'emplacements", ascending=False)
df_axe = data.groupby('AXE_PRODUIT').size().reset_index(name="Nombre d'emplacements").sort_values(by="Nombre d'emplacements", ascending=False)
df_axe_r = df_with_reserve.groupby('AXE_PRODUIT').size().reset_index(name="Nombre d'emplacements").sort_values(by="Nombre d'emplacements", ascending=False)
df_FP = data[(data['CODBLO'] == 'FP') & (data['TYPE'] != 'Réserve')]
df_FP = df_FP.groupby(['ALLSTS']).size().reset_index(name = "Nombre d'emplacements FP").sort_values(by = "ALLSTS", ascending = False)


if st.sidebar.button("♻️ Recharger les données"):
    st.cache_data.clear()
    

st.title("🗂️ Gestion des Produits")
st.info("Veuillez cocher ou décocher une case suivant le besoin.")

if st.sidebar.checkbox('📁 Gestion des Réserves', True, key = 'CB1'):
    st.subheader('📁 Gestion des Réserves ​​⏬')
    
    df_filtered = df_with_reserve.copy()
    #df_filtered = df_filtered.set_index(df_filtered.columns[0])
    
    axes_selectionnes = st.session_state.get("axes_res", "")
    code_shop = st.session_state.get("code_res", "")
    zone = st.session_state.get("zone_res", "")
    allee = st.session_state.get("allee_res", "")
    
    axes_selectionnes = st.multiselect("Choisir un ou plusieurs axes", options=df_filtered['AXE_PRODUIT'].unique(), key='axes_res')
    code_shop = st.text_input("Entrer un CODE SHOP :", key='code_res')
    zone = st.text_input("Entrer une Zone :", key='zone_res')
    allee = st.text_input("Entrer l'allée :", key='allee_res')

    if axes_selectionnes:
        df_filtered = df_filtered[df_filtered['AXE_PRODUIT'].isin(axes_selectionnes)]
    if code_shop:
        df_filtered = df_filtered[df_filtered['CODPRO'].str.contains(code_shop, case=False, na=False)]
    if zone:
        df_filtered = df_filtered[df_filtered['ZONSTS'].astype(str).str.contains(zone, case=False, na=False)]
    if allee:
        df_filtered = df_filtered[df_filtered['ALLSTS'].astype(str).str.contains(allee, case=False, na=False)]
    if df_filtered.empty:
        st.error("❌ CETTE ALLEE N'EST PAS UNE RESERVE")

    st.markdown("### Résultats de la recherche (Réserves)")
    st.dataframe(df_filtered, use_container_width=True, height=600)
    st.markdown("----------------------------------------------------------------------------------------------------------")


# ---------------------- Filtres Produits ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if st.sidebar.checkbox('📂 Gestion des Produits (Hors Réserves)', True, key = 'CB2'):
    st.subheader('📂 Gestion des Produits (Hors Réserves) ​​⏬ ')

    
    df_filtered1 = df_without_reserve.copy()
    #df_filtered1 = df_filtered1.set_index(df_filtered1.columns[0])
    
    axes_selectionnes1 = st.session_state.get("axes_sdv","")
    code_shop1 = st.session_state.get("code_sdv", "")
    zone1 = st.session_state.get("zone_res", "")
    allee1 = st.session_state.get("allee_sdv", "")
    marque = st.session_state.get("marque_sdv", "")
    
    axes_selectionnes1 = st.multiselect("Choisir un ou plusieurs axes", options=df_filtered1['AXE_PRODUIT'].unique(), key='axes_sdv')
    code_shop1 = st.text_input("Entrer un CODE SHOP :", key='code_sdv')
    zone1 = st.text_input("Entrer une Zone :", key='zone_sdv')
    allee1 = st.text_input("Entrer l'allée :", key='allee_sdv')
    marque = st.text_input("Choisir la lettre de marque :", key='marque_sdv')          

    if axes_selectionnes1:
        df_filtered1 = df_filtered1[df_filtered1['AXE_PRODUIT'].isin(axes_selectionnes1)]
    if code_shop1:
        df_filtered1 = df_filtered1[df_filtered1['CODPRO'].str.contains(code_shop1, case=False, na=False)]
    if zone1:
        df_filtered1 = df_filtered1[df_filtered1['ZONSTS'].astype(str).str.contains(zone1, case=False, na=False)]
    if allee1:
        df_filtered1 = df_filtered1[df_filtered1['ALLSTS'].astype(str).str.contains(allee1, case=False, na=False)]
    if marque:
        df_filtered1 = df_filtered1[df_filtered1['Classement Marque A-Z'].astype(str).str.startswith(marque.upper())]
    if df_filtered1.empty:
        st.error("❌ CETTE ALLEE EST UNE RESERVE")    
    

    st.markdown("### Résultats de la recherche (Hors Réserves)")
    st.dataframe(df_filtered1,use_container_width=True,height=600)
    st.markdown("----------------------------------------------------------------------------------------------------------")
    
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


if st.sidebar.checkbox('📂 Gestion des CODBLO', True, key = "CB3"):
    st.subheader('📂 Gestion des CODBLO ​​⏬ ')
    df_filtered4 = data[(data['CODBLO'].isin(['NEX','FP','OCC','PAS','DYN']))] 
    #df_filtered4 = df_filtered4.set_index(df_filtered4.columns[0])
    
    codblo = st.session_state.get("codblo", "")
    zone3 = st.session_state.get("zone_sdv1", "")
    allee3 = st.session_state.get("allee_sdv1", "")
    
    codblo = st.sidebar.multiselect("Choisir un ou plusieurs CODBLO", options=df_filtered4['CODBLO'].unique(), key='codblo')
    zone3 = st.sidebar.text_input("Entrer une Zone :", key='zone_sdv1')
    allee3 = st.sidebar.text_input("Entrer l'allée :", key='allee_sdv1')
    

    if codblo:
        df_filtered4 = df_filtered4[df_filtered4['CODBLO'].isin(codblo)]
    if zone3:
        df_filtered4 = df_filtered4[df_filtered4['ZONSTS'].astype(str).str.contains(zone3, case=False, na=False)]
    if allee3:
        df_filtered4 = df_filtered4[df_filtered4['ALLSTS'].astype(str).str.contains(allee3, case=False, na=False).sort_values(ascending = False)]

    st.markdown("### Résultats de la recherche des CODBLO")
    st.dataframe(df_filtered4, use_container_width=True, height=600)
    st.markdown("----------------------------------------------------------------------------------------------------------")





























