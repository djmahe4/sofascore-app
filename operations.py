import json
import matplotlib.pyplot as plt
import random
import seaborn as sns
import os
import requests
import numpy as np
import shutil
import datetime
from urllib.parse import urlparse,urlencode
import http.client
import http.cookiejar
from num_fotmob import extraction
import streamlit as st
from urllib.parse import urlparse
import http.client
@st.cache_resource
def conn_make():
    if 'conn' not in st.session_state:
        url = f"https://www.sofascore.com/api/v1/event/12527965"
        parsed = urlparse(url)
        conn = http.client.HTTPSConnection(parsed.netloc)
        st.session_state.conn=conn


positions={2:"Midfielder",3:"Forward",1:"Defender",0:"Goalkeeper"}

def get_sofascore(url):
    parsed = urlparse(url)
    conn = http.client.HTTPSConnection(parsed.netloc)
    conn.request("GET", parsed.path)
    res = conn.getresponse()
    data = res.read()
    jdata = json.loads(data.decode("utf-8"))
    return jdata
def retry(url,params):
    headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'priority': 'u=1, i',
    'referer': 'https://www.fotmob.com/',
    'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'x-mas': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySWQiOiI2NzgxZWQ3MWExNDdhZWI0ODYxNmNiYWIiLCJuYmYiOjE3MzY1NjgxNzcsImV4cCI6MTczOTE5NjE3NywiaWF0IjoxNzM2NTY4MTc3LCJpc3MiOiJXU0MifQ.BFQtbgESVzCWc002Hk_kPvuv4u3y_c7-vEDibACoVoA=',
    }
    try:
        return requests.get(url,params=params,headers=headers).json()
    except:
        return url_extract(params,url)
def url_extract(params={"id":"42","ccode3":"USA_OR"},uri="https://www.fotmob.com/api/leagues"):
    # Create a cookie jar to store cookies 
    #cookie_jar = http.cookiejar.CookieJar() # Define the opener to handle cookies 
    #opener =urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    params = urlencode(params)
    url = f'{uri}?{params}'
# Create a request object
    conn = http.client.HTTPSConnection('www.fotmob.com')
    headers = {
    'sec-ch-ua-platform': '"Windows"',
    'Referer': 'https://www.fotmob.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'x-mas': 'eyJib2R5Ijp7InVybCI6Ii9hcGkvbGVhZ3Vlcz9pZD00MiZjY29kZTM9SU5EJm5ld1VlZmFCcmFja2V0PXRydWUiLCJjb2RlIjoxNzM2MDUzNDQzNDc0LCJmb28iOiJhODBhZDM3NjMifSwic2lnbmF0dXJlIjoiMzhGOEE3NjJBQTIzN0M2MUNBRjcxMkEyNUY4NUI2NEMifQ==',
    'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
}
    conn.request('GET', url.split('www.fotmob.com')[-1], headers=headers)
    response = conn.getresponse()
    data=json.loads(response.read().decode('utf-8'))
    return data

def performance(id,vs):
    headers = {
            'sec-ch-ua-platform': '"Windows"',
            'Referer': 'https://www.fotmob.com/players/1083323/pedri',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
            'x-mas': 'eyJib2R5Ijp7InVybCI6Ii9hcGkvcGxheWVyU3RhdHM/cGxheWVySWQ9MTA4MzMyMyZzZWFzb25JZD0wLTEmaXNGaXJzdFNlYXNvbj1mYWxzZSIsImNvZGUiOjE3MzU0NDg2MjI1NDIsImZvbyI6ImU5NmI2MGEyMSJ9LCJzaWduYXR1cmUiOiIzM0FENzdFNzI5NTk2OTVBRDFGRERFM0JEQjMxQkFFOCJ9',
            'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
    }
    params={'id':id}
    response=requests.get(f"https://www.fotmob.com/api/playerData",headers=headers)
    try:
        recent=json.loads(response.text)['recentMatches']
    except:
        recent=retry(f"https://www.fotmob.com/api/playerData",params)['recentMatches']
    #recent=response.json()['recentMatches']
    total=0
    matches=0
    for i in recent:
        if recent.index(i)<5:
            total += float(i['ratingProps']['num']) * 0.9
            matches += 1
        if i['opponentTeamName']==vs and float(i['ratingProps']['num'])!=0:
            total+=float(i['ratingProps']['num'])
            matches+=1
    try:
        return total/matches
    except ZeroDivisionError:
        return 0

