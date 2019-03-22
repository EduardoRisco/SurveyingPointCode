import unittest

import ezdxf

from SurveyingPointCode.app.conversor import genera_dxf, upload_txt, get_points
from SurveyingPointCode.app.geometric_tools import create_layers, create_points

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

    def test_create_points_number_file_correct(self):
        upload_txt("test/input_files/Example_1.txt")
        create_points(dwg, msp, get_points())
        n_file=len(get_points())
        n=0
        for e in msp:
            if e.dxftype()=='POINT':
                n=n+1

        self.assertEqual(n,n_file,FAILURE) 
        self.assertNotEqual(n,0,FAILURE)       




if __name__ == '__main__':
    unittest.main()
    
