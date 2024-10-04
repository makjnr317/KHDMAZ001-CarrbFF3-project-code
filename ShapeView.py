import math

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor, QPolygonF, QPen
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsTextItem
from PyQt6.QtCore import pyqtSignal

# Class used for thw 2D visualisation
class ShapeView(QGraphicsView):
    linkage_clicked = pyqtSignal(str)
    def __init__(self, residues):
        """
        Initializes the ShapeView with a list of residues and sets up the scene.

        :param residues: List of residue names to be visualized as shapes in the scene.
        """
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setBackgroundBrush(QColor('white'))
        self.create_shapes(residues, [])
        self.lines = dict()
        self.residues = None
        self.linkages = None

    def create_shapes(self, residues, connections):
        """
        Creates shapes (pentagons or hexagons) for each residue and adds them to the scene.
        Connects shapes with lines and adds labels to the scene.

        :param residues: List of residue names to determine which shapes to draw.
        """
        self.residues = residues
        self.connections = connections
        self.scene.clear()
        x = 50
        y = 50
        previous_end_vertex = None
        previous_edge_vertex = None

        for index, residue in enumerate(residues):
            if residue.endswith('f'):
                shape = self.create_pentagon(QPointF(x, y))
            else:
                shape = self.create_hexagon(QPointF(x, y))

            self.scene.addPolygon(shape, brush=QColor('orange'))

            text_item = QGraphicsTextItem(residue)
            text_item.setDefaultTextColor(QColor('black'))
            text_item.setPos(x +20, y - 25)
            self.scene.addItem(text_item)

            if previous_end_vertex:
                middle_current_vertex_2 = QPointF(shape.at(1).x(), (shape.at(1).y() + previous_edge_vertex.y()) / 2)
                line_item = self.scene.addLine(previous_end_vertex.x(), previous_end_vertex.y(),
                                               middle_current_vertex_2.x(), middle_current_vertex_2.y(), QPen(QColor('black'), 2))

                self.lines[line_item] = index - 1

                line_item = self.scene.addLine(middle_current_vertex_2.x(), middle_current_vertex_2.y(),
                                               shape.at(0).x(), shape.at(0).y(), QPen(QColor('black'), 2))

                self.lines[line_item] = index - 1

                # vertex_label = QGraphicsTextItem(str(index))
                # vertex_label.setDefaultTextColor(QColor('blue'))
                # vertex_label.setPos(previous_end_vertex.x() - 10, previous_end_vertex.y() - 10)
                # self.scene.addItem(vertex_label)

            previous_end_vertex = shape.at(3)
            previous_edge_vertex = shape.at(2)
            y += 100

        vertex_label = QGraphicsTextItem(str(len(residues)))
        vertex_label.setDefaultTextColor(QColor('blue'))
        if previous_end_vertex:
            vertex_label.setPos(previous_end_vertex.x() - 10, previous_end_vertex.y() - 10)
            # self.scene.addItem(vertex_label)

    def create_pentagon(self, center):
        """
        Creates a pentagon shape centered at the given point.

        :param center: QPointF object representing the center of the pentagon.
        :return: QPolygonF object representing the pentagon shape.
        """
        radius = 25
        points = [QPointF(center.x() + radius * math.cos(2 * math.pi * i / 5 - math.pi / 2),
                          center.y() + radius * math.sin(2 * math.pi * i / 5 - math.pi / 2)) for i in range(5)]
        return QPolygonF(points)

    def create_hexagon(self, center):
        """
        Creates a hexagon shape centered at the given point.

        :param center: QPointF object representing the center of the hexagon.
        :return: QPolygonF object representing the hexagon shape.
        """
        radius = 25
        points = [QPointF(center.x() + radius * math.cos(2 * math.pi * i / 6 - math.pi / 2),
                          center.y() + radius * math.sin(2 * math.pi * i / 6 - math.pi / 2)) for i in range(6)]
        return QPolygonF(points)

    def mousePressEvent(self, event):
        """
        Handles mouse press events to interact with the shapes.

        :param event: QMouseEvent object representing the mouse event.
        """
        print(self.connections)
        pos = event.pos()
        item = self.itemAt(pos)
        if item in self.lines.keys():
            print(self.connections[self.lines[item]])
            self.linkage_clicked.emit(self.connections[self.lines[item]])
        else:
            super().mousePressEvent(event)