import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns


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
    

show_table = st.sidebar.checkbox("Afficher la répartition des Marque par Allée", True, key = "CB4")

if show_table:

    def valeur_cellule(data, zonsts, allsts, dplsts, nivsts):
        filtres = (
            (data['ZONSTS'] == zonsts) &
            (data['ALLSTS'] == allsts) &
            (data['DPLSTS'] == dplsts) &  
            (data['NIVSTS'] == nivsts)
        )

        ligne = data[filtres]
        if ligne.empty:
            return "N/C"

        ligne = ligne.iloc[0]

        if ligne["Classement Marque A-Z"] in ["NAN"]:
            return ligne["CODBLO"]
        elif ligne["TYPE"] == "Réserve":
            return ligne["AXE_PRODUIT"]
        else:
            return ligne["Classement Marque A-Z"]

    st.title("📊 Affichage des Marques par allées (vue implantation par allée)")
    
    zonsts_input = st.session_state.get("zoneMarque", "")
    allsts_input = st.session_state.get("allMarque", "")
    filtre_parite = st.session_state.get("CB5", "")

    zonsts_input = st.selectbox("Choisir une Zone :", (data['ZONSTS'].unique()), key = 'zoneMarque')
    allsts_input = st.selectbox("Choisir une Allée :", (data['ALLSTS'].unique()), key = 'allMarque')

    sous_df = data[(data['ZONSTS'] == zonsts_input) & (data['ALLSTS'] == allsts_input)]
    dplsts_all = sorted(pd.to_numeric(sous_df['DPLSTS'], errors='coerce').dropna().astype(int).unique()) 
    nivsts_list = list(range(6))  

    filtre_parite = st.radio("Afficher les Déplacements :", options=["Tous", "Pairs seulement", "Impairs seulement"], key = "CB5")

    if filtre_parite == "Pairs seulement":
        dplsts_list = [d for d in dplsts_all if d % 2 == 0]
    elif filtre_parite == "Impairs seulement":
        dplsts_list = [d for d in dplsts_all if d % 2 == 1]
    else:
        dplsts_list = dplsts_all


    grille = pd.DataFrame(index=dplsts_list, columns=nivsts_list)

    for dpl in dplsts_list:
        for niv in nivsts_list:
            grille.at[dpl, niv] = valeur_cellule(data, zonsts_input, allsts_input, dpl, niv)

    grille = grille.T.sort_index(ascending=False)  
    lettres = list("1ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    palette = sns.color_palette("hls", len(lettres)).as_hex()
    couleur_par_lettre = {lettres[i]: palette[i] for i in range(len(lettres))}

    def couleur(val):
        if val == "N/C":
            return "color: #888"
        elif val == 'DYN':
            return "background-color: #3498DB; color: white"
        elif val == "NEX":
            return "color : #FF69B4"
        elif val == 'FP':
            return "background-color: #FF69B4; color: white"
        elif val == 'OCC':
            return "background-color: #FF6F61; color: white"
        elif isinstance(val, str) and val[0].upper() in couleur_par_lettre:
            color = couleur_par_lettre[val[0].upper()]
            return f"background-color: {color}; color: black"
        else:
            return ""
    
    
    lettre_order = ['1','A','B','C',
                    'D','E','F','G',
                    'H','I','J','K',
                    'L','M','N','O',
                    'P','Q','R','S',
                    'T','U','V','W',
                    'X','Y','Z','NEX',
                    'DYN','FP','OCC','PAS'] 
    
    valeurs = grille.values.flatten()
    valeurs_utiles = [v.strip() for v in valeurs if isinstance(v, str) and v != "N/C"]

    
    df_histo = pd.DataFrame(valeurs_utiles, columns=["Lettres"])
    df_histo['Lettre'] = pd.Categorical(df_histo['Lettres'], categories=lettre_order, ordered = True)
    df_histo = df_histo[df_histo['Lettre'].notna()]
    


    valeurs_uniques = sorted(set(df_histo["Lettres"]))
    couleur_par_valeur = {}

    for val in valeurs_uniques:
        if val == "DYN":
            couleur_par_valeur[val] = "#3498DB"
        elif val == "NEX":
            couleur_par_valeur[val] = "#FF69B4"
        elif val == "FP":
            couleur_par_valeur[val] = "#FF69B4"
        elif val == "OCC":
            couleur_par_valeur[val] = "#FF6F61"
        elif val[0].upper() in couleur_par_lettre:
            couleur_par_valeur[val] = couleur_par_lettre[val[0].upper()]
        else:
            couleur_par_valeur[val] = "#CCCCCC"  


    fig = px.histogram(
    df_histo,
    x="Lettres",
    color="Lettre",
    color_discrete_map=couleur_par_valeur,
    text_auto = True,
    title=(f"📊 Fréquence des Lettres dans l'Allée {allsts_input}"),
    category_orders={"Lettres": lettre_order}
    )

    

    styled_grille = grille.style.applymap(couleur)

    st.markdown(f"### Répartition des marques pour la Zone `{zonsts_input}` | Allée `{allsts_input}` | {filtre_parite}")
    st.write(styled_grille)
    st.plotly_chart(fig)


else:
    st.info("✅ Grille masquée. Cochez la case dans la sidebar pour l'afficher.")


