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


df_with_reserve = (data[(data['TYPE'] == 'Réserve') &
                        (data['CODPRO'] != "") &
                        (data['CODBLO'].isin(['NAN'])) &
                        (data["AXE_PRODUIT"] != "")])

df_without_reserve = (data[(data['TYPE'] != 'Réserve') &
                           (data['CODPRO'] != "") &
                           (data['CODBLO'].isin(['NAN'])) &
                           (data["AXE_PRODUIT"] != "")])

df_codblo = (data.groupby(['ZONSTS', 'ALLSTS', 'CODBLO','AXE_PRODUIT']).size()
             .reset_index(name="Nombre d'emplacements")
             .sort_values(by="Nombre d'emplacements", 
                          ascending=False))


df_axe = (df_without_reserve.groupby('AXE_PRODUIT')['CODPRO'].size()
          .reset_index(name="Nombre d'emplacements")
          .sort_values(by="Nombre d'emplacements",
                       ascending=False))

df_axe2 = (df_without_reserve.groupby('AXE_PRODUIT')['UVC_STOCK'].sum()
           .reset_index(name = "Nombre d'UVC par AXE").
           sort_values(by = "Nombre d'UVC par AXE", 
                       ascending = False))

df_axe_mrg = df_axe.merge(df_axe2, on = 'AXE_PRODUIT') 
   
df_axe_r = (df_with_reserve.groupby('AXE_PRODUIT')['CODPRO'].size()
            .reset_index(name="Nombre d'emplacements Réserves")
            .sort_values(by="Nombre d'emplacements Réserves", 
                         ascending=False))

df_axe_r2 = (df_with_reserve.groupby('AXE_PRODUIT')['UVC_STOCK'].sum()
             .reset_index(name = "Nombre d'UVC en Réserves")
             .sort_values(by ="Nombre d'UVC en Réserves", 
                          ascending = False))

df_axe_r2_mrg = df_axe_r.merge(df_axe_r2, on = "AXE_PRODUIT")


df_FP = data[(data['CODBLO'] == 'FP') & (data['TYPE'] != 'Réserve')]
df_FP = df_FP.groupby(['ALLSTS']).size().reset_index(name = "Nombre d'emplacements FP").sort_values(by = "ALLSTS", ascending = False)

df_abc = data.copy()
df_abc = df_abc[(df_abc['TYPE'] != "Réserve") & (df_abc['CODPRO'] != "") & (df_abc['ABC_ROT'] != "NAN")]
df_abc = df_abc[['CODPRO','ABC_ROT','AXE_PRODUIT']]
df_abc = df_abc.groupby(['AXE_PRODUIT','ABC_ROT'])['CODPRO'].nunique().reset_index(name = "Nombre d'article")


df_prep = data[['CODPRO',"ANAPRO","Désignation",'AXE_PRODUIT','ZONSTS','ALLSTS','DPLSTS','NIVSTS','UVC_STOCK','UVC_ENCOURS','UVC_RESTANT']]
df_prep = df_prep[df_prep['AXE_PRODUIT'] != ""]
df_prep = df_prep[df_prep['UVC_ENCOURS'] !=0].sort_values(by = 'UVC_ENCOURS',ascending = False)

top_enc_uvc = (df_prep.groupby('AXE_PRODUIT')['UVC_ENCOURS'].sum()
               .reset_index(name = "Nombre d'UVC en Encours")
               .sort_values(by = "Nombre d'UVC en Encours", 
                            ascending = False))

top_enc_code = (df_prep.groupby('AXE_PRODUIT')['CODPRO'].size()
                .reset_index(name = "Nombre de Code en Encours")
                .sort_values(by = "Nombre de Code en Encours", 
                             ascending = False))

top_mrg = top_enc_code.merge(top_enc_uvc, on = 'AXE_PRODUIT')

nb_code = (data[(data['CODPRO'] != " ") &
           (data['TYPE'] != 'Réserve')])

nb_code = nb_code['CODPRO'].nunique()

uvc = data[data['TYPE'] !='Réserve']
uvc = uvc['UVC_STOCK'].sum()
uvc_en = data[data['TYPE'] !='Réserve']
uvc_en = uvc_en['UVC_ENCOURS'].sum()
percent_uvc = ((uvc_en/uvc)*100).round(2)



if st.sidebar.button("♻️ Recharger les données"):
    st.cache_data.clear()

st.sidebar.metric(label = "Pourcentage D'UVC en Encours", value = f'{percent_uvc:,}%', border = True)

fig_enc = px.pie(top_mrg, values= "Nombre d'UVC en Encours", names = 'AXE_PRODUIT', hover_data= "Nombre de Code en Encours")

st.sidebar.plotly_chart(fig_enc)


