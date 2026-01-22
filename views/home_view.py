"""
VIEW HOME - Camada de Apresentação (MVC)
Apenas UI + callbacks para Controller
Sem lógica de negócio, sem banco
"""
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.screenmanager import Screen
from typing import Callable, List


class HomeView(Screen):
    def __init__(self, controller_callback: Callable, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        self.controller_callback = controller_callback  # Referência ao Controller
        self.selecionadas = set()
        self._build_ui()
    
    def _build_ui(self):
        """Constrói interface completa"""
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Toolbar
        toolbar = MDTopAppBar(title="🛒 Minhas Listas")
        layout.add_widget(toolbar)
        
        # Filtro
        filtro_layout = MDBoxLayout(size_hint_y=None, height=60, spacing=10)
        self.input_filtro = MDTextField(
            hint_text="🔍 Filtrar listas...", 
            on_text_validate=lambda x: self.controller_callback('filter_lists', self.input_filtro.text)
        )
        btn_limpar = MDIconButton(
            icon="close-circle", on_release=lambda x: self._clear_filter()
        )
        filtro_layout.add_widget(self.input_filtro)
        filtro_layout.add_widget(btn_limpar)
        layout.add_widget(filtro_layout)
        
        # Inputs + botões
        input_layout = MDBoxLayout(size_hint_y=None, height=60, spacing=10)
        self.input_nova = MDTextField(hint_text="Nome da lista")
        btn_nova = MDRaisedButton(
            text="➕ Criar", 
            size_hint_x=0.3,
            on_release=lambda x: self._create_lista()
        )
        self.btn_exportar = MDRaisedButton(
            text="📊 Exportar", size_hint_x=0.25, disabled=True,
            on_release=lambda x: self.controller_callback('export_selected')
        )
        input_layout.add_widget(self.input_nova)
        input_layout.add_widget(btn_nova)
        input_layout.add_widget(self.btn_exportar)
        layout.add_widget(input_layout)
        
        self.container_listas = MDBoxLayout(orientation='vertical', spacing=15, adaptive_height=True)
        layout.add_widget(self.container_listas)
        
        self.add_widget(layout)
    
    def _create_lista(self):
        """Callback para Controller criar lista"""
        nome = self.input_nova.text.strip()
        if nome:
            self.controller_callback('create_lista', nome)
            self.input_nova.text = ""
    
    def _clear_filter(self):
        """Limpa filtro"""
        self.input_filtro.text = ""
        self.controller_callback('filter_lists', "")
    
    def update_listas(self, listas_data: List, selecionadas: set):
        """Atualiza display das listas (chamado pelo Controller)"""
        self.container_listas.clear_widgets()
        self.selecionadas = selecionadas
        
        if not listas_data:
            texto = "📝 Crie sua primeira lista!" if not self.input_filtro.text else "❌ Nenhuma encontrada"
            self.container_listas.add_widget(MDLabel(text=texto, halign="center"))
            self.btn_exportar.disabled = True
            return
        
        for lista_id, nome in listas_data:
            self._create_lista_card(lista_id, nome)
        
        self.btn_exportar.disabled = len(selecionadas) == 0
    
    def _create_lista_card(self, lista_id: int, nome: str):
        """Cria card individual da lista"""
        card = MDCard(size_hint_y=None, height=90, radius=[12], padding=15, elevation=2)
        layout = MDBoxLayout(orientation='horizontal', spacing=8, adaptive_height=True)
        
        # Checkbox
        checkbox = MDCheckbox(active=lista_id in self.selecionadas, size_hint_x=None, width=48)
        checkbox.bind(active=lambda x, lid=lista_id: self._toggle_selecao(lid, x.active))
        
        # Nome
        nome_label = MDLabel(text=f"📋 {nome}", theme_text_color="Primary")
        
        # Espaço flexível
        flex_space = MDLabel(size_hint_x=1)
        
        # Botões (chamam Controller)
        btn_excel = MDIconButton(
            icon="file-excel", icon_color=(0, 0.8, 0, 1), size_hint_x=None, width=48,
            on_release=lambda x: self.controller_callback('export_excel', [lista_id])
        )
        btn_pdf = MDIconButton(
            icon="file-pdf-box", icon_color=(0.8, 0, 0, 1), size_hint_x=None, width=48,
            on_release=lambda x: self.controller_callback('export_pdf', [lista_id])
        )
        btn_delete = MDIconButton(
            icon="trash-can-outline", icon_color=(1, 0, 0, 1), size_hint_x=None, width=48,
            on_release=lambda x: self.controller_callback('confirm_delete_lista', lista_id)
        )
        
        # Monta card
        layout.add_widget(checkbox)
        layout.add_widget(nome_label)
        layout.add_widget(flex_space)
        layout.add_widget(btn_excel)
        layout.add_widget(btn_pdf)
        layout.add_widget(btn_delete)
        card.add_widget(layout)
        card.bind(on_release=lambda x: self.controller_callback('open_lista', lista_id))
        
        self.container_listas.add_widget(card)
    
    def _toggle_selecao(self, lista_id: int, ativo: bool):
        """Gerencia seleção"""
        if ativo:
            self.selecionadas.add(lista_id)
        else:
            self.selecionadas.discard(lista_id)
        self.btn_exportar.disabled = len(self.selecionadas) == 0
    
    def show_message(self, texto: str):
        """Exibe diálogo de mensagem"""
        dialog = MDDialog(
            text=texto,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
    
    def show_export_dialog(self, num_listas: int):
        """Diálogo de confirmação export múltiplo"""
        botoes = [MDFlatButton(text="Cancelar", on_release=lambda x: self.export_dialog.dismiss())]
        botoes.append(MDRaisedButton(
            text=f"📊 Excel ({num_listas})",
            on_release=lambda x: self.controller_callback('export_excel', list(self.selecionadas))
        ))
        botoes.append(MDRaisedButton(
            text=f"📄 PDF ({num_listas})",
            on_release=lambda x: self.controller_callback('export_pdf', list(self.selecionadas))
        ))
        
        self.export_dialog = MDDialog(
            title="Exportar Listas", text=f"Exportar {num_listas} lista(s)?", buttons=botoes
        )
        self.export_dialog.open()
    
    def show_confirm_dialog(self, title: str, text: str, on_confirm: Callable):
        """Diálogo genérico de confirmação"""
        dialog = MDDialog(
            title=title, text=text,
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="CONFIRMAR", on_release=lambda x: on_confirm(dialog))
            ]
        )
        dialog.open()
