import requests
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import seaborn as sns
import time
from operations import retry,get_sofascore
from test import advanced_extraction,season_final
def new_plot_funct(b,desired,name,season):
    #present=[]
    necessary=[]
    for i in b:
        #print(b[i]['title'])
        #for items in b[i]:
            #present.append(items)
            #st.write(items['title'],st.session_state.pposition)
        if b[i]["title"] in desired[st.session_state.pposition]:
                #necessary.append(items)
                #print(items["title"])
            necessary.append({'title':b[i]['title'],**b[i]['items']})
    print(necessary)
    #print(present)
        #if p9!=st.session_state.per90:
            #st.session_state.per90=p9
        #p9 = input("Per 90 stats (y/n):")
        #p9=st.selectbox("Per90?",[True,False])
        #st.session_state.per90=p9
        #if st.button("Done.."):
            #st.session_state.per90=p9
        #else:
            #st.session_state.per90=p9
    if st.session_state.pposition:
            # Convert the data into a pandas DataFrame
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        df = pd.DataFrame(necessary)
            # Convert 'statValue' to numeric
        df['statValue'] = pd.to_numeric(df['statValue'])
        df['per90'] = pd.to_numeric(df['per90'])
        df['percentileRankPer90'] = pd.to_numeric(df['percentileRankPer90'])
        df['percentileRank'] = pd.to_numeric(df['percentileRank'])
            # Assuming 'df' is your DataFrame
        #df.drop(columns=['localizedTitleId', 'statFormat'], inplace=True)
        rdf = df
        print(rdf)
        st.dataframe(rdf)
            # Create a color palette
        palette = sns.color_palette("bright", len(df))
            # Create the bar plot
        plt.figure(figsize=(20, 10))
        if st.session_state.per90:
            bar_plot = sns.barplot(x='title', y='percentileRankPer90', data=df, palette=palette)
                # Display the 'per90' above the bars
            for i, row in df.iterrows():
                bar_plot.text(i, row.percentileRankPer90 + 0.5, round(row.per90, 2), color='black', ha="center")
        else:
            bar_plot = sns.barplot(x='title', y='percentileRank', data=df, palette=palette)
                # Display the 'statValue' above the bars
            for i, row in df.iterrows():
                bar_plot.text(i, row.percentileRank + 0.5, round(row.statValue, 2), color='black', ha="center")
        
        plt.axhline(50, color='red', linestyle='dashed')
        
            # Rotate x-axis labels for better visibility
            # plt.xticks(rotation=90, fontsize=10)
        
            # Set plot title and labels
            #name = input("Enter player name:")
            # tname=input("Enter season:")
        plt.title(f'Season Stats of {name.title()} in {season}', fontsize=20, color=random.choice(palette))
        plt.xlabel('Stats', fontsize=15, color='green')
        plt.ylabel('Percentile ranking', fontsize=15, color='red')
            # Add an annotation
        plt.annotate('@DJMahe04', xy=(0.1, 0.1), xycoords='axes fraction',  # Position in axes coordinates
                fontsize=12, ha='left', va='bottom', alpha=0.4)
            # Adjust the subplot parameters to give the x-axis labels more space
        plt.subplots_adjust(bottom=0.4)
        st.pyplot(plt)
def get_season_stats_destruct():
    st.session_state.pposition=None
    st.session_state.per90=False
def get_season_stats(name,id=1083323,season="LaLiga"):
    if "pposition" not in st.session_state:
        st.session_state.pposition=None
    if "per90" not in st.session_state:
        st.session_state.per90=False
    #if 'player_analysis' not in st.session_state:
        #st.session_state.player_analysis=False
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
    lid, sid = st.session_state.leagues[st.session_state.opt2]
    pos=list(st.session_state.returned.values())[0][1]
    url = f"https://www.sofascore.com/api/v1/player/{id}/unique-tournament/{lid}/season/{sid}/statistics/overall"
    jdata = get_sofascore(url)['statistics']
    b=advanced_extraction(name,jdata,pos,lid,sid)
    new_plot_funct(b,desired,name,season)
    #return
def season_comparison_destruct():
    st.session_state.atype1 = None
    st.session_state.atype2 = None
    st.session_state.pposition=None
    st.session_state.per90=None
    st.session_state.posa=None
