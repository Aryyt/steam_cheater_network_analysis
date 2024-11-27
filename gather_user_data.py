import requests
import yaml
import pandas as pd
import random

def get_player_summaries(api_key, steam_ids):
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
    params = {
        'key': api_key,
        'steamids': steam_ids
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data['response']['players']

def get_friend_list(api_key, steam_id, relationship="friend"):
    url = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/'
    params = {
        'key': api_key,
        'steamid': steam_id,
        'relationship': relationship
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('friendslist', {}).get('friends', [])

def get_user_group_list(api_key, steam_id):
    url = 'http://api.steampowered.com/ISteamUser/GetUserGroupList/v1/'
    params = {
        'key': api_key,
        'steamid': steam_id
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('response', {}).get('groups', [])

def get_owned_games(api_key, steam_id):
    url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
    params = {
        'key': api_key,
        'steamid': steam_id,
        'include_appinfo': 1,
        'include_played_free_games': 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('response', {}).get('games', [])

def get_player_bans(api_key, steam_ids):
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/'
    params = {
        'key': api_key,
        'steamids': steam_ids
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('players', [])

def get_recent_playtime(api_key, steam_id):
    url = 'http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/'
    params = {
        'key': api_key,
        'steamid': steam_id
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('response', [])

def get_full_data_on_player(api_key, steam_id):
    
    # Initializubg a dictionary to hold the data
    data_dict = {}
    
    players = get_player_summaries(api_key, steam_id)
    if not players:
        return False
    player = players[0]
    
    # Get SteamID
    id = player.get('steamid', 'Unknown')
    data_dict['steamid'] = id
    
    # Get nickname
    
    nickname = player.get('personaname', 'Unknown')
    data_dict['Nickname'] = nickname
    
    # Determine privacy settings
    visibility_state = player.get('communityvisibilitystate', 0)
    if visibility_state == 3:
        privacy_setting = 'Public'
    elif visibility_state == 1:
        privacy_setting = 'Private'
    else:
        privacy_setting = 'Friends-Only or Other'
    data_dict['Privacy Setting'] = privacy_setting
        
    # Get friends list
    friends = get_friend_list(api_key, steam_id)
    friend_ids = [friend['steamid'] for friend in friends]
    data_dict['Friends List'] = friend_ids
    
    # Get group memberships
    groups = get_user_group_list(api_key, steam_id)
    group_ids = [group['gid'] for group in groups]
    data_dict['Group Memberships'] = group_ids
    
    # Get owned games and gameplay statistics
    games = get_owned_games(api_key, steam_id)
    owned_games = []
    for game in games:
        game_info = {
            'appid': game.get('appid'),
            'name': game.get('name'),
            'playtime_forever_hours': game.get('playtime_forever', 0) / 60  # Convert minutes to hours
        }
        owned_games.append(game_info)
    data_dict['Owned Games'] = owned_games

        
    # Get self-reported geographical location
    country_code = player.get('loccountrycode', 'Unknown')
    state_code = player.get('locstatecode', 'Unknown')
    city_id = player.get('loccityid', 'Unknown')
    data_dict['Country Code'] = country_code
    data_dict['State Code'] = state_code
    data_dict['City ID'] = city_id
    
    # Get cheating status (VAC ban)
    bans = get_player_bans(api_key, steam_id)
    vac_banned = False
    if bans:
        # print(bans)
        vac_banned = bans[0].get('VACBanned', False)
        community_banned = bans[0].get('CommunityBanned', False)
        economy_banned = bans[0].get('EconomyBan', False)
        num_of_vac_bans = bans[0].get('NumberOfVACBans', 0)
        days_since_last_ban = bans[0].get('DaysSinceLastBan', 0)
        num_of_game_bans = bans[0].get('NumberOfGameBans', 'none')
    data_dict['VAC Banned'] = vac_banned
    data_dict['Community Banned'] = community_banned
    data_dict['Economy Banned'] = economy_banned
    data_dict['Num of Vac Bans'] = num_of_vac_bans
    data_dict['Days Since Last Ban'] = days_since_last_ban
    data_dict['Num Of Game Bans'] = num_of_game_bans
    
    df = pd.DataFrame([data_dict])
    return df

def generate_random_steam64_id():
    base_id = 76561197960265728  # Base SteamID64
    account_id = random.randint(0, 2**32 - 1)  # Random 32-bit unsigned integer
    steam64_id = base_id + account_id
    return str(steam64_id)



def main():
    with open("config/api.yaml", "r") as file:
        api = yaml.safe_load(file)
        print(api)
    api_key = api['api']
    
    steam_id = "76561198073475099"
    # df_test = pd.DataFrame()
    # df = get_full_data_on_player(api_key, steam_id) 
    # df2 = get_full_data_on_player(api_key, '76561198028800822') 
    # df_test = pd.concat([df_test, df, df2])
    # df_test.to_csv('./data/test.csv', index=False)
    # print(df_test)
    # for name in df_test.columns:
    #     print(name)
    #     print(df[name])
    
    # Generate random Steam IDs
    # steam_ids = []
    # for _ in range(10000):
    #     id = generate_random_steam64_id()
    #     steam_ids.append(id)
        
        
    # calls = 0
    # hits = 0
    # checked_id = []
    df_initial = pd.read_pickle("./initial_user_sample.pkl")
    print(df_initial)
    print(df_initial[df_initial['steamid'].duplicated() == False])
    print(df_initial[df_initial['VAC Banned'] == True])

    # itter = 0
    # for player_id in steam_ids:
    #     itter += 1
    #     candidate = get_full_data_on_player(api_key, player_id) 
    #     if not isinstance(candidate, pd.DataFrame):
    #         calls += 1
    #     else:
    #         hits += 1
    #         calls += 5
    #         checked_id.append(player_id)
    #         df_initial = pd.concat([df_initial, candidate])
    #     if itter % 50 == 0:
    #         print(itter)
    #     if calls != 0 and calls % 500 == 0:
    #         print("calls made: ", calls)
    #         df_initial.to_pickle("./initial_user_sample.pkl")
    #     if calls == 90000:
    #         break
        
    # df_initial.to_pickle("./initial_user_sample.pkl")
    # print(itter)
    # print(calls)
    # print(hits)
            

if __name__ == "__main__":
    # main()
    with open("config/api.yaml", "r") as file:
        api = yaml.safe_load(file)
        print(api['api'])
