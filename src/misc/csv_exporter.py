import csv

from model.players_table_model import PlayersTableModel


class CsvExporter:
    def __init__(self):
        pass

    def export(self, players_manager, output_filename):
        with open(output_filename, 'w') as csv_file:
            table_header = PlayersTableModel.TableHeader.headers

            csv_writer = csv.DictWriter(csv_file, fieldnames=table_header, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            csv_writer.writeheader()

            for page in players_manager.get_all_cached_pages().values():
                for player in page:
                    csv_writer.writerow({
                        table_header[0]: player.name,
                        table_header[1]: player.role,
                        table_header[2]: player.age,
                        table_header[3]: player.nationality,
                        table_header[4]: player.club,
                        table_header[5]: player.price,
                    })
