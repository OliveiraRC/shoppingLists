"""
LISTA DE COMPRAS - ARQUITETURA MVC CORRIGIDA
TechList Solutions - KivyMD 1.2.0
"""
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from models.database import db
from views.home_view import HomeView
from views.lista_view import ListaView
from controllers.home_controller import HomeController
from controllers.lista_controller import ListaController


class MVCApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        
        sm = ScreenManager()
        
        # ✅ CORRIGIDO: Controllers primeiro
        self.lista_controller = ListaController(None, None)  # Temporário
        self.home_controller = HomeController(None, self.lista_controller)
        
        # ✅ CORRIGIDO: Views com callbacks VINCULADOS aos controllers
        home_view = HomeView(lambda action, *args: self.home_controller.handle_event(action, *args))
        lista_view = ListaView(lambda action, *args: self.lista_controller.handle_event(action, *args))
        
        # Injeta ScreenManager e controllers
        home_view.sm = sm
        lista_view.sm = sm
        self.home_controller.view = home_view
        self.lista_controller.lista_view = lista_view
        self.lista_controller.home_view = home_view
        
        sm.add_widget(home_view)
        sm.add_widget(lista_view)
        sm.current = 'home'
        
        return sm
    
    def _create_controller_callback(self, action: str, *args):
        """Callback genérico para views chamarem controllers"""
        # Este método será chamado pelas views
        pass  # Controllers já injetados nas views


if __name__ == '__main__':
    MVCApp().run()
