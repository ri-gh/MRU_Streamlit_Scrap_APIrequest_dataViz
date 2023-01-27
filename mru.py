import pandas as pd
import numpy as np
import plotly.express as px
import requests
import streamlit as st
from datetime import timedelta
import os

st.set_page_config(
    page_title="Hotel analysis for Mauritius Island",
    page_icon="🛫❤️",
    layout="wide"
)

st.title("🏝️ ☀️ Mauritius Island trip analysis ❤️ 🦤🏝️")

st.subheader("""
    Welcome to this dashboard, we are going to analyze hotel location, score , actual temperature and so on, if you feel like to trip to Mauritius shortly 🛫:
    
    * We choose some of the most famous cities of the island
    * What are the places with the most pleasant weather for you within the next days ?
    * What are the best rated hotels by booking.com user for each city ?
    Let see this right now 😎
    
""")

@st.cache (allow_output_mutation=True)
def load_data():
    list_of_cities = ['Port Louis Mauritius',
    'Vacoas Mauritius',
    'Quatre Bornes Mauritius',
    'Rose Hill Mauritius',
    'Blue Bay Mauritius',
    'Flic en Flac Mauritius',
    'Le Morne Brabant Mauritius',
    'Trou aux Biches Mauritius',
    'Grand baie Mauritius']

    data = pd.DataFrame()
    for i in list_of_cities:
    # Make a request to the API to get the gps data for each city and put them in a df :
        r = requests.get("https://nominatim.openstreetmap.org/search/{}?format=json&addressdetails=1&limit=1".format(i),verify=False)
        data= data.append(r.json())
                
    data_gps = data[['display_name','lon','lat']]
        #extract cities name without the full details to put them in a new column :
    nom_villes = pd.DataFrame(data_gps['display_name'].str.split(',',expand = True))
        
    data_gps['nom_des_villes'] = nom_villes[0]
    data_gps = data_gps[['nom_des_villes','lon','lat']]
    #we take round 2 for the lat & lon in order to find the weather data for each city then:
    data_gps['lon'] = data_gps['lon'].astype(float).round(2)
    data_gps['lat'] = data_gps['lat'].astype(float).round(2)
    return data_gps
data_gps = load_data()

@st.cache (allow_output_mutation=True)
def load_data():
        #we want to fetch weather data for each city thanks to their GPS data:
        #we create an empty df to put in the weather infos for each city:
    datameteo=pd.DataFrame()

    #we make a loop to request the API and get weather info for each city
    for i in range(len(data_gps)):
        lat = data_gps['lat'].values[i]
        lon = data_gps['lon'].values[i]


        url = ('https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units=metric&exclude=hourly,minutely&lang=fr&daily.rain&appid=ca3f2f4db31a746f86984f4983d23752'.format(lat,lon))

        response = requests.get(url)
        datameteo = datameteo.append(response.json(), ignore_index=True)
    return datameteo
datameteo = load_data()

