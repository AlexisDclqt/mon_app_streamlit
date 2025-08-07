import streamlit as st
import pandas as pd
import seaborn as sns




DATA = r"C:\Users\adecloquement\Desktop\VAE\Certif et revision\Projet_ST\imp\imp.xlsx"


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



show_table1 = st.sidebar.checkbox("Afficher la répartition des Classe de Rotation", True)

if show_table1:

    def Rot_ABC(data, zonsts1, allsts1, dplsts1, nivsts1):
        filtres_ABC = (
            (data['ZONSTS'] == zonsts1) &
            (data['ALLSTS'] == allsts1) &
            (data['DPLSTS'] == dplsts1) &  
            (data['NIVSTS'] == nivsts1)
        )

        abc = data[filtres_ABC]
        if abc.empty:
            return "N/C"

        abc = abc.iloc[0]

        if abc["ABC_ROT"] in ['NAN']:
            return abc["CODBLO"]
        else:
            return abc['ABC_ROT']
        

    st.title("📊 Affichage des Classe de rotation par allées")
    
    zonsts_input1 = st.session_state.get("zoneABC","")
    allsts_input1 = st.session_state.get("allABC","")
    filtre_parite1 = st.session_state.get("filtre_abc","")

    zonsts_input1 = st.selectbox("Choisir Zone (ABC):", sorted(data['ZONSTS'].unique()), key = 'zoneABC')
    allsts_input1 = st.selectbox("Choisir une Allée (ABC):", sorted(data['ALLSTS'].unique()), key = 'allABC')

    sous_df1 = data[(data['ZONSTS'] == zonsts_input1) & (data['ALLSTS'] == allsts_input1)]
    dplsts_all1 = sorted(pd.to_numeric(sous_df1['DPLSTS'], errors='coerce').dropna().astype(int).unique()) 
    nivsts_list1 = list(range(6))  

    filtre_parite1 = st.radio("Afficher les Déplacements :", options=["Tous", "Pairs seulement", "Impairs seulement"], key = 'filtre_abc')

    if filtre_parite1 == "Pairs seulement":
        dplsts_list1 = [x for x in dplsts_all1 if x % 2 == 0]
    elif filtre_parite1 == "Impairs seulement":
        dplsts_list1 = [x for x in dplsts_all1 if x % 2 == 1]
    else:
        dplsts_list1 = dplsts_all1


    grille1 = pd.DataFrame(index=dplsts_list1, columns=nivsts_list1)

    for dpl1 in dplsts_list1:
        for niv1 in nivsts_list1:
            grille1.at[dpl1, niv1] = Rot_ABC(data, zonsts_input1, allsts_input1, dpl1, niv1)

    grille1 = grille1.T.sort_index(ascending=False)  
    lettres1 = list("ABCDR")
    palette1 = sns.color_palette("hls", len(lettres1)).as_hex()
    couleur_par_lettre1 = {lettres1[i]: palette1[i] for i in range(len(lettres1))}

    def couleur1(val1):
        if val1 == "N/C":
            return "color: #888"
        elif val1 == 'DYN':
            return "background-color: #3498DB; color: white"
        elif val1 == "NEX":
            return "color : #FF69B4"
        elif val1 == 'FP':
            return "background-color: #FF69B4; color: white"
        elif val1 == 'OCC':
            return "background-color: #FF6F61; color: white"
        elif isinstance(val1, str) and val1[0].upper() in couleur_par_lettre1:
            color = couleur_par_lettre1[val1[0].upper()]
            return f"background-color: {color}; color: black"
        else:
            return ""


    

    styled_grille1 = grille1.style.applymap(couleur1)

    st.markdown(f"### Répartition des Classe de rotation pour la Zone `{zonsts_input1}` | Allée `{allsts_input1}` | {filtre_parite1}")
    st.write(styled_grille1)
    


else:
    st.info("✅ Grille masquée. Cochez la case dans la sidebar pour l'afficher.")



#  graph pour les axes dans la répartition par marque si réserrve
