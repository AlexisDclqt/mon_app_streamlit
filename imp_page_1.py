import streamlit as st
import pandas as pd
from difflib import get_close_matches



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
    
    
    
st.title("📦 🤖 Suggestion d’implantation intelligente. ​​⏬ ")
st.info("""Entrer la première lettre de la marque puis choisir l'axe du produit à implanter.
            \n- Proposition de FP dans l'allée où la première lettre de la marque est la plus présente.
            \n- Si pas de place dans l'allée de référence, alors 3 allées de subsitution sont proposées
            \n- ....""")
            
lettre_marque = st.session_state.get("LM", "").strip().upper()
axe_choisi = st.session_state.get("axe_imp", "")

lettre_marque = st.text_input("Première lettre de la marque :", max_chars=1,key = "LM").strip().upper()
axe_choisi = st.selectbox("Choisir l'AXE PRODUIT", options=sorted(data['AXE_PRODUIT'].dropna().unique()), key = "axe_imp")



data_r = data[(~data['TYPE'].isin(['Réserve']) & (~data['AXE_PRODUIT'].isin(['NAN'])))]


if lettre_marque and axe_choisi:
    data_axe = data_r[(data_r['AXE_PRODUIT'] == axe_choisi)]
    

    allées_par_lettre = (
        data_axe[data_axe['Classement Marque A-Z'].str.startswith(lettre_marque)]
        .groupby('ALLSTS')
        .size()
        .reset_index(name='nb_articles')
        .sort_values(by='nb_articles', ascending=False)
    )
    

    if allées_par_lettre.empty:
        st.error(f"❌ Aucune allée contenant des marques '{lettre_marque}' dans l'axe {axe_choisi}")
    else:
        allée_ref = allées_par_lettre.iloc[0]['ALLSTS']
        st.info(f"🏷️ Allée référence : `{allée_ref}` (max marques '{lettre_marque}')")

        fp_in_ref = data_r[
            (data_r['ALLSTS'] == allée_ref) &
            (data_r['AXE_PRODUIT'] == axe_choisi) &
            (data_r['CODBLO'] == 'FP')  
            
        ].sort_values(by = 'ALLSTS',ascending=True)

        if not fp_in_ref.empty:
            st.success(f"✅ FP trouvé dans allée `{allée_ref}`")
            st.dataframe(fp_in_ref, use_container_width=True)
        else:
            st.warning("🔁 Pas de FP dans cette allée. Recherche d’alternative...")

            allées_fp_dispo = data_r[
                (data_r['CODBLO'] == 'FP') & (data_r['AXE_PRODUIT'] == axe_choisi)
            ]['ALLSTS'].dropna().astype(str).unique()

            proches = get_close_matches(str(allée_ref), sorted(allées_fp_dispo), n=3)

            if proches:
                for allee_proche in proches:
                    st.markdown(f"### 🔁 Substitution : Allée `{allee_proche}`")
                    suggestion = data_r[
                        (data_r['ALLSTS'] == allee_proche) &
                        (data_r['CODBLO'] == 'FP') &
                        (data_r['AXE_PRODUIT'] == axe_choisi)
                         
                    ]
                    st.dataframe(suggestion, use_container_width=True)
            else:
                fallback_fp = data_r[
                    (data_r['CODBLO'] == 'FP') &
                    (data_r['AXE_PRODUIT'] == axe_choisi)
                ]
                if not fallback_fp.empty:
                    st.success(f"✅ Emplacements FP disponibles dans l'axe {axe_choisi}")
                    st.dataframe(fallback_fp, use_container_width=True, height=400)
                else:
                    st.error(f"🚫 Aucun emplacement FP disponible dans l'axe '{axe_choisi}'")
                    
st.markdown("----------------------------------------------------------------------------------------------------------")



nb_emp_fp = df_FP["Nombre d'emplacements FP"].sum()

st.sidebar.metric(label="Nombre d'emplacements FP dans le dépot :", value= f'{nb_emp_fp}', border = True)






