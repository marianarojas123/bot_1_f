#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archivo WSGI para despliegue en Hostinger
Este archivo es el punto de entrada para el servidor web
"""

import os
import sys

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(__file__))

# Importar la aplicación Flask
from app import app

# Configurar para producción
if __name__ == "__main__":
    app.run()
else:
    # Para servidores WSGI como Gunicorn
    application = app
