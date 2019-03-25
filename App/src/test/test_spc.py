# -*- coding: utf-8 -*-
#
# Units test
#
# J. Eduardo Risco 25-03-2019
#


import unittest

import ezdxf

from prototipo_flask.app.conversor import (genera_dxf, get_circles,
                                              get_curves, get_lines,
                                              get_points, get_rectangles,
                                              get_squares, upload_txt)
from prototipo_flask.app.geometric_tools import (create_circles,
                                                    create_curves,
                                                    create_layers,
                                                    create_lines,
                                                    create_points,
                                                    create_rectangles,
                                                    create_squares)

FAILURE = 'incorrect value'
# File config user
file_user = [
    ['E', 'Edificio', (38, 140, 89)], ['A', 'Acera', 0],
    ['FA', 'Farola', 2], ['TEL', 'Telecomunicaciones', 3],
    ['RE', 'Red_Electrica', 161], ['SAN', 'Saneamiento', 220],
    ['M', 'Muro', 1], ['B', 'Bordillo', 0],
    ['B1', 'Bordillo', 0], ['R', 'Relleno', 0],
    ['ARB', 'Arbol', 60], ['C', 'Calzada', 141],
    ['C1', 'Calzada', 141]]

# Created layers
layers = ['Edificio', 'Acera', 'Farola', 'Telecomunicaciones', 'Red_Electrica',
          'Saneamiento', 'Muro', 'Bordillo', 'Relleno', 'Arbol', 'Calzada',
          'Points', 'Number_Points', 'Altitude', 'Label', '0', 'Defpoints',
          'View Port']

dwg = ezdxf.new('AC1018')
msp = dwg.modelspace()
create_layers(dwg, file_user)
upload_txt("test/input_files/Example_1.txt")
create_points(dwg, msp, get_points())
n_points = len(get_points())
n_texts = n_points*3
create_circles(msp, get_circles(), file_user)
create_curves(msp, get_curves(), file_user)


class SurveyingPointCode(unittest.TestCase):

    def test_create_layers_number(self):
        self.assertEqual(len(dwg.layers), 18, FAILURE)
        self.assertNotEqual(len(dwg.layers), 10, FAILURE)

    def test_create_layers_types(self):
        for layer in dwg.layers:
            self.assertIn(layer.dxf.name, layers, FAILURE)

    def test_create_points_number_file_correct(self):
        n = 0
        for e in msp:
            if e.dxftype() == 'POINT':
                n = n+1
        self.assertEqual(n, n_points, FAILURE)
        self.assertNotEqual(n, 0, FAILURE)

    def test_create_points_texts_file_correct(self):
        n = 0
        for e in msp:
            if e.dxftype() == 'TEXT':
                n = n+1
        self.assertEqual(n, n_texts, FAILURE)
        self.assertNotEqual(n, 0, FAILURE)

    def test_create_circles_number(self):

        n = 0
        for e in msp:
            if e.dxftype() == 'CIRCLE':
                n = n+1
        self.assertEqual(n, 2, FAILURE)
        self.assertNotEqual(n, 0, FAILURE)

    def test_create_splines_number(self):
        n = 0
        for e in msp:
            if e.dxftype() == 'SPLINE':
                n = n+1
        self.assertEqual(n, 1, FAILURE)
        self.assertNotEqual(n, 0, FAILURE)

    def test_create_lines_number(self):
        msp = dwg.modelspace()
        create_lines(msp, get_lines(), file_user)
        n = 0
        for e in msp:
            if e.dxftype() == 'LWPOLYLINE':
                n = n+1
        self.assertEqual(n, 5, FAILURE)
        self.assertNotEqual(n, 0, FAILURE)

    def test_create_squares_number(self):
        msp = dwg.modelspace()
        create_squares(msp, get_squares(), file_user)
        n = 0
        for e in msp:
            if e.dxftype() == 'LWPOLYLINE' and e.dxf.count == 5:
                n = n+1
        self.assertEqual(n, 4, FAILURE)
        self.assertNotEqual(n, 0, FAILURE)

    def test_create_rectangles_number(self):
        msp = dwg.modelspace()
        create_rectangles(msp, get_rectangles(), file_user)
        n = 0
        for e in msp:
            if e.dxftype() == 'LWPOLYLINE' and e.dxf.count == 5:
                n = n+1
        self.assertEqual(n, 1, FAILURE)
        self.assertNotEqual(n, 0, FAILURE)


if __name__ == '__main__':
    unittest.main()
