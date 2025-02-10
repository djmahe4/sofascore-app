import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi
import numpy as np
import time
import json
import http.client
import http.cookiejar
import streamlit as st
from urllib.parse import urlparse
import http.client
import datetime
from icecream import ic
def destruct_all():
    st.session_state.mul_sele = 0
    # Initialize session state variables if they are not already set
    st.session_state.opt1 = None
    st.session_state.leagues = {}
    st.session_state.opt2 = None
    st.session_state.choosen = None
    st.session_state.tid = None
    st.session_state.opt3 = None
    st.session_state.teams = {}
    st.session_state.selected_players = []
    st.session_state.stat_coll = {'Players': []}
    st.session_state.players = {}
    st.session_state.diff_returned = {}
    st.session_state.pposition = None
    st.session_state.per90 = False
def get_sofascore(url):
    parsed = urlparse(url)
    conn = http.client.HTTPSConnection(parsed.netloc)
    conn.request("GET", parsed.path)
    res = conn.getresponse()
    data = res.read()
    jdata = json.loads(data.decode("utf-8"))
    return jdata


def create_radar_chart2(df):
    """Generates a radar chart comparing players from a DataFrame with percentile-based standardization."""

    st.dataframe(df)
    num_players = len(df)

    if not 2 <= num_players <= 4:
        raise ValueError("Number of players must be between 2 and 4.")

    # Extract categories and ensure correct order
    categories = list(df.columns[1:])  # Exclude 'Players' column
    num_categories = len(categories)

    # Calculate percentiles using rank instead of qcut for better tie handling
    standardized_df = df.copy()
    standardized_df[categories] = df[categories].rank(pct=True) * 99

    # Calculate angles for radar chart
    angles = np.linspace(0, 2 * np.pi, num_categories, endpoint=False).tolist()
    angles += angles[:1]  # Close the plot

    # Create plot
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
    palette = sns.color_palette("husl", num_players)

    # Plot each player's data
    for idx, row in standardized_df.iterrows():
        values = row[categories].tolist()
        values += values[:1]  # Close the plot

        ax.plot(angles, values, marker='o',
                label=row['Players'],  # Use direct column access
                color=palette[idx],
                linewidth=2,
                markersize=8)
        ax.fill(angles, values, color=palette[idx], alpha=0.25)

    # Format axes
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=12)
    ax.set_yticks(np.arange(0, 100, 20))
    ax.set_ylim(0, 99)
    ax.set_rlabel_position(30)

    # Add legend and title
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    title = 'Player Comparison ' + (' (per90)' if st.session_state.per90 else '')
    ax.set_title(title, size=14, pad=20)

    # Display plot
    plt.tight_layout()
    st.pyplot(fig)

def create_radar_chart(df):
    """Generates a radar chart comparing players from a DataFrame."""
    st.dataframe(df)
    num_players = len(df)
    if not 2 <= num_players <= 4:
        raise ValueError("Number of players must be between 2 and 4.")

    categories = list(df.columns[1:])  # Exclude 'Player' column
    num_categories = len(categories)

    # Calculate angles for the radar chart
    angles = [n / float(num_categories) * 2 * pi for n in range(num_categories)]
    angles += angles[:1]  # Close the plot

    # Set up the plot with seaborn style
    sns.set_theme(style="whitegrid")  # Or any other seaborn style you prefer
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))  # Adjust size if needed

    # Color palette (using seaborn for consistency)
    palette = sns.color_palette("husl", num_players) # You can use other palettes

    for i in range(num_players):
        values = df.iloc[i][1:].values.flatten().tolist()
        values += values[:1]  # Close the plot

        ax.plot(angles, values, marker='o', label=df['Players'][i], color=palette[i])
        ax.fill(angles, values, alpha=0.25, color=palette[i]) # Fill the area

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_yticks(np.arange(0, 11, 2)) # Adjust range as needed
    ax.set_ylim(0, 10)  # Ensure consistent y-axis limits
    ax.legend(loc=(0.9,0.9)) # Place legend outside
    if not st.session_state.per90:
        plt.title('Player Comparison')
    else:
        plt.title('Per90 Player Comparison')

    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    st.pyplot(plt)


