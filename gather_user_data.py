import requests
import yaml

def get_friend_list(api_key, steam_id):
    url = "http://api.steampowered.com/ISteamUser/GetFriendList/v1/"
    params = {
        'key': api_key,
        'steamid': steam_id,
        'relationship': 'friend'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def get_player_summaries(api_key, steam_ids):
    url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {
        'key': api_key,
        'steamids': ','.join(steam_ids)
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def get_player_bans(api_key, steam_ids):
    url = "http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/"
    params = {
        'key': api_key,
        'steamids': ','.join(steam_ids)
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def get_owned_games(api_key, steam_id):
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        'key': api_key,
        'steamid': steam_id,
        'include_appinfo': 1,
        'include_played_free_games': 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def main():
    api_key = ""
    steam_id = "76561198073475099"
    
    # Get friend list
    friend_list_data = get_friend_list(api_key, steam_id)
    if 'friendslist' in friend_list_data:
        friend_ids = [friend['steamid'] for friend in friend_list_data['friendslist']['friends']]
        print(f"Number of Friends: {len(friend_ids)}")
    else:
        friend_ids = []
        print("Could not retrieve friend list. The user's friend list may be private.")
    
    # Get player summaries
    player_summary_data = get_player_summaries(api_key, [steam_id])
    if 'response' in player_summary_data and 'players' in player_summary_data['response']:
        player_info = player_summary_data['response']['players'][0]
        country_code = player_info.get('loccountrycode', 'N/A')
        print(f"User's Country Code: {country_code}")
    else:
        print("Could not retrieve player summaries.")
    
    # Get player bans
    player_bans_data = get_player_bans(api_key, [steam_id])
    if 'players' in player_bans_data:
        ban_info = player_bans_data['players'][0]
        print("User's Ban Information:")
        print(f"VAC Banned: {ban_info['VACBanned']}")
        print(f"Number of VAC Bans: {ban_info['NumberOfVACBans']}")
        print(f"Days Since Last Ban: {ban_info['DaysSinceLastBan']}")
        print(f"Community Banned: {ban_info['CommunityBanned']}")
        print(f"Economy Ban: {ban_info['EconomyBan']}")
    else:
        print("Could not retrieve ban information.")
    
    # Get owned games
    owned_games_data = get_owned_games(api_key, steam_id)
    if 'response' in owned_games_data and 'games' in owned_games_data['response']:
        games = owned_games_data['response']['games']
        print(f"Number of Owned Games: {len(games)}")
        for game in games:
            print(f"Game Name: {game['name']}, Playtime Forever: {game['playtime_forever']} minutes")
    else:
        print("Could not retrieve owned games. The user's game library may be private.")
    
    # Get friends' country codes and ban statuses
    if friend_ids:
        print("\nFriends' Information:")
        for i in range(0, len(friend_ids), 100):
            batch_ids = friend_ids[i:i+100]
            friend_summaries = get_player_summaries(api_key, batch_ids)
            friend_bans = get_player_bans(api_key, batch_ids)
            if 'response' in friend_summaries and 'players' in friend_summaries['response']:
                summaries = {player['steamid']: player for player in friend_summaries['response']['players']}
            else:
                summaries = {}
            if 'players' in friend_bans:
                bans = {player['SteamId']: player for player in friend_bans['players']}
            else:
                bans = {}
            for steamid in batch_ids:
                summary = summaries.get(steamid, {})
                ban = bans.get(steamid, {})
                persona_name = summary.get('personaname', 'Unknown')
                country_code = summary.get('loccountrycode', 'N/A')
                vac_banned = ban.get('VACBanned', 'N/A')
                number_of_vac_bans = ban.get('NumberOfVACBans', 'N/A')
                days_since_last_ban = ban.get('DaysSinceLastBan', 'N/A')
                print(f"Friend: {persona_name} ({steamid})")
                print(f"  Country Code: {country_code}")
                print(f"  VAC Banned: {vac_banned}")
                print(f"  Number of VAC Bans: {number_of_vac_bans}")
                print(f"  Days Since Last Ban: {days_since_last_ban}")
    else:
        print("No friends to display.")

if __name__ == "__main__":
    # main()
    with open("config/api.yaml", "r") as file:
        api = yaml.safe_load(file)
        print(api['api'])
