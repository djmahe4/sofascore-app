import time
import math
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
from matplotlib import dates
from datetime import date, timedelta
from datetime import datetime as dt
import http.client
import json
from urllib.parse import urlparse
import urllib.request
import urllib.parse
import datetime
import math
import requests
import os
import json
# from operations import url_extract
from bs4 import BeautifulSoup
import streamlit as st
import pytz
#from operations import retry
from timezonefinder import TimezoneFinder as Tf

@st.cache_resource
def conn_make():
    if 'conn' not in st.session_state:
        url = f"https://api.sofascore.com/api/v1/event/12437786"
        parsed = urlparse(url)
        conn = http.client.HTTPSConnection(parsed.netloc)
        st.session_state.conn=conn

def convert_psuedo_timestamp_to_local(timestamp=1730988000,source_timezone='America/New_York', timezone_tar='Asia/Kolkata'):
    """
    Converts a UTC timestamp (in seconds since the epoch) to a datetime object in a specified timezone.

    Args:
        utc_timestamp (int): A UTC timestamp representing seconds since the epoch (1970-01-01 00:00:00 UTC).
        timezone_str (str): A string representing the timezone to convert to (e.g., 'America/Los_Angeles').

    Returns:
        str: A formatted string representing the local time in the specified timezone,
             in the format 'YYYY-MM-DDTHH:MM:SS.ffffff'.  Returns None if there is an error.
    """
    try:

        stz=pytz.timezone(source_timezone)
        dtz=pytz.timezone(timezone_tar)
        dt_source=dt.fromtimestamp(timestamp,stz)
        st_target=dt_source.astimezone(dtz)

        # Format the local datetime object to a string
        formatted_local_datetime = st_target.strftime("%Y-%m-%dT%H:%M:%S.%f")
        #st.write(formatted_local_datetime,convert_timestamp(utc_timestamp))
        return formatted_local_datetime

    except ValueError as e:
        print(f"Error: Invalid timestamp or timezone. {e}")
        return None
    except pytz.exceptions.UnknownTimeZoneError as e:
        print(f"Error: Invalid timezone. {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def venue_timezone(lat,long):
    tf=Tf()
    return tf.timezone_at(lat=lat, lng=long)

def get_timezone():
    # Fetch public IP address
    ip = requests.get('https://api.ipify.org').text

    # Use IP to get geolocation (example: ip-api.com)
    response = requests.get(f'http://ip-api.com/json/{ip}').json()
    print(response['timezone'])
    return response['timezone']
def venue_det():
    pitch=scraper(f'https://api.sofascore.com/api/v1/event/{st.session_state.mmid}/')
    p_tz=get_timezone()
    v_timezone=venue_timezone(pitch['event']['venue']['venueCoordinates']['latitude'],pitch['event']['venue']['venueCoordinates']['longitude'])
    match_date=convert_psuedo_timestamp_to_local(pitch['event']['startTimestamp'],p_tz,v_timezone)
    return match_date,v_timezone

#@st.cache_resource
def scraper(url):
    #st.write(url)
    #url =
    #ic(url)
    parsed = urlparse(url)
    #conn = http.client.HTTPSConnection(parsed.netloc)
    try:
        #conn_make()
        st.session_state.conn.request("GET", parsed.path)
    except Exception as e:
        st.error(e)
        #conn_make()
        st.session_state.conn.request("GET", parsed.path)
    res = st.session_state.conn.getresponse()
    data = res.read()
    #try:
    details = json.loads(data.decode("utf-8"))
    return details
    #except:
        #st.write(data.decode("utf-8"))
    #ic(details.keys())
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
    'x-mas': 'eyJib2R5Ijp7InVybCI6Ii9hcGkvbWF0Y2hlcz9kYXRlPTIwMjUwMTAyIiwiY29kZSI6MTczNTc5MDk2NzU5MywiZm9vIjoiZTk2YjYwYTIxIn0sInNpZ25hdHVyZSI6IjZCMTM3NDdBNjU0OEI4OUFERkM2RjgzODUyRjNCNjlEIn0=',
    }
    return requests.get(url,params=params,headers=headers).json()