st.sidebar.metric(label="Nombre codpro", value= f'{nb_code:,} articles', width = "content",border = True)
st.sidebar.metric(label="Nombre d'UVC au PICKING", value= f'{uvc:,} UVC', border = True)
st.sidebar.metric(label="Nombre d'UVC en ENCOURS", value= f'{uvc_en:,} UVC', border = True)



st.title("Encours de préparation prévus :")

axes_selectionnes3 = st.session_state.get("axes_prep",[])
code_prep = st.session_state.get("code_prep",[])
nb_enc = st.session_state.get("nb_uvc","")
choix_marque = st.session_state.get("anapro", [])

axes_selectionnes3 = st.multiselect("Choisir un ou plusieurs axes de préparation", 
                                    options=df_prep['AXE_PRODUIT'].unique(), 
                                    key='axes_prep')

code_prep = st.text_input("Renseigner un Code Shop: ", 
                          key = "code_prep")

nb_enc = st.slider("Nombre d'UVC en ENCOURS",
                   min_value= 1,
                   max_value= int(df_prep['UVC_ENCOURS'].max()),
                   value=(int(df_prep['UVC_ENCOURS'].min()), int(df_prep['UVC_ENCOURS'].max())),
                   step= 50,
                   key = "nb_uvc")


if axes_selectionnes3:
    df_prep = df_prep[df_prep['AXE_PRODUIT'].isin(axes_selectionnes3)]
if code_prep:
    df_prep = df_prep[df_prep['CODPRO'].str.contains(code_prep, case=False, na=False)]
if nb_enc:
    df_prep = df_prep[df_prep['UVC_ENCOURS'].between(nb_enc[0], nb_enc[1])]
    


st.dataframe(df_prep, use_container_width= True, height = 600, hide_index= True)


st.markdown("----------------------------------------------------------------------------------------------------------")
st.subheader("Mettre un Titre...")

df_edit = data.copy()
df_edit = df_edit[(df_edit['TYPE'] != "Réserve") & (df_edit['AXE_PRODUIT'] != "")]

edit_data = df_edit[['CODPRO','ANAPRO',"Désignation",'UVC_STOCK','AXE_PRODUIT']].dropna().sort_values(by = "ANAPRO", ascending = True)

edit_data_code = (edit_data.groupby(["ANAPRO","AXE_PRODUIT"])["CODPRO"].nunique()
             .reset_index(name = "Nombre de CODPRO par Marque")
             .sort_values(by = "Nombre de CODPRO par Marque", ascending = False))

edit_data_uvc = (edit_data.groupby(["ANAPRO","AXE_PRODUIT"])["UVC_STOCK"].sum()
             .reset_index(name = "Nombre d'UVC par Marque")
             .sort_values(by = "Nombre d'UVC par Marque", ascending = False))

# edit_data_axe = (edit_data.groupby(["AXE_PRODUIT",'ANAPRO'])["UVC_STOCK"].sum()
#              .reset_index(name = "Nombre d'UVC par Axe")
#              .sort_values(by = "Nombre d'UVC par Axe", ascending = False))

edit_data_clean = edit_data_code.merge(edit_data_uvc, on = ['ANAPRO',"AXE_PRODUIT"], how = 'inner')

edit_data_pivot = edit_data_clean.pivot(columns = "AXE_PRODUIT", 
                                        index = ["ANAPRO","Nombre de CODPRO par Marque"], 
                                        values = "Nombre d'UVC par Marque")

edit_data_pivot = edit_data_pivot.astype("object")  
edit_data_pivot.fillna("-", inplace=True)


choix_marque = st.multiselect("Choisir une Marque: ", options=edit_data_pivot.index.get_level_values("ANAPRO").unique(), key='anapro')
# choix_axe = st.multiselect("Choisir un Axe: ", options = final_edit.columns.get_level_values('AXE_PRODUIT'), key = "axep")

if choix_marque:
    edit_data_pivot = edit_data_pivot.loc[edit_data_pivot.index.get_level_values("ANAPRO").isin(choix_marque)]

# if choix_axe:
#     final_edit = final_edit[final_edit.columns.get_level_values('AXE_PRODUIT').isin(choix_axe)]

st.dataframe(edit_data_pivot, use_container_width= True, height = 600, width = 600,)



st.data_editor(
    edit_data_clean, 
               column_config = {
                               "Nombre d'UVC par Marque" : 
                                st.column_config.ProgressColumn("Nb UVC",
                                format = "%f",
                                min_value = int(edit_data_clean["Nombre d'UVC par Marque"].min()),
                                max_value = int(edit_data_clean["Nombre d'UVC par Marque"].max()),
                                ),
                                },
                                hide_index = True,
                                use_container_width = True,
                                height = 600)



