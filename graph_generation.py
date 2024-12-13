import networkx as nx
import pandas as pd
import pickle


# df_full_data = pd.read_pickle('./data/full_user_data.pkl')

# print(df_full_data[df_full_data['steamid'] == '76561199776871995']['VAC Banned'].iloc[0])

def check_status(ban_status: bool):
    if ban_status == True:
        return 'Cheater'
    return 'Legit'


# Deprecated
def generate_vac_graph_only():
    G = nx.Graph()
    df_full_data = pd.read_pickle('./data/full_user_data.pkl')

    id_list = df_full_data['steamid']

    for _, row in df_full_data.iterrows():
        current_id = row['steamid']
        vac_banned = row['VAC Banned']

        status = check_status(vac_banned)

        G.add_node(current_id, status=status)

        for friend in row["Friends List"]:

            if friend in id_list.unique():

                friend_ban_status = df_full_data[df_full_data['steamid'] == friend]['VAC Banned'].iloc[0]
                friend_status = check_status(friend_ban_status)
                G.add_node(friend, status=friend_status)
                G.add_edge(current_id, friend, edge_type='friend')

            else:
                G.add_node(friend, status='Not Processed')
                G.add_edge(current_id, friend, edge_type='friend')
    nx.write_gexf(G, "./data/tennative_graph.gexf")
    print('Done')
    return G


# Deprecated
def generate_vac_graph_only_processed():
    G = nx.Graph()
    df_full_data = pd.read_pickle('./data/full_user_data.pkl')

    id_list = df_full_data['steamid']

    for _, row in df_full_data.iterrows():
        current_id = row['steamid']
        vac_banned = row['VAC Banned']

        status = check_status(vac_banned)

        G.add_node(current_id, status=status)

        for friend in row["Friends List"]:

            if friend in id_list.unique():
                friend_ban_status = df_full_data[df_full_data['steamid'] == friend]['VAC Banned'].iloc[0]
                friend_status = check_status(friend_ban_status)
                G.add_node(friend, status=friend_status)
                G.add_edge(current_id, friend, edge_type='friend')
    print('Done')
    nx.write_gexf(G, "data/tennative_graph_only_processed_new.gexf")
    return G


def get_vac_graph() -> nx.Graph:
    with open('data/tennative_graph_only_processed_new.gexf', "rb") as dataPickle:
        G = nx.read_gexf('data/tennative_graph_only_processed_new.gexf')
    return G


def get_vac_graph_graphml() -> nx.Graph:
    with open('data/final.graphml', "rb") as dataPickle:
        G = nx.read_graphml('data/final.graphml')
    return G


def get_vac_graph_graphml_sample() -> nx.Graph:
    with open('data/final_sample.graphml', "rb") as dataPickle:
        G = nx.read_graphml('data/final_sample.graphml')
    return G



def ExtractNetwork():

    # Create an empty graph
    G = nx.Graph()

    # Load and filter data
    df_full_data = pd.read_pickle('data/bloomData.pkl')
    df_full_data = df_full_data[df_full_data["friendsList"].apply(lambda x: len(x) > 0)]

    # Create mappings for faster lookups
    id_set = set(df_full_data['SteamId'])
    id_to_attributes = df_full_data.set_index('SteamId').to_dict('index')

    for _, row in df_full_data.iterrows():
        current_id = row['SteamId']
        vac_banned = row['VACBanned']
        status = check_status(vac_banned)

        # Add the current node
        G.add_node(current_id, status=status)

        # Process unique friends in the friends list
        unique_friends = set(friend['steamid'] for friend in row['friendsList'] if isinstance(friend, dict) and 'steamid' in friend)
        for friend in unique_friends:
            if friend in id_set:
                # Get friend's attributes
                friend_attributes = id_to_attributes[friend]
                friend_ban_status = friend_attributes['VACBanned']
                friend_status = check_status(friend_ban_status)

                # Add friend node and edge
                G.add_node(friend, status=friend_status)
                G.add_edge(current_id, friend, edge_type='friend')

        # Uncomment the following block if you want to process friends not in id_set
        # else:
        #     G.add_node(friend, status='Not Processed')
        #     G.add_edge(current_id, friend, edge_type='friend')

    # Save the graph to a file
    nx.write_gexf(G, "./data/optimized_net.gexf")
    print('Done')
    return G

    
