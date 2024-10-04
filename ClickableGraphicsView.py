from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QMouseEvent, QPen, QBrush
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem


class ClickableGraphicsView(QGraphicsView):
    """
    A subclass of QGraphicsView that supports clickable interactions and displays dots on click.
    """

    clicked = pyqtSignal(int, int)

    def __init__(self, pixmap, molecule_id, parent=None):
        """
        Initializes the ClickableGraphicsView with a pixmap and molecule ID.

        :param pixmap: QPixmap to be displayed in the view.
        :param molecule_id: Identifier for the molecule related to this view.
        :param parent: parent widget.
        """
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)
        self.setFixedHeight(306)

        self.dots = []
        self.molecule_id = molecule_id

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handles mouse press events. Emits a signal with the click coordinates and adds or removes dots.

        :param event: The QMouseEvent representing the mouse press event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            click_pos = self.mapToScene(event.pos())
            self.clicked.emit(int(click_pos.x()), int(click_pos.y()))
            dot_clicked = self.handle_dot_click(click_pos)
            if not dot_clicked:
                self.add_dot(click_pos)
        super().mousePressEvent(event)

    def add_dot(self, pos):
        """
        Adds a dot to the scene at the specified position.

        :param pos: QPointF representing the position where the dot will be added.
        """
        dot_radius = 3
        dot = self.scene.addEllipse(pos.x() - dot_radius, pos.y() - dot_radius,
                                    dot_radius * 2, dot_radius * 2,
                                    QPen(Qt.GlobalColor.red), QBrush(Qt.GlobalColor.red))
        self.dots.append(dot)
        dot.setData(0, self.molecule_id)

    def handle_dot_click(self, pos):
        """
        Checks if the click position intersects with any existing dot. Removes the dot if clicked.

        :param pos: QPointF -  the position of the click.
        :return: True if a dot was clicked and removed, False otherwise.
        """
        dot_clicked = False
        for dot in self.dots:
            if dot.contains(pos):
                self.scene.removeItem(dot)
                self.dots.remove(dot)
                dot_clicked = True
                break

        return dot_clicked

    def clear_dots(self):
        """Clear all existing dots from the view."""
        for dot in self.dots:
            self.scene.removeItem(dot)
        self.dots.clear()