def match_id_init():
    conn_make()
    # requests.get("https://www.fotmob.com/matches")
    # global st

    z = datetime.date.today().strftime("%Y-%m-%d")

    url = f"https://www.sofascore.com/api/v1/sport/football/scheduled-events/{z}"
    b = []
    a = get_sofascore(url)['events']
    lid=None
    for i in a:
        if lid!=i['tournament']['uniqueTournament']['id']:
            lid=i['tournament']['uniqueTournament']['id']
            b.append({lid:[{i['season']['id']:[]}]})
        #else:
        result = next((list(entry.values())[0] for entry in b if lid in entry), None)
        if result is not None:  # Check if result is not None before proceeding
            inner_dict = result[0]  # access the inner dictionary
            inner_key = list(inner_dict.keys())[0]  # get the key of the inner dictionary
            try:
                inner_dict[inner_key].append({i['id']: [[i['homeTeam']['name'], i['awayTeam']['name']],
                                                        [i['homeScore']['current'], i['awayScore']['current']]]})
            except:
                inner_dict[inner_key].append({i['id']: [[i['homeTeam']['name'], i['awayTeam']['name']]]})
        else:
            print(f"No entry found for lid: {lid}")
        #newl = [entry[lid] if lid in entry else None for entry in b]  # append None if key is not found
    with open("leagues.json", 'w') as file:
        # obj=json.load(open("leagues.json"))
        # obj["date"]=date.today()
        json.dump(b, file, indent=2)
    return b

