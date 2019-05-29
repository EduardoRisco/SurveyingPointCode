<p align="center">
  <img src="https://github.com/EduardoRisco/SurveyingPointCode/blob/master/Docs/Logo/Logo_spc.png">
</p>   

[![License](https://flat.badgen.net/badge/license/GPL%203/cyan)](https://github.com/EduardoRisco/SurveyingPointCode/blob/master/LICENSE.txt)
[![Docker1](https://flat.badgen.net/badge/docker-python/3.7Alpine/blue?icon=docker)](https://hub.docker.com/_/python)
[![Docker2](https://flat.badgen.net/badge/docker-postgis/mdillon\postgis/blue?icon=docker)](https://hub.docker.com/r/mdillon/postgis/)
[![Docker3](https://flat.badgen.net/badge/docker-pgadmin4/dpage\pgadmin4/blue?icon=docker)](https://hub.docker.com/r/dpage/pgadmin4/)
[![CodeBEAT](https://flat.badgen.net/badge/codebeat/3,80%20GPA/green)](https://codebeat.co/projects/github-com-eduardorisco-surveyingpointcode-master)


# Surveying Point Code      
![Iconos](https://github.com/EduardoRisco/SurveyingPointCode/blob/master/Docs/Logo/Transf_opt.png)
## Allows to automate the delineation process in CAD, by coding points in a topographic survey.



### Key features:

- Topographic coding customized by the user.
- It links topographic codes to : layers, colours and CAD blocks.
- Automatic drawing of lines and splines.
- Simplified and automatic drawing of squares, rectangles and circles.
- Automatic insertion of symbols and CAD blocks.
- It generates different versions of DXF: DXF 2018  DXF 2013, DXF 2010, DXF 2007 and DXF 2004

![Iconos](https://github.com/EduardoRisco/SurveyingPointCode/blob/master/Docs/Logo/portada2.png)

### Environment setup instructions:

- Docker installation.
- Docker Compose installation.
- Cloning the main repository.
- Run in the SurveyingPointCode/ directory:
   ```
   sh app_install.sh
   ```
- In order to install  with PgAdmin4, run in the SurveyingPointCode/ directory: 
   ```
   sh app_install_pgadmin.sh
   ```
- URL  SurveyingPointCode  http://0.0.0.0:5000 
- URL  PgAdmin4  http://0.0.0.0:80

## License

Copyright © 2018-2019 J. Eduardo Risco

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
