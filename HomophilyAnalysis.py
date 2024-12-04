import pandas as pd
import networkx as nx
import pickle
from graph_generation import get_vac_graph
import matplotlib.pyplot as plt
import numpy as np
from plotnine import ggplot, aes, geom_density, labs, theme_light
from scipy.stats import ks_2samp

class HomophilyAnalysis:

    def __init__(self, G):

        self.G = self.remove_unconnected_nodes(G)
        self.cheater_proportions, self.noncheater_proportions = self.get_proportions(self.G)
        self.summary = self.create_summary(self.cheater_proportions, self.noncheater_proportions)
        self.density_plot = self.plot_density(self.cheater_proportions, self.noncheater_proportions)
        self.statistic, self.p_value = self.KS_test(self.cheater_proportions, self.noncheater_proportions)

    def remove_unconnected_nodes(self, G):

        unconnected_nodes = list(nx.isolates(G))
        G.remove_nodes_from(unconnected_nodes)
        return G

    def cheater_proportion(self, G, node):
        neighbors = G.neighbors(node)
        total_neighbors = 0
        cheater_count = 0
        for neighbor in neighbors:
            total_neighbors += 1
            if G.nodes[neighbor]['status'] == 'Cheater':
                cheater_count += 1
        return cheater_count / total_neighbors

    def get_proportions(self,G):

        # getting the proportions
        node_ids = list(G.nodes)
        cheater_proportions = [self.cheater_proportion(G, node) for node in node_ids if G.nodes[node]['status'] == "Cheater"]
        noncheater_proportions = [self.cheater_proportion(G, node) for node in node_ids if G.nodes[node]['status'] == "Legit"]

        return cheater_proportions, noncheater_proportions

    def create_summary(self, cheater_proportions, noncheater_proportions):

        # summary of data
        df_cheater_proportions = pd.DataFrame(cheater_proportions, columns=['cheater_proportion'])
        df_noncheater_proportions = pd.DataFrame(noncheater_proportions, columns=['noncheater_proportion'])
        # Show summary
        cheater_summary = df_cheater_proportions['cheater_proportion'].describe()
        noncheater_summary = df_noncheater_proportions['noncheater_proportion'].describe()

        summary = pd.concat([cheater_summary,noncheater_summary], axis=1)

        return summary

    def plot_density(self,cheater_proportions, noncheater_proportions):
        # Visualize distribution

        df = pd.DataFrame({
            'value': cheater_proportions + noncheater_proportions,
            'group': ['cheaters'] * len(cheater_proportions) + ['non_cheaters'] * len(noncheater_proportions)
        })

        # Create density plot
        densityplot = (
            ggplot(df, aes(x='value', color='group')) +
            geom_density() +
            theme_light() +
            labs(title="Distribution of the proportion of cheating friends", x="Proportion", y="Density")
        )

        return densityplot

    def KS_test(self,cheater_proportions, noncheater_proportions):

        statistic, p_value = ks_2samp(cheater_proportions, noncheater_proportions)
        return statistic, p_value

