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

#id=333143
#big_data=percentile_extraction()
#big_data.pop('type')
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
def stats_collect(sname,big_data):
    if "per 90" in sname:
        dper90 = per90_calc(big_data)
        return dper90['names'],dper90[sname.split(" per 90")[0]]
    else:
        return big_data['names'],big_data[sname]


#stat1="goals per 90"
#stat2="assists"
#url = f'https://www.sofascore.com/api/v1/unique-tournament/1900/season/65961/top-players/overall'
#jdata=get_sofascore(url)['topPlayers']
#dict1={}
#dict2={}
#pos="F"
#lid=1900
#sid=65961
#if stat1 in jdata:
    #for i in jdata[stat1]:
        #dict1.update({i['player']['name']:i['statistics'][stat1]})
#else:
def season_final(stat1,stat2,lid,sid):
    pos=st.session_state.posa
    big_data = percentile_extraction(pos, lid, sid)
    big_data.pop('type')
    #st.dataframe(pd.DataFrame(big_data))
    a,b=stats_collect(stat1, big_data)
    dict1=dict(zip(a,b))
    a,b=stats_collect(stat2, big_data)
    dict2 = dict(zip(a, b))
    #st.write(dict1,dict2)
    return dict1,dict2


def match_id_init(): #copied to operation.py
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
def match_details(id):
    url = f'https://www.sofascore.com/api/v1/event/{id}/statistics'
    jdata = get_sofascore(url)
    print(jdata['statistics'])
    for i in jdata['statistics']:
        if i['period'] == "ALL":
            record = i['groups']
    stats = {}
    ppda_h = {}
    ppda_a = {}
    for i in record:
        for j in i['statisticsItems']:
            if "Total" in j['name']:
                continue
            stats.update({j['name']: [j['home'], j['away']]})
            if j['name'] == "Tackles":
                ppda_h.update({j['name']: j['home']})
                ppda_a.update({j['name']: j['away']})
            elif j['name'] == "Clearances":
                ppda_h.update({j['name']: j['home']})
                ppda_a.update({j['name']: j['away']})
            elif j['name'] == "Interceptions":
                ppda_h.update({j['name']: j['home']})
                ppda_a.update({j['name']: j['away']})
            elif j['name'] == "Final third phase":
                ppda_h.update({j['name']: j['away'].split("/")[0]})
                ppda_a.update({j['name']: j['home'].split("/")[0]})
    ppdah = int(ppda_a["Final third phase"]) / (
                int(ppda_h["Interceptions"]) + int(ppda_h["Tackles"]) + int(ppda_h["Clearances"]))
    ppdaa = int(ppda_h["Final third phase"]) / (
                int(ppda_a["Interceptions"]) + int(ppda_a["Tackles"]) + int(ppda_a["Clearances"]))
    stats.update({"PPDA": [str(ppdah), str(ppdaa)]})
    with open("impstats.json", "w", encoding='utf-8') as file:
        json.dump(stats, fp=file, indent=2)
    url = f'https://www.sofascore.com/api/v1/event/{id}'
    jdata = get_sofascore(url)['event']
    return stats,[jdata['homeTeam']['name'],jdata['awayTeam']['name']],[jdata['homeScore']['current'],jdata['awayScore']['current']]
def create_comparison_data(t1, t2):
    """Creates comparison data suitable for a horizontal bar graph."""
    d1=[]
    d2=[]
    for i, (x, y) in enumerate(zip(t1, t2)):
        y=abs(y)
        try:
            if x == 0 and y == 0:
                comp1 = 0
                comp2 = 0
            else:
                try:
                    comp1 = (x-y)/y
                    #if comp1<0:
                        #comp1=-comp1
                except ZeroDivisionError:
                    comp1=0
                try:
                    comp2 = (y-x)/x
                    #if comp2>0:
                        #comp2=-comp2
                except ZeroDivisionError:
                    comp2=0
            if comp1>abs(comp2):
                #print(comp1,comp2,"109")
                comp2=0
            elif comp1<abs(comp2):
                #print(comp1, comp2, "112")
                comp1=0
            else:
                d1.append(0)
                d2.append(0)
                continue
            d1.append(comp1)
            d2.append(-comp2)
        except TypeError:
            print("Type error encountered. Make sure the inputs are numbers")
            return None
    return d1,d2
