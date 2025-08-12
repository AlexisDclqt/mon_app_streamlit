import streamlit as st

# Lancement dans le shell : cd "Desktop\VAE\Certif et revision\Projet_ST\imp"
#                           streamlit run imp_v5.py


# conn = pyodbc.connect("Driver={SQL Server};Server=TON_SERVEUR;Database=TA_BDD;Trusted_Connection=yes;")
# query =
# SELECT * FROM Table

# df = pd.read_sql(query, conn)

def check_password():
    def password_entered():
        if st.session_state["password"] == "deret2025!":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Mot de passe", type="password", on_change=password_entered, key="password")
        return False

    elif not st.session_state["password_correct"]:
        st.text_input("Mot de passe", type="password", on_change=password_entered, key="password")
        st.error("Mot de passe incorrect")
        return False
    else:
        return True
        
if check_password():
    st.set_page_config(layout="wide")

    page_1 = st.Page("imp_page_1.py", title= "1. 🤖Implantation Intelligente")
    page_2 = st.Page("imp_page_2.py", title= "2. 📦📂Gestion des Produits")
    page_3 = st.Page("imp_page_3.py", title= "3. 📊 Répartiton des Marques")
    page_4 = st.Page("imp_page_4.py", title= "4. 📊 Répartition des Classe de Rotations")
    page_5 = st.Page("imp_page_5.py", title= "5. 📊 Graphiques Divers")
    page_6 = st.Page("imp_page_6.py", title= "6. Gestion des Encours")


    pg = st.navigation([page_1, page_2, page_3, page_4, page_5,page_6])

    def preserve_session_keys(*keys):
        for key in keys:
            if key in st.session_state:
                st.session_state[key] = st.session_state[key]

    preserve_session_keys("LM","axe_imp","axes_res","code_res","zone_res","allee_res","axes_sdv","code_sdv","zone_sdv","allee_sdv",
                      "marque_sdv","codblo","zone_sdv1","allee_sdv1","zoneMarque",
                      "allMarque","zoneABC","allABC","filtre_abc","CB1","CB2","CB3","CB4","CB5","axes_prep")


    pg.run()









