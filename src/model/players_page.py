from bs4 import BeautifulSoup
import requests

from model.player import Player


class PlayersPage:
    ''' This class manages one page with footbal players from transfermarkt.com '''

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

    class SortType:
        NONE = 0
        ASC = 1
        DESC = 2

    def __init__(self, app_config):
        ''' Constructs PlayersPage instance

        Parameters
        ----------
            app_config : AppConfig
                Instance of application configuration file.
        '''

        self.config = app_config.transfermarkt
        self.url = self.config['baseUrl'] + self.config['playersPageUrl']
        self._players_on_page = self.config['playersOnPage']

    def players_on_page(self):
        ''' Returns number of players on the page. '''

        return self._players_on_page

    def download(self, page_number=1, sort_type=SortType.DESC):
        ''' Downloads and parses all the footbal players from the given page.

        Parameters
        ----------
            page_nubmer : int
                number of the page to download.

            sorted : SortType
                How to sort the data.

        Returns
        -------
            List of the Player instances parsed from downloaded page.

        '''

        # Generate URL accordgin to the input arguments
        url = self.url + '?' + self.config['ajaxArg']

        url += '&' + 'page={}'.format(page_number)

        # Append sort type
        if sort_type == PlayersPage.SortType.DESC:
            url += '&' + self.config['sortDescArg']
        elif sort_type == PlayersPage.SortType.ASC:
            url += '&' + self.config['sortAscArg']

        # Perform request and parse the response
        soup = self.__download_page(url)
        player_items = soup.findAll('tr', {'class': ['even', 'odd']})

        player_list = []

        for item in player_items:
            name = str(self.__parse_player_name(item))
            role = str(self.__parse_player_role(item))
            age = int(self.__parse_player_age(item))
            nationality = str(self.__parse_player_nationality(item))
            club = str(self.__parse_player_club(item))
            price = str(self.__parse_player_price(item))

            player_list.append(Player(name, role, age, nationality, club, price))

        return player_list

    def __download_page(self, url):
        ''' [Private] Internal helper for serialize page using bs. '''

        tree = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(tree.content, 'html.parser')

        return soup

    @staticmethod
    def __parse_player_name(soup):
        return soup.find('a', {'class': 'spielprofil_tooltip'}).string

    @staticmethod
    def __parse_player_role(soup):
        return soup.find('table', {'class': 'inline-table'}).findAll('tr')[1].string

    @staticmethod
    def __parse_player_age(soup):
        return soup.findAll('td', {'class': 'zentriert'})[1].string

    @staticmethod
    def __parse_player_nationality(soup):
        return soup.findAll('td', {'class': 'zentriert'})[2].find('img')['title']

    @staticmethod
    def __parse_player_club(soup):
        return soup.findAll('td', {'class': 'zentriert'})[3].find('img')['alt']

    @staticmethod
    def __parse_player_price(soup):
        return soup.find('td', {'class': 'rechts hauptlink'}).find('b').string