def analyze_player_stats(stats,name,st):
    analysis = f"**{name}:**\n"
    # x=stats["Player"].index(i)
    isgoalie = False

    # Positive aspects
    analysis += "\n+ves:\n"
    if 'expected_goals_on_target_faced' in stats and stats['expected_goals_on_target_faced'] < 0.5 and stats[
        'expected_goals_on_target_faced'] != 0:  # Adjust this threshold based on your criteria
        analysis += f"- Expected to face few on-target shots ({stats['expected_goals_on_target_faced']} xGOTF)\n"
        isgoalie = True

        if 'saves' in stats and stats['saves'] >= 5:
            analysis += f"- Had Saves: {stats['saves']}\n"
        if 'expected_goals_on_target_faced' in stats and stats[
            'expected_goals_on_target_faced'] > 0.3:  # Adjust this threshold based on your criteria
            analysis += f"- Expected to face on-target shots ({stats['expected_goals_on_target_faced']} xGOT)\n"
        if 'goals_prevented' in stats and stats['goals_prevented'] > 0:  # Adjust this threshold based on your criteria
            analysis += f"- Prevented {stats['goals_prevented']} goals\n"
        if 'accurate_passes' in stats and stats['accurate_passes'] > 20:
            analysis += f"- Had Good accurate passing ({stats['accurate_passes']} passes )\n"
        if 'recoveries' in stats and stats['recoveries'] >= 4:  # Adjust this threshold based on your criteria
            analysis += f"- Made {stats['recoveries']} recoveries\n"
        analysis += "\n-ves:\n"
        if 'minutes_played' in stats and stats['minutes_played'] <= 45:
            analysis += f"- Had Less game time ({stats['minutes_played']} minutes played)\n"
        if 'accurate_passes' in stats and stats['accurate_passes'] < 8:
            analysis += f"- Less accurate passes:({stats['accurate_passes']} )\n"
        if 'recoveries' in stats and stats['recoveries'] < 4:  # Adjust this threshold based on your criteria
            analysis += f"- Made insufficient ball recoveries ({stats['recoveries']} recoveries)\n"
        if 'goals_prevented' in stats and stats['goals_prevented'] < 0:  # Adjust this threshold based on your criteria
            analysis += f"- Prevented {stats['goals_prevented']} goals\n"
        if 'goals_conceded' in stats and stats['goals_conceded'] > 0:
            analysis += f"- Conceeded {stats['goals_conceded']} goals\n"
        analysis += "\nOverall Influence:\n"
        if ('rating_title' in stats and stats['rating_title'] > 7.0 and
                ('saves' in stats and stats['saves'] > 10 or
                 'goals_prevented' in stats and stats['goals_prevented'] > 2 or
                 'long_balls_accurate' in stats and stats['long_balls_accurate'] > 7 or
                 'touches_opp_box' in stats and stats['touches_opp_box'] > 5 or
                 'recoveries' in stats and stats['recoveries'] > 10)):
            # analysis += "- Significant overall influence on the game\n"

            analysis += "- Overall, a highly influential performance on the pitch\n\n"
        elif 'rating_title' in stats and stats['rating_title'] < 6.0:
            analysis += "- Needs improvement\n\n"
        else:
            analysis += "- A performance with both positive and negative aspects\n\n"
        st.write(analysis)
        return
    # if stats['rating_title'] > 7.0:
    # analysis += "- Impressive overall performance.\n"
    if 'chances_created' in stats and stats['chances_created'] > 0:
        analysis += f"- Created {stats['chances_created']} chances\n"
    if 'expected_goals' in stats and stats[
        'expected_goals'] > 0.5:  # Adjust this threshold based on your criteria
        analysis += f"- Expected to score goals ({stats['expected_goals']} xG)\n"
    if 'expected_goals_on_target_variant' in stats and stats[
        'expected_goals_on_target_variant'] > 0.5:  # Adjust this threshold based on your criteria
        analysis += f"- Expected to score goals on target ({stats['expected_goals']} xGOT)\n"
    if 'goals' in stats and stats['goals'] > 0:
        analysis += f"- {stats['goals']} goals\n"
    if 'assists' in stats and stats['assists'] > 0:
        analysis += f"- {stats['assists']} assists\n"
    if 'passes_into_final_third' in stats and stats['passes_into_final_third'] >= 6:  # Adjust this threshold based on your criteria
        analysis += f"- Successfully passed into the final third ({stats['passes_into_final_third']} times)\n"
    if 'xG Non-penalty' in stats and stats["xG Non-penalty"] > 0.2:  # Adjust this threshold based on your criteria
        analysis += f"- Was Dangerous infront of goal ({stats['xG Non-penalty']} xGNP)\n"
    if 'expected_assists' in stats and stats[
        'expected_assists'] > 0.2:  # Adjust this threshold based on your criteria
        analysis += f"- Expected to provide assists ({stats['expected_assists']} xA)\n"
    # ... add more positive aspects based on specific stats
    if 'accurate_crosses' in stats and stats['accurate_crosses'] > 3:  # Adjust this threshold based on your criteria
        analysis += f"- Successfully delivered accurate crosses ({stats['accurate_crosses']})\n"
    if 'duel_won' in stats and stats['duel_won'] >= 5:  # Adjust this threshold based on your criteria
        analysis += f"- Duels Won {stats['duel_won']}\n"
    if 'recoveries' in stats and stats['recoveries'] >= 4:  # Adjust this threshold based on your criteria
        analysis += f"- Made {stats['recoveries']} recoveries\n"
    if 'dribbles_succeeded' in stats and stats['dribbles_succeeded'] >= 5:  # Adjust this threshold based on your criteria
        analysis += f"- Successfully completed {stats['dribbles_succeeded']} of dribbles attempted\n"
    if 'was_fouled' in stats and stats['was_fouled'] >= 4:  # Adjust this threshold based on your criteria
        analysis += f"- Was fouled {stats['was_fouled']} times, drawing fouls\n"
    if 'blocked_shots' in stats and stats['blocked_shots'] > 0:  # Adjust this threshold based on your criteria
        analysis += f"- Blocked {stats['blocked_shots']} shots\n"
    if 'tackles_succeeded' in stats and stats['tackles_succeeded'] > 5:
        analysis += f"- Tackles successful : {stats['tackles_succeeded']}\n"
    if 'touches' in stats and stats['touches'] > 48:  # Adjust this threshold based on your criteria
        analysis += f"- Had {stats['touches']} touches, indicating active involvement in the game\n"
    if 'clearances' in stats and stats['clearances'] > 0:  # Adjust this threshold based on your criteria
        analysis += f"- Made {stats['clearances']} clearances\n"
    if 'accurate_passes' in stats and stats['accurate_passes'] > 20:
        analysis += f"- Had Good accurate passing ({stats['accurate_passes']} passes )\n"
    if 'defensive_actions' in stats and stats['defensive_actions'] > 0:  # Adjust this threshold based on your criteria
        analysis += f"- Had {stats['defensive_actions']} defensive action(s) during the game\n"
    if 'duel_lost' in stats and stats['duel_lost'] == 0:  # Adjust this threshold based on your criteria
        analysis += f"- Lost {stats['duel_lost']} duels\n"
    if 'ground_duels_won' in stats and stats['ground_duels_won'] > 5:  # Adjust this threshold based on your criteria
        analysis += f"- Won {stats['ground_duels_won']} ground duels\n"
    if 'shot_accuracy' in stats and stats['shot_accuracy'] > 0:
        analysis += f"- Accurate shots: {stats['shot_accuracy']}\n"
    if 'touches_opp_box' in stats and stats['touches_opp_box'] >= 5:  # Adjust this threshold based on your criteria
        analysis += f"- Had {stats['touches_opp_box']} touches in the opponent's box\n"
    if 'interceptions' in stats and stats['interceptions'] > 0:  # Adjust this threshold based on your criteria
        analysis += f"- Made {stats['interceptions']} interceptions\n"
    if 'aerials_won' in stats and stats['aerials_won'] > 5:  # Adjust this threshold based on your criteria
        analysis += f"- Aeriels won {stats['aerials_won']}\n"
    if 'long_balls_accurate' in stats and stats['long_balls_accurate'] > 6 and stats[
        'long_balls_accurate'] != 0:  # Adjust this threshold based on your criteria
        analysis += f"- Successful in playing accurate long balls ({stats['long_balls_accurate']} accuracy)\n"
    if 'long_balls_accurate'in stats and stats['long_balls_accurate'] < 4 and stats[
        'long_balls_accurate'] != 0:  # Adjust this threshold based on your criteria
        analysis += f"- Ineffective in playing accurate long balls: ({stats['long_balls_accurate']})\n"

    # Negative aspects
    analysis += "\n-ves:\n"
    if 'expected_goals_on_target_faced' in stats and stats['expected_goals_on_target_faced'] > 0.5 and stats[
        'expected_goals_on_target_faced'] != 0:  # Adjust this threshold based on your criteria
        analysis += f"- Expected to face high on-target shots ({stats['expected_goals_on_target_faced']} xGOTF)\n"
        isgoalie = True
    if 'rating_title' in stats and stats['rating_title'] < 6.0:
        analysis += "- Poor performance.\n"
    if 'minutes_played'in stats and stats['minutes_played'] <= 45:
        analysis += f"- Had Less game time ({stats['minutes_played']} minutes played)\n"
    if 'accurate_passes' in stats and stats['accurate_passes'] < 8:
        analysis += f"- Less accurate passes:({stats['accurate_passes']} )\n"
    # ... add more negative aspects based on specific stats
    if 'expected_goals' in stats and stats['expected_goals'] < 0.1 and stats[
        'expected_goals'] != 0:  # Adjust this threshold based on your criteria
        analysis += f"- Failed to generate significant goal-scoring opportunities ({stats['expected_goals']} xG)\n"
    if isgoalie==False and 'accurate_crosses' in stats and stats['accurate_crosses'] < 3 and stats[
        'accurate_crosses'] != 0:  # Adjust this threshold based on your criteria
        analysis += f"- Crosses were not accurate enough ({stats['accurate_crosses']})\n"
    if 'long_balls_accurate'in stats and stats['long_balls_accurate'] < 4 and stats[
        'long_balls_accurate'] != 0:  # Adjust this threshold based on your criteria
        analysis += f"- Ineffective in playing accurate long balls: ({stats['long_balls_accurate']})\n"
    if 'recoveries'in stats and stats['recoveries'] < 4:  # Adjust this threshold based on your criteria
        analysis += f"- Made insufficient ball recoveries ({stats['recoveries']} recoveries)\n"
    if 'dribbles_succeeded' in stats and stats['dribbles_succeeded'] < 3 and stats[
        'dribbles_succeeded'] != 0:  # Adjust this threshold based on your criteria
        analysis += f"- completed a low number of dribbles ({stats['dribbles_succeeded']})\n"
    if 'touches' in stats and stats['touches'] < 25:  # Adjust this threshold based on your criteria
        analysis += f"- Had {stats['touches']} touches, indicating less involvement in buildups\n"
    if 'dispossessed' in stats and stats['dispossessed'] > 0:  # Adjust this threshold based on your criteria
        analysis += f"- Was Dispossessed {stats['dispossessed']} times\n"
    if 'fouls' in stats and stats['fouls'] > 1:  # Adjust this threshold based on your criteria
        analysis += f"- Committed fouls {stats['fouls']} times\n"
    if isgoalie == False and 'defensive_actions' in stats and stats['defensive_actions'] == 0:  # Adjust this threshold based on your criteria
        analysis += f"- Was not active in any defensive action during the game\n"
    if 'duel_lost' in stats and stats['duel_lost'] > 4:  # Adjust this threshold based on your criteria
        analysis += f"- Lost {stats['duel_lost']} duels\n"
    if isgoalie == False and 'ground_duels_won' in stats and stats['ground_duels_won'] < 5 :  # Adjust this threshold based on your criteria
        analysis += f"- Won only {stats['ground_duels_won']} ground duels\n"
    if 'big_chance_missed_title' in stats and stats['big_chance_missed_title'] > 0:
        analysis += f"- Missed {stats['big_chance_missed_title']} big chances\n"
    if 'Offsides' in stats and stats['Offsides'] > 0:  # Adjust this threshold based on your criteria
        analysis += f"- Caught offside {stats['Offsides']} times\n"
    if 'dribbled_past' in stats and stats['dribbled_past'] > 0:  # Adjust this threshold based on your criteria
        analysis += f"- Was Dribbled past {stats['dribbled_past']} times\n"
    if 'aerials_won'in stats and stats['aerials_won'] < 5 and stats[
        'aerials_won'] != 0:  # Adjust this threshold based on your criteria
        analysis += f"- Aeriels won is only {stats['aerials_won']}\n"
    if 'saves' in stats and stats['saves'] < 5 and stats['saves']:
        analysis += f"- Saves: {stats['saves']}\n"


    # ... add more negative aspects based on specific stats

    # Overall Influence
    # Overall Influence
    analysis += "\nOverall Influence:\n"
    if ('rating_title' in stats and stats['rating_title'] > 7.0 and
            ('passes_into_final_third' in stats and stats['passes_into_final_third'] > 10 or
             'accurate_crosses' in stats and stats['accurate_crosses'] > 5 or
             ('duel_won' in stats and 'duel_lost' in stats and stats['duel_won'] >= 5 and stats['duel_lost'] < 5) or
             'dribbles_succeeded' in stats and stats['dribbles_succeeded'] >= 7 or
             'long_balls_accurate' in stats and stats['long_balls_accurate'] > 7 or
             'touches_opp_box' in stats and stats['touches_opp_box'] > 5 or
             'recoveries' in stats and stats['recoveries'] > 10)):
        #analysis += "- Significant overall influence on the game\n"

        analysis += "- Overall, a highly influential performance on the pitch\n\n"
    elif 'rating_title' in stats and stats['rating_title'] < 6.0:
        analysis += "- Needs improvement\n\n"
    else:
        analysis += "- A performance with both positive and negative aspects\n\n"
    st.write(analysis)