def headtohead(data,teams,score):
    x = data
    t1 = []
    t2 = []
    rem = []
    keys = list(x.keys())
    for i in x:
        if x[i][0] == x[i][1] == 0 or x[i][0] == x[i][1] == None:
            rem.append(i)
            continue
        t1.append(x[i][0])
        t2.append(x[i][1])
    for i in rem:
        print(i)
        keys.remove(i)
    # print(t1)
    ls1 = {}
    ls2 = {}
    for i in t1:
        c = t1.index(i)
        if i == None:
            t1[c] = 0
            # elif i==True or i==False:
            # t1.pop(t1.index(i))
        elif type(i) == str and "(" in i:
            a = i.split("(")
            b = a[1].split('%')
            # c=t1.index(i)
            t1[c] = float(b[0])
            t1[c] = round(t1[c], 2)
            ls1.update({keys[c]: f"{b[0]}%"})
        elif type(i) == str and "%" in i:
            a = i.split("%")[0]
            t1[c] = float(a)
            t1[c] = round(t1[c], 2)
            ls1.update({keys[c]: f"{a}%"})
        elif type(i) == str and "-" in i:
            a = i.split("-")[-1]
            t1[c] = float(a)
            t1[c] = round(t1[c], 2)
            ls1.update({keys[c]: f"-{a}"})
        elif type(i) == str:
            a = float(i)
            b = t1.index(i)
            t1[b] = round(a, 2)
    for i in t2:
        c = t2.index(i)
        if i == None:
            t2[c] = 0
            # elif i==True or i==False:
            # t1.pop(t1.index(i))
        elif type(i) == str and "(" in i:
            a = i.split("(")
            b = a[1].split('%')
            # c = t2.index(i)
            t2[c] = float(b[0])
            t2[c] = round(t2[c], 2)
            ls2.update({keys[c]: f"{b[0]}%"})
        elif type(i) == str and "%" in i:
            a = i.split("%")[0]
            t2[c] = float(a)
            t2[c] = round(t2[c], 2)
            ls2.update({keys[c]: f"{a}%"})
        elif type(i) == str:
            a = float(i)
            b = t2.index(i)
            t2[b] = round(a, 2)
    keys = keys
    print(keys)

    t2 = [-abs(x) for x in t2]
    print(t1)
    print(t2)
    print(len(t1), len(t2))
    b1 = {}
    b2 = {}

    # teams=['home','away']
    # score=[0,0]
    d1, d2 = create_comparison_data(t1, t2)
    print(d1)
    print(d2)
    # Create a figure and a set of subplots with increased size
    fig, ax = plt.subplots(figsize=(15, 15))  # Adjust as needed
    plt.style.use('ggplot')  # Use the 'ggplot' style
    # Set the y positions
    y_pos = np.arange(len(keys))
    # Create a color palette
    colors = sns.color_palette("bright")
    # Randomly select two distinct colors
    color1, color2 = random.sample(colors, 2)
    # Create the horizontal bars with the new colors
    bar1 = ax.barh(y_pos, d1, color=color1, label=f'{teams[0]}')
    bar2 = ax.barh(y_pos, d2, color=color2, label=f'{teams[1]}')

    # ... your existing code ...
    # Set the y-axis limits to make smaller bars appear larger
    # ax.set_xlim([-max(max(t1), max(t2)) * 1.2, max(max(t1), max(t2)) * 1.2])

    # Add the category names as y-tick labels with increased font size
    ax.set_yticks(y_pos)
    ax.set_yticklabels(keys, fontsize=12)  # Adjust as needed
    # Add gridlines
    ax.grid(True, linestyle='--', alpha=0.6)

    # Sort bars
    # t1, t2, keys = zip(*sorted(zip(t1, t2, keys)))

    # Hide the y-axis values
    ax.yaxis.set_tick_params(length=0)

    # Add the stat values beside the bars
    for i, (v, z) in enumerate(zip(t1, d1)):
        ax.text(z + 0.1, i, str(v), color='black', va='center')
    for i, (v, z) in enumerate(zip(t2, d2)):
        ax.text(z - 0.1, i, str(abs(v)), color='black', va='center', ha='right')

        # Add watermark with Twitter handle
    plt.text(0.1, 0.5, '@DJMahe04', fontsize=14, ha='center', va='center', alpha=0.5, transform=ax.transAxes)
    # Create a string with the keys and values from 'ls'
    ls_text = "\n".join(f"{k}: {v}" for k, v in ls1.items())

    # Add the text box to the plot
    ax.text(0.8, -0.05, ls_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor=color1, alpha=0.5))
    # Create a string with the keys and values from 'ls'
    ls_text = "\n".join(f"{k}: {v}" for k, v in ls2.items())

    # Add the text box to the plot
    ax.text(0.1, -0.05, ls_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor=color2, alpha=0.5))
    ax.legend(loc='upper right')
    plt.title(f'[{score[1]}] {teams[1]} vs {teams[0]} [{score[0]}]', size=16, weight='bold', color='#333333')
    st.pyplot(plt)
