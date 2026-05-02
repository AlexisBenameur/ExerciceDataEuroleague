import requests
import streamlit as st 
import plotly.express as px
import pandas as pd

url = "https://live.euroleague.net/api/v2/private"

credentials = {"user": "" , "password" : ""}


@st.cache_data
def get_gamecodes(season = 2024):
    try :
        r = requests.get(f"{url}/games", params = {**credentials, "seasoncode" : f"E{season}"})
        r.raise_for_status() 

        games_data = r.json()
        list_gamecodes = []

        for game in games_data["games"]:
            code = game.get("gamecode")
            if code :
                list_gamecodes.append(code)

        return list_gamecodes 
      
    except Exception as e:
        print(f"Erreur lors de la récupération des gamecodes : {e}")
        return []

@st.cache_data
def get_scores( season = 2024):
    list_gamecodes = get_gamecodes(season)
    dico = {}
    for gamecode in list_gamecodes:
        try :
            r = requests.get(f"{url}/graphicstats", params = {**credentials, "gamecode" : gamecode, "seasoncode" : f"E{season}"})
            r.raise_for_status()

            data = r.json()
            d = {}

            if data["mainData"]["Live"] == False and data["mainData"]["ScoreA"]>data["mainData"]["ScoreB"]: 
                d["win"] = True
                d["winner"] = data["mainData"]["TeamA"]
                d["loser"] = data["mainData"]["TeamB"]

                for i in range (1, 4):
                    d[f"diffQT{i}"] = data["mainData"][f"ScoreQuarter{i}A"] - data["mainData"][f"ScoreQuarter{i}B"]

            elif data["mainData"]["Live"] == False and data["mainData"]["ScoreA"] <data["mainData"]["ScoreB"]:
                d["win"] = False
                d["winner"] = data["mainData"]["TeamB"]
                d["loser"] = data["mainData"]["TeamA"]

                for i in range (1, 4):
                    d[f"diffQT{i}"] = data["mainData"][f"ScoreQuarter{i}A"] - data["mainData"][f"ScoreQuarter{i}B"]

            dico[gamecode] = d

        except Exception as e:
            print(f"Erreur sur le match {gamecode} : {e}")
            continue
        
    return dico

@st.cache_data
def proba_win_given_diff(season, QT, diff):
    dico = get_scores(season)
    count_win = 0
    count_total = 0

    for gamecode, data in dico.items():

        if data[f"diffQT{QT}"] == diff:
            count_total += 1
            if data["win"] :
                count_win += 1

        if data[f"diffQT{QT}"] == -diff:
            count_total += 1
            if not data["win"] :
                count_win += 1

    if count_total > 0:
        return count_win / count_total
    
    else:
        return (f"Cette différence de points n'a jamais été observée à la fin du QT {QT}")

@st.cache_data 
def plot_proba_win(season, diff):
    try : 
        data = []

        for QT in range(1, 4):
            proba = proba_win_given_diff(season, QT, diff)
            data.append({"QT": f"QT{QT}", "Probabilité": proba})

        df = pd.DataFrame(data)
        fig = px.line(df, x="QT", y="Probabilité", title=f"Probabilité de victoire en fonction de la différence de points à la fin d'un quart temps pour une différence de {diff} points en {season}")
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Erreur lors de la génération du graphique : {e}")

@st.cache_data
def get_comeback_games(season):
    dico = get_scores(season)
    comeback_games = []

    for gamecode, data in dico.items():
        if (data["diffQT1"] <= -10 and data["win"]) or (data["diffQT1"] >= 10 and not data["win"]):
            comeback_games.append(gamecode)

    return comeback_games

@st.cache_data
def get_shot_numbers(season) : 
    comeback_games = get_comeback_games(season)
    dico = {}

    for gamecode in comeback_games:
        fga3q1, fga3q2, fga3q3, fga3q4 = 0, 0, 0, 0
        fgm3q1, fgm3q2, fgm3q3, fgm3q4 = 0, 0, 0, 0
        fga2q1, fga2q2, fga2q3, fga2q4 = 0, 0, 0, 0
        d = {}
        try :
            r = requests.get(f"{url}/shootingchart", params = {**credentials, "gamecode" : gamecode, "seasoncode" : f"E{season}"})
            r.raise_for_status()
            data = r.json()
            donnees = data["points"]["Rows"]

            for play in donnees:

                if play["MINUTE"] <10:
                    if play["ID_ACTION"]=="3FGA":
                        fga3q1 += 1
                    elif play["ID_ACTION"]=="3FGM":
                        fgm3q1 += 1
                        fga3q1 += 1
                    elif play["ID_ACTION"]=="2FGA" or play["ID_ACTION"]=="2FGM":
                        fga2q1 += 1

                if play["MINUTE"] >= 10 and play["MINUTE"] < 20 :
                    if play["ID_ACTION"]=="3FGA":
                        fga3q2 += 1
                    elif play["ID_ACTION"]=="3FGM":
                        fgm3q2 += 1
                        fga3q2 += 1
                    elif play["ID_ACTION"]=="2FGA" or play["ID_ACTION"]=="2FGM":
                        fga2q2 += 1

                if play["MINUTE"] >= 20 and play["MINUTE"] < 30 :
                    if play["ID_ACTION"]=="3FGA":
                        fga3q3 += 1
                    elif play["ID_ACTION"]=="3FGM":
                        fgm3q3 += 1
                        fga3q3 += 1
                    elif play["ID_ACTION"]=="2FGA" or play["ID_ACTION"]=="2FGM":
                        fga2q3 += 1

                if play["MINUTE"] >= 30 :
                    if play["ID_ACTION"]=="3FGA":
                        fga3q4 += 1
                    elif play["ID_ACTION"]=="3FGM":
                        fgm3q4 += 1
                        fga3q4 += 1
                    elif play["ID_ACTION"]=="2FGA" or play["ID_ACTION"]=="2FGM":
                        fga2q4 += 1
            
            d[1] = [fgm3q1, fga3q1, fga2q1]
            d[2] = [fgm3q2, fga3q2, fga2q2]
            d[3] = [fgm3q3, fga3q3, fga2q3]
            d[4] = [fgm3q4, fga3q4, fga2q4]

            dico[gamecode] = d
            
        except Exception as e:
            print(f"Erreur sur le match {gamecode} : {e}")
            continue
    
    return dico

