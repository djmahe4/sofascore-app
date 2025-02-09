import time,json
from urllib.parse import urlparse
import http.client
import numpy
import cachetools
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import datetime
import streamlit as st
from operations import get_sofascore
import matplotlib.pyplot as plt
import random
import seaborn as sns
import numpy as np

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

def calc_perc(arr,val):
    return (sum(x <= val for x in arr)/len(arr))*100
def percentile_extraction(position="F",lid=1900,sid=65961):
  teams={}
  url = f"https://www.sofascore.com/api/v1/unique-tournament/{lid}/season/{sid}/standings/total"
  parsed = urlparse(url)
  conn = http.client.HTTPSConnection(parsed.netloc)
  conn.request("GET", parsed.path)
  res = conn.getresponse()
  data = res.read()
  jdata = json.loads(data.decode("utf-8"))
  for i in jdata['standings'][0]['rows']:
    teams.update({f"{i['team']['name']}":i['team']['id']})
  players={}
  for i in teams:
    url = f"https://www.sofascore.com/api/v1/team/{teams[i]}/players"
    parsed = urlparse(url)
    conn = http.client.HTTPSConnection(parsed.netloc)
    conn.request("GET", parsed.path)
    res = conn.getresponse()
    data = res.read()
    jdata = json.loads(data.decode("utf-8"))
    for i in jdata['players']:
      try:
        if i['player']['position']==position:
            players.update({i['player']['name']:i['player']['id']})
      except:
          continue
  big_data={'names':list(players.keys())}
  for j in players:
    with st.spinner(f"Geting stats for {j}"):
        url = f"https://www.sofascore.com/api/v1/player/{players[j]}/unique-tournament/{lid}/season/{sid}/statistics/overall"
        parsed = urlparse(url)
        conn = http.client.HTTPSConnection(parsed.netloc)
        conn.request("GET", parsed.path)
        res = conn.getresponse()
        data = res.read()
        jdata = json.loads(data.decode("utf-8"))
        # Initialize a flag to check if we need to append 0
        append_zero = False

        try:
            a = jdata['statistics']
            if a['minutesPlayed'] == 0:
                append_zero = True
        except KeyError:
            append_zero = True

        # Append 0 to all keys except 'names' if needed
        if append_zero:
            for c in list(big_data.keys()):
                if c != 'names':
                    big_data[c].append(0)
            continue

        #print(list(jdata['statistics'].keys()))
        for i in a:
            if i not in big_data:
                big_data[i] = []
            big_data[i].append(jdata['statistics'][i])
    time.sleep(0.1)
  return big_data

def advanced_extraction(name,comp,pos,lid,sid):
    big_data=percentile_extraction(pos,lid,sid)
    big_data.pop('type')
    # print(big_data)
    new_rec = {}
    dper90 = per90_calc(big_data)
    print(dper90)
    #name = 'Jamie MacLaren'
    for k in dper90['names']:
        if name == k:
            ind = dper90['names'].index(k)
            print(ind)
    for i in big_data:
        if i == "type":
            continue
        # new_rec.update({i:{"title":i,'items':{}}})
        # items=new_rec[i]['items']
        items = {}
        if i in comp:
            items.update({'statValue': comp[i]})
            items.update({'percentileRank': calc_perc(big_data[i], comp[i])})

            if "Percentage" not in i:
                items.update({'per90': dper90[i][ind]})
                items.update({'percentileRankPer90': calc_perc(dper90[i], dper90[i][ind])})
            else:
                items.update({'per90': comp[i]})
                items.update({'percentileRankPer90': calc_perc(big_data[i], comp[i])})
            new_rec.update({i: {"title": i, 'items': items}})
    print(new_rec)
    return new_rec
def get_season_stats_destruct():
    st.session_state.pposition=None
    st.session_state.per90=False
def get_sofascore(url):
    parsed = urlparse(url)
    conn = http.client.HTTPSConnection(parsed.netloc)
    conn.request("GET", parsed.path)
    res = conn.getresponse()
    data = res.read()
    jdata = json.loads(data.decode("utf-8"))
    return jdata
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
    #new_plot_funct(b,desired,name,season)
