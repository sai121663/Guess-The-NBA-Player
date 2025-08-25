"""This file will contain the backend of the 'Guess the Player' game."""

import requests
import os
import random
from typing import Optional
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import json
from nba_api.stats.endpoints import leagueleaders

# Public variables
# Generates a list[dict] of active and all players respectively
all_players = players.get_players()
unvalid_ids = set()     # Set of player IDs that return an unvalid headhshot
used_players = set()    # Player IDs that have already been used

# Loading the JSON files containing player data
with open('casual_players.json', 'r') as file1:
    casual_data = json.load(file1)

with open('diehard_players.json', 'r') as file2:
    diehard_data = json.load(file2)


class NBAPlayer:
    """Python class for an NBA player."""

    id: int
    full_name: str
    first_name: str
    last_name: str
    category: Optional[str]

    def __init__(self, player_dict: dict):
        self.id = player_dict['id']
        self.full_name = player_dict['full_name']
        self.first_name = player_dict['first_name']
        self.last_name = player_dict['last_name']
        self.category = self.categorize_player()

    # We're abandoning this method FOR NOW
    # def get_nickname(self) -> Optional[str]:
    #     """Return the nickname of the current player."""
    #
    #     url = "https://en.wikipedia.org/wiki/List_of_nicknames_in_basketball"
    #
    #     # Turns the webpage's info into a searchable object
    #     response = requests.get(url)
    #     soup = BeautifulSoup(response.content, 'html.parser')
    #
    #     nickname_lines = soup.select("li")
    #
    #     # Default: saying that the player's nickname doesn't appear on the Wiki page
    #     nickname = None
    #     for line in nickname_lines:
    #         text = line.get_text()  # Extracting the text from the Wiki page
    #
    #         # Checking if the user's name appears in the text
    #         if self.full_name.lower() in text.lower():
    #             nicknames_list = re.search(r'–\s*"([^"]+)"', text)  # Searching for a list of nicknames using '-'
    #
    #             if nicknames_list:
    #                 nickname = nicknames_list.group(1).strip()
    #
    #     return nickname

    def categorize_player(self) -> Optional[str]:
        """Return whether the NBA player's level is CASUAL, DIEHARD, or None."""

        career = playercareerstats.PlayerCareerStats(player_id=self.id)   # Fetching player's career stats
        table = career.get_data_frames()[0]     # Transforming the data into a readable table

        # Return None if the dataframe is empty (e.g. the player didn't play any official games)
        if table.empty:
            return None

        # Calculate the player's career PPG
        total_points = table['PTS'].sum()
        total_games = table['GP'].sum()

        # Get the last season of the player
        # [:4] only takes the first 4 characters (e.g. '1995-96' would be counted as '1995')
        last_season = int(table['SEASON_ID'].iloc[-1][:4])

        if total_games > 0:
            career_ppg = total_points / total_games
        else:
            career_ppg = 0

        if (last_season > 1995 and career_ppg > 18) or (last_season > 2015 and total_games > 1200):
            return "casual"

        elif last_season > 2015 and career_ppg < 8 and total_games >= 82:
            return "diehard"

        else:
            return None


def get_player(mode: str) -> NBAPlayer:
    """Return an NBAPlayer instance of a random player, based on whether the user selected CASUAL or DIEHARD."""

    while True:

        # From the JSON files containing CASUAL or DIEHARD players, this randomly selects a dict representing a
        # SINGLE player (e.g. {'id': ..., 'full_name': ..., ...})
        if mode == "casual":
            random_player = random.choice(casual_data)
        else:
            random_player = random.choice(diehard_data)

        # Checking if the player was already USED or their headshot was INVALID
        if random_player['id'] in unvalid_ids or random_player['id'] in used_players:
            continue

        curr_player = NBAPlayer(random_player)

        # Automatically downloads the player's headshot
        # If the headshot isn't downloaded, try again
        if download_headshot(curr_player.id):
            used_players.add(curr_player.id)
            return curr_player
        else:
            unvalid_ids.add(curr_player.id)


