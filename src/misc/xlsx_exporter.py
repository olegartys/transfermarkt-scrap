import xlsxwriter

from model.players_table_model import PlayersTableModel


class XlsxExporter:
    def __init__(self):
        pass

    def export(self, players_manager, output_filename):
        table_header = PlayersTableModel.TableHeader.headers

        workbook = xlsxwriter.Workbook(output_filename)
        worksheet = workbook.add_worksheet()

        # write header
        row = 0
        col = 0

        for head in table_header:
            worksheet.write(row, col, head)
            col += 1

        # write players data
        row = 0
        col = 0

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