def get_data(type): # player, season, team
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://www.fotmob.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'x-mas': 'eyJib2R5Ijp7InVybCI6Ii9hcGkvYWxsTGVhZ3Vlcz9sb2NhbGU9ZW4mY291bnRyeT1JTkQiLCJjb2RlIjoxNzM1MjE1OTA2NzI2LCJmb28iOiJlOTZiNjBhMjEifSwic2lnbmF0dXJlIjoiNjJBNjFEODA1MzVDMUI0N0EwMjAxRERENUI0NTBGNjAifQ==',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
    }

    params = {
        'locale': 'en',
        #'country': st.session_state.get('ccode3', ''),
    }

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
        st.session_state.tid=None
    if 'opt3' not in st.session_state:
        st.session_state.opt3 = None
    if 'teams' not in st.session_state:
        st.session_state.teams = {}
    if 'opt4' not in st.session_state:
        st.session_state.opt4 = None
    if 'players' not in st.session_state:
        st.session_state.players = {}
    if 'returned' not in st.session_state:
        st.session_state.returned ={}

    # Select league nation if opt1 is None
    leagues={}
    if st.session_state.opt1 is None and st.session_state.leagues =={}:
        date = datetime.date.today().strftime("%Y-%m-%d")
        jdata=get_sofascore(f"https://www.sofascore.com/api/v1/sport/football/scheduled-events/{date}")
        for i in jdata['events']:
            if i['tournament']['uniqueTournament']['name'] not in leagues:
                leagues.update({i['tournament']['uniqueTournament']['name']: [i['tournament']['uniqueTournament']['id'],
                                                                              i['season']['id']]})
        st.session_state.leagues = leagues
        st.session_state.opt2=None

    # Display league selection if leagues are available
    if st.session_state.leagues and st.session_state.opt2 is None:
        # Select league from available leagues
        selected_league = st.selectbox("Select league", list(st.session_state.leagues.keys()),key="League_select",
                                       index=list(st.session_state.leagues.keys()).index(
                                           st.session_state.opt2) if st.session_state.opt2 else 0)

        # Confirm selection
        if st.button("Confirm"):
            # Store the selected league in session state
            st.session_state.opt2 = selected_league

            # Display confirmation message
            st.write("You have selected:", st.session_state.opt2)
            st.session_state.teams={}
            if type == "league":
                st.session_state.returned = {st.session_state.opt2: st.session_state.leagues[st.session_state.opt2]}
                # return st.session_state.opt2,st.session_state.leagues[st.session_state.opt2]
                return st.session_state.returned
            #st.write("Current session state:", st.session_state)
    teams={}
    # Final display of selected league or prompt
    if st.session_state.opt2 and st.session_state.teams=={}:
        #st.session_state.leagues={}
        st.write("Confirmed League:", st.session_state.opt2, "with ID:",
                 st.session_state.leagues[st.session_state.opt2])
        #teams=season_team_extract(st.session_state.leagues[st.session_state.opt2])
        tid=st.session_state.leagues[st.session_state.opt2][0]
        sid=st.session_state.leagues[st.session_state.opt2][1]
        url = f"https://www.sofascore.com/api/v1/unique-tournament/{tid}/season/{sid}/standings/total"
        jdata=get_sofascore(url)
        for i in jdata['standings'][0]['rows']:
            teams.update({f"{i['team']['name']}": i['team']['id']})
        st.session_state.teams = teams
        st.session_state.players={}

        # Display league selection if leagues are available
    players={}
    if st.session_state.teams and st.session_state.players=={}:
        #st.session_state.leagues={}
        #st.session_state.opt2=None
            # Select league from available leagues
        selected_team = st.selectbox("Select team", list(st.session_state.teams.keys()),key="team_select",
                                           index=list(st.session_state.teams.keys()).index(
                                               st.session_state.opt3) if st.session_state.opt3 else 0)

            # Confirm selection
        if st.button("Sure!",key="sure_1"):
                # Store the selected league in session state
            st.session_state.opt3 = selected_team

                # Display confirmation message
            st.write("Selected team:", st.session_state.opt3,"with tid",st.session_state.teams[st.session_state.opt3])
            if type == "team":
                st.session_state.returned={st.session_state.opt3: st.session_state.teams[st.session_state.opt3]}
                #return st.session_state.opt3, st.session_state.teams[st.session_state.opt3]
                return st.session_state.returned
            tid = st.session_state.teams[st.session_state.opt3]
            url = f"https://www.sofascore.com/api/v1/team/{tid}/players"
            jdata = get_sofascore(url)
            for i in jdata['players']:
                players.update({i['player']['name']: [i['player']['id'], i['player']['position']]})
            st.session_state.players=players
            st.session_state.opt4=None
    if st.session_state.players and st.session_state.opt4 is None:
        #st.session_state.teams={}
        #st.session_state.opt3=None
            # Select league from available leagues
        selected_player = st.selectbox("Select player", list(st.session_state.players.keys()),key="select_player",
                                           index=list(st.session_state.players.keys()).index(
                                               st.session_state.opt4) if st.session_state.opt4 else 0)

            # Confirm selection
        if st.button("Sure!",key='sure_2'):
                # Store the selected league in session state
            st.session_state.opt4 = selected_player

                # Display confirmation message
            st.write("Selected player:", st.session_state.opt4,"with pid",st.session_state.players[st.session_state.opt4])
            if type == "player":
                st.session_state.returned={st.session_state.opt4: st.session_state.players[st.session_state.opt4]}
                #return st.session_state.opt4, st.session_state.players[st.session_state.opt4],st.session_state.opt2,st.session_state.leagues[st.session_state.opt2]
                return st.session_state.returned
            #st.session_state.players=squad_extract(st.session_state.teams[st.session_state.opt3])

def multi_get():
    if "pposition" not in st.session_state:
        st.session_state.pposition = None
    if "per90" not in st.session_state:
        st.session_state.per90 = False
    if "indivs" not in st.session_state:
        st.session_state.indivs = False
    if 'select' not in st.session_state:
        st.session_state.select = None
    pos = st.selectbox("Choose position to analyse:", list(desired.keys()))
    if st.button("Position"):
        st.session_state.pposition = pos
        st.write(f"Selected position:{st.session_state.pposition}")
    if st.session_state.pposition:
        p9 = st.selectbox("Per90?", [True, False])
        if st.button("p90"):
            st.session_state.per90 = p9
            st.write(f"Per90:{st.session_state.per90}")
            st.session_state.indivs = True
            st.session_state.select = True
        st.warning("please click 'Finished1' if u want to change options")
    # st.write(st.session_state)
    # get_data_destruct()

    if not st.session_state.returned and st.session_state.select:
        a = get_data("player")
        st.write(a)
    # st.write(st.session_state)
    if st.session_state.returned:
        if st.session_state.indivs:
            print(list(st.session_state.returned.keys())[0], list(st.session_state.returned.values())[0],
                  st.session_state.opt2)
            get_season_stats(list(st.session_state.returned.keys())[0], list(st.session_state.returned.values())[0][0],
                             st.session_state.opt2)