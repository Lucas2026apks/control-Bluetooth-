[app]
title = control bluetooth
package.name = control 
package.domain = org.Lucas mateo anez
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 0.1

# Requerimientos de software
requirements = python3,kivy,pyjnius

# Permisos para Bluetooth y ubicación (necesario en Android moderno)
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, ACCESS_FINE_LOCATION

# Orientación para el control
orientation = landscape
fullscreen = 1

# Configuración para la "fábrica" de GitHub
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
