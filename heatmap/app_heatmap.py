import requests
import streamlit as st 
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

url = "https://live.euroleague.net/api/v2/private"

credentials = {"user": "" , "password" : ""}

@st.cache_data
def get_camecodes(season):
    try :
        r = requests.get(f"{url}/games", params = {**credentials, "seasoncode" : f"E{season}"})
        r.raise_for_status() 

        games_data = r.json()
        dico_gamecodes = {}

        for game in games_data["games"]:
            code = game.get("gamecode")
            teamA = game.get("team1")
            teamB = game.get("team2")
            if code :
                dico_gamecodes[code] = {"teamA": teamA, "teamB": teamB}

        return dico_gamecodes 
      
    except Exception as e:
        print(f"Erreur lors de la récupération des gamecodes : {e}")
        return []

@st.cache_data    
def get_fg(season, gamecode):
    try :
        r = requests.get(f"{url}/shootingchart", params = {**credentials, "gamecode" : gamecode, "seasoncode" : f"E{season}"})
        r.raise_for_status()
        data = r.json()
        
        teamA = data["mainData"]["CodeTeamA"]
        teamB = data["mainData"]["CodeTeamB"]

        dA = {"C" : (0,0), "D" : (0,0), "E" : (0,0), "F" : (0,0), "G" : (0,0), "H" : (0,0), "I" : (0,0), "J" : (0,0), "K" : (0,0), "L" : (0,0), }
        dB = {"C" : (0,0), "D" : (0,0), "E" : (0,0), "F" : (0,0), "G" : (0,0), "H" : (0,0), "I" : (0,0), "J" : (0,0), "K" : (0,0), "L" : (0,0), }
        donnees = data["points"]["Rows"]

        for play in donnees : 

            if play["CodeTeam"] == teamA :
                if play["ID_ACTION"] == "2FGA" or play["ID_ACTION"] == "3FGA" :
                    dA[play["ZONE"]] = (dA[play["ZONE"]][0], dA[play["ZONE"]][1]+1)
                elif play["ID_ACTION"] == "2FGM" or play["ID_ACTION"] == "3FGM" :
                    dA[play["ZONE"]] = (dA[play["ZONE"]][0]+1, dA[play["ZONE"]][1]+1)

            elif play["CodeTeam"] == teamB :
                if play["ID_ACTION"] == "2FGA" or play["ID_ACTION"] == "3FGA" :
                    dB[play["ZONE"]] = (dB[play["ZONE"]][0], dB[play["ZONE"]][1]+1)
                elif play["ID_ACTION"] == "2FGM" or play["ID_ACTION"] == "3FGM" :
                    dB[play["ZONE"]] = (dB[play["ZONE"]][0]+1, dB[play["ZONE"]][1]+1)
        
        return dA, dB, teamA, teamB
    
    except Exception as e:
        print(f"Erreur lors de la récupération des données de tir : {e}")
        return {}, {}, "", ""

@st.cache_data   
def get_fg_all_season(season) : 
    gamecodes = get_camecodes(season)
    dico = {}

    for gamecode in gamecodes.keys() : 
        dA, dB, code_teamA, code_teamB = get_fg(season, gamecode)

        if code_teamA not in dico :
            dico[code_teamA] = dA
        
        else :
            dictA= dico[code_teamA]
            for zone in dA.keys() :
                dictA[zone] = (dictA[zone][0]+dA[zone][0], dictA[zone][1]+dA[zone][1])
            dico[code_teamA] = dictA

        if code_teamB not in dico :
            dico[code_teamB] = dB
       
        else :
            dictB= dico[code_teamB]
            for zone in dB.keys() :
                dictB[zone] = (dictB[zone][0]+dB[zone][0], dictB[zone][1]+dB[zone][1])
            dico[code_teamB] = dictB
        
    return dico

@st.cache_data
def get_fg_percentage(season) : 
    dico = get_fg_all_season(season)
    dico_percentage = {}

    for team in dico.keys() :
        dico_percentage[team] = {}
        
        for zone in dico[team].keys() :
            if dico[team][zone][1] != 0 :
                dico_percentage[team][zone] = dico[team][zone][0]/dico[team][zone][1]
    
    return dico_percentage

@st.cache_data
def reduce_fg (season, gamecode, team) :
    dA, dB, code_teamA, code_teamB = get_fg(season, gamecode)
    dico = get_fg_percentage(season)
    dA_percentage, dB_percentage = {}, {}

    if team == code_teamA :
        for zone in dB.keys() :
            dB_percentage[zone] = dB[zone][0]/dB[zone][1] - dico[code_teamB][zone] if dB[zone][1] != 0 else 0
        return dB_percentage
    
    elif team == code_teamB :
        for zone in dA.keys() :
            dA_percentage[zone] = dA[zone][0]/dA[zone][1] - dico[code_teamA][zone] if dA[zone][1] != 0 else 0
        return dA_percentage

