import csv

from model.players_table_model import PlayersTableModel


class CsvExporter:
    '''A class is used to export football players infromation to the disk in the CSV format.'''

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