#match_id_init()



def create_radar_chart(stats, name, pos, color1, color2, color3):
    """Creates a radar chart from player stats."""
    y = list(stats.keys())
    values = list(stats.values())
    num_categories = len(y)

    # Normalize the values to a range between 0 and 1
    max_values = max(values)
    min_values = min(values)
    if max_values == min_values:
        normalized_stats = [0.5] * num_categories
    else:
        normalized_stats = [(x - min_values) / (max_values - min_values) for x in values]

    # Step 2: Calculate the angle for each category
    angles = np.linspace(0, 2 * np.pi, num_categories, endpoint=False).tolist()

    # Step 3: Close the plot (no longer needed here)

    # Step 4: Create the plot
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))  # adjust figure size
    plt.style.use('ggplot')
    # Plot the data
    ax.plot(angles, normalized_stats, 'o-', linewidth=2, color=color1, markersize=8, alpha=0.7)
    ax.fill(angles, normalized_stats, color=color1, alpha=0.3)

    # Set category labels on the plot
    ax.set_xticks(angles)  # remove the -1 from the slicing to include the last tick
    ax.set_xticklabels(y, fontsize=8, weight='bold', color=color2)

    # Textbox with original values
    for i, (angle, stat) in enumerate(zip(angles, values)):  # use the original values here
        x = angle
        y_pos = normalized_stats[i] + 0.1
        text = f"{stat:.2f}" if isinstance(stat, float) else str(stat)
        ax.text(x, y_pos, text, fontsize=8, ha='center', va='center', color=color3,
                bbox=dict(boxstyle='square', facecolor='white', alpha=0.5))

    # Add watermark
    plt.text(0.5, 0.05, '@DJMahe04', fontsize=12, ha='center', va='center', alpha=0.2, transform=ax.transAxes)

    # Set axis limits to 0-1
    ax.set_ylim(0, 1)

    # Step 6: Display the plot
    plt.title(f'Player Performance {name} ({pos})', size=16, weight='bold', color='#333333')
    plt.tight_layout()
    #plt.savefig(f'Player Performance {name} ({pos}).jpg')
    st.pyplot(plt)

