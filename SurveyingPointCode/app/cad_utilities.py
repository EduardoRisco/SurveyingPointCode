"""
 SurveyingPointCode
 Copyright © 2018-2019 J. Eduardo Risco
 
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.txt>.
"""

# cad_utilities.py
# Module containing cad utilities

# Different version options to generate the dxf file
cad_versions = {
    'DXF 2018': 'AC1032',
    'DXF 2013': 'AC1027',
    'DXF 2010': 'AC1024',
    'DXF 2007': 'AC1021',
    'DXF 2004': 'AC1018'
}
# Cad Colors Palette
cad_colors_palette = [(0, 0, 0), (255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255),
                      (0, 0, 255), (255, 0, 255), (255, 255, 255), (128, 128, 128),
                      (192, 192, 192), (255, 0, 0), (255, 127, 127), (204, 0, 0),
                      (204, 102, 102), (153, 0, 0), (153, 76, 76), (127, 0, 0),
                      (127, 63, 63), (76, 0, 0), (76, 38, 38), (255, 63, 0),
                      (255, 159, 127), (204, 51, 0), (204, 127, 102), (153, 38, 0),
                      (153, 95, 76), (127, 31, 0), (127, 79, 63), (76, 19, 0),
                      (76, 47, 38), (255, 127, 0), (255, 191, 127), (204, 102, 0),
                      (204, 153, 102), (153, 76, 0), (153, 114, 76), (127, 63, 0),
                      (127, 95, 63), (76, 38, 0), (76, 57, 38), (255, 191, 0),
                      (255, 223, 127), (204, 153, 0), (204, 178, 102), (153, 114, 0),
                      (153, 133, 76), (127, 95, 0), (127, 111, 63), (76, 57, 0),
                      (76, 66, 38), (255, 255, 0), (255, 255, 127), (204, 204, 0),
                      (204, 204, 102), (152, 152, 0), (152, 152, 76), (127, 127, 0),
                      (127, 127, 63), (76, 76, 0), (76, 76, 38), (191, 255, 0),
                      (223, 255, 127), (153, 204, 0), (178, 204, 102), (114, 152, 0),
                      (133, 152, 76), (95, 127, 0), (111, 127, 63), (57, 76, 0),
                      (66, 76, 38), (127, 255, 0), (191, 255, 127), (102, 204, 0),
                      (153, 204, 102), (76, 152, 0), (114, 152, 76), (63, 127, 0),
                      (95, 127, 63), (38, 76, 0), (57, 76, 38), (63, 255, 0),
                      (159, 255, 127), (51, 204, 0), (127, 204, 102), (38, 152, 0),
                      (95, 152, 76), (31, 127, 0), (79, 127, 63), (19, 76, 0),
                      (47, 76, 38), (0, 255, 0), (127, 255, 127), (0, 204, 0),
                      (102, 204, 102), (0, 152, 0), (76, 152, 76), (0, 127, 0),
                      (63, 127, 63), (0, 76, 0), (38, 76, 38), (0, 255, 63),
                      (127, 255, 159), (0, 204, 51), (102, 204, 127), (0, 152, 38),
                      (76, 152, 95), (0, 127, 31), (63, 127, 79), (0, 76, 19),
                      (38, 76, 47), (0, 255, 127), (127, 255, 191), (0, 204, 102),
                      (102, 204, 153), (0, 152, 76), (76, 152, 114), (0, 127, 63),
                      (63, 127, 95), (0, 76, 38), (38, 76, 57), (0, 255, 191),
                      (127, 255, 223), (0, 204, 153), (102, 204, 178), (0, 152, 114),
                      (76, 152, 133), (0, 127, 95), (63, 127, 111), (0, 76, 57),
                      (38, 76, 66), (0, 255, 255), (127, 255, 255), (0, 204, 204),
                      (102, 204, 204), (0, 152, 152), (76, 152, 152), (0, 127, 127),
                      (63, 127, 127), (0, 76, 76), (38, 76, 76), (0, 191, 255),
                      (127, 223, 255), (0, 153, 204), (102, 178, 204), (0, 114, 152),
                      (76, 133, 152), (0, 95, 127), (63, 111, 127), (0, 57, 76),
                      (38, 66, 76), (0, 127, 255), (127, 191, 255), (0, 102, 204),
                      (102, 153, 204), (0, 76, 152), (76, 114, 152), (0, 63, 127),
                      (63, 95, 127), (0, 38, 76), (38, 57, 76), (0, 63, 255),
                      (127, 159, 255), (0, 51, 204), (102, 127, 204), (0, 38, 152),
                      (76, 95, 152), (0, 31, 127), (63, 79, 127), (0, 19, 76),
                      (38, 47, 76), (0, 0, 255), (127, 127, 255), (0, 0, 204),
                      (102, 102, 204), (0, 0, 152), (76, 76, 152), (0, 0, 127),
                      (63, 63, 127), (0, 0, 76), (38, 38, 76), (63, 0, 255),
                      (159, 127, 255), (51, 0, 204), (127, 102, 204), (38, 0, 152),
                      (95, 76, 152), (31, 0, 127), (79, 63, 127), (19, 0, 76),
                      (47, 38, 76), (127, 0, 255), (191, 127, 255), (102, 0, 204),
                      (153, 102, 204), (76, 0, 152), (114, 76, 152), (63, 0, 127),
                      (95, 63, 127), (38, 0, 76), (57, 38, 76), (191, 0, 255),
                      (223, 127, 255), (153, 0, 204), (178, 102, 204), (114, 0, 152),
                      (133, 76, 152), (95, 0, 127), (111, 63, 127), (57, 0, 76),
                      (66, 38, 76), (255, 0, 255), (255, 127, 255), (204, 0, 204),
                      (204, 102, 204), (152, 0, 152), (152, 76, 152), (127, 0, 127),
                      (127, 63, 127), (76, 0, 76), (76, 38, 76), (255, 0, 191),
                      (255, 127, 223), (204, 0, 153), (204, 102, 178), (152, 0, 114),
                      (152, 76, 133), (127, 0, 95), (127, 63, 111), (76, 0, 57),
                      (76, 38, 66), (255, 0, 127), (255, 127, 191), (204, 0, 102),
                      (204, 102, 153), (152, 0, 76), (152, 76, 114), (127, 0, 63),
                      (127, 63, 95), (76, 0, 38), (76, 38, 57), (255, 0, 63),
                      (255, 127, 159), (204, 0, 51), (204, 102, 127), (152, 0, 38),
                      (152, 76, 95), (127, 0, 31), (127, 63, 79), (76, 0, 19),
                      (76, 38, 47), (51, 51, 51), (91, 91, 91), (132, 132, 132),
                      (173, 173, 173), (214, 214, 214), (255, 255, 255)]
