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
from prototipo_flask.app.geometric_tools import (calculate_angle,
                                                    calculate_azimut_distance,
                                                    calculate_increment_x_y,
                                                    create_circles,
                                                    create_curves,
                                                    create_layers,
                                                    create_lines,
                                                    create_points,
                                                    create_rectangles,
                                                    create_squares,
                                                    insert_symbols)
from prototipo_flask.app.upload_optional_files import (extract_symbols,
                                                          get_symbols)

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


class SurveyingPointCode(unittest.TestCase):

    def test_create_layers_number(self):
        self.assertEqual(len(dwg.layers), 18, FAILURE)
        self.assertNotEqual(len(dwg.layers), 10, FAILURE)

    def test_create_layers_types(self):
        for layer in dwg.layers:
            self.assertIn(layer.dxf.name, layers, FAILURE)

    def test_create_points_number_file_correct(self):
        create_points(dwg, msp, get_points())
        n_points = len(get_points())
        n = 0
        for e in msp:
            if e.dxftype() == 'POINT':
                n = n+1
        self.assertEqual(n, n_points, FAILURE)
        self.assertNotEqual(n, 0, FAILURE)

    def test_create_points_texts_file_correct(self):
        n_points = len(get_points())
        n_texts = n_points*3
        n = 0
        for e in msp:
            if e.dxftype() == 'TEXT':
                n = n+1
        self.assertEqual(n, n_texts, FAILURE)
        self.assertNotEqual(n, 0, FAILURE)

    def test_create_circles_number(self):
        create_circles(msp, get_circles(), file_user)
        n = 0
        for e in msp:
            if e.dxftype() == 'CIRCLE':
                n = n+1
        self.assertEqual(n, 2, FAILURE)
        self.assertNotEqual(n, 0, FAILURE)

    def test_create_splines_number(self):
        create_curves(msp, get_curves(), file_user)
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

    def test_not_create_circles(self):
        upload_txt("test/input_files/Example_2.txt")
        dwg2 = ezdxf.new('AC1018')
        msp2 = dwg2.modelspace()
        create_circles(msp2, get_circles(), file_user)
        n = 0
        for a in msp2:
            if a.dxftype() == 'CIRCLE':
                n = n+1
        self.assertEqual(n, 0, FAILURE)

    def test_not_create_splines(self):
        upload_txt("test/input_files/Example_2.txt")
        dwg2 = ezdxf.new('AC1018')
        msp2 = dwg2.modelspace()
        create_curves(msp2, get_curves(), file_user)
        n = 0
        for a in msp2:
            if a.dxftype() == 'SPLINE':
                n = n+1
        self.assertEqual(n, 0, FAILURE)

    def test_not_create_lines(self):
        upload_txt("test/input_files/Example_2.txt")
        dwg2 = ezdxf.new('AC1018')
        msp2 = dwg2.modelspace()
        create_lines(msp2, get_lines(), file_user)

        n = 0
        for a in msp2:
            if a.dxftype() == 'LWPOLYLINE':
                n = n+1
        self.assertEqual(n, 0, FAILURE)

    def test_not_create_squares_rectangles(self):
        upload_txt("test/input_files/Example_2.txt")
        dwg2 = ezdxf.new('AC1018')
        msp2 = dwg2.modelspace()
        create_squares(msp2, get_squares(), file_user)
        create_rectangles(msp2, get_rectangles(), file_user)

        n = 0
        for a in msp2:
            if a.dxftype() == 'LWPOLYLINE':
                n = n+1
        self.assertEqual(n, 0, FAILURE)

    def test_azimut_distance(self):
        a = [1, (0, 0, 0), 'E']
        b = [2, (100, 100, 0), 'E']
        az, dist = calculate_azimut_distance(a, b)

        self.assertEqual(az, 45, FAILURE)
        self.assertEqual(dist, 141.4213562373095, FAILURE)
        self.assertNotEqual(az, 50, FAILURE)
        self.assertNotEqual(dist, 145, FAILURE)

    def test_increment_x_y(self):
        az = 45
        dist = 141.4213562373095
        Inc_x, Inc_y = calculate_increment_x_y(az, dist)

        self.assertEqual(round(Inc_x, 3), 100, FAILURE)
        self.assertEqual(round(Inc_y, 3), 100, FAILURE)
        self.assertNotEqual(Inc_x, 150, FAILURE)
        self.assertNotEqual(Inc_y, 145, FAILURE)

    def test_angle_direction(self):
        az = 125

        self.assertEqual(calculate_angle(az, 10), 215, FAILURE)
        self.assertEqual(calculate_angle(az, -10), 35, FAILURE)
        self.assertNotEqual(calculate_angle(az, -10), 215, FAILURE)

    def test_extract_symbols(self):
        extract_symbols("test/input_files/simbolos.dxf")
        for s in get_symbols():
            self.assertIn(s, ['Farola', 'Arbol', 'Vertice'], FAILURE)
            self.assertNotIn(s, ['Casa', 'Banco'], FAILURE)
        self.assertEqual(len(get_symbols()), 3, FAILURE)
        self.assertNotEqual(len(get_symbols()), 0, FAILURE)


if __name__ == '__main__':
    unittest.main()
