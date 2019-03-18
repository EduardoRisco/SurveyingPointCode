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

    layer_color = set()
    for i in file_user:
        layer_color.add((i[1], i[2]))

    for l in layer_color:
        if isinstance(l[1], tuple):
            color = (l[1][0] * 6 / 256) * 36 + (l[1][1] * 6 / 256) * 6 + (
                l[1][2] * 6 / 256)
        else:
            color = l[1]
        dwg.layers.new(name=l[0], dxfattribs={'color': color})

    # Capas obligatorias
    dwg.layers.new('Points', dxfattribs={'color': 0})
    dwg.layers.new('Altitude', dxfattribs={'color': 0})
    dwg.layers.new('Label', dxfattribs={'color': 5})


def create_points(dwg, msp, points):
    ''' 
    Función que añade todos los puntos al modelo, en la capa 'Points',
    la altitud en la capa 'Altitude' y el código en la capa 'Label'.
    '''
    # Definición de estilos de texto, elevación y etiqueta
    dwg.styles.new('elevation', dxfattribs={'font': 'arial.ttf', 'width': 0.5})
    dwg.styles.new('label', dxfattribs={'font': 'times.ttf', 'width': 0.8})

    for p in points:
        msp.add_point((p[1][0], p[1][1]), dxfattribs={'layer': 'Points'})
        msp.add_text(p[1][2],
                     dxfattribs={
            'style': 'elevation',
            'height': 0.35,
            'layer': 'Altitude'
        }).set_pos(((p[1][0] + 0.5, p[1][1] + 0.5)), align='LEFT')
        msp.add_text(p[2],
                     dxfattribs={
            'style': 'label',
            'height': 0.35,
            'layer': 'Label'
        }).set_pos(((p[1][0] - 0.5, p[1][1] - 0.5)), align='RIGHT')


def create_circles(msp, circles, file_user):
    ''' 
    Función que crea los circulos con el radio definido por el 
    usuario , y los añade al modelo, en la capa correspondiente.
    '''
    for c in circles:
        for l in file_user:
            if c[3][1] == l[0]:
                layer = l[1]

        msp.add_circle(
            (c[1][0], c[1][1]), c[3][0], dxfattribs={'layer': layer})


def create_lines(msp, lines, file_user):
    ''' 
   Función que crea las lineas definidas por el usuario,
   y las añade al modelo, en la capa correspondiente.
   '''

    for p in lines:
        code_line = p[0][2]
        lin_coord = []
        for coord_points in p:
            lin_coord.append(coord_points[1])
        for l in file_user:
            if code_line == l[0]:
                layer = l[1]
        msp.add_lwpolyline(lin_coord, dxfattribs={'layer': layer})


def create_curves(msp, curves, file_user):
    ''' 
   Función que crea las curvas definidas por el usuario,
   y las añade al modelo, en la capa correspondiente.
   '''

    for p in curves:
        code_line = p[0][2]
        lin_coord = []
        for coord_points in p:
            lin_coord.append(coord_points[1])
        for l in file_user:
            if code_line == l[0]:
                layer = l[1]
        msp.add_spline(lin_coord, dxfattribs={'layer': layer})
