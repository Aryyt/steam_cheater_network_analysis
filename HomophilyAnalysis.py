import pandas as pd
import networkx as nx
import pickle
from graph_generation import get_vac_graph
import matplotlib.pyplot as plt
import numpy as np
from plotnine import ggplot, aes, geom_density, labs, theme_light, scale_y_log10, facet_wrap, geom_line
from scipy.stats import ks_2samp

class HomophilyAnalysis:

    def __init__(self, G, remove_unprocessed = True):

        self.G = self.remove_unconnected_nodes(G)
        if remove_unprocessed:
            self.G = self.remove_unprocessed(self.G)
        self.cheater_proportions, self.noncheater_proportions = self.get_proportions(self.G)
        self.summary = self.create_summary(self.cheater_proportions, self.noncheater_proportions)
        self.density_plot = self.plot_density(self.cheater_proportions, self.noncheater_proportions)
        self.statistic, self.p_value = self.KS_test(self.cheater_proportions, self.noncheater_proportions)
        self.cdf = self.plot_cdf_ccdf(self.cheater_proportions, self.noncheater_proportions)

    def remove_unprocessed(self, G):
        print('Removing unprocessed nodes:')
        nodes_to_include = [n for n, data in G.nodes(data=True) if data.get("label") != "Un-processed"]
        subgraph = G.subgraph(nodes_to_include)
        return subgraph

    def remove_unconnected_nodes(self, G):
        print("Removing unconnected nodes:")
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

        densityplot = (
                ggplot(df, aes(x='value')) +
                geom_density(color='blue', fill='blue', alpha=0.3) +
                facet_wrap('~group', scales='free') +  # Create a separate plot for each group
                theme_light() +
                labs(title="Distribution of Cheater vs Non-Cheater Proportions",
                     x="Proportion",
                     y="Density")
        )

        return densityplot

    def plot_cdf_ccdf(self, cheater_proportions, noncheater_proportions):
        # Prepare data for CDF and CCDF
        df = pd.DataFrame({
            'value': cheater_proportions + noncheater_proportions,
            'group': ['cheaters'] * len(cheater_proportions) + ['non_cheaters'] * len(noncheater_proportions)
        })

        # Compute CDF and CCDF
        df = df.sort_values('value').reset_index(drop=True)
        df['rank'] = df.groupby('group').cumcount() + 1
        df['cdf'] = df['rank'] / df.groupby('group')['rank'].transform('max')
        df['ccdf'] = 1 - df['cdf']

        # Melt the data for faceting
        melted_df = pd.melt(
            df,
            id_vars=['value', 'group'],
            value_vars=['cdf', 'ccdf'],
            var_name='Function',
            value_name='Probability'
        )

        # Create the plot using plotnine
        cdf_ccdf_plot = (
                ggplot(melted_df, aes(x='value', y='Probability', color='group')) +
                geom_line() +
                facet_wrap('~Function', scales='free_y') +  # Create subplots for CDF and CCDF
                theme_light() +
                labs(
                    title="CDF and CCDF of Cheater vs Non-Cheater Proportions",
                    x="Value",
                    y="Probability"
                )
        )

        return cdf_ccdf_plot

    def KS_test(self,cheater_proportions, noncheater_proportions):

        statistic, p_value = ks_2samp(cheater_proportions, noncheater_proportions)
        return statistic, p_value

