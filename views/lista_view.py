"""
VIEW LISTA - Interface dos Itens
"""
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.screenmanager import Screen
from typing import Callable, List


class ListaView(Screen):
    def __init__(self, controller_callback: Callable, **kwargs):
        super().__init__(**kwargs)
        self.name = 'lista'
        self.controller_callback = controller_callback
        self.lista_id = None
        self._build_ui()
    
    def _build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Toolbar com voltar
        toolbar = MDTopAppBar(title="Itens da Lista")
        toolbar.left_action_items = [['arrow-left', lambda x: self.controller_callback('go_home')]]
        layout.add_widget(toolbar)
        
        self.lbl_total = MDLabel(text="Total comprados: R$ 0,00", bold=True, size_hint_y=None, height=50)
        layout.add_widget(self.lbl_total)
        
        # Filtro itens
        filtro_layout = MDBoxLayout(size_hint_y=None, height=60, spacing=10)
        self.input_filtro_item = MDTextField(
            hint_text="🔍 Filtrar itens...", on_text_validate=lambda x: self._apply_filter()
        )
        btn_limpar = MDIconButton(icon="close-circle", on_release=lambda x: self._clear_filter())
        filtro_layout.add_widget(self.input_filtro_item)
        filtro_layout.add_widget(btn_limpar)
        layout.add_widget(filtro_layout)
        
        # Inputs itens
        input_layout = MDBoxLayout(size_hint_y=None, height=60, spacing=10)
        self.input_nome = MDTextField(hint_text="Item", size_hint_x=0.5)
        self.input_qtd = MDTextField(hint_text="Qtd", input_filter="float", size_hint_x=0.25)
        self.input_preco = MDTextField(hint_text="R$", input_filter="float", size_hint_x=0.25)
        input_layout.add_widget(self.input_nome)
        input_layout.add_widget(self.input_qtd)
        input_layout.add_widget(self.input_preco)
        layout.add_widget(input_layout)
        
        btn_add = MDRaisedButton(
            text="➕ Adicionar", height=50, on_release=lambda x: self._add_item()
        )
        layout.add_widget(btn_add)
        
        self.container_itens = MDBoxLayout(orientation='vertical', spacing=10, adaptive_height=True)
        layout.add_widget(self.container_itens)
        
        self.add_widget(layout)
    
    def show_lista(self, lista_id: int):
        """Carrega lista específica"""
        self.lista_id = lista_id
        self.input_filtro_item.text = ""
        self.controller_callback('load_itens', lista_id)
    
    def _add_item(self):
        """Adiciona item (chama Controller)"""
        nome = self.input_nome.text.strip()
        try:
            qtd = float(self.input_qtd.text or 0)
            preco = float(self.input_preco.text or 0)
            if nome and qtd > 0 and preco > 0 and self.lista_id:
                self.controller_callback('add_item', self.lista_id, nome, qtd, preco)
                self.input_nome.text = self.input_qtd.text = self.input_preco.text = ""
        except ValueError:
            pass
    
    def _apply_filter(self):
        """Aplica filtro de itens"""
        if self.lista_id:
            self.controller_callback('filter_itens', self.lista_id, self.input_filtro_item.text)
    
    def _clear_filter(self):
        self.input_filtro_item.text = ""
        if self.lista_id:
            self.controller_callback('filter_itens', self.lista_id, "")
    
    def update_itens(self, itens_data: List, total: float):
        """Atualiza lista de itens (Controller chama)"""
        self.container_itens.clear_widgets()
        
        if not itens_data:
            self.container_itens.add_widget(MDLabel(text="Nenhum item", halign="center"))
            self.lbl_total.text = "Total comprados: R$ 0,00"
            return
        
        for item_id, nome, qtd, preco, comprado in itens_data:
            self._create_item_row(item_id, nome, qtd, preco, comprado)
        
        self.lbl_total.text = f"Total comprados: R$ {total:.2f}"
    
    def _create_item_row(self, item_id: int, nome: str, qtd: float, preco: float, comprado: int):
        """Linha individual do item"""
        linha = MDBoxLayout(size_hint_y=None, height=55, spacing=10)
        
        chk = MDCheckbox(active=bool(comprado))
        chk.bind(on_release=lambda x: self.controller_callback('toggle_item', item_id, x.active))
        
        subtotal = qtd * preco if comprado else 0
        texto = f"{nome} | {qtd:.1f}x R${preco:.2f}"
        texto += f" = R${subtotal:.2f}" if comprado else " (pendente)"
        
        info = MDLabel(text=texto)
        btn_delete = MDIconButton(
            icon="trash-can-outline", icon_color="red",
            on_release=lambda x: self.controller_callback('confirm_delete_item', item_id)
        )
        
        linha.add_widget(chk)
        linha.add_widget(MDBoxLayout(orientation='vertical', size_hint_x=0.75, children=[info]))
        linha.add_widget(btn_delete)
        self.container_itens.add_widget(linha)
    
    def show_confirm_dialog(self, title: str, text: str, on_confirm: Callable):
        dialog = MDDialog(
            title=title, text=text,
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="EXCLUIR", on_release=lambda x: on_confirm(dialog))
            ]
        )
        dialog.open()