def plot_biorhythm_chart(combined_points, dates, name, cycle_label="Combined"):
    """Plots the biorhythm chart with dates using matplotlib.pyplot."""

    if len(combined_points) != len(dates):
        raise ValueError("Combined points and dates lists must have the same length.")
    # fig,ax=plt.subplots()
    fig = plt.figure(figsize=(10, 6))
    plt.plot(combined_points, label=cycle_label)

    # Customize x-axis labels with numbers (optional)
    plt.xticks(range(len(combined_points)))  # Use data point indices

    # Add dates below the x-axis (optional, adjust spacing as needed)
    plt.xticks(range(len(combined_points)), [d[:5] for d in dates], rotation=0, ha='center', va='bottom', fontsize=6)
    # Add an annotation
    plt.annotate('@DJMahe04', xy=(0.1, 0.1), xycoords='axes fraction',  # Position in axes coordinates
            fontsize=12, ha='left', va='bottom', alpha=0.4)
    plt.xlabel("Day")  # Adjust label if needed
    plt.ylabel("Biorhythm Level")
    plt.title(f"Biorhythm Chart ({name})")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()  # Adjust spacing to avoid overlapping labels
    # return plt
    # plt.show()
    st.pyplot(fig)


def extraction(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Find the <script> tag with id="__NEXT_DATA__"
    script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')

    # Extract the JSON content
    if script_tag:
        json_content = script_tag.string
        if json_content:
            data = json.loads(json_content)
    return data


def usedata(name, n):
    for i in range(len(n)):
        if name in n[i]:
            # st.write("Name of the player:", n[i])
            pname = n[i]
            dob = n[i + 1]
            sr = ""
            form_dob = dob.split("/")[::-1]
            for i in form_dob:
                sr += i + "-"
            return sr[:-1], pname

def days_since_birth(date_of_birth,today=date.today()):
    """Calculates the number of days since birth considering leap years"""
    #today = date.today()
    # Extract year, month, day from the provided date of birth string
    #date_str = "1995-10-19T00:00:00.000Z"

    # Parse the date string into a datetime object
    date_obj = dt.strptime(date_of_birth, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Extract the year, month, and day
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day

    # Create a date object representing the date of birth
    birth_date = date(year, month, day)

    # Calculate the difference between today and date of birth in days
    time_delta = dt.date(today) - birth_date
    return time_delta.days


def calculate_bhagyank(date_of_birth):
    """Calculates Bhagyank from date of birth"""
    date_obj = dt.strptime(date_of_birth, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Extract the year, month, and day
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day
    sum = 0
    for i in str(day):
        sum = sum + int(i)
    if sum > 9:
        sum1 = 0
        for i in str(sum):
            sum1 = sum1 + int(i)
        sum = sum1
    for i in str(month):
        sum = sum + int(i)
    if sum > 9:
        sum2 = 0
        for i in str(sum):
            sum2 = sum2 + int(i)
        sum = sum2
    for i in str(year):
        sum = sum + int(i)
    if sum > 9:
        sum3 = 0
        for i in str(sum):
            sum3 = sum3 + int(i)
        sum = sum3
    if sum > 9:
        sum4 = 0
        for i in str(sum):
            sum4 = sum4 + int(i)
        sum = sum4
    return sum
    # return (day + month + (year % 100) + (year // 100)) % 9 + 1  # Ensure Bhagyank is 1-9


def calculate_naamank(name):
    aldict = {'a': 1, 'j': 1, 's': 1, 'b': 2, 'k': 2, 't': 2, 'c': 3, 'l': 3, 'u': 3, 'd': 4, 'm': 4, 'v': 4, 'e': 5,
              'n': 5, 'w': 5, 'f': 6, 'o': 6, 'x': 6, 'g': 7, 'p': 7, 'y': 7, 'h': 8, 'q': 8, 'z': 8, 'i': 9, 'r': 9}
    """Calculates Naamank (sum of numerological letter values)"""
    name_sum = 0
    for letter in name.lower().strip():
        if letter != " ":
            number = aldict.get(letter, 0)  # Initialize number with 0 if letter not found
            name_sum += number

    while name_sum > 9:
        sum_digits = 0
        for digit in str(name_sum):
            sum_digits += int(digit)
        name_sum = sum_digits
    if name_sum + 3 > 9:
        name_sum = name_sum - 3
    else:
        name_sum = name_sum + 3
    return name_sum


def calculate_moolank(date_of_birth):
    """Calculates Moolank from date of birth"""
    date_obj = dt.strptime(date_of_birth, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Extract the year, month, and day
    day = date_obj.day
    sum = 0
    for i in str(day):
        sum = sum + int(i)
    if sum > 9:
        sum1 = 0
        for i in str(sum):
            sum1 = sum1 + int(i)
        sum = sum1
    # return sum
    return sum


def combine_numbers(moolank, bhagyank, naamank):
    """Combines Moolank, Bhagyank, and Naamank with Fibonacci offset (not scientific)"""
    # combined = (moolank * 3 + bhagyank * 2 + normalized_naamank)  # / 6
    # combined= moolank+(bhagyank*naamank)
    combined = bhagyank + (moolank * naamank)
    # print('{}*{}+{}={}'.format(bhagyank, naamank, moolank, combined))
    print('{}+({}*{})={}'.format(bhagyank, moolank, naamank, combined))
    st.write('{}+({}*{})={}'.format(bhagyank, moolank, naamank, combined))
    typ = +9.81
    # if combined<=9:
    # combined = bhagyank * naamank
    # print("Alternate {}*{}={}".format(bhagyank,naamank,combined))
    # combined = moolank + (bhagyank * naamank)
    # print('{}*{}+{}={}'.format(bhagyank, naamank, moolank, combined))
    # typ= -9.81
    return combined, typ


# if moolank> else ValueError # - fibonacci_offset, fibonacci_sequence


def biorhythm_chart(days, combined):
    """Generates biorhythm chart using Fibonacci sequences (not scientific)"""
    biorhythm_data = []
    # for cycle, factor in zip(cycles, fibonacci_scaling_factors):
    # fibonacci_values = [f * factor for f in fibonacci_sequence[:cycle]]
    biorhythm_data.append([math.sin(2 * math.pi * i / combined) for i in range(days - 15, days + 15)])

    return biorhythm_data[0]


def get_date_range(today="",days_before=-15, days_after=14):
  """
  Finds today's date and a range of dates before and after in dd-mm-yyyy format.

  Args:
      days_before (int, optional): Number of days before today (default: 15).
      days_after (int, optional): Number of days after today (default: 14).

  Returns:
      list: A list of strings representing the dates in dd-mm-yyyy format.
  """
  if today=="":
    today = date.today()
  date_range = []

  # Add date 15 days before today
  #date_range.append(today - timedelta(days=days_before))
  for i in range(days_before, days_after +1):
    date_range.append(today - timedelta(days=i))
  formatted_dates = [date.strftime("%d-%m-%Y") for date in date_range]
  return formatted_dates
def get_tids():
    teams=scraper(f"https://api.sofascore.com/api/v1/event/{st.session_state.mmid}")['event']
    return teams['homeTeam']['id'],teams['awayTeam']['id']
def squad_players():
    h_id,a_id=get_tids()
    dat = {}
    h_details=scraper(f"https://api.sofascore.com/api/v1/team/{h_id}/players")
    for i in h_details['players']:
        print(i['player'])
        dat[i['player']['slug']] = i['player']['dateOfBirthTimestamp']
    a_details = scraper(f"https://api.sofascore.com/api/v1/team/{a_id}/players")
    for i in a_details['players']:
        print(i['player'])
        dat[i['player']['slug']] = i['player']['dateOfBirthTimestamp']
    return dat

def match11():
    try:
        time.sleep(2)
        details=scraper(url = f"https://api.sofascore.com/api/v1/event/{st.session_state.mmid}/lineups")
    except json.JSONDecodeError:
        time.sleep(3)
        return squad_players()
    dat = {}
    try:
        details['home']
    except:
        time.sleep(3)
        return squad_players()
    for i in details['home']['players']:
        if i=='error':
            dat=squad_players()
        print(i['player'])
        dat[i['player']['slug']] = i['player']['dateOfBirthTimestamp']
    for i in details['away']['players']:
        print(i['player'])
        dat[i['player']['slug']] = i['player']['dateOfBirthTimestamp']
    return dat

def main():
    # Get the date range
    try:
        print(st.session_state.conn)
    except:
        conn_make()
        print(st.session_state.conn)
    playersd=match11()
    mdate=venue_det()
    st.write("Match Date:",mdate[0])
    st.write("Timezone:",mdate[1])
    st.divider()
    #matchid=url
    print(playersd)
    #date_of_birth,name=usedata(y,n)
    data=playersd
    for name, date_of_birth in data.items():
        st.markdown(f"# {name}")
        # Parse the original date string to a datetime object
        st.write(date_of_birth)
        try:
            #date_obj = dt.strptime(date_of_birth, '%Y-%m-%dT%H:%M:%S.%Z')
            date_obj=dt.utcfromtimestamp(date_of_birth)
        except ValueError:
            continue

        # Convert the datetime object to the desired format
        formatted_date_str = date_obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        print(f"Formatted Date: {formatted_date_str}")
        st.write(f"Name: {name}")
        #st.write(f"DOB: {date_of_birth}")
        st.write(f"DOB: {formatted_date_str}")
        bhagyank = calculate_bhagyank(formatted_date_str)
        moolank = calculate_moolank(formatted_date_str)
        naamank = calculate_naamank(name)

        st.write(f"Bhagyank: {bhagyank}")
        st.write(f"Naamank: {naamank}")
        st.write("Moolank:",moolank)
        # Biorhythm chart parameters (adjust as needed)
        # cycles = [23, 28, 33]  # Physical,
        comb,typ = combine_numbers( moolank,bhagyank, naamank)
        match_date = mdate[0]
        days = days_since_birth(formatted_date_str,dt.strptime(match_date, "%Y-%m-%dT%H:%M:%S.%f"))
        bio = biorhythm_chart(days,comb)
        di={}

        # Parse the original date string to a datetime object
        date_obj = dt.strptime(match_date, "%Y-%m-%dT%H:%M:%S.%f")
        # Convert the datetime object to the desired format
        formatted_date_str = date_obj.strftime("%Y-%m-%d")
        today = dt.strptime(formatted_date_str, "%Y-%m-%d")
        date_list = get_date_range(today)
        for i,date in enumerate(date_list):
            di.update({date:bio[i]})
        #st.write(di)
        # st.write table header
        st.write("-" * 58)
        new = pd.DataFrame(di.items(), columns=["Date", "Values"])
        st.table(new)
        #plot_biorhythm_chart(bio, date_list)
        ck=16 #ck should be set to 15 by default
        st.write("BIO:",bio[ck])
        if abs(float(f"{bio[ck - 1]:.4f}")) == abs(float(f"{bio[ck + 1]:.4f}")):
            st.write("Warning!! Prediction may fail!")
        #st.write(bio)
        ls=[abs(round(ele,4)) for ele in bio[:-(30-ck+1):-1]]
        #st.write(ls)
        mx=max(ls)
        ln=0
        found=False
        while ln < len(ls):
            last = ls[ln]
            try:
                if ls[ln - 1] == mx and ln >= 0:
                    found = True
                    # ln += 1
                    # continue
                elif ls[ln + 1] == mx:
                    found = True
                    # ln += 2
                    # continue
                    ln += 1
            except IndexError:
                st.write("Passed {}".format(ls[ln]))
                # pass
            if ls[ln] == mx:
                found = True
                # ln+=1
                # continue
            if found:
                st.write(ls[ln])
                ln = ln + 2
            else:
                st.write("Not found {}".format(ls[ln]))
                ln = ln + 1

        if last == ls[-1]:
            st.write("Great..")
        else:
            st.write("Flop :(")
        #if round_to_binary(bio[ck-1]) == 0 or round_to_binary(bio[ck+1])==0 or round_to_binary(bio[ck-1]) == 1 or round_to_binary(bio[ck+1])==1:
            #st.write("Bingo..")
            #st.write(bio[ck-1],bio[ck+1])
        for i in ls[-4:]:
            if ls[-4:].count(i) > 1:
                st.write("Pipe!")
                break
        plot_biorhythm_chart(list(di.values()),list(di.keys()),name)
        st.write("-"*58)
        st.write("-" * 58)
        #save_plt(plt,matchid,name)