@st.cache(allow_output_mutation=True)
def load_data():
    #we merge both df in order to get the lat,lon & weather infos in one df:
    datamerge = datameteo.merge(data_gps)

    #we reorganize order of the columns:
    datamerge = datamerge[['nom_des_villes','lat','lon','daily']]

    #now let's get all the info needed to put them in a global df:
    list_info = []
    for i in range(0,9):
            list_info.append(datamerge['daily'][i])
    
    list_of_dates = []
    list_of_temp_max = []
    sunrise = []
    sunset =[]
    pop = []
    humidity = []
    rain = []
    for i in range(0,9):
        for j in range(0,8):
            list_of_temp_max.append(list_info[i][j].get('temp').get('max'))
            list_of_dates.append(list_info[i][j].get('dt'))
            sunrise.append(list_info[i][j].get('sunrise'))
            sunset.append(list_info[i][j].get('sunset'))
            pop.append(list_info[i][j].get('pop'))
            humidity.append(list_info[i][j].get('humidity'))
            rain.append(list_info[i][j].get('rain'))

    #put the lists into a df and format them correctly:
    df_global = pd.DataFrame()
    df_global['date'] = list_of_dates
    df_global['date'] = pd.to_datetime(df_global['date'],unit='s').dt.strftime('%B  %d  %Y')   
    df_global['day_of_the_week'] = pd.to_datetime(df_global['date']).dt.day_name()
    df_global['temp_max(°C)'] = list_of_temp_max
    df_global['temp_max(°C)'] =df_global['temp_max(°C)'].astype(float).round(2)
    df_global['sunrise'] = sunrise
    df_global['sunrise'] = pd.to_datetime(df_global['sunrise'], unit='s') + timedelta(hours = 4)
    df_global['sunrise'] = df_global['sunrise'].dt.strftime('%H:%M')
    df_global['sunset'] = sunset
    df_global['sunset'] = pd.to_datetime(df_global['sunset'], unit='s') + timedelta(hours = 4)
    df_global['sunset'] = df_global['sunset'].dt.strftime('%H:%M')
    df_global['pop'] = pop
    df_global['pop'] =df_global['pop'].astype(float).round(2)
    df_global['humidity in %'] = humidity
    df_global['rain'] = rain
    df_global['rain'] = df_global.rain.fillna(0)
    df_global['City'] = 0

 
    #let's add cities names and their gps coord to our df
    list_city = datamerge['nom_des_villes'].tolist()

    for j in range (0,9):
            df_global['City'][j*8:(j*8)+8] = list_city[j]

    df_global['lat'] = 0
    df_global['lon'] = 0

    list_lat = datamerge['lat'].tolist()

    for k in range (0,9):
            df_global['lat'][k*8:(k*8)+8] = list_lat[k]

    list_lon = datamerge['lon'].tolist()
    for l in range (0,9):
            df_global['lon'][l*8:(l*8)+8] = list_lon[l]

    df_global = df_global[['City','day_of_the_week','date','temp_max(°C)','rain','humidity in %','sunrise','sunset','pop','lon','lat']]
    return df_global

df_global = load_data()


st.markdown("---")
st.subheader(' ☀️🌡️ Weather Analysis 🤓 🌦️ ')
st.markdown(""" Now let's focus on weather issue first :

    ->  Let's check some criteria for each city during the next 8 days.
 """)
st.markdown("   ")


date_choice = df_global['date'].unique()
date_selection = st.selectbox("📆 Please select your date :", date_choice)

df_per_day = df_global[df_global['date'] == date_selection].reset_index(drop=True) #on utilise un df avec un choix de date du user

fig = px.scatter_mapbox(df_per_day, lat="lat", lon="lon",zoom=8,size = 'temp_max(°C)', color = 'temp_max(°C)',\
                        mapbox_style="carto-positron",custom_data=['City','temp_max(°C)','pop','humidity in %','rain','sunrise','sunset'])
fig.update_layout(title='Wheater informations in Mauritius for {} of {} : '.format(df_per_day['day_of_the_week'][0],date_selection))
fig.update_traces(
    hovertemplate="<br>".join([
        "City : %{customdata[0]}",
        "Max temperature : %{customdata[1]}°C ",
        "Probability of precipitation : %{customdata[2]}",
        "Humidity : %{customdata[3]}%",
        "Rain : %{customdata[4]} cm",
        "Sunrise: %{customdata[5]}",
        "Sunset: %{customdata[6]} "
    ])
)


st.write(fig)


st.markdown("---")
st.subheader("""Let's see what will be the evolution of weather criteria for each town within the 8 next days.
""")

city_choice = df_global['City'].unique()
city_choice = np.sort(city_choice, axis = 0)
city_selection = st.selectbox("📍Please select your city :", city_choice)

df_per_city = df_global[df_global['City'] == city_selection]

fig2 = px.line(df_per_city, x="date", y=["temp_max(°C)",'pop','humidity in %','rain'], title='Weather infos for {} within the 8 next days'.format(city_selection))
st.write(fig2)



st.markdown("---")
st.subheader("""Let's compare cities evolution of each criteria during the next 8 days """)
criteria_choice = ["temp_max(°C)",'pop','humidity in %','rain']
criteria_choice= np.sort(criteria_choice, axis= 0)
criteria_selection = st.selectbox("🗒️ Please select your criteria :", criteria_choice)


fig1 = px.line(df_global, x="date", y=criteria_selection, color ='City', title='{} within the 8 next days'.format(criteria_selection))
fig1.update_traces(mode='markers+lines',marker=dict(color='red', size=5))
st.write(fig1)




st.markdown("---")
st.subheader(' 🏨 😴 Hotel Analysis 🤓 🛏️ ')
st.markdown("""Let's now focus on booking.com users' reviews to find a good location to stay!

==>  We only keep hotels with rating equals or higher than 8  😎 

Now pick the city you'd rather stay to after the weather analysis and find your best location there !
""")

