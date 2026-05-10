import socket
import json
import os
import threading # Para no congelar la app mientras busca
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle

# --- CONFIGURACIÓN ---
# Ya no dependemos de una MAC estática obligatoriamente
MAC_ADDRESS_DEFAULT = "00:18:E4:34:55:A2" 

class BotonPersonalizado(Button):
    def __init__(self, letra='P', **kwargs):
        super().__init__(**kwargs)
        self.letra = letra
        self.text = letra
        self.size_hint = (None, None)
        self.size = (180, 180)
        self.background_normal = '' 
        self.background_color = (0.2, 0.6, 1, 1)
        self.font_size = '30sp'

    def on_touch_down(self, touch):
        if App.get_running_app().modo_edicion and self.collide_point(*touch.pos):
            if touch.is_double_tap:
                App.get_running_app().canvas_layout.remove_widget(self)
                return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if App.get_running_app().modo_edicion and self.collide_point(*touch.pos):
            self.center = touch.pos
            return True
        return super().on_touch_move(touch)

    def on_press(self):
        if not App.get_running_app().modo_edicion:
            self.background_color = (0, 1, 0.4, 1) 
            App.get_running_app().enviar_comando(self.letra)
    
    def on_release(self):
        if not App.get_running_app().modo_edicion:
            self.background_color = (0.2, 0.6, 1, 1)