def test():
    # Example usage with variable number of players:

    # Example 1: 3 players
    data1 = {'Player': ['A', 'B', 'C'],
             'Speed': [8, 9, 7],
             'Strength': [7, 8, 9],
             'Agility': [9, 7, 8],
             'Skill': [8, 8, 8]}
    df1 = pd.DataFrame(data1)
    create_radar_chart(df1)

    # Example 2: 2 players
    data2 = {'Player': ['X', 'Y'],
             'Speed': [5, 9],
             'Strength': [9, 6],
             'Agility': [7, 8],
             'Skill': [8, 7]}
    df2 = pd.DataFrame(data2)
    create_radar_chart(df2)

    # Example 3: 4 players
    data3 = {'Player': ['P', 'Q', 'R', 'S'],
             'Speed': [8, 9, 7, 6],
             'Strength': [7, 8, 9, 5],
             'Agility': [9, 7, 8, 4],
             'Skill': [8, 8, 8, 7]}
    df3 = pd.DataFrame(data3)
    create_radar_chart(df3)

    #Example 4: Error handling (5 players)
    data4 = {'Player': ['P', 'Q', 'R', 'S', 'T'],
             'Speed': [8, 9, 7, 6, 9],
             'Strength': [7, 8, 9, 5, 8],
             'Agility': [9, 7, 8, 4, 7],
             'Skill': [8, 8, 8, 7, 9]}
    df4 = pd.DataFrame(data4)
    create_radar_chart(df4) # This will raise the ValueError
def get_player_data(num_players):
    """Efficiently collects league, team, and player names from the user."""

    player_data = []

    for i in range(num_players):
        st.subheader(f"Player {i+1}")  # Clearer section headers

        # Use columns for better layout, especially for multiple inputs per player
        col1, col2, col3 = st.columns(3)  # Adjust number of columns as needed

        with col1:
            league = st.text_input(f"League (Player {i+1})", placeholder="e.g., Premier League")
        with col2:
            team = st.text_input(f"Team (Player {i+1})", placeholder="e.g., Manchester United")
        with col3:
            player_name = st.text_input(f"Player Name (Player {i+1})", placeholder="e.g., Cristiano Ronaldo")

        # Validate inputs (optional, but good practice)
        if not league or not team or not player_name:  # Check if any input is missing
            st.warning(f"Please fill in all details for Player {i+1}")
            # You might want to prevent proceeding until all data is entered
            # st.stop()  # Uncomment if you want to stop execution

        player_data.append({'League': league, 'Team': team, 'Player': player_name})

    return pd.DataFrame(player_data)

def get_teams():
    #jdata={}
    teams = {}
    for l in st.session_state.opt2:
        #st.session_state.leagues[l]
        tid = st.session_state.leagues[l][0]
        sid = st.session_state.leagues[l][1]
        url = f"https://www.sofascore.com/api/v1/unique-tournament/{tid}/season/{sid}/standings/total"

        jdata=get_sofascore(url)

        for i in jdata['standings'][0]['rows']:
            teams.update({f"{i['team']['name']}": [i['team']['id'],tid,sid]})
        #ic(jdata)
        #st.write(teams)
    return teams
def per90_calc(dic):
    ndic={}
    for i in dic:
        if i=="id" or i=='names':
            ndic.update({i:dic[i]})
            continue
        arr=[]
        for j in range(len(dic[i])):
            #try:
            ns=(dic['minutesPlayed'][j])/90
            try:
                arr.append(dic[i][j]/ns)
            except ZeroDivisionError:
                arr.append(0)
        ndic.update({i:arr})
    return ndic
def get_players():
    players = {}
    for t in st.session_state.opt3:
        tid = st.session_state.teams[t][0]
        lid,sid=st.session_state.teams[t][1],st.session_state.teams[t][2]
        url = f"https://www.sofascore.com/api/v1/team/{tid}/players"
        jdata=get_sofascore(url)

        for i in jdata['players']:
            players.update({i['player']['name']: [i['player']['id'], i['player']['position'],lid,sid]})
    return players
