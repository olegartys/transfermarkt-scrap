import xlsxwriter

from model.players_table_model import PlayersTableModel


class XlsxExporter:
    '''A class is used to export football players infromation to the disk in the XLSX format.'''

    def export(self, players_manager, output_filename):
        ''' Exports cached data from players_manager into a output_filename file.

        Parameters
        ----------
        players_manager : PlayersManager
            Class that stores players information. Only cached players will be dumped
            to the disk.

        output_filename : str
            Path to the file where to store players information.
        '''

        table_header = PlayersTableModel.TableHeader.headers

        workbook = xlsxwriter.Workbook(output_filename)
        worksheet = workbook.add_worksheet()

        # write header
        col = 0

        for head in table_header:
            worksheet.write(0, col, head)
            col += 1

        # write players data
        row = 0

        for page in players_manager.get_all_cached_pages().values():
            for player in page:
                row += 1

                worksheet.write(row, 0, player.name)
                worksheet.write(row, 1, player.role)
                worksheet.write(row, 2, player.age)
                worksheet.write(row, 3, player.nationality)
                worksheet.write(row, 4, player.club)
                worksheet.write(row, 5, player.price)

        workbook.close()