def subdataext(id,record,records):
    global positions
    l=[]
    x=record
    #print(x)
    #print(x.keys())
    try:
        position=positions[id['usualPlayingPositionId']]
    except KeyError:
        print("line178")
        print(id)
    name=id['name']
    #fname=name['fullName']
    if x is None:
        st.warning("Stats not available")
    stats=x[str(id['id'])]["stats"]
    #print("stats",stats)
    stats0=stats[:]
    #print(stats0)
    rstats={}
    l = []
    for i in range(len(stats0)):
        stats00 = stats0[i]
        only = stats00['stats']
        print("only", only)
        for key in only:
            try:
                l.append({only[key]['key']:only[key]['stat']['value']})
                fraction_str = f"{only[key]['stat']['value']}/{only[key]['stat']['total']}"

                # Split the string into numerator and denominator
                #numerator, denominator = map(int, fraction_str.split('/'))

                # Calculate the percentage
                #try:
                    #percentage = (numerator / denominator) * 100
                #except ZeroDivisionError:
                    #percentage=0
                l.append({f"{only[key]['key']}%": fraction_str})
            except KeyError:
                continue
    l.append({"position": position})
    records.update({name: l})
    return records
def get_player_stats(a,records):
    global anew
    b = a["lineup"]
    try:
        c = b['homeTeam']['starters']
    except KeyError:
        print(b.keys())
    # x = c.pop()
    y = b['awayTeam']['starters']
    a = anew["content"]
    b = a['playerStats']
    for i in c:
        subdataext(i, b,records)
    # print()
    # exit(0)
    # print(y)
    # lineup=y['lineup'][0]
    # ben1=lineup['bench']
    for i in y:
        subdataext(i, b,records)
    return records
