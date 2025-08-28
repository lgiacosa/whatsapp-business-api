#!/usr/bin/env python3

import sys
import os

# Agregar el directorio del proyecto al path
path = '/home/tuusuario/whatsapp-api'
if path not in sys.path:
    sys.path.append(path)

from wsp_server import app as application

if __name__ == "__main__":
    application.run()
