# -*- coding: utf-8 -*-
#
# Prototipo App, Funciones geométricas, capas y simbolos.
#
# Se requiere ezdxf.
#
# J. Eduardo Risco 15-03-2019
#

import ezdxf


def create_layers(dwg, file_user):
    ''' 
    Función que lee un archivo y crea las capas definidas por el
    usuario, añadiendolas al modelo.
    '''

    layer = set()
    for i in file_user:
        layer.add((i[1], i[2]))

    for l in layer:
        if isinstance(l[1], tuple):
            color = (l[1][0]*6/256)*36 + (l[1][1]*6/256)*6 + (l[1][2]*6/256)
        else:
            color = l[1]
        dwg.layers.new(name=l[0], dxfattribs={'color': color})

    # Capas obligatorias
    dwg.layers.new('Points', dxfattribs={'color': 0})   
    dwg.layers.new('Altitude', dxfattribs={'color': 0}) 
    dwg.layers.new('Label', dxfattribs={'color': 0}) 



