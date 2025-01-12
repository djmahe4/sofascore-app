import streamlit as st
import requests,json
from check import get_season_stats,season_comparison,get_season_stats_destruct,season_comparison_destruct
from operations import retry,get_sofascore
import datetime

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
def psearch(name):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,en-IN;q=0.8',
        # 'cookie': '__gpi=UID=00000de55eeafc9b:T=1712677321:RT=1712677321:S=ALNI_Mbzxe_PMDTNBzcRWRn2EjB3ptaQAA; _ga=GA1.1.2076984740.1712677318; _cc_id=7be34bda8ef5c90644fbb00c411b806b; _ga_G0V1WDW9B2=deleted; _hjSessionUser_2585474=eyJpZCI6IjIxZDk5Y2IyLWYzYWItNWU4My04MjZkLTg4ZWQzNTJiNjhiZCIsImNyZWF0ZWQiOjE3MzI0NTQ1NDEwOTgsImV4aXN0aW5nIjp0cnVlfQ==; panoramaId_expiry=1735383329968; panoramaId=804c193543df94bdaf3775cce9894945a702c8a27ba6aba96dc7c0055b26d49c; panoramaIdType=panoIndiv; cto_bundle=6VXOlF9XdHpnQ0lrS0x2VUdmcU93UGZNUWdyWFhzJTJCNkNndXAlMkJXWndpOHI0SEF5NFFpOExtMlZoWUglMkJ6VW1MMzJGMGd3WHhraWpNajNyTm1yRDhpZnBKRDVnaXBsSnl0anF0MWx6QXBiZHZvQ1NXMmhxd1g4YndzelpJNjVoblBZWHlRYXUlMkZHNVI4NXFqbk9FdmxuREFNMFVVdyUzRCUzRA; g_state={"i_p":1737618382846,"i_l":4}; u:location=%7B%22countryCode%22%3A%22IN%22%2C%22ccode3%22%3A%22IND%22%2C%22timezone%22%3A%22Asia%2FCalcutta%22%2C%22ip%22%3A%222406%3A8800%3A9015%3Ac550%3Aeca6%3A44f2%3Affeb%3A2379%22%2C%22regionId%22%3A%22KL%22%2C%22regionName%22%3A%22Kerala%22%7D; _hjSession_2585474=eyJpZCI6Ijk4ZjUzOTBhLTY2ODgtNDQxMy04NWNkLTljNzg5YjliN2NkNCIsImMiOjE3MzUyMDU5NTEzMTgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=; __gads=ID=faa1e9087fd1c078:T=1712677321:RT=1735205957:S=ALNI_Ma6L5CmpnceQeaPqEFWmPNRuYfEgA; __eoi=ID=66fbdc7ff144ff21:T=1729334344:RT=1735205957:S=AA-Afjb4iGP-5-EUcCydc8gEb6xn; FCNEC=%5B%5B%22AKsRol-7wz6Zzh_kziamYUpXqMUFBf9S_ja9qzOGSERxIX9L1XjEQCLwLC0WC5UpJSl1b3ZTYhjLKV5oiqD-FX-vQ4T_6MQoUt3YtyQ5uWRAl5VwMfuFRJ4Fig4pxLFaFrCIQ30ql5GzT73cpm10ULrSlcHjpEZy_g%3D%3D%22%5D%5D; _ga_G0V1WDW9B2=GS1.1.1735205896.6.1.1735206031.0.0.0',
        'if-none-match': '"10gql3603y2al"',
        'priority': 'u=1, i',
        'referer': 'https://www.fotmob.com/',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'x-mas': 'eyJib2R5Ijp7InVybCI6Ii9hcGkvc2VhcmNoL3N1Z2dlc3Q/aGl0cz01MCZsYW5nPWVuJnRlcm09YWRyaWFuK2x1bmEiLCJjb2RlIjoxNzM1MjA2MDU2NDM2LCJmb28iOiJlOTZiNjBhMjEifSwic2lnbmF0dXJlIjoiMURFNENGNDQ2RDVFOEExMjM3RDI2MEYxRUFDQ0NGQzUifQ==',
    }

    params = {
        'hits': '50',
        'lang': 'en',
        'term': f'{name}',
    }

    response = requests.get('https://www.fotmob.com/api/search/suggest', params=params,
                            headers=headers)
    st.write(response.status_code)
    return response.json()[0]['suggestions']['id'],response.json()[0]['suggestions']['id']
def squad_extract(id):
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://www.fotmob.com/teams/8634/overview/barcelona',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'x-mas': 'eyJib2R5Ijp7InVybCI6Ii9hcGkvdGVhbXM/aWQ9ODYzNCZjY29kZTM9SU5EIiwiY29kZSI6MTczNTQ0MjYyMzU3MywiZm9vIjoiZTk2YjYwYTIxIn0sInNpZ25hdHVyZSI6IjNDRDA1Qzg2NEU3N0NDMzJGQTZENjdDRjA4OUFDMzgxIn0=',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
    }

    params = {
        'id': f'{id}',
        'ccode3': f'{st.session_state.ccode3}',
    }

    response = requests.get('https://www.fotmob.com/api/teams', params=params, headers=headers)
    #print(response.json())
    try:
        det=response.json()
    except:
        det=retry('https://www.fotmob.com/api/teams',params)
    players = {}
    for i in det['squad'][1:]:
        for j in i['members']:
            players.update({j['name']: j['id']})
    return players