class ControlBluetoothApp(App):
    modo_edicion = False
    s = None
    mac_seleccionada = MAC_ADDRESS_DEFAULT

    def build(self):
        self.main_layout = BoxLayout(orientation='horizontal')
        
        # --- PANEL LATERAL IZQUIERDO ---
        self.menu_lateral = BoxLayout(
            orientation='vertical', 
            size_hint=(None, 1), 
            width=220, 
            spacing=8, 
            padding=10
        )
        
        with self.menu_lateral.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            self.rect = Rectangle(size=self.menu_lateral.size, pos=self.menu_lateral.pos)
        self.menu_lateral.bind(size=self._update_rect, pos=self._update_rect)

        # Secciones del Menú
        self.menu_lateral.add_widget(Label(text="CONEXIÓN", bold=True, color=(0, 1, 1, 1)))
        
        btn_scan = Button(text="BUSCAR HC-05", background_color=(0.2, 0.4, 1, 1))
        btn_scan.bind(on_release=self.popup_escaneo)
        self.menu_lateral.add_widget(btn_scan)

        self.lbl_status = Label(text="Estado: Desconectado", font_size='12sp', color=(1, 0, 0, 1))
        self.menu_lateral.add_widget(self.lbl_status)

        self.menu_lateral.add_widget(Label(text="CONTROLES", bold=True))
        
        btn_add = Button(text="[+] CREAR", background_color=(0, 0.8, 0, 1))
        btn_add.bind(on_release=self.popup_nuevo_boton)
        
        self.btn_edit = Button(text="MODO: JUGAR", background_color=(0.3, 0.3, 0.3, 1))
        self.btn_edit.bind(on_release=self.alternar_edicion)
        
        btn_save = Button(text="GUARDAR JSON")
        btn_save.bind(on_release=self.guardar_config)
        
        btn_load = Button(text="CARGAR JSON")
        btn_load.bind(on_release=self.cargar_config)

        self.menu_lateral.add_widget(btn_add)
        self.menu_lateral.add_widget(self.btn_edit)
        self.menu_lateral.add_widget(btn_save)
        self.menu_lateral.add_widget(btn_load)
        self.menu_lateral.add_widget(Label()) 

        # --- ÁREA DE JUEGO (DERECHA) ---
        self.canvas_layout = FloatLayout()
        
        self.main_layout.add_widget(self.menu_lateral)
        self.main_layout.add_widget(self.canvas_layout)
        
        return self.main_layout

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    # --- LÓGICA DE BÚSQUEDA PROPIA ---
    def popup_escaneo(self, instance):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.lista_dispositivos = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.lista_dispositivos.bind(minimum_height=self.lista_dispositivos.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.lista_dispositivos)
        
        layout.add_widget(Label(text="Dispositivos Vinculados/Cercanos:", size_hint_y=None, height=40))
        layout.add_widget(scroll)
        
        btn_cerrar = Button(text="Cerrar", size_hint_y=None, height=50)
        layout.add_widget(btn_cerrar)
        
        self.pop_bt = Popup(title="Escáner Bluetooth", content=layout, size_hint=(0.8, 0.8))
        btn_cerrar.bind(on_release=self.pop_bt.dismiss)
        
        self.pop_bt.open()
        # Iniciar búsqueda en un hilo separado para no trabar la interfaz
        threading.Thread(target=self.buscar_dispositivos_bt).start()

    def buscar_dispositivos_bt(self):
        # En Android/Linux, socket.discover_devices() busca señales en el aire
        try:
            import bluetooth # Requiere PyBluez o similar en PC, Pyjnius en Android
            nearby_devices = bluetooth.discover_devices(duration=4, lookup_names=True, flush_cache=True)
        except:
            # Simulación si no hay librería bluetooth instalada
            nearby_devices = [("00:18:E4:34:55:A2", "HC-05 (Simulado)"), ("12:34:56:78:90:AB", "Otro Dispositivo")]

        self.lista_dispositivos.clear_widgets()
        for addr, name in nearby_devices:
            btn_dev = Button(text=f"{name}\n{addr}", size_hint_y=None, height=80, halign='center')
            btn_dev.bind(on_release=lambda x, a=addr: self.conectar_a_mac(a))
            self.lista_dispositivos.add_widget(btn_dev)

    def conectar_a_mac(self, mac):
        self.mac_seleccionada = mac
        try:
            if self.s: self.s.close()
            self.s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.s.connect((self.mac_seleccionada, 1))
            self.lbl_status.text = f"Conectado a:\n{self.mac_seleccionada}"
            self.lbl_status.color = (0, 1, 0, 1)
            if hasattr(self, 'pop_bt'): self.pop_bt.dismiss()
        except Exception as e:
            self.lbl_status.text = "Error de Conexión"
            self.lbl_status.color = (1, 0, 0, 1)
            print(f"Error: {e}")

    # --- RESTO DE FUNCIONES (IGUALES) ---
    def enviar_comando(self, letra):
        if self.s:
            try:
                self.s.send(bytes(letra, 'UTF-8'))
            except:
                self.lbl_status.text = "Desconectado"
                self.lbl_status.color = (1, 0, 0, 1)
        print(f"Enviando: {letra}")

    def alternar_edicion(self, instance):
        self.modo_edicion = not self.modo_edicion
        if self.modo_edicion:
            instance.text = "MODO: EDITAR\n(Doble tap borrar)"
            instance.background_color = (1, 0.5, 0, 1)
        else:
            instance.text = "MODO: JUGAR"
            instance.background_color = (0.3, 0.3, 0.3, 1)

    def popup_nuevo_boton(self, instance):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.txt_letra = TextInput(text='W', multiline=False, halign='center', font_size=40)
        self.txt_size = TextInput(text='180', multiline=False, halign='center')
        layout.add_widget(Label(text="Letra para Arduino:"))
        layout.add_widget(self.txt_letra)
        layout.add_widget(Label(text="Tamaño (px):"))
        layout.add_widget(self.txt_size)
        btn_confirm = Button(text="CREAR", size_hint_y=None, height=100)
        layout.add_widget(btn_confirm)
        self.pop = Popup(title="Nuevo Control", content=layout, size_hint=(0.5, 0.6))
        btn_confirm.bind(on_release=self.crear_boton_final)
        self.pop.open()

    def crear_boton_final(self, instance):
        l = self.txt_letra.text.upper()
        s = int(self.txt_size.text) if self.txt_size.text.isdigit() else 180
        btn = BotonPersonalizado(letra=l, pos=(300, 300))
        btn.size = (s, s)
        self.canvas_layout.add_widget(btn)
        self.pop.dismiss()

    def guardar_config(self, instance):
        config = []
        for b in self.canvas_layout.children:
            if isinstance(b, BotonPersonalizado):
                config.append({'letra': b.letra, 'pos': b.pos, 'size': b.size})
        with open('mi_auto.json', 'w') as f:
            json.dump(config, f)

    def cargar_config(self, instance):
        if not os.path.exists('mi_auto.json'): return
        with open('mi_auto.json', 'r') as f:
            config = json.load(f)
        self.canvas_layout.clear_widgets()
        for c in config:
            btn = BotonPersonalizado(letra=c['letra'], pos=c['pos'])
            btn.size = c['size']
            self.canvas_layout.add_widget(btn)

    def on_stop(self):
        if self.s: self.s.close()

if __name__ == '__main__':
    ControlBluetoothApp().run()