def get_options(curr_name: str) -> list[str]:
    """Return a list of 4 UNIQUE options for each question."""

    options = [curr_name]

    # Keep adding players' names to the list until we have 4 options
    while len(options) < 4:
        random_choice = random.choice(all_players)
        if random_choice['full_name'] not in options:
            options.append(random_choice['full_name'])

    random.shuffle(options)     # Shuffle the order of the options
    return options


def download_headshot(player_id: int) -> bool:
    """Downloading an image of a player's headshot, based on their ID."""

    url = f'https://cdn.nba.com/headshots/nba/latest/260x190/{player_id}.png'

    # Retrieves bytes of data from the URL
    response = requests.get(url)
    response.raise_for_status()     # Checks if the website returns an error message

    # If the size of the image data is less than 5000, it's likely a blank placeholder image
    # Hence, we want to select a different player
    if len(response.content) < 5000:
        return False

    # If there is an image already named 'curr_player' in the file, delete it
    if os.path.exists('curr_player.jpg'):
        os.remove('curr_player.jpg')

    # Converts the data into an image named "curr_player.jpg"
    with open('curr_player.jpg', 'wb') as image:
        image.write(response.content)

    return True


def update_casual_players() -> None:
    """Store players that are categorized as CASUAL into a permanent JSON file."""

    casual_player_pool = []

    for year in range(1990, 2025):

        # Getting the current season (e.g. 1995-1996)
        curr_season = f"{year}-{str(year + 1)[-2:]}"

        stat_leaders = leagueleaders.LeagueLeaders(season=curr_season)
        table = stat_leaders.get_data_frames()[0]

        # Takes the top 10 leaders in TOTAL POINTS & turns their player IDs into a set
        # (e.g. [1628983, 1630162, 203999, 203507, 1628369])
        top_scorers_ids = table.iloc[:10]["PLAYER_ID"].tolist()

        # Turns a list of IDs into a list of player dictionaries
        # (e.g. [955, ...] -> [{'id': 955, 'full_name': 'Samaki Walker', ...}, ...]
        top_scorers_by_dict = [create_player_with_id(id_num) for id_num in top_scorers_ids]

        casual_player_pool.extend(top_scorers_by_dict)

    with open("casual_players.json", "w") as file:
        json.dump(casual_player_pool, file)


def update_diehard_players() -> None:
    """Store players that are categorized as DIEHARD into a permanent JSON file."""

    diehard_player_pool = []
    seasons_done = 0    # Testing purposes

    for year in range(1990, 2025):

        curr_season = f"{year}-{str(year + 1)[-2:]}"

        stat_leaders = leagueleaders.LeagueLeaders(season=curr_season)
        table = stat_leaders.get_data_frames()[0]

        # Fetching players that are ranked in the MIDDLE tier on the total scoring list
        # (e.g. If 500 players played in a particular season, we'd get the players ranking from 245 to 255)
        mid_index = len(table) // 2
        mid_scorers_ids = table.iloc[mid_index - 5: mid_index + 5]['PLAYER_ID'].tolist()

        mid_scorers_by_dict = [create_player_with_id(id_num) for id_num in mid_scorers_ids]

        diehard_player_pool.extend(mid_scorers_by_dict)

        seasons_done += 1
        print(seasons_done)

    with open("diehard_players.json", "w") as file:
        json.dump(diehard_player_pool, file)


def create_player_with_id(player_id: int) -> Optional[NBAPlayer]:
    """Return the dict of the player with the matching ID."""

    for player in all_players:

        if player['id'] == player_id:
            return player

    return None


    # INSTRUCTIONS:
    # - Create separate methods to fetch CASUAL and DIEHARD players
    # - To get casual players, find the league leaders in stats for each season since 2000 & randomize their order
    # - https://chatgpt.com/c/689132db-d184-8009-abfc-fb09696c6cc8


# ERROR:
# - When running Frontend.py, there are cases where player.full_name is a player that doesn't appear in the all_players
# list
# INSTRUCTIONS:
#