#let's scrap the data needed with scrapy on booking.com
#due to multithread issue with streamlit we have to use 'os' module
#to put signal on the main thread
@st.cache
def os_use():
    os.system('python run.py')
    return pd.read_json('src/All_Booking_mru.json')

datahotel = os_use()

#let's scrap the hotel gps data with scrapy on booking.com
#due to multithread issue with streamlit we have to use 'os' module
#to put signal on the main thread
@st.cache
def os_use2():
    os.system('python rungps.py')
    return pd.read_json('src/hotel_coord_mru.json')

datahotelgps = os_use2()

#let's put all datas in one well formatted df:
@st.cache (allow_output_mutation=True)
def load_data1():
    datahotelgps =pd.read_json('src/hotel_coord_mru.json')
    datahotelgps = pd.DataFrame(datahotelgps)
    datahotelgps = datahotelgps['lat_lon'].str.split(',',expand=True)
    datahotelgps['Lat_hotel'] = datahotelgps[0]
    datahotelgps['Long_hotel'] = datahotelgps[1]
    datahotelgps = datahotelgps[['Lat_hotel','Long_hotel']]

    data_all_details = pd.read_json('src/All_Booking_mru.json').reset_index()
    data_all_details = pd.DataFrame(data_all_details)

    #we join both dataset in one global df
    data_all =datahotelgps.reset_index().join(data_all_details,on = 'index', lsuffix='_')

    data_all['Score'] = data_all['Score given by the website users']
    data_all = data_all[data_all['Score'] >= 8]
    data_all['Long_hotel'] = data_all['Long_hotel'].astype(float).round(2)
    data_all['Lat_hotel'] = data_all['Lat_hotel'].astype(float).round(2)
    data_all = data_all[['city','hotel_name','url','Score','Lat_hotel','Long_hotel','Text description of the hotel']]

    list_of_cities = ['Port Louis',
    'Quatre Bornes',
    'Rose Hill',
    'Blue Bay',
    'Blue Bay Beach, Blue Bay',
    'Flic-en-Flac',
    'Flic-en-Flac Beach, Flic-en-Flac',
    'Grand Baie',
    'Grand Baie Beach, Grand Baie',
    'Le Morne',
    'Trou aux Biches','Trou Aux Biches Beach, Trou aux Biches']
    data_all= data_all[data_all['city'].isin(list_of_cities)]
    data_all['city'] = data_all['city'].replace({'Grand Baie Beach, Grand Baie':'Grand Baie','Trou Aux Biches Beach, Trou aux Biches':'Trou aux Biches'\
    ,'Blue Bay Beach, Blue Bay':'Blue Bay','Flic-en-Flac Beach, Flic-en-Flac':'Flic-en-Flac'})
    return data_all 

data_all = load_data1()

st.markdown("   ")
city_choice = data_all['city'].unique()
city_choice= np.sort(city_choice, axis= 0)
city_choice_selection = st.selectbox("🏩 Please select your city location 📍:", city_choice)

df_city = data_all[data_all['city'] == city_choice_selection].reset_index(drop=True) #on utilise un df avec un choix de ville du user

fig = px.scatter_mapbox(df_city,lat="Lat_hotel", lon="Long_hotel",zoom=8, size ='Score', color = 'Score',color_continuous_scale='magma' \
    ,mapbox_style="carto-positron", custom_data=['city','hotel_name','Score'])
fig.update_layout(title="Hotels scores in  '{}' area".format(city_choice_selection),
    title_font_family="Times New Roman",
    title_font_color="white",
)
fig.update_traces(
    hovertemplate="<br>".join([
        "City : %{customdata[0]}",
        "Score : %{customdata[2]}",
        "Hotel Name : %{customdata[1]}",
                    ])
)

st.write(fig)

st.write("👨‍✈️ Hope you had a nice trip with us, see you soon 👋")


### Side bar 
st.sidebar.header("Dashboard summary")
st.sidebar.markdown("""
    * [Mauritius Island trip analysis](#mauritius-island-trip-analysis)
    * [Weather Analysis](#weather-analysis)
    * [Hotel Analysis](#hotel-analysis)

    """)
e = st.sidebar.empty()
e.write("Enjoy your trip through this app🌴")