def season_team_extract(id):
    headers = {
    'sec-ch-ua-platform': '"Windows"',
    'Referer': 'https://www.fotmob.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'x-mas': 'eyJib2R5Ijp7InVybCI6Ii9hcGkvbGVhZ3Vlcz9pZD00MiZjY29kZTM9SU5EJm5ld1VlZmFCcmFja2V0PXRydWUiLCJjb2RlIjoxNzM1NDA2NTQzOTYzLCJmb28iOiJlOTZiNjBhMjEifSwic2lnbmF0dXJlIjoiNTk1MUEwRTIwRDE1NjFFQkE5OTgyRjk2RTdFMTRFNDIifQ==',
    'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    }

    params = {
        'id': f'{id}',
        'ccode3': f'{st.session_state.ccode3}',
         #'newUefaBracket': 'true',
    }
    st.write(params)

    response = requests.get('https://www.fotmob.com/api/leagues', params=params, headers=headers)
    try:
        det=response.json()
    except:
        det=retry('https://www.fotmob.com/api/leagues',params)
    teams={}
    for i in det['table'][0]['data']['table']['all']:
        print(i['name'], i['id'])
        teams.update({i['name']:i['id']})
    return teams
def get_data_destruct():
    st.session_state.opt1 = None
    st.session_state.leagues = {}
    st.session_state.opt2 = None
    st.session_state.choosen = None
    st.session_state.tid = None
    st.session_state.opt3 = None
    st.session_state.teams = {}
    st.session_state.opt4 = None
    st.session_state.players = {}
    st.session_state.returned = {}
    st.session_state.select=False
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
def main():
    global desired
    choice2=st.selectbox("Choose:",["Individual Season Stats","Season Stats Comparison","Player v Player comparison"])
    if st.button("Continue"):
        st.session_state.choice2=choice2
    if st.session_state.choice2=="Individual Season Stats":
        if "pposition" not in st.session_state:
            st.session_state.pposition=None
        if "per90" not in st.session_state:
            st.session_state.per90=False
        if "indivs" not in st.session_state:
            st.session_state.indivs=False
        if 'select' not in st.session_state:
            st.session_state.select=None
        pos=st.selectbox("Choose position to analyse:",list(desired.keys()))
        if st.button("Position"):
            st.session_state.pposition=pos
            st.write(f"Selected position:{st.session_state.pposition}")
        if st.session_state.pposition:
            p9=st.selectbox("Per90?",[True,False])
            if st.button("p90"):
                   st.session_state.per90=p9
                   st.write(f"Per90:{st.session_state.per90}")
                   st.session_state.indivs=True
                   st.session_state.select=True
            st.warning("please click 'Finished1' if u want to change options")
        #st.write(st.session_state)
        #get_data_destruct()
      
        if not st.session_state.returned and st.session_state.select:
            a=get_data("player")
            st.write(a)
        #st.write(st.session_state)
        if st.session_state.returned:
            if st.session_state.indivs:
                print(list(st.session_state.returned.keys())[0],list(st.session_state.returned.values())[0],st.session_state.opt2)
                get_season_stats(list(st.session_state.returned.keys())[0],list(st.session_state.returned.values())[0][0],st.session_state.opt2)
            #get_data_destruct()
        if st.button("Finished1"):
                season_comparison_destruct()
                get_season_stats_destruct()
                get_data_destruct()
        st.write(st.session_state)
    elif st.session_state.choice2=="Season Stats Comparison":
        if "posa" not in st.session_state:
            st.session_state.posa=None
        if "lid" not in st.session_state:
            st.session_state.lid=None
        if "sid" not in st.session_state:
            st.session_state.sid=None
        if "sname" not in st.session_state:
            st.session_state.sname=None
        if st.session_state.opt4:
            get_data_destruct()

        #get_season_stats_destruct()
        if not st.session_state.lid and not st.session_state.posa:
            b=get_data("league")
            st.write(b)
            if b is not None:
                st.session_state.lid=list(b.values())[0][0]
                st.session_state.sid=list(b.values())[0][1]
                st.session_state.sname=list(b.keys())[0]
        st.write(st.session_state)
        posa = st.selectbox("Choose position to analyse:", ['F', 'M', 'D', 'G'])
        if st.button("Position"):
            st.session_state.posa = posa
            st.write(f"Selected position:{st.session_state.posa}")
        #st.write(st.session_state)
        if st.session_state.lid and st.session_state.posa:
            st.warning("please click 'Finished2' if u want to change options")
            season_comparison(st.session_state.lid,st.session_state.sid)
        if st.button("Finished2"):
            get_season_stats_destruct()
            season_comparison_destruct()
            get_data_destruct()
    st.divider()
if __name__ =="__main__":
    main()