desired = {
        "Goalkeeper": [
            "saves",
            'cleanSheet',
            'goalsConceded',
            'punches',
            'cleanSheet',
            'highClaims',
            'accuratePasses',
            'accurateLongBalls'
        ],
        "Centre-Back": [
            'goals',
            'tacklesWon',
            'groundDuelsWon',
            'aerialDuelsWon',
            'interceptions',
            'blockedShots',
            'ballRecovery',
            'dribbledPast',
            'accuratePasses',
            'accuratePassesPercentage',
            'accurateLongBalls',
            'touches'
        ],
        "Full-Back/Wing-Back": [
            'assists',
            'groundDuelsWon',
            "interceptions",
            'ballRecovery',
            'successfulDribbles',
            'accuratePasses',
            'accuratePassesPercentage',
            'accurateLongBalls',
            'touches',
            'accurateCrosses',
            'dribbledPast',
            'accurateCrossesPercentage'
        ],
        "Defensive Midfielder": [
            'goalsAssistsSum',
            "assists",
            "interceptions",
            'accuratePasses',
            'accuratePassesPercentage',
            'tacklesWon',
            'totalDuelsWon',
            'accurateLongBalls',
            "touches",
            "dispossessed",
            "interceptions",
            'ballRecovery',
            'dribbledPast'
        ],
        "Central Midfielder": [
            'goalsAssistsSum',
            "assists",
            'accuratePasses',
            'accuratePassesPercentage',
            'accurateLongBalls',
            'bigChancesCreated',
            'keyPasses',
            "touches",
            "dispossessed",
            "interceptions",
            'ballRecovery',
        ],
        "Attacking midfielder/Second Striker":[
            'possessionWonAttThird',
            'assists',
            'goalsAssistsSum',
            'goals',
            'bigChancesCreated',
            'keyPasses',
            'successfulDribbles',
            'accurateCrosses',
            'totalShots',
            'shotsOnTarget'
        ],
        "Wide Midfielder/Winger": [
            'possessionWonAttThird',
            "goals",
            'totalShots',
            'shotsOnTarget'
            "assists",
            'successfulDribbles',
            'accurateFinalThirdPasses',
            'accurateCrosses',
            'touches'
        ],
        "Forward/Striker": [
            "goals",
            'totalShots',
            'shotsOnTarget'
            "assists",
            "successfulDribbles",
            "touches",
            'groundDuelsWon',
            'aerialDuelsWon',
            'ballRecovery'
        ]
    }
positions={2:"Midfielder",3:"Forward",1:"Defender",0:"Goalkeeper"}
#new st.session_state.stat_coll={'Players':[]}
#def cal_p90():

def get_dataframe():
    #stat_coll = {'Players': []}
    #id = 1009327
    #lid = 1900
    #sid = 65961
    #lid, sid = st.session_state.leagues[st.session_state.opt2]
    #pname='kazhiveri'
    for pname in st.session_state.diff_returned['players']:
        st.write(st.session_state.diff_returned['players'])
        diction=st.session_state.diff_returned['players'][pname]
        id=diction[0]
        lid=diction[2]
        sid=diction[3]
        st.session_state.stat_coll['Players'].append(pname)
        url = f"https://www.sofascore.com/api/v1/player/{id}/unique-tournament/{lid}/season/{sid}/statistics/overall"
        try:
            stats=get_sofascore(url)['statistics']
        except:
            st.write(url)
            print(get_sofascore(url))

        if not st.session_state.per90:
            for i in stats:
                if i in desired[st.session_state.pposition]:
                    try:
                        st.session_state.stat_coll[i].append(stats[i])
                    except:
                        st.session_state.stat_coll.update({i:[stats[i]]})

        else:
            for i in stats:
                if i in desired[st.session_state.pposition]:
                    if "Percentage" in i:
                        try:
                            st.session_state.stat_coll[i].append(stats[i])
                        except:
                            st.session_state.stat_coll.update({i:[stats[i]]})
                    else:
                        try:
                            st.session_state.stat_coll[i].append(stats[i]/(stats['minutesPlayed']/90))
                        except:
                            st.session_state.stat_coll.update({i:[stats[i]/(stats['minutesPlayed']/90)]})

    create_radar_chart2(pd.DataFrame(st.session_state.stat_coll))
