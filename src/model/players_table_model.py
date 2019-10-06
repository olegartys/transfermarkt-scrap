from PyQt5.QtCore import Qt, QAbstractTableModel


class PlayersTableModel(QAbstractTableModel):
    class TableHeader:
        headers = [
            "имя",
            "роль",
            "возраст",
            "национальность",
            "клуб",
            "доход",
        ]

        COLUMN_COUNT = len(headers)

        @staticmethod
        def get(index):
            return PlayersTableModel.TableHeader.headers[index]

    def __init__(self, app_config, players_list, parent=None):
        super(self.__class__, self).__init__(parent)

        self.main_window_ref = parent

        config = app_config.players_table_model

        self.row_count = config['initRowCount']
        self.max_row_count = config['maxRowCount']

        self.readahead_row_step = config['rowCountIncStep']
        self.last_read_row = -1

        self.players_list = players_list
        self.players_list.download_finished_signal.connect(self.data_ready)

    def rowCount(self, parent=None, *args, **kwargs):
        return self.row_count

    def columnCount(self, parent=None, *args, **kwargs):
        return PlayersTableModel.TableHeader.COLUMN_COUNT

    def headerData(self, index, Qt_Orientation, role=None):
        if role != Qt.DisplayRole:
            return None

        if Qt_Orientation == Qt.Horizontal:
            return PlayersTableModel.TableHeader.get(index)

        if Qt_Orientation == Qt.Vertical:
            return index + 1

        return None

    def canFetchMore(self, parent):
        if self.last_read_row >= self.max_row_count:
            return False

        if self.last_read_row + self.readahead_row_step > self.row_count:
            return True

        return False

    def fetchMore(self, parent):
        self.beginInsertRows(parent, self.row_count, self.row_count + self.readahead_row_step)
        self.row_count = self.row_count + self.readahead_row_step
        self.endInsertRows()

    def data(self, index, role=None):
        if not index.isValid():
            return None

        if index.column() > self.TableHeader.COLUMN_COUNT:
            return None

        if role != Qt.DisplayRole:
            return None

        if index.row() > self.max_row_count:
            return None

        self.last_read_row = index.row() + 1
        player_number = index.row() + 1

        if not self.players_list.is_cached(player_number):
            self.data_not_ready()
            self.players_list.get(player_number)

            return None

        player = self.players_list.get_cached(player_number)

        return self.get_player_field_by_idx(player, index.column())

    def goto_row(self, row):
        if row < self.row_count:
            return

        self.beginInsertRows(self.index(self.row_count, 0), self.row_count, self.row_count + row)
        self.row_count = self.row_count + row
        self.endInsertRows()

    def data_ready(self, player_num_start, player_num_end):
        print("Players from {} to {} are ready".format(player_num_start, player_num_end))

        updated_index_begin = self.index(player_num_start, self.TableHeader.COLUMN_COUNT)
        updated_index_end = self.index(player_num_end, self.TableHeader.COLUMN_COUNT)

        self.dataChanged.emit(updated_index_begin, updated_index_end)
        self.main_window_ref.set_table_active()

    def data_not_ready(self):
        self.main_window_ref.set_table_inactive()

    def drop_data(self):
        self.players_list.drop_cache()

    @staticmethod
    def get_player_field_by_idx(player, idx):
        if idx == 0:
            return player.name

        elif idx == 1:
            return player.role

        elif idx == 2:
            return player.age

        elif idx == 3:
            return player.nationality

        elif idx == 4:
            return player.club

        elif idx == 5:
            return player.price
