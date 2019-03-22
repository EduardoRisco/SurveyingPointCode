import unittest

import ezdxf

from prototipo_flask.app.conversor import genera_dxf, upload_txt
from prototipo_flask.app.geometric_tools import create_layers

FAILURE = 'incorrect value'

file_user = [
        ['E', 'Edificio', (38, 140, 89)], ['A', 'Acera', 0],
        ['FA', 'Farola', 2], ['TEL', 'Telecomunicaciones', 3],
        ['RE', 'Red_Electrica', 161], ['SAN', 'Saneamiento', 220],
        ['M', 'Muro', 1], ['B', 'Bordillo', 0],
        ['B1', 'Bordillo', 0], ['R', 'Relleno', 0],
        ['ARB', 'Arbol', 60], ['C', 'Calzada', 141],
        ['C1', 'Calzada', 141]]

dwg = ezdxf.new('AC1018')
msp = dwg.modelspace()

class SurveyingPointCode(unittest.TestCase):

    
    def test_create_layers_number(self):
        create_layers(dwg,file_user)
        self.assertEqual(len(dwg.layers),18,FAILURE)
        self.assertNotEqual(len(dwg.layers),10,FAILURE)

        


if __name__ == '__main__': 
    unittest.main()