def main():
    if 'mul_sele' not in st.session_state:
        st.session_state.mul_sele=0
    # Initialize session state variables if they are not already set
    if 'opt1' not in st.session_state:
        st.session_state.opt1 = None
    if 'leagues' not in st.session_state:
        st.session_state.leagues = {}
    if 'opt2' not in st.session_state:
        st.session_state.opt2 = None
    if 'choosen' not in st.session_state:
        st.session_state.choosen = None
    if 'tid' not in st.session_state:
        st.session_state.tid = None
    if 'opt3' not in st.session_state:
        st.session_state.opt3 = None
    if 'teams' not in st.session_state:
        st.session_state.teams = {}
    if 'selected_players' not in st.session_state:  # Changed from 'opt4'
        st.session_state.selected_players = []
    if 'start_col' not in st.session_state:
        st.session_state.stat_coll = {'Players': []}
    if 'players' not in st.session_state:
        st.session_state.players = {}
    if 'diff_returned' not in st.session_state:
        st.session_state.diff_returned = {}
    if "pposition" not in st.session_state:
        st.session_state.pposition=None
    if "per90" not in st.session_state:
        st.session_state.per90=False
    st.info("Choose common position to compare!")
    if st.button("Reset"):
        destruct_all()
        #main()
    if not st.session_state.pposition:
        pos = st.selectbox("Choose position to analyse:", list(desired.keys()))
        if st.button("Position"):
            st.session_state.pposition = pos
            st.write(f"Selected position:{st.session_state.pposition}")
    if st.session_state.pposition:
        p9 = st.selectbox("Per90?", [True, False])
        if st.button("p90"):
            st.session_state.per90 = p9
            st.write(f"Per90:{st.session_state.per90}")
    mul_sele=st.slider("Select number of players",min_value=2,max_value=4,step=1)
    if st.session_state.mul_sele==0:
        if st.button("Slided"):
            st.session_state.mul_sele=mul_sele
    if st.session_state.mul_sele!=0:
    # Select league nation if opt1 is None
        leagues = {}
        if st.session_state.opt1 is None and st.session_state.leagues == {}:
            date = datetime.date.today().strftime("%Y-%m-%d")
            jdata = get_sofascore(f"https://www.sofascore.com/api/v1/sport/football/scheduled-events/{date}")
            for i in jdata['events']:
                if i['tournament']['uniqueTournament']['name'] not in leagues:
                    leagues.update({i['tournament']['uniqueTournament']['name']: [
                        i['tournament']['uniqueTournament']['id'],
                        i['season']['id']
                    ]})
            st.session_state.leagues = leagues
            st.session_state.opt2 = None

        # Display league selection
        if st.session_state.leagues and st.session_state.opt2 is None:
            selected_leagues = st.multiselect(
                "Select leagues",
                list(st.session_state.leagues.keys()),
                key="League_select",
                max_selections=st.session_state.mul_sele
            )
            if st.button("Confirm"):
                st.session_state.opt2 = selected_leagues
                st.write("You have selected:", st.session_state.opt2)
                st.session_state.teams = {}
                st.session_state.players = {}

        # Display teams
        if st.session_state.opt2 and st.session_state.teams == {}:
            #st.write("Confirmed League:", st.session_state.opt2, "with IDs:",
                     #st.session_state.leagues[st.session_state.opt2])
            for l in st.session_state.opt2:
                st.write("Confirmed League:", l, "with ID:",
                         st.session_state.leagues[l])
            jdata=get_teams()

            st.session_state.teams = jdata

        # Team selection
        if st.session_state.teams and st.session_state.players == {}:
            selected_teams = st.multiselect(
                "Select team",
                list(st.session_state.teams.keys()),
                key="team_select",
                max_selections=st.session_state.mul_sele
            )
            if st.button("Sure!", key="sure_1"):
                st.session_state.opt3 = selected_teams
                for t in st.session_state.opt3:
                    st.write("Confirmed Team:", t, "with ID:",
                             st.session_state.teams[t][0])

                jdata = get_players()

                st.session_state.players = jdata
                st.session_state.selected_players = []

        # Player selection (modified for multiple choices)
        if st.session_state.players:
            selected_players = st.multiselect(  # Changed to multiselect
                "Select 2-4 players",
                list(st.session_state.players.keys()),
                key="select_player",
                default=st.session_state.selected_players,
                max_selections=st.session_state.mul_sele
            )

            if st.button("Confirm Players", key='sure_2'):
                if 2 <= len(selected_players) <= 4:
                    st.session_state.selected_players = selected_players
                    st.session_state.diff_returned = {
                        "league": st.session_state.opt2,
                        "team": st.session_state.opt3,
                        "players": {
                            player: st.session_state.players[player]
                            for player in selected_players
                        }
                    }
                    st.write("Selected players:", st.session_state.selected_players)
                    st.write("Final data:", st.session_state.diff_returned)
                    #for i in st.session_state.diff_returned:
                        #st.write(i,st.session_state.diff_returned[i])
                    get_dataframe()
                else:
                    st.error("Please select between 2 and 4 players")
#main()