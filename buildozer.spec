[app]
title = Control Bluetooth
package.name = control_anez
package.domain = org.anez
source.dir = .
# ... resto de la configuración ...
source.include_exts = py,png,jpg,kv,json
version = 0.1
requirements = python3,kivy,pyjnius
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, ACCESS_FINE_LOCATION
orientation = landscape
fullscreen = 1
android.api = 31
android.minapi = 21
android.ndk = 23b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
