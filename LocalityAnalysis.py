import networkx as nx
import pandas as pd
import pickle
import math
import numpy as np
from plotnine import ggplot, aes, geom_line, labs, theme_minimal, scale_color_manual

coordinates_df = pd.read_pickle('./coordinates.pkl')
coordinates_df = coordinates_df.dropna(axis=0, how='any')

def haversine(country1, country2):
    if country1 == country2:
        return 0
    if country1 in coordinates_df["loccountrycode"].values and country2 in coordinates_df["loccountrycode"].values:
        lat1 = coordinates_df[coordinates_df["loccountrycode"] == country1]['Latitude'].values[0]
        lon1 = coordinates_df[coordinates_df['loccountrycode'] == country1]['Longitude'].values[0]
        lat2 = coordinates_df[coordinates_df['loccountrycode'] == country2]['Latitude'].values[0]
        lon2 = coordinates_df[coordinates_df['loccountrycode'] == country2]['Longitude'].values[0]

        # Radius of the Earth in kilometers
        R = 6371.0

        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Differences in coordinates
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Haversine formula
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Distance in kilometers
        distance = R * c
        return distance

    return None

class LocalityAnalysis(object):

    def __init__(self, generate = False, sample = False):
        if generate:
            if sample:
                self.G = self.ExtractLocalNetwork_sample()
            else:
                self.G = self.ExtractLocalNetwork()
        else:
            if sample:
                self.G = self.LoadLocalNetwork_sample()
            else:
                self.G = self.LoadLocalNetwork()

        self.CheatertoCheaterNetwork = self.separate_cheaters()
        self.CommunityLocality, self.CheaterNodesLocality, self.Duvs_community, self.Duvs_cheaters = self.calculate_node_locality(self.G)
        self.CheaterOnlyLocality, _, self.Duvs_cheatersOnly, _= self.calculate_node_locality(self.CheatertoCheaterNetwork)
        self.NLSummary = self.NodeLocalitySummary()
        self.cdf_plot = self.plot_cdf()


    def separate_cheaters(self):
        subgraph = [node for node, attributes in self.G.nodes(data=True) if attributes.get('status') == 'Cheater']
        return self.G.subgraph(subgraph)

    def calculate_node_locality(self, G):
        try:
            # Precompute all pairwise shortest path lengths using Dijkstra's algorithm for weighted graphs
            all_distances = dict(nx.all_pairs_dijkstra_path_length(G, weight='distance'))

        except nx.NetworkXError:
            print("NetworkX Error")
            return None
        print("Done precomputing node locality")
        # Collect all d_uv distances for finding d_max
        DUV = []
        for u in G.nodes():
            friends = list(G.neighbors(u))
            DUV.extend([all_distances[u].get(v, float('inf')) for v in friends])

        # Determine d_max from all distances
        d_max = max(DUV) if DUV else float('inf')  # Select maximum from DUV list

        # Initialize dictionaries for locality calculations
        node_locality = {}
        node_locality_cheaters = {}
        DUV_cheaters = []

        # Iterate over all nodes to compute locality
        for u in G.nodes():
            friends = list(G.neighbors(u))
            k_u = len(friends)  # Degree of the node
            if k_u == 0:  # If no friends, locality is undefined or set to 0
                node_locality[u] = 0
                continue

            # Compute locality for node u based on precomputed distances
            locality_sum = 0
            for v in friends:
                d_uv = all_distances[u].get(v, float('inf'))  # Fetch precomputed distance
                locality_sum += (d_max - d_uv) / d_max if d_max > 0 else 0
                if G.nodes[u]['status'] == 'Cheater':
                    DUV_cheaters.append(d_uv)

            # Calculate NL(u)
            node_locality[u] = locality_sum / k_u

            # Special handling for cheaters
            if G.nodes[u]['status'] == 'Cheater':
                node_locality_cheaters[u] = locality_sum / k_u

        return node_locality, node_locality_cheaters, DUV, DUV_cheaters

    def NodeLocalitySummary(self):

        community = ["Steam Community",
                     len(self.G.nodes),
                     len(self.G.edges),
                     np.mean(self.Duvs_community),
                     sum(data['distance'] for u, v, data in self.G.edges(data=True))/len(self.G.edges),
                     np.mean(list(self.CommunityLocality.values()))]

        cheaters = ["Steam Community - Cheaters",
                    sum(1 for node, data in self.G.nodes(data=True) if data.get("status") == "Cheater"),
                    np.NaN,
                    np.mean(self.Duvs_cheaters),
                    sum(data['distance'] for u, v, data in self.G.edges(data=True))/len(self.G.edges),
                    np.mean(list(self.CheaterNodesLocality.values()))]

        cheaters_to_cheaters = ["Cheater-to-Cheater",
                                sum(1 for node, data in self.CheatertoCheaterNetwork.nodes(data=True) if data.get("status") == "Cheater"),
                                len(self.CheatertoCheaterNetwork.edges),
                                np.mean(self.Duvs_cheatersOnly),
                                sum(data['distance'] for u, v, data in self.CheatertoCheaterNetwork.edges(data=True))/len(self.CheatertoCheaterNetwork.edges),
                                np.mean(list(self.CheaterOnlyLocality.values()))]
        data = [community, cheaters, cheaters_to_cheaters]
        columns=["Network", "# of Nodes", "# of Edges", "Avg Dist uv", "Avg link length", "Node Locality"]

        summary = pd.DataFrame(data, columns=columns)

        return summary

    def plot_cdf(self):
        # Sort the data to compute the CDF
        sorted_community = np.sort(list(self.CommunityLocality.values()))
        sorted_cheater = np.sort(list(self.CheaterNodesLocality.values()))
        sorted_cheater_only = np.sort(list(self.CheaterOnlyLocality.values()))

        # Compute the CDFs
        cdf_community = np.arange(1, len(sorted_community) + 1) / len(sorted_community)
        cdf_cheater = np.arange(1, len(sorted_cheater) + 1) / len(sorted_cheater)
        cdf_cheater_only = np.arange(1, len(sorted_cheater_only) + 1) / len(sorted_cheater_only)

        # Create a DataFrame for ggplot
        df_community = pd.DataFrame({'value': sorted_community, 'cdf': cdf_community, 'distribution': 'Whole Network'})
        df_cheater = pd.DataFrame({'value': sorted_cheater, 'cdf': cdf_cheater, 'distribution': 'Whole Network: Cheaters'})
        df_cheater_only = pd.DataFrame(
            {'value': sorted_cheater_only, 'cdf': cdf_cheater_only, 'distribution': 'Cheater to Cheater Network'})

        # Combine all DataFrames into one
        df_all = pd.concat([df_community, df_cheater, df_cheater_only])

        # Create the CDF plot using ggplot
        plot = (ggplot(df_all, aes(x='value', y='cdf', color='distribution'))
                + geom_line()
                + labs(title='CDF of node locality', x='Node Locality', y='CDF')
                + scale_color_manual(values=['blue', 'green', 'red'])
                + theme_minimal())

        # Show the plot
        return plot

    def check_status(self, ban_status: bool):
        if ban_status == True:
            return 'Cheater'
        return 'Legit'

    def ExtractLocalNetwork(self):
        import networkx as nx
        import pandas as pd

        # Create an empty graph
        G = nx.Graph()

        # Load and filter data
        df_full_data = pd.read_pickle('./locnetData.pkl')
        df_full_data = df_full_data[df_full_data["friendsList"].apply(lambda x: len(x) > 0)]

        # Create mappings for faster lookups
        id_set = set(df_full_data['SteamId'])
        id_to_attributes = df_full_data.set_index('SteamId').to_dict('index')

        for _, row in df_full_data.iterrows():
            current_id = row['SteamId']
            vac_banned = row['VACBanned']
            country = row['loccountrycode']
            status = self.check_status(vac_banned)

            # Add the current node
            G.add_node(current_id, status=status, country=country)

            # Process unique friends in the friends list
            unique_friends = set(friend['steamid'] for friend in row['friendsList'] if isinstance(friend, dict) and 'steamid' in friend)
            for friend in unique_friends:
                if friend in id_set:
                    # Get friend's attributes
                    friend_attributes = id_to_attributes[friend]
                    friend_ban_status = friend_attributes['VACBanned']
                    friend_status = self.check_status(friend_ban_status)
                    friend_country = friend_attributes['loccountrycode']

                    # Add friend node and edge
                    G.add_node(friend, status=friend_status, country=friend_country)
                    distance = haversine(country, friend_country)
                    if distance is not None:
                        G.add_edge(current_id, friend, edge_type='friend', distance=distance)

            # Uncomment the following block if you want to process friends not in id_set
            # else:
            #     G.add_node(friend, status='Not Processed')
            #     G.add_edge(current_id, friend, edge_type='friend')

        isolated_nodes = [node for node in G.nodes if G.degree(node) == 0]
        G.remove_nodes_from(isolated_nodes)
        # Save the graph to a file
        nx.write_gexf(G, "./data/local_network.gexf")
        print('Done')
        return G

    def ExtractLocalNetwork_sample(self):

        # Create an empty graph
        G = nx.Graph()

        # Load and filter data
        df_full_data = pd.read_pickle('./locnetData.pkl')
        df_full_data = df_full_data[df_full_data["friendsList"].apply(lambda x: len(x) > 0)]
        df_full_data = df_full_data.sample(frac=0.3, random_state=0)

        # Create mappings for faster lookups
        id_set = set(df_full_data['SteamId'])
        id_to_attributes = df_full_data.set_index('SteamId').to_dict('index')

        for _, row in df_full_data.iterrows():
            current_id = row['SteamId']
            vac_banned = row['VACBanned']
            country = row['loccountrycode']
            status = self.check_status(vac_banned)

            # Add the current node
            G.add_node(current_id, status=status, country=country)

            # Process unique friends in the friends list
            unique_friends = set(friend['steamid'] for friend in row['friendsList'] if isinstance(friend, dict) and 'steamid' in friend)
            for friend in unique_friends:
                if friend in id_set:
                    # Get friend's attributes
                    friend_attributes = id_to_attributes[friend]
                    friend_ban_status = friend_attributes['VACBanned']
                    friend_status = self.check_status(friend_ban_status)
                    friend_country = friend_attributes['loccountrycode']

                    # Add friend node and edge
                    G.add_node(friend, status=friend_status, country=friend_country)
                    distance = haversine(country, friend_country)
                    if distance is not None:
                        G.add_edge(current_id, friend, edge_type='friend', distance=distance)

            # Uncomment the following block if you want to process friends not in id_set
            # else:
            #     G.add_node(friend, status='Not Processed')
            #     G.add_edge(current_id, friend, edge_type='friend')

        isolated_nodes = [node for node in G.nodes if G.degree(node) == 0]
        G.remove_nodes_from(isolated_nodes)
        # Save the graph to a file
        nx.write_gexf(G, "./data/local_network.gexf")
        print('Done')
        return G

    def LoadLocalNetwork(self):
        G = nx.read_gexf("./data/local_network.gexf")
        return G

    def LoadLocalNetwork_sample(self):
        G = nx.read_gexf("./data/local_network_sample.gexf")
        return G