def re_plotting(pos_check,jdata):
    st.markdown("# Away Team")
    records = {}
    for i in jdata['away']['players']:
        # print(i.keys())
        # print(i['player']['name'])
        # print(i['position'])
        # print(i['statistics'])
        if i['statistics'] != {}:
            stats = i['statistics']
            try:
                stats.pop('ratingVersions')
            except:
                continue
            stats.update({'position': i['position']})
            records.update({i['player']['name']: stats})
    print(records)
    new_rec = {}
    colors = sns.color_palette("husl", 12)
    for name in records:
        i = name
        pos = records[i]['position']
        dic = records[i]
        dic.pop('position')
        # dic.pop("fantasy_points")
        # try:
        # rating = dic["rating_title"]
        # except KeyError:
        # rating = None
        x = dic.copy()
        # st.write(name)
        # st.write(pos)
        # st.write(dic)
        # x.update({"rating": rating})

        # Process dictionary values
        ls = {}
        for key in enumerate(dic):
            # st.write(key[0])
            keys = list(dic.keys())[key[0]]
            val = list(dic.values())[key[0]]
            # print(key[1],val)
            # st.write(keys)
            # st.write(val)
            if val is None:
                x.pop(key[1])
            elif isinstance(val, bool):
                x.pop(key[1])
            elif isinstance(val, str) and "/" in val:
                # a = val.split("(")
                # b = a[1].split("%")
                # x[key[0]] = float(b[0])
                x.pop(key[1])
                ls.update({keys: val})
            elif isinstance(val, str) and "%" in keys:
                # a = val.split("/")
                # b = a[1].split("%")
                # x[key[0]] = float(b[0])
                x.pop(key[1])
                ls.update({keys: val})
            elif isinstance(val, str):
                try:
                    x[key[1]] = float(val)
                except ValueError:
                    x.pop(key[1])
            else:
                x[key[1]] = val
        print(x)
        c1, c2, c3 = random.sample(colors, 3)
        create_radar_chart(x, name, pos_check[pos], c1, c2, c3)
def plotting(mid="12437809"):
    st.markdown("# Home Team")
    pos_check = {'G': 'Goalkeeper', 'D': 'Defender', 'M': 'Midfielder', 'F': 'Forward'}
    # plt.savefig("test2.jpg")
    url = f'https://www.sofascore.com/api/v1/event/{mid}/lineups'
    jdata = get_sofascore(url)
    records = {}
    for i in jdata['home']['players']:
        # print(i.keys())
        # print(i['player']['name'])
        # print(i['position'])
        # print(i['statistics'])
        if i['statistics'] != {}:
            stats = i['statistics']
            stats.pop('ratingVersions')
            stats.update({'position': i['position']})
            records.update({i['player']['name']: stats})
    print(records)
    new_rec = {}
    colors = sns.color_palette("husl", 12)
    for name in records:
        i = name
        pos = records[i]['position']
        dic = records[i]
        dic.pop('position')
        # dic.pop("fantasy_points")
        # try:
        # rating = dic["rating_title"]
        # except KeyError:
        # rating = None
        x = dic.copy()
        # st.write(name)
        # st.write(pos)
        # st.write(dic)
        # x.update({"rating": rating})

        # Process dictionary values
        ls = {}
        for key in enumerate(dic):
            # st.write(key[0])
            keys = list(dic.keys())[key[0]]
            val = list(dic.values())[key[0]]
            # print(key[1],val)
            # st.write(keys)
            # st.write(val)
            if val is None:
                x.pop(key[1])
            elif isinstance(val, bool):
                x.pop(key[1])
            elif isinstance(val, str) and "/" in val:
                # a = val.split("(")
                # b = a[1].split("%")
                # x[key[0]] = float(b[0])
                x.pop(key[1])
                ls.update({keys: val})
            elif isinstance(val, str) and "%" in keys:
                # a = val.split("/")
                # b = a[1].split("%")
                # x[key[0]] = float(b[0])
                x.pop(key[1])
                ls.update({keys: val})
            elif isinstance(val, str):
                try:
                    x[key[1]] = float(val)
                except ValueError:
                    x.pop(key[1])
            else:
                x[key[1]] = val
        print(x)
        c1,c2,c3=random.sample(colors,3)
        create_radar_chart(x,name,pos_check[pos],c1,c2,c3)
        #break
    st.divider()
    re_plotting(pos_check,jdata)
#plotting()
