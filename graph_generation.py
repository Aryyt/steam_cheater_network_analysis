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

    
