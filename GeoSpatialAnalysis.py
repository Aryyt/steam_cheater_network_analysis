import pandas as pd
import networkx as nx
import pickle
from graph_generation import get_vac_graph
import matplotlib.pyplot as plt
import numpy as np
from plotnine import ggplot, aes, geom_density, labs, theme_light, scale_y_log10, facet_wrap
from scipy.stats import ks_2samp
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

class GeoSpatialAnalysis:

    def __init__(self, G):
        self.G = G
        self.data = self.load_data()
        self.vac_ban_freqs = self.get_vac_ban_freq()
        self.total_users = self.group_by_country()
        self.geo_data = self.merge_freqs()

    def load_data(self):
        data = pickle.load(open('data/bloomData.pkl', 'rb'))
        loc_data = data.dropna(subset=["loccountrycode"])
        return loc_data

    def get_vac_ban_freq(self):
        loc_data_banned = self.data[self.data['VACBanned'] == True]
        freq_df = loc_data_banned['loccountrycode'].value_counts().reset_index()
        freq_df.columns = ['loccountrycode', 'Frequency']
        return freq_df

    def plot_freq(self,t,col):

        top_t_data = self.geo_data.sort_values(by=col, ascending=False).head(t)

        plt.figure(figsize=(8, 6))
        sns.barplot(data=top_t_data, x="loccountrycode", y=col, palette='viridis')
        plt.title(f'Top {t} Countries with highest number of bans: {col}')
        plt.xlabel('Country')
        plt.ylabel(col)
        plt.legend(title='VACBanned')
        plt.show()

        return plt

    def plot_freq_all(self,t, weight_population = 0.5,  weight_user = 0.5):
        scaler = MinMaxScaler()

        col1 = "Frequency"
        col2 = "relative_frequency_global"
        col3 = "relative_frequency_steam_players"

        data = self.geo_data.copy()

        data['combined_score'] = ((data[col2] * weight_population) + (data[col3] * weight_user))*data[col1]
        top_t_data = data.sort_values(by='combined_score', ascending=False).head(t)

        # Create the plot
        plt.figure(figsize=(10, 6))
        sns.barplot(data=top_t_data, x="loccountrycode", y="combined_score", color='purple', alpha=0.7)

        # Set plot labels and title
        plt.title(f'Top {t} Countries by average_ban_score')
        plt.xlabel('Country')
        plt.ylabel('average_ban_score')
        # plt.legend(title='Frequency Columns')

        plt.tight_layout()
        plt.show()

        return plt

    def plot_normalized_populations(self):
        data = self.geo_data.copy()

        # Normalize cheater and non-cheater populations to real-world population
        data['NormalizedCheaters'] = data["relative_frequency_global"]
        data['NormalizedNonCheaters'] = (data['total players'] - data["relative_frequency_global"]) / data[
            '2022 Population']

        # Sort data by real-world population in descending order
        data = data.sort_values(by='2022 Population', ascending=False)

        # Get top 10 countries by user and cheater populations
        top_user_countries = data.nlargest(10, 'total players')['loccountrycode']
        top_cheater_countries = data.nlargest(10, 'Frequency')['loccountrycode']

        # Get the union of the top countries
        top_countries = set(top_user_countries).union(set(top_cheater_countries))

        # Filter data to include only the top countries
        filtered_data = data[data['loccountrycode'].isin(top_countries)]

        # Plot the data
        plt.figure(figsize=(12, 6))

        # X-axis positions
        x_positions = range(len(filtered_data))

        # Plot stacked bar chart for cheaters and non-cheaters
        plt.bar(x_positions, filtered_data['NormalizedNonCheaters'] * 100,
                label='Non-Cheaters')
        plt.bar(x_positions, filtered_data['NormalizedCheaters'] * 100,
                bottom=filtered_data['NormalizedNonCheaters'] * 100,
                label='Cheaters')

        # Set x-axis labels and ticks
        plt.xticks(x_positions, filtered_data['loccountrycode'], rotation=45, ha='right')

        # Add labels and legend
        plt.xlabel('Country')
        plt.ylabel('Population Percentage (%)')
        plt.title('Cheater vs Non-Cheater Populations by Country')
        plt.legend()

        # Show the plot
        plt.tight_layout()
        plt.show()

    def group_by_country(self):
        total_users = self.data.groupby('loccountrycode').size().reset_index(name="total players")
        return total_users

    def merge_freqs(self):
        population = pd.read_pickle('populations.pkl')
        merged = pd.merge(self.vac_ban_freqs, population, on='loccountrycode', how='inner')
        merged = pd.merge(merged,self.total_users, on = "loccountrycode", how = "inner")
        merged["relative_frequency_global"] = merged["Frequency"]/merged["2022 Population"]
        merged["relative_frequency_steam_players"] = merged["Frequency"] / merged["total players"]
        return merged

