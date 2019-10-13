from PyQt5.QtCore import pyqtSignal, QObject, QThread, QMutex, QWaitCondition

from model.lru_page_cache import LRUPageCache
from model.players_page import PlayersPage


class PlayersManager(QObject):
    ''' High-level class used to get footbal player by its number.
    It uses LRUPageCache to store pages with players.
    If the page with requested player does not exists, it downloads it.
    '''

    download_finished_signal = pyqtSignal(int, int, name='page_download_finished')

    class PlayersDownloadManager(QThread):
        ''' Helper class to defer HTTP workload.
        At this point it downloads only one page in parallel.
        Need to migrate to QRunnable and ThreadPool instead.
        '''

        def __init__(self, players_page_mgr, sort_type):
            ''' Constructs PlayersDownloadManager instance.

            Parameters
            ----------
                players_page_mgr : PlayersPage
                    players_page_mgr is used to download page with
                    particular number
            '''

            super(self.__class__, self).__init__()

            self.players_page_mgr = players_page_mgr
            self.sort_type = sort_type

            self.download_requested_lock = QMutex()
            self.download_requested_cv = QWaitCondition()

            self.stopped = False

            self.download_pending = False
            self.page_to_download = -1

            self.on_data_ready = None
            self.on_error = None

        def __del__(self):
            ''' Override in order to stop internal thread. '''
            self.stopped = True
            self.download_requested_cv.wakeOne()

        def run(self):
            ''' This code runs in the separate thread. '''
            while not self.stopped:

                # wait until somebody requsted page download
                self.download_requested_lock.lock()
                if not self.download_pending or not self.stopped:
                    self.download_requested_cv.wait(self.download_requested_lock)

                self.download_requested_lock.unlock()

                page_number = self.page_to_download
                page = self.players_page_mgr.download(page_number, self.sort_type)

                self.download_pending = False

                if self.on_data_ready:
                    self.on_data_ready(page_number, page)

        def schedule_download(self, page_number, on_data_ready=None, on_error=None):
            ''' Schedule page download into the deferred context.

            Parameters
            ----------
                page_number : int
                    the page to download

                on_data_ready : callable
                    will be called when download finished

                on_error : callable, unused
            '''

            if self.download_pending:
                return

            # store the data in locked context and notify download thread
            self.download_requested_lock.lock()

            self.page_to_download = page_number
            self.on_data_ready = on_data_ready
            self.on_error = on_error

            self.download_pending = True

            self.download_requested_lock.unlock()

            self.download_requested_cv.wakeOne()

    def __init__(self, app_config):
        ''' Constructs PlayersManage instance

        Parameters
        ----------
            app_config : AppConfig
                Instance of application configuration file.
        '''

        super(self.__class__, self).__init__()

        config = app_config.players_manager

        self._cached_page_number = config['pageNumber']

        # Choose default data sorting method.
        # It will be used to generate URL when downloading
        # pages with players info.
        if config['sortMethod'] == 'NONE':
            self._players_sort_method = PlayersPage.SortType.NONE
        elif config['sortMethod'] == 'DESC':
            self._players_sort_method = PlayersPage.SortType.DESC
        elif config['sortMethod'] == 'ASC':
            self._players_sort_method = PlayersPage.SortType.ASC
        else:
            raise Exception('Unknown sorting method {}'.format(config['sortMethod']))

        players_page = PlayersPage(app_config)
        self._players_on_page = players_page.players_on_page()

        self._page_cache = LRUPageCache(capacity=self._cached_page_number)

        self._players_download_manager = self.PlayersDownloadManager(players_page, self._players_sort_method)
        self._players_download_manager.start()

    def is_cached(self, player_number):
        ''' Checks if the player is stored in the cache.

        Parameters
        ----------
            player_number : int
                Number of the player.

        Returns
        -------
            True if stored in the cache, False otherwise
        '''

        page_number = self._get_page_number(player_number, self._players_on_page)

        return self._page_cache.is_cached(page_number)

    def get(self, player_number):
        ''' Schedules page with the player_number download.

        Parameters
        ----------
            player_number : int
                number of the player to download.
        '''

        page_number = self._get_page_number(player_number, self._players_on_page)

        if self.is_cached(player_number):
            return

        self._players_download_manager.schedule_download(page_number, on_data_ready=self._download_finished_cb)

    def get_cached(self, player_number):
        ''' Return the player info from the cache.

        Parameters
        ----------
            player_number : int
                number of the player to return.

        Returns
        -------
            Player class instance with the player_number player.
        '''

        page_number = self._get_page_number(player_number, self._players_on_page)
        player_on_page_offset = player_number % self._players_on_page

        if not self.is_cached(player_number):
            return None

        page = self._page_cache[page_number]

        return page[player_on_page_offset]

    def get_all_cached_pages(self):
        ''' Return all the cached pages from the internal LRU.

        Returns
        -------
            OrderedDict with all the cached pages.
        '''

        return self._page_cache.get_all()

    def drop_cache(self):
        ''' Drops the LRU cache. '''
        self._page_cache = LRUPageCache(capacity=self._cached_page_number)

    @staticmethod
    def _get_page_number(player_number, players_on_page):
        ''' [Private] Maps the player number into the page number.

        Parameters
        ----------
            player_number : int
                number of the player

            players_on_page : int
                size of the page in players number

        Returns
        -------
            Page number with the player player_number.
        '''

        page_number = player_number // players_on_page
        if page_number == 0:
            page_number = 1

        return page_number

    def _download_finished_cb(self, page_number, page):
        ''' Is called by the PlayersDownloadManager when the data is ready.
        Used to notify the listeners of the 'download_finished_signal'.

        Parameters
        ----------
            page_number : int
                number of the downloaded page

            page : PlayersPage
                the page itself
        '''

        self._page_cache.append(page_number, page)

        player_num_start = self._players_on_page * (page_number - 1) + 1
        player_num_end = self._players_on_page * page_number

        self.download_finished_signal.emit(player_num_start, player_num_end)
