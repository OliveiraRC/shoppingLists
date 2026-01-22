"""
CONTROLLER LISTA - Lógica de itens (MVC)
"""
from typing import List, Tuple, Callable
from models.database import db


class ListaController:
    def __init__(self, lista_view, home_view):
        self.lista_view = lista_view
        self.home_view = home_view
    
    def handle_event(self, action: str, *args):
        """Dispatcher de eventos da tela de itens"""
        handlers = {
            'load_itens': self.load_itens,
            'add_item': self.add_item,
            'filter_itens': self.filter_itens,
            'toggle_item': self.toggle_item,
            'confirm_delete_item': self.confirm_delete_item,
            'go_home': self.go_home
        }
        handlers[action](*args)
    
    def show_lista(self, lista_id: int):
        """Carrega itens da lista específica"""
        print(f"📋 ListaController: Carregando lista {lista_id}")  # DEBUG
        self.lista_view.show_lista(lista_id)
        self.lista_view.lista_id = lista_id  # ✅ ARMAZENA ID ATUAL
        self.lista_view.sm.current = 'lista'  # ✅ ATIVA TELA
        self.load_itens(lista_id)  # ✅ CARREGA ITENS
    
    def load_itens(self, lista_id: int):
        """Carrega todos itens da lista"""
        self._refresh_itens(lista_id, "")
    
    def filter_itens(self, lista_id: int, filtro: str):
        """Filtra itens por nome"""
        self._refresh_itens(lista_id, filtro)
    
    def _refresh_itens(self, lista_id: int, filtro: str):
        """Atualiza view com itens filtrados"""
        itens = db.get_itens(lista_id, filtro)
        total = db.get_total_comprados(lista_id)
        self.lista_view.update_itens(itens, total)
    
    def add_item(self, lista_id: int, nome: str, qtd: float, preco: float):
        """Adiciona novo item"""
        db.create_item(lista_id, nome, qtd, preco)
        self._refresh_itens(lista_id, "")
    
    def toggle_item(self, item_id: int, comprado: bool):
        """Marca/desmarca item como comprado"""
        db.toggle_item(item_id, comprado)
        # Recarrega lista atual se estiver aberta
        if self.lista_view.lista_id:
            self._refresh_itens(self.lista_view.lista_id, "")
    
    def confirm_delete_item(self, item_id: int):
        """Confirma exclusão de item"""
        def on_confirm(dialog):
            db.delete_item(item_id)
            if self.lista_view.lista_id:
                self._refresh_itens(self.lista_view.lista_id, "")
            dialog.dismiss()
        
        self.lista_view.show_confirm_dialog(
            "Excluir Item?", 
            "Este item será removido permanentemente.", 
            on_confirm
        )
    
    def go_home(self):
        """Volta para tela inicial"""
        self.home_view.sm.current = 'home'