def plotting(records,st):
    new_rec={}
    colors = sns.color_palette("husl", 12)
    for i in records:
        name = i
        pos = records[i][-1]['position']
        dic = records[i]
        # dic.pop("fantasy_points")
        #try:
            #rating = dic["rating_title"]
        #except KeyError:
            #rating = None
        x = dic.copy()
        #st.write(name)
        #st.write(pos)
        #st.write(dic)
        #x.update({"rating": rating})

        # Process dictionary values
        ls = {}
        for key in enumerate(dic):
            #st.write(key[0])
            keys = list(dic[key[0]].keys())[0]
            val = list(dic[key[0]].values())[0]
            #st.write(keys)
            #st.write(val)
            if val is None:
                x.remove(dic[key[0]])
            elif isinstance(val, bool):
                x.remove(dic[key[0]])
            elif isinstance(val, str) and "/" in val:
                #a = val.split("(")
                #b = a[1].split("%")
                #x[key[0]] = float(b[0])
                x.remove(dic[key[0]])
                ls.update({keys: val})
            elif isinstance(val, str) and "%" in keys:
                #a = val.split("/")
                #b = a[1].split("%")
                #x[key[0]] = float(b[0])
                x.remove(dic[key[0]])
                ls.update({keys: val})
            elif isinstance(val, str):
                try:
                    x[key[0]] = float(val)
                except ValueError:
                    x.remove(dic[key[0]])
        #st.write("newtest")
        #st.write(ls)
        #return
        #x.pop()
        print(x)
        haha=x.copy()
        #y = list(x.keys())
        #z = list(x.values())
        y = []
        z = []
        for dictionary in x:
            y.extend(dictionary.keys())
            z.extend(dictionary.values())
        new_rec[name] = y
        # Normalize data to fit within the range [0, 1]
        real = z.copy()
        zc = z.copy()
        for value in z:
            ind = zc.index(value)
            try:
                if float(value) is None or value <= 0.1:
                    zc.pop(ind)
                    y.pop(ind)
                    real.pop(ind)
                elif int(value) < 1:
                    zc[ind] = value * 100
                elif int(value) < 10:
                    zc[ind] = value * 10
            except TypeError as e:
                print(e)


        color1, color2, color3 = random.sample(colors, 3)
        max_stat = max(zc)
        normalized_stats = [(stat - 0) / (max_stat - 0) for stat in zc]

        # Number of categories
        for i in y:
            ind = y.index(i)
            if i == 'rating_title':
                y[ind] = 'rating'
        num_categories = len(y)

        # Step 2: Calculate the angle for each category
        angles = np.linspace(0, 2 * np.pi, num_categories, endpoint=False).tolist()
        # Step 3: Close the plot
        normalized_stats += [normalized_stats[0]]
        angles += [angles[0]]
        # Step 4: Create the plot
        fig = plt.figure()
        ax = fig.add_subplot(111, polar=True)
        # ax.set_ylim(0, 0.8)

        # Plot the data
        ax.plot(angles, normalized_stats, 'o-', linewidth=2, color=color1, markersize=8, alpha=0.7)
        ax.fill(angles, normalized_stats, color=color1, alpha=0.3)

        # ax.set_aspect("equal")
        ax.margins(len(y) / 30)

        # Set category labels on the plot with clear font
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(y, fontsize=6, weight='bold', color=color2, rotation_mode="anchor")

        # Textbox
        for i, (angle, stat, label) in enumerate(zip(angles, real, y)):
            x = angle + np.pi / 2 if angle < np.pi else angle - np.pi / 2
            y = normalized_stats[i] + 0.355
            text = f"{int(stat)}" if isinstance(stat, int) else f"{float(stat)}"
            ax.text(angle, y, text, fontsize=8, ha='center', va='center', color=color3,
                    bbox=dict(boxstyle='square', facecolor='white'))

        # Add watermark with Twitter handle
        plt.text(-0.05, -0.05, '@DJMahe04', fontsize=12, ha='center', va='center', alpha=0.2, transform=ax.transAxes)

        # Create a string with the keys and values from 'ls'
        ls_text = "\n".join(f"{k}: {v}" for k, v in ls.items())

        # Add the text box to the plot
        ax.text(1.2, 0.25, ls_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.4))

        # Step 6: Display the plot
        plt.title(f'Player Performance {name} ({pos})', size=16, weight='bold', color='#333333')
        st.pyplot(fig)
        combined_dict = {}
        for d in haha:
            combined_dict.update(d)
        analyze_player_stats(combined_dict,st,name)
        #return
#a,teamnames,score,records=match_details("4621519") #here records includes the stats of subs in dictionary with stats as key list
#get_player_stats(a)
#print("records",records) #now records are complete
