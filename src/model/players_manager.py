from PyQt5.QtCore import pyqtSignal, QObject, QThread, QMutex, QWaitCondition

from model.lru_page_cache import LRUPageCache
from model.players_page import PlayersPage


class PlayersManager(QObject):
    '''
    '''

    download_finished_signal = pyqtSignal(int, int, name='page_download_finished')

    class PlayersDownloadManager(QThread):
        def __init__(self, players_page_mgr):
            super(self.__class__, self).__init__()

            self.players_page_mgr = players_page_mgr

            self.download_requested_lock = QMutex()
            self.download_requested_cv = QWaitCondition()

            self.stopped = False

            self.download_pending = False
            self.page_to_download = -1

            self.on_data_ready = None
            self.on_error = None

        def __del__(self):
            self.stopped = True
            self.download_requested_cv.wakeOne()

        def run(self):
            while not self.stopped:
                self.download_requested_lock.lock()
                if not self.download_pending or not self.stopped:
                    self.download_requested_cv.wait(self.download_requested_lock)

                self.download_requested_lock.unlock()

                page_number = self.page_to_download
                page = self.players_page_mgr.download(page_number)

                self.download_pending = False

                if self.on_data_ready:
                    self.on_data_ready(page_number, page)

        def schedule_download(self, page_number, on_data_ready=None, on_error=None):
            if self.download_pending:
                return

            self.download_requested_lock.lock()

            self.page_to_download = page_number
            self.on_data_ready = on_data_ready
            self.on_error = on_error

            self.download_pending = True

            self.download_requested_lock.unlock()

            self.download_requested_cv.wakeOne()

    def __init__(self, app_config):
        super(self.__class__, self).__init__()

        config = app_config.players_list_storage

        self._cached_page_number = config['pageNumber']

        players_page = PlayersPage(app_config)
        self._players_on_page = players_page.players_on_page()

        self._page_cache = LRUPageCache(capacity=self._cached_page_number)

        self._players_download_manager = self.PlayersDownloadManager(players_page)
        self._players_download_manager.start()

    def is_cached(self, player_number):
        page_number = self.get_page_number(player_number, self._players_on_page)

        return self._page_cache.is_cached(page_number)

    def get(self, player_number):
        page_number = self.get_page_number(player_number, self._players_on_page)

        if self.is_cached(player_number):
            return

        self._players_download_manager.schedule_download(page_number, on_data_ready=self.download_finished_cb)

    def get_cached(self, player_number):
        page_number = self.get_page_number(player_number, self._players_on_page)
        player_on_page_offset = player_number % self._players_on_page

        if not self.is_cached(player_number):
            return None

        page = self._page_cache[page_number]

        return page[player_on_page_offset]

    def drop_cache(self):
        self._page_cache = LRUPageCache(capacity=self._cached_page_number)

    @staticmethod
    def get_page_number(player_number, players_on_page):
        page_number = player_number // players_on_page
        if page_number == 0:
            page_number = 1

        return page_number

    def download_finished_cb(self, page_number, page):
        self._page_cache.append(page_number, page)

        player_num_start = self._players_on_page * (page_number - 1) + 1
        player_num_end = self._players_on_page * page_number

        self.download_finished_signal.emit(player_num_start, player_num_end)