def season_comparison(lid,sid):
    if "atype1" not in st.session_state:
        st.session_state.atype1=None
    if "atype2" not in st.session_state:
        st.session_state.atype2=None

    comp = {
        "goals per 90": "assists",
        "totalShots": "goals per 90",
        "bigChancesCreated": "assists",
        "successfulDribbles per 90": "goalsAssistsSum",
        "cleanSheet": "saves",
        "interceptions per 90": 'possessionWonAttThird',
        "goals per 90": "shotsFromInsideTheBox per 90",
        "shotsOnTarget per 90": "goals per 90",
        "totalShots per 90": "shotsFromOutsideTheBox",
        "accuratePasses per 90": "assists",
        "bigChancesMissed": "goals per 90",
        "penaltyWon": "goals per 90",
        # "Successful tackles per 90": "Interceptions per 90",
        "clearances per 90": "blockedShots per 90",
        "cleanSheet": "goalsConceded per 90",
        "redCards":"fouls per 90",
        # "Expected goals (xG)": "Assists",
        "accurateLongBalls per 90": "assists",
         "assists":"keyPasses",
        "goalsAssistsSum per 90": "goalsAssistsSum",
        # "Successful dribbles per 90": "Chances created",
         "clearances per 90":"tacklesWon per 90",
         "saves": "savedShotsFromInsideTheBox",
        # "Fouls committed per 90": "Yellow cards",
         "goals per 90":"possessionWonAttThird per 90"
    }
    comments = [
        "Analyzes the relationship between scoring and assisting.",
        "Compares shots with actual goals scored.",
        "Understands how creating chances translates to assists.",
        "Analyzes the impact of dribbling on direct goal contributions.",
        "Evaluates the goalkeeper's performance.",
        "Assesses defensive effectiveness in the final third.",
        "Evaluates the efficiency of a player in scoring compared to shots inside the box.",
        "Sees how shots on target correlate with actual goals scored.",
        "Analyzes the quality of shots taken.",
        "Determines the impact of passing accuracy on creating goal opportunities.",
        "Understands the impact of missed opportunities on a player's goal tally.",
        "Assesses the contribution of penalties won to the total number of goals.",
        # "Compares defensive actions and their frequency.",
        "Evaluates different aspects of defensive play.",
        "Observes the relationship between the frequency of conceding goals and keeping clean sheets.",
        "Explores the severity of fouls and their consequences.",
        # "Explores the relationship between xG and assists.",
        "Analyzes the impact of accurate long balls on assists.",
        "Assesses the contribution of xA to assists.",
        "Evaluates the efficiency of xG and xA combined.",
        # "Analyzes the impact of successful dribbles on creating chances.",
        "Assesses defensive contributions to preventing goals.",
        "Evaluates the goalkeeper's impact on preventing goals.",
        # "Explores disciplinary actions related to fouls.",
        "Explores the impact of winning possession in the final third on scoring."
    ]
    keyvals=[x+" vs "+comp[x] for x in comp]
    if st.session_state.atype1 is None:
        atype=st.radio("Select analysis type",keyvals,captions=comments)
        if st.button("Analysis selected!"):
            st.session_state.atype1=atype.split(" vs ")[0]
            st.session_state.atype2 = atype.split(" vs ")[1]
            stat1=st.session_state.atype1
            stat2=st.session_state.atype2
            data1_dict,data2_dict=season_final(stat1,stat2,lid,sid)
            # Get all players
            # all_players = set(list(data1_dict.keys()) + list(data2_dict.keys()))

            # Prepare the data for scatter plot
            players = []
            # stat1_values = []
            # stat2_values = []
            # Get the intersection of the two sets of players
            common_players = list(set(list(data1_dict.keys())) & set(list(data2_dict.keys())))

            # Filter the data to include only the common players
            stat1_values = [data1_dict[player] for player in common_players]
            stat2_values = [data2_dict[player] for player in common_players]

            # Create a DataFrame from the data
            df = pd.DataFrame({
                'Player': common_players,
                stat1: stat1_values,
                stat2: stat2_values
            })
            # Sort the DataFrame by stat1 and get the top 5 players
            top5_stat1 = df.sort_values(by=stat1, ascending=False).head(5)

            # Sort the DataFrame by stat2 and get the top 5 players
            top5_stat2 = df.sort_values(by=stat2, ascending=False).head(5)

            # Concatenate the two dataframes
            top5_both = pd.concat([top5_stat1, top5_stat2])

            # Remove duplicates
            top5_both = top5_both.drop_duplicates()

            # Reset index
            top5_both = top5_both.reset_index(drop=True)
            print(top5_both)
            st.dataframe(top5_both)
            #tname = input("Enter league name:")
            # feedback = f"This a dataframe: {top5_both} ;it contains season wise comparison of {stat1} vs {stat2}. Make a twitter thread analysing both the stats (of current season), both critical and optimistic and human type."

            palette = sns.color_palette("bright", 3)
            color1, color2, color3 = random.sample(palette, 3)
            # Create the scatterplot with seaborn
            plt.figure(figsize=(10, 6))
            sns.scatterplot(data=df, x=stat1, y=stat2, palette='hls')  # hls
            sns.set_style("whitegrid")
            plt.title(f'{st.session_state.sname} {stat1} vs {stat2}', fontsize=14, color=color1)
            # Add an annotation
            plt.annotate('@DJMahe04', xy=(0.1, 0.1), xycoords='axes fraction',  # Position in axes coordinates
            fontsize=12, ha='left', va='bottom', alpha=0.4)
            plt.xlabel(stat1, fontsize=12, color=color2)
            plt.ylabel(stat2, fontsize=12, color=color3)
            for i, player in enumerate(common_players):
                plt.annotate(player, (stat1_values[i], stat2_values[i]))
            # Avoid overlapping
            plt.tight_layout()
            st.pyplot(plt)