@st.cache_data
def get_reduced_fg_all_season(season, team) : 
    gamecodes = get_camecodes(season)
    dico = {}

    for gamecode in gamecodes.keys() :
        if team in gamecodes[gamecode].values() : 
            d_percentage = reduce_fg(season, gamecode, team)
            for zone in d_percentage.keys() :
                if zone in dico:
                    dico[zone].append(d_percentage[zone])
                else:
                    dico[zone] = [d_percentage[zone]]

        else : 
            continue
    
    for zone in dico.keys() :
        dico[zone] = sum(dico[zone]) / len(dico[zone])
    
    return dico

@st.cache_data
def plot_defensive_heatmap(season, team):
    dico_reduced = get_reduced_fg_all_season(season, team)
    zones_coords = {
        "C": {"x": 0, "y": 100},    # Sous le panier (Restricted Area)
        "D": {"x": -150, "y": 250}, # Raquette basse gauche
        "F": {"x": 150, "y": 250},  # Raquette basse droite
        "E": {"x": -150, "y": 450}, # Raquette haute gauche (High Post)
        "J": {"x": 150, "y": 450},  # Raquette haute droite
        "G": {"x": -350, "y": 100}, # Corner 3PT gauche
        "H": {"x": 350, "y": 100},  # Corner 3PT droit
        "I": {"x": -250, "y": 600}, # Aile 3PT gauche (Wing)
        "K": {"x": 250, "y": 600},  # Aile 3PT droite
        "L": {"x": 0, "y": 700}     # Axe central 3PT (Top of the key)
    }

    data = []
    for zone, reduction in dico_reduced.items():
        if zone in zones_coords:
            data.append({
                "zone": zone,
                "Reduction" : reduction,
                "x": zones_coords[zone]["x"],
                "y": zones_coords[zone]["y"],  
                "Texte_Affichage": f"{reduction*100:.1f}%"
            })

    df = pd.DataFrame(data)

    if df.empty:
        st.warning(f"Pas de données de tir trouvées pour {team}.")
        return None

    fig = px.scatter(
        df, 
        x="X", y="Y", 
        color="Reduction",
        text="Texte_Affichage",
        color_continuous_scale=px.colors.diverging.RdYlGn[::-1],
        range_color=[-0.15, 0.15], # Échelle fixe de -15% à +15%
        title=f"Heatmap Défensive : {team} (Stop Rate)"
    )

    fig.update_traces(
        marker=dict(size=45, line=dict(width=2, color='black')),
        textfont_color='black',
        textfont_size=13,
        textfont_family="Arial Black" # Pour que le texte ressorte bien
    )

    fig.add_layout_image(
        dict(
            source="terrain_euroleague.png", 
            xref="x", yref="y",
            x=-400,     # Centre l'image horizontalement
            y=850,      # Aligne le haut de l'image
            sizex=800,  # Largeur totale
            sizey=850,  # Hauteur totale
            sizing="stretch",
            opacity=0.6,
            layer="below"
        )
    )

    fig.update_xaxes(visible=False, range=[-400, 400])
    fig.update_yaxes(visible=False, range=[0, 850])

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", 
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title="Variation d'Adresse",
            tickformat=".0%" # Affiche des % sur la barre de couleur
        )
    )

    return fig

@st.cache_data
def get_teams_code(season):
    gamecodes = get_camecodes(season)
    teams = []
    i = 0

    try :
        r = requests.get(f"{url}/shootingchart", params = {**credentials, "gamecode" : gamecode, "seasoncode" : f"E{season}"})
        r.raise_for_status()
        data = r.json()

        teamA = data["mainData"]["CodeTeamA"]
        teamB = data["mainData"]["CodeTeamB"]
        
        if not teamA in teams :
            teams.append(teamA)
            i+=1
        if not teamB in teams :
            teams.append(teamB)
            i+=1
        if i >=20 :
            return teams
    
    except Exception as e:
        print(f"Erreur lors de la récupération des données de tir : {e}")
        return teams



st.set_page_config(page_title="🏀Heatmap Euroleague", layout="wide")
st.title("Analyse des données de l'Euroleague pour construire une heatmap défensive")

code_css = """
<style>
 .stApp {
   background-color: #0A192F;
   }
.stApp {
   color: #FFFFFF;
   }
.stAPP {
   # padding: 20px; 
    } 
.stApp label p {
    color: #FFFFFF !important; 
    }
    [data-testid="stSidebar"] {
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] {
        background-color: #0A193F;
    }
    [data-testid="stSidebar"] label p {
            color: #FFFFFF !important; 
            font-size: 16px;}
    """

st.markdown(code_css, unsafe_allow_html=True)
st.markdown("Cette carte montre l'impact de la défense sur l'adresse adverse par zone. \n* **Vert** : L'équipe fait chuter l'adresse de l'adversaire.\n* **Rouge** : L'équipe subit dans cette zone.*")

with st.sidebar:
    st.header("Paramètres")
    season = st.selectbox("Saison", [2021, 2022, 2023, 2024])

team_selected = st.selectbox("Sélectionnez l'équipe à analyser :", get_teams_code(season))

if st.button("Tracer la Heatmap"):
    with st.spinner("Analyse des données défensives en cours..."):
        fig_heatmap = plot_defensive_heatmap(season, team_selected)

        if fig_heatmap : 
            st.plotly_chart(fig_heatmap, use_container_width=True)