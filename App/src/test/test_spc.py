import unittest

import ezdxf

from SurveyingPointCode.app.conversor import genera_dxf, upload_txt
from SurveyingPointCode.app.geometric_tools import create_layers

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


class SurveyingPointCode(unittest.TestCase):

    def test_create_layers_number(self):
        self.assertEqual(len(dwg.layers), 18, FAILURE)
        self.assertNotEqual(len(dwg.layers), 10, FAILURE)

    def test_create_layers_types(self):
        for layer in dwg.layers:
            self.assertIn(layer.dxf.name, layers, FAILURE)


if __name__ == '__main__':
    unittest.main()
