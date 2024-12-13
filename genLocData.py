import requests
import pandas as pd

def get_country_coordinates(country_code, type):
    # GeoNames API endpoint for retrieving country information
    url = f"http://api.geonames.org/countryInfoJSON"
    username = 'cristinaafanasii'
    params = {
        'lang': 'en',  # Language of the response (optional)
        'country': country_code,  # Country code (Alpha-2 country code)
        'username': username  # Your GeoNames username
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        if 'geonames' in data and len(data['geonames']) > 0:
            geoname = data['geonames'][0]

            if type == 'Longitude':
                east = geoname['east']
                west = geoname['west']

                # Calculate central coordinates (latitude and longitude)

                central_longitude = (west + east) / 2

                return central_longitude

            if type == 'Latitude':
                south = geoname['south']
                north = geoname['north']

                central_latitude = (south + north) / 2

                return central_latitude

        else:
            print(f"No data found for {country_code}.")
            return None
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None

def gen_loc_data():
    df_full_data = pd.read_pickle('./data/BloomData.pkl')
    loc_network_data = df_full_data[df_full_data["loccountrycode"].notna()]
    loc_network_data = loc_network_data[["SteamId", "VACBanned", "friendsList", "loccountrycode"]]

    lng_lat_df = pd.DataFrame(loc_network_data["loccountrycode"].unique(), columns=["loccountrycode"])
    lng_lat_df["Longitude"] = lng_lat_df["loccountrycode"].apply(lambda x: get_country_coordinates(x, "Latitude"))
    lng_lat_df["Latitude"] = lng_lat_df["loccountrycode"].apply(lambda x: get_country_coordinates(x, "Longitude"))

    lng_lat_df.to_pickle('coordinates.pkl')
    loc_network_data.to_pickle('locnetData.pkl')