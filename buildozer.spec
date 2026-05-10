name: Fabricar mi APK
on:
  push:
    branches: [ master ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build with Buildozer
        uses: ArtemSBulgakov/buildozer-action@v1.6.1
        with:
          command: buildozer android debug
          buildozer_version: master

      - name: Subir APK Final
        uses: actions/upload-artifact@v4
        with:
          name: Control_Auto_Anez
          path: bin/*.apk
