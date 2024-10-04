import json
import os
import re
import subprocess
import sys
import time
import shutil
from PyQt6.QtCore import Qt, QPointF, QTimer
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QLineEdit, QGridLayout, QHBoxLayout, QScrollArea,
                             QStatusBar, QFileDialog, QMessageBox, QTabWidget, QLabel, QSizePolicy, QInputDialog,QFileDialog,QTextEdit)
from PyQt6.QtGui import QAction

from CarbUtils import CarbUtils
from DatabaseManager import DatabaseManager
from MakeDehidrils import make_dehidrals

from ShapeView import ShapeView
from ClickableGraphicsView import ClickableGraphicsView
from PDBViewer import PDBViewer
from Worker import Worker

start_time = 0
end_time = 0


def scale_coordinate(x):
    if 3 <= x <= 297:
        return -60 / 49 * (x - 3) + 180
    return None


class MainWindow(QMainWindow):
    """
    Main window that Handles UI setup and interactions.
    """
    def __init__(self):
        super().__init__()
        self.output_viewer_layout = None
        self.angles_display = None
        self.linkage_views = {}
        self.current_highlighted = None  # Track the currently highlighted view

        self.cursor = None
        self.worker = None
        self.pdb_viewer_widget = None
        self.connections = []
        self.prev_molecule = None
        self.setWindowTitle("Shapes for Residues")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)

        # Create a QTabWidget and add it to the main layout
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Creation Tab
        self.creation_tab = QWidget()
        self.creation_layout = QVBoxLayout(self.creation_tab)

        self.top_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter molecule sequence")
        self.input_field.returnPressed.connect(self.update_view)
        self.top_layout.addWidget(self.input_field)

        self.horizontal_layout = QHBoxLayout()

        self.left_layout = QVBoxLayout()
        self.view = ShapeView([])
        self.view.setFixedWidth(300)
        self.left_layout.addWidget(self.view)
        self.horizontal_layout.addLayout(self.left_layout)

        self.scroll_area = QScrollArea()
        self.image_widget = QWidget()
        self.image_layout = QGridLayout(self.image_widget)
        self.image_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.image_widget.setStyleSheet("background-color: white;")

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_widget)
        self.horizontal_layout.addWidget(self.scroll_area)

        self.creation_layout.addLayout(self.top_layout)
        self.creation_layout.addLayout(self.horizontal_layout)

        self.horizontal_layout.setStretch(0, 0)
        self.horizontal_layout.setStretch(1, 1)

        # Add the creation tab to the tabs widget
        self.tabs.addTab(self.creation_tab, "Creation")

        # Output Tab
        self.output_tab = QWidget()
        self.output_layout = QVBoxLayout(self.output_tab)

        # Add the output tab to the tabs widget
        self.tabs.addTab(self.output_tab, "Output")

        self.setCentralWidget(self.central_widget)

        self.create_menu_bar()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_menu_bar(self):
        """
        Creates and sets up the menu bar with file and help options.
        """
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        generate_action = QAction("Generate", self)
        generate_action.setShortcut("Ctrl+G")
        generate_action.triggered.connect(self.print_dot_positions)
        file_menu.addAction(generate_action)

        save_action = QAction("Save Configuration", self)
        save_action.setShortcut("Ctrl+P")
        save_action.triggered.connect(self.save_angle_configuration)
        file_menu.addAction(save_action)

        load_action = QAction("Load Configuration", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_configuration)
        file_menu.addAction(load_action)

        save_pdb_action = QAction("Save PDB", self)
        save_pdb_action.setShortcut("Ctrl+S")
        save_pdb_action.triggered.connect(self.save_pdb_file)
        file_menu.addAction(save_pdb_action)

        help_menu = menu_bar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def print_dot_positions(self):
        """
        Generates and saves dihedral angles for the current connections, and  a process to build the structure.
        """
        output = make_dehidrals(self.connections)
        for i in range(self.image_layout.count()):
            widget = self.image_layout.itemAt(i).widget().children()[2]
            if isinstance(widget, ClickableGraphicsView):
                for dot in widget.dots:
                    pos = dot.boundingRect().center()
                    x = pos.x()
                    y = pos.y()
                    scaled_x = scale_coordinate(x) * -1
                    scaled_y = scale_coordinate(y)
                    molecule_id = dot.data(0)
                    output[molecule_id].append(f"{scaled_x:.1f} {scaled_y:.1f}")

        file_output = ""
        for i in output:
            file_output += ",".join(i) + "\n"

        with open("CBv2.1.45/structureFile/dihedrals.txt", "w") as file:
            file.write(file_output)

            # Run CarbBuilder and capture the output using subprocess
        try:
            process = subprocess.Popen(
                ['CBv2.1.45/CarbBuilder2.exe', '-i', self.input_field.text(), '-o', 'output'],
                cwd="CBv2.1.45",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            output, error = process.communicate()

            if error:
                self.show_error_message("CarbBuilder Error", error)
                return

            if "PDB file Built" in output:
                self.status_bar.showMessage("Generation completed successfully", 5000)
                final_linkages = self.extract_final_linkages(output)
                if final_linkages:
                    angle_info = "\n".join(final_linkages)
                else:
                    self.show_error_message("No Angles Found", "No angles were found in the CarbBuilder output.")
                self.visualize_pdb(angle_info)
            else:
                self.show_error_message("Build Failed", "The build was unsuccessful. Try different angles.")
                self.show_error_message("CarbBuilder Output", output)

        except Exception as e:
            self.show_error_message("Error", str(e))

    def extract_final_linkages(self,output):
        linkages = []

        # Ensure output is a string
        output = str(output)

        # Split the output by new lines
        lines = output.split('\n')

        for line in lines:
            # Look for lines that start with "FINAL linkage:"
            if "FINAL linkage:" in line:
                parts = line.strip().split("FINAL linkage:")[1].strip()

                if ":" in parts:
                    linkage_info, angles_info = parts.split(":", 1)
                    linkage_info = linkage_info.strip()
                    angles_info = angles_info.strip()

                    # Format the output
                    linkage = f"Linkage: {linkage_info}, Angles: {angles_info}"
                    pattern = re.compile(r"#\d+")
                    linkage = pattern.sub("", linkage)
                    linkages.append(linkage)

        return linkages

    def visualize_pdb(self,angle_info):
        """Visualizes the generated PDB file in the output tab."""
        pdb_file_path = 'CBv2.1.45/output.pdb'

        # Check if output.pdb exists
        if not os.path.exists(pdb_file_path):
            self.show_error_message("Error", "Could not generate PDB file. Please check the input or try again.")
            return

        # Clear the output layout
        for i in reversed(range(self.output_layout.count())):
            widget = self.output_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Switch to the Output tab
        self.tabs.setCurrentWidget(self.output_tab)
        self.pdb_viewer_widget = PDBViewer(pdb_file_path)
        self.pdb_viewer_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.angles_display = QTextEdit()
        self.angles_display.setReadOnly(True)
        self.angles_display.setFixedWidth(320)
        self.angles_display.setStyleSheet("background-color: lightgray;")
        self.angles_display.setText(angle_info)


        self.angles_label = QLabel("Dihedral Angles Used")
        self.angles_label.setStyleSheet("font-weight: bold; font-size: 14px; color: black;background-color: lightgray;")
        self.angles_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.angles_layout = QVBoxLayout()
        self.angles_layout.addWidget(self.angles_label)  # Add the label on top
        self.angles_layout.addWidget(self.angles_display)

        # Create a horizontal layout to place both the PDB viewer and angles display side by side
        self.output_viewer_layout = QHBoxLayout()
        self.output_viewer_layout.addWidget(self.pdb_viewer_widget)
        self.output_viewer_layout.addLayout(self.angles_layout)

        # Create a QWidget to hold the horizontal layout and add it to the output tab layout
        self.output_viewer_widget = QWidget()
        self.output_viewer_widget.setLayout(self.output_viewer_layout)

        # Clear the output layout if necessary (remove previous widgets)
        while self.output_layout.count():
            widget = self.output_layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()

        # Add the widget containing the PDB viewer and angles display to the output tab layout
        self.output_layout.addWidget(self.output_viewer_widget)

    def resizeEvent(self, event):
        """
        Override the resize event to adjust the size of the 3Dmol viewer dynamically.
        """
        super().resizeEvent(event)
        if self.pdb_viewer_widget is not None:
            new_width = self.pdb_viewer_widget.width()  # Get the new width of the parent widget
            new_height = self.pdb_viewer_widget.height()  # Get the new height of the parent widget

            # Update the viewer's size based on the new dimensions
            self.pdb_viewer_widget.viewer.setSize(width=new_width, height=new_height)

    def save_pdb_file(self):
        """
        Prompts the user to save the output.pdb file to a location of their choice.
        """
        # Check if the PDB file exists before attempting to save
        pdb_file_path = 'CBv2.1.45/output.pdb'
        if not os.path.exists(pdb_file_path):
            self.show_error_message("Save Error", "PDB file not found. Please generate it first.")
            return



        # Prompt the user to select a destination file path
        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDB File", "", "PDB Files (*.pdb);;All Files (*)")

        if save_path:
            try:
                # Copy the output.pdb to the selected location
                shutil.copy(pdb_file_path, save_path)
                self.status_bar.showMessage(f"PDB file saved to {save_path}", 5000)
            except Exception as e:
                self.show_error_message("Save Error", f"Failed to save PDB file: {str(e)}")

    def update_view(self):
        """Updates the view based on the input molecule sequence. Creates shapes and displays images."""

        # Delete output.pdb if it exists
        pdb_file_path = 'CBv2.1.45/output.pdb'
        if os.path.exists(pdb_file_path):
            try:
                os.remove(pdb_file_path)
            except Exception as e:
                print(f"Error deleting {pdb_file_path}: {e}")

        self.prev_molecule = self.input_field.text().strip()
        if not self.prev_molecule:
            self.show_error_message("Error", "Molecule sequence is empty. Please enter a valid sequence.")
            return



        # if not re.match(casper_regex, self.prev_molecule):
        #     # If input is not in the correct CASPER format, show an error message
        #     self.show_error_message(
        #         "Invalid Input",
        #         "The molecule sequence is not in the correct CASPER format. "
        #         "Please follow this format:\n"
        #         "Example 1: aDGal(1->3)bDGalf(1->2)aDMan\n"
        #         "Example 2: aLFuc(1->3)bDGalNAc\n"
        #         "Each residue should start with a/b followed by D/L, and residues should be separated by (d->d)."
        #     )
        #     return

        self.clear_previous_views()

        carb_builder = CarbUtils(self.prev_molecule)
        carb_builder.parse_sequence()
        residues = carb_builder.get_residues()
        self.connections = carb_builder.get_connections()
        self.view.create_shapes(residues, self.connections)
        seen = set()
        result = []
        for item in self.connections:
            if item not in seen:
                result.append(item)
                seen.add(item)

        self.connections =result
        self.display_images(self.connections)

        # Use a QTimer to periodically check if the layout is updated
        self.check_layout_timer = QTimer(self)
        self.check_layout_timer.timeout.connect(lambda: self.check_layout_and_place_dots(start_time))
        self.check_layout_timer.start(100)
        self.view.linkage_clicked.connect(self.highlight_linkage_plot)

    def highlight_linkage_plot(self, linkage):
        """
        Highlights the grid plot corresponding to the clicked linkage.
        :param linkage: The name of the clicked linkage.
        """
        if self.current_highlighted:
            # Reset the border style of the previously highlighted view
            self.current_highlighted.setStyleSheet("""
                        border: none;
                        box-sizing: border-box;
                    """)

        # Find the corresponding graphics view for the clicked linkage
        if linkage in self.linkage_views:
            self.current_highlighted = self.linkage_views[linkage]
            # Set the border style to highlight
            self.current_highlighted.setStyleSheet("border: 2px solid blue;")

    def clear_previous_views(self):
        """Clears old images, linkage views, and resets state for the new molecule."""
        # Remove all items from the grid layout
        for i in reversed(range(self.image_layout.count())):
            widget = self.image_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Clear linkage views and any currently highlighted linkage
        self.linkage_views = {}
        self.current_highlighted = None

    def check_layout_and_place_dots(self,start_time):
        """
        Checks if the layout has been updated with images and places saved dots if a configuration is loaded.
        """
        if self.image_layout.count() == len(set(self.connections)):

            self.check_layout_timer.stop()

            # Place saved dots if loading a configuration
            if hasattr(self, 'saved_dots'):
                for index, linkage in enumerate(self.connections):
                    if linkage in self.saved_dots:
                        graphics_view = self.image_layout.itemAt(index).widget().children()[2]
                        if isinstance(graphics_view, ClickableGraphicsView):
                            for x, y in self.saved_dots[linkage]:
                                graphics_view.add_dot(graphics_view.mapToScene(x, y))
                del self.saved_dots  # Clean up after loading the dots

        # Else, the timer continues to check

    def display_images(self, connections):
        """Displays images for the given connections by starting a worker thread."""
        for i in reversed(range(self.image_layout.count())):
            self.image_layout.itemAt(i).widget().setParent(None)

        self.worker = Worker(connections)
        self.worker.image_ready.connect(self.add_image_to_grid)
        self.worker.error_occurred.connect(lambda message: self.show_error_message("Plot generation failed", message))
        self.worker.start()


    def add_image_to_grid(self, index, pixmap):
        """
        Adds an image to the grid layout with a title and a ClickableGraphicsView widget.

        :param index: The index of the image in the connections list.
        :param pixmap: The QPixmap image to be added.
        """
        linkage = self.connections[index]
        linkage_name = f"Linkage: {linkage}"

        # Create a QLabel for the title
        title_label = QLabel(linkage_name)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("background-color: white; color: black; border: 1px solid black;")
        title_label.setFixedHeight(20)
        title_label.setFixedWidth(300)
        # title_label.setMa

        # ensure the label and image have the same width
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        title_label.setSizePolicy(size_policy)

        # Create a ClickableGraphicsView for the image
        scaled_pixmap = pixmap.scaledToHeight(300)
        graphics_view = ClickableGraphicsView(scaled_pixmap, index)
        graphics_view.clicked.connect(self.handle_image_click)
        graphics_view.setFixedWidth(306)
        graphics_view.setFixedHeight(306)
        graphics_view.setViewportMargins(0,0,0,0)

        graphics_view.setStyleSheet("""
                border: none;
                box-sizing: border-box;
            """)

        self.linkage_views[linkage] = graphics_view

        # Create a vertical layout to stack the label and image
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(title_label)
        vertical_layout.addWidget(graphics_view)
        vertical_layout.setContentsMargins(0, 0, 0, 0)  # Optional: Remove margins



        # Create a widget to hold the vertical layout
        container_widget = QWidget()
        container_widget.setLayout(vertical_layout)
        container_widget.setFixedHeight(332)

        # Add the container widget to the grid layout
        row = index // 3
        col = index % 3
        self.image_layout.addWidget(container_widget, row, col)

    def handle_image_click(self, x, y):
        self.status_bar.showMessage(f"Image clicked at: ({x}, {y})", 2000)

    def save_file(self):
        """
        Opens a dialog to save the current input text to a file.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_name:
            try:
                with open(file_name, 'w') as file:
                    file.write(self.input_field.text())
                self.status_bar.showMessage("File saved successfully", 5000)
            except Exception as e:
                self.show_error_message("Save Error", str(e))

    def load_file(self):
        """
        Opens a dialog to load text from a file into the input field and updates the view.
        """
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    content = file.read()
                self.input_field.setText(content)
                self.update_view()
                self.status_bar.showMessage("File loaded successfully", 5000)
            except Exception as e:
                self.show_error_message("Load Error", str(e))

    def show_about_dialog(self):
        QMessageBox.about(self, "About", "This is a PyQt application for visualizing molecular structures.")

    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)

    def save_angle_configuration(self):
        """
        Prompts the user to enter a name and saves the current configuration to the database.
        """
        # Prompt the user for a configuration name
        config_id, ok = QInputDialog.getText(self, "Save Configuration", "Enter a name for the configuration:")
        if not ok or not config_id:
            self.status_bar.showMessage("Configuration save canceled", 5000)
            return

        # Get the molecule name from the input field
        molecule_name = self.prev_molecule.strip()
        if not molecule_name:
            self.show_error_message("Error", "Molecule name is empty. Please enter a valid molecule name.")
            return

        # Prepare the configuration data
        config_data = {}
        for i in range(self.image_layout.count()):
            container_widget = self.image_layout.itemAt(i).widget()
            title_label = container_widget.layout().itemAt(0).widget()
            connection_name = title_label.text().replace("Linkage: ", "")
            graphics_view = container_widget.layout().itemAt(1).widget()

            points = []
            for dot in graphics_view.dots:
                pos = dot.boundingRect().center()
                points.append([int(pos.x()), int(pos.y())])

            if points:
                config_data[connection_name] = points

        # Save configuration data to the database
        db_manager = DatabaseManager()
        db_manager.save_configuration(config_id, molecule_name, config_data)
        db_manager.close()

        self.status_bar.showMessage(f"Configuration '{config_id}' for molecule '{molecule_name}' saved successfully",
                                    5000)

    def load_configuration(self):
        # Prompt the user to select a configuration
        db_manager = DatabaseManager()
        self.cursor = db_manager.conn.cursor()

        self.cursor.execute('SELECT config_id FROM configurations')
        configs = [row[0] for row in self.cursor.fetchall()]

        if not configs:
            self.show_error_message("Load Error", "No configurations found.")
            return

        config_id, ok = QInputDialog.getItem(self, "Load Configuration", "Select a configuration to load:", configs, 0,
                                             False)
        if not ok or not config_id:
            self.status_bar.showMessage("Configuration load canceled", 5000)
            return

        # Query the molecule name and dots based on the selected configuration
        self.cursor.execute('SELECT molecule_name, data FROM configurations WHERE config_id = ?', (config_id,))
        result = self.cursor.fetchone()

        if result:
            molecule_name, dots_json = result
            self.input_field.setText(molecule_name)
            self.saved_dots = json.loads(dots_json) if dots_json else {}  # Load dots as a dictionary
            self.update_view()  # Call update_view with the molecule name
            self.status_bar.showMessage(f"Configuration '{config_id}' loaded successfully", 5000)
        else:
            self.show_error_message("Load Error", "Failed to load configuration.")

        db_manager.close()

    def closeEvent(self, event):
        """This method is called when the application is closed to It delete the output.pdb file if it exists."""
        pdb_file_path = 'CBv2.1.45/output.pdb'

        # Check if the file exists and delete it
        if os.path.exists(pdb_file_path):
            try:
                os.remove(pdb_file_path)
            except Exception as e:
                print(f"Error deleting {pdb_file_path}: {e}")

        # Accept the close event to allow the window to close
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