@st.cache_data
def comeback_fg_percentage(season) : 
    dico = get_shot_numbers(season)
    scores_info = get_scores(season)
    raw_data = []

    for gamecode, data in dico.items():
        team_name = scores_info[gamecode]["winner"]

        for qt in range(1, 5):
            fg3_percentage = data[qt][0] / data[qt][1] if data[qt][1] > 0 else 0
            raw_data.append({"Team": team_name, "Quarter": f"QT{qt}", "3FG_Percentage": fg3_percentage})
        
    return pd.DataFrame(raw_data)

@st.cache_data
def comeback_3pt_attempt_rate (season):
    dico = get_shot_numbers(season)
    scores_info = get_scores(season)
    raw_data = []

    for gamecode, data in dico.items():
        team_name = scores_info[gamecode]["winner"]

        for qt in range(1, 5):
            total_attempts = data[qt][1] + data[qt][2]
            if total_attempts > 0:
                three_pt_attempt_rate = data[qt][1] / total_attempts
            else:
                three_pt_attempt_rate = 0
            
            raw_data.append({"Team": team_name, "Quarter": f"QT{qt}", "3PT_Attempt_Rate": three_pt_attempt_rate})
    
    return pd.DataFrame(raw_data)


st.set_page_config(page_title="🏀Analyse Euroleague", layout="wide")
st.title("Analyse des données de l'Euroleague")
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
            font-size: 16px;
        }"""

st.markdown(code_css, unsafe_allow_html=True)

with st.sidebar:
    st.header("Paramètres")
    season = st.selectbox("Saison", [2021, 2022, 2023, 2024])
    diff_target = st.slider("Différence de points à la fin du QT", -20, 20, 0)

vue_choisie = st.sidebar.radio("Choisissez une analyse", ("Probabilité de victoire en fonction de la différence de points", "Statistiques des comebacks"))

if vue_choisie == "Probabilité de victoire en fonction de la différence de points":
    plot_proba_win(season, diff_target)

if vue_choisie == "Statistiques des comebacks":
    st.header(f"Analyse des stratégies de comeback pour la saison {season}")

    if st.checkbox("Afficher le pourcentage de réussite à 3 points en comeback"):

        df_percentage = comeback_fg_percentage(season)

        if not df_percentage.empty:
            all_teams = sorted(df_percentage["Team"].unique())
            selected_teams = st.multiselect("Sélectionnez les équipes à afficher", all_teams, default=all_teams[:2] if len(all_teams)>1 else all_teams)
        
            if selected_teams:
                df_filtered = df_percentage[df_percentage["Team"].isin(selected_teams)]
                df_plot = df_filtered.groupby(["Team", "Quarter"])["3FG_Percentage"].mean().reset_index()

                df_league_avg = df_plot.groupby("Quarter")["3FG_Percentage"].mean().reset_index()
                df_league_avg["Team"] = "Moyenne Ligue"
                df_final = pd.concat([df_plot, df_league_avg])

                fig = px.line(df_final, x="Quarter", y="3FG_Percentage", color="Team", markers=True, title=f"Pourcentage de réussite à 3 points des équipes en comeback - Saison {season}")
            
                fig.update_layout(yaxis_title="Pourcentage de réussite à 3 points", xaxis_title="Quart-temps")
                st.plotly_chart(fig, use_container_width=True)

            else : 
                st.write("Aucune équipe sélectionnée.")
        else : 
            st.write("Aucune donnée de comeback disponible pour cette saison.")
    
    if st.checkbox("Afficher le taux de tentatives à 3 points en comeback"):

        df_attempt_rate = comeback_3pt_attempt_rate(season)

        if not df_attempt_rate.empty:
            all_teams = sorted(df_attempt_rate["Team"].unique())
            selected_teams = st.multiselect("Sélectionnez les équipes à afficher", all_teams, default=all_teams[:2] if len(all_teams)>1 else all_teams)
        
            if selected_teams:
                df_filtered = df_attempt_rate[df_attempt_rate["Team"].isin(selected_teams)]
                df_plot = df_filtered.groupby(["Team", "Quarter"])["3PT_Attempt_Rate"].mean().reset_index()

                df_league_avg = df_plot.groupby("Quarter")["3PT_Attempt_Rate"].mean().reset_index()
                df_league_avg["Team"] = "Moyenne Ligue"
                df_final = pd.concat([df_plot, df_league_avg])

                fig = px.line(df_final, x="Quarter", y="3PT_Attempt_Rate", color="Team", markers=True, title=f"Taux de tentatives à 3 points des équipes en comeback - Saison {season}")
            
                fig.update_layout(yaxis_title="Taux de tentatives à 3 points", xaxis_title="Quart-temps")
                st.plotly_chart(fig, use_container_width=True)
            
            else :
                st.write("Aucune équipe sélectionnée.")
        else :
            st.write("Aucune donnée de comeback disponible pour cette saison.")