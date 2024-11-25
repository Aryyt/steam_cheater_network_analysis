import requests
import yaml
import pandas as pd
import pickle

def get_player_summaries(api_key, steam_ids):
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
    params = {
        'key': api_key,
        'steamids': steam_ids
    }
    response = requests.get(url, params=params)
    if (response.status_code == 429):
        print("rate limit reached")
        return None
    elif (response.status_code != 200):
        print("Error: ", response.status_code)
        return None
    data = response.json()
    return data['response']['players']

def get_friend_list(api_key, steam_id):
    url = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/'
    params = {
        'key': api_key,
        'steamid': steam_id,
        'relationship': 'friend'
    }
    response = requests.get(url, params=params)
    if (response.status_code == 429):
        print("rate limit reached")
        return None
    elif (response.status_code != 200):
        print("Error: ", response.status_code)
        return None
    data = response.json()
    return data.get('friendslist', {}).get('friends', [])

def get_user_group_list(api_key, steam_id):
    url = 'http://api.steampowered.com/ISteamUser/GetUserGroupList/v1/'
    params = {
        'key': api_key,
        'steamid': steam_id
    }
    response = requests.get(url, params=params)
    if (response.status_code == 429):
        print("rate limit reached")
        return None
    elif (response.status_code != 200):
        print("Error: ", response.status_code)
        return None
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
    if (response.status_code == 429):
        print("rate limit reached")
        return None
    elif (response.status_code != 200):
        print("Error: ", response.status_code)
        return None
    data = response.json()
    return data.get('response', {}).get('games', [])

def get_player_bans(api_key, steam_ids):
    url = 'http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/'
    params = {
        'key': api_key,
        'steamids': steam_ids
    }
    response = requests.get(url, params=params)
    if (response.status_code == 429):
        print("rate limit reached")
        return None
    elif (response.status_code != 200):
        print("Error: ", response.status_code)
        return None
    data = response.json()
    return data.get('players', [])

def get_full_data_on_player(api_key, steam_id):
    
    # Initializubg a dictionary to hold the data
    data_dict = {}
    
    players = get_player_summaries(api_key, steam_id)
    if players == None:
        return None
    if not players:
        return None
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
    if friends == None:
        return None
    friend_ids = [friend['steamid'] for friend in friends]
    data_dict['Friends List'] = friend_ids
    
    # Get group memberships
    groups = get_user_group_list(api_key, steam_id)
    if groups == None:
        return None
    group_ids = [group['gid'] for group in groups]
    data_dict['Group Memberships'] = group_ids
    
    # Get owned games and gameplay statistics
    games = get_owned_games(api_key, steam_id)
    if games == None:
        return None
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
    if bans == None:
        return None
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


def main():
    with open("config/api.yaml", "r") as file:
            api = yaml.safe_load(file)
            api_key = api['api']
        
    df_full_data = pd.read_pickle('./data/full_user_data.pkl')
    print(df_full_data)
    
    queue_path = "./data/queue.pkl"
    err_path = "./data/errors.pkl"
    
    with open(queue_path, "rb") as pkl:
        queue = pickle.load(pkl)
    itter = 0
    calls = 0
    good_response = True
    print(len(queue))
    c = get_full_data_on_player(api_key, queue[1])
    print(c)
    while good_response:
        
        skip = False
        itter += 1
        id = queue.pop(0)
        candidate = get_full_data_on_player(api_key, id)
        calls += 5
        
        # reqquest fails
        if not isinstance(candidate, pd.DataFrame):
            with open(err_path, "rb") as pkl:
                err = pickle.load(pkl)
            err.append(id)
            with open(err_path, "wb") as pkl:
                pickle.dump(err, pkl)
            
            with open(queue_path, "wb") as pkl:
                pickle.dump(queue, pkl)
            df_full_data.to_pickle('./data/full_user_data.pkl')
            skip = True
            
        # print(candidate)
        # Add freinds to the queue
        if skip == False:
            id_list = df_full_data['steamid']
            for friend in candidate['Friends List'].iloc[0]:
                if friend not in id_list.unique():
                    # print('hit')
                    queue.append(friend)
                
            # Concatonate dataframes
            df_full_data = pd.concat([df_full_data, candidate])
        
        # Print iteration every 50 iterations
        if itter % 50 == 0:
            print(itter)

        # Save and print every 500 calls
        if calls != 0 and calls % 500 == 0:
            with open(queue_path, "wb") as pkl:
                pickle.dump(queue, pkl)
            
            print("calls made: ", calls)
            df_full_data.to_pickle('./data/full_user_data.pkl')
        if calls == 100000:
            with open(queue_path, "wb") as pkl:
                pickle.dump(queue, pkl)
            
            print("calls made: ", calls)
            df_full_data.to_pickle('./data/full_user_data.pkl')
            break
            
    with open(queue_path, "wb") as pkl:
        pickle.dump(queue, pkl)
    df_full_data.to_pickle('./data/full_user_data.pkl')
            
        
    
if __name__ == "__main__":
    main()


# err = []
# err_path = "./data/errors.pkl"
# with open(err_path, "wb") as pkl:
#         pickle.dump(err, pkl)




# queue = []
# df = pd.read_pickle('./data/full_user_data.pkl')

# for friends in df['Friends List']:
#     for friend in friends:
#         queue.append(friend)
        
# queue_path = "./data/queue.pkl"

# with open(queue_path, "rb") as pkl:
#     l = pickle.load(pkl)
    
# print(l)







# MAYBE USEFULL FOR THE FUTURE


# id_list = df['steamid']
# print(id_list)
# # print(df.iloc[2])
# id = df.iloc[2]['steamid']
# friends2 = df.iloc[2]['Friends List']
# print(friends2, id)

# print('sampled user in ids: ', id in id_list.unique())
# print('first freind in ids: ', friends2[0] in id_list.unique())

# queue = []

# with open(queue_path, "a") as pkl:
#     pickle.dump(queue, pkl)
# queue_path = "./data/queue.pkl"
# with open(queue_path, "a") as pkl:
#     pickle.dump(queue, pkl)
    
# with open(queue_path, "a") as pkl:
#     queue = pickle.load(pkl)
# print(queue)


    
