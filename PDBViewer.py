import py3Dmol
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMainWindow


class PDBViewer(QWidget):
    def __init__(self, pdb_file_path):
        super().__init__()
        # Initialize the QWidget and set up the layout
        self.viewer = None
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Create a QWebEngineView widget for displaying the 3D visualisation
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Load the PDB file
        self.load_pdb_file(pdb_file_path)

    def load_pdb_file(self, pdb_file_path):
        """Load the PDB file and display it using py3Dmol in the QWebEngineView."""
        with open(pdb_file_path, 'r') as file:
            pdb_data = file.read()

        # Create a py3Dmol viewer instance
        self.viewer = py3Dmol.view(width=800, height=560)
        self.viewer.addModel(pdb_data, 'pdb')
        self.viewer.setStyle({'stick': {}})
        self.viewer.zoomTo()

        # Get the HTML representation of the viewer
        html = self.viewer._make_html()

        # Set the HTML to the QWebEngineView
        self.web_view.setHtml(html)

