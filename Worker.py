from io import BytesIO

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

from DatabaseManager import DatabaseManager
from PlotPMF import plot_pmf_image


class Worker(QThread):
    """
    A worker thread class for generating images from data and emitting signals
    when the images are ready.
    """
    image_ready = pyqtSignal(int, QPixmap)
    error_occurred = pyqtSignal(str)

    def __init__(self, connections):
        """
        Initializes the Worker with a list of connections.

        :param connections: List of connections for which images will be generated.
        """
        super().__init__()
        self.connections = connections

    def run(self):
        """
        Executes the thread's task of generating images for each connection.
        """

        # Create a new database connection in the worker thread
        db_manager = DatabaseManager()

        for index, connection in enumerate(self.connections):
            try:
                # get data for the current connection
                data = db_manager.query_data_by_file(connection)
                if data is None:
                    raise FileNotFoundError(f"No data found in the database for {connection}")

                # Plot the image using the retrieved data
                fig = plot_pmf_image(connection, connection,data)
                buf = BytesIO()
                fig.savefig(buf, format='png')
                buf.seek(0)
                pixmap = QPixmap()
                pixmap.loadFromData(buf.getvalue())
                buf.close()
                self.image_ready.emit(index, pixmap)
            except Exception as e:
                error_message = f"Error generating image for {connection}: {e}"
                self.error_occurred.emit(error_message)
                continue

        # Close the database connection in the worker thread
        db_manager.close()



