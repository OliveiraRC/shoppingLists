"""
CONTROLLER HOME - Lógica de Negócio (MVC)
Mediador entre Model e View
"""
import os
from datetime import datetime
from typing import List, Tuple
from models.database import db
from views.home_view import HomeView


class HomeController:
    def __init__(self, view: HomeView, lista_controller):
        self.view = view
        self.lista_controller = lista_controller
        self.selecionadas = set()
    
    def handle_event(self, action: str, *args):
        """Dispatcher central de eventos"""
        print(f"🔥 EVENTO: {action}, args: {args}")  # DEBUG
        handlers = {
            'create_lista': self.create_lista,
            'filter_lists': self.filter_lists,
            'export_selected': self.export_selected,
            'export_excel': self.export_excel,
            'export_pdf': self.export_pdf,
            'confirm_delete_lista': self.confirm_delete_lista,
            'open_lista': self.open_lista
        }
        handlers[action](*args)
    
    def create_lista(self, nome: str):
        db.create_lista(nome)
        self.refresh_listas()
    
    def filter_lists(self, filtro: str):
        self.refresh_listas(filtro)
    
    def refresh_listas(self, filtro: str = ""):
        listas = db.get_listas(filtro)
        if self.view:
            self.view.update_listas(listas, self.selecionadas)
    
    def export_selected(self):
        if self.selecionadas:
            self.view.show_export_dialog(len(self.selecionadas))
    
    def toggle_selecao(self, lista_id: int, ativo: bool):
        if ativo:
            self.selecionadas.add(lista_id)
        else:
            self.selecionadas.discard(lista_id)
        self.refresh_listas()
    
    def export_excel(self, lista_ids: List[int]):
        self._export_file(lista_ids, self._create_excel)
    
    def export_pdf(self, lista_ids: List[int]):
        self._export_file(lista_ids, self._create_pdf)
    
    def _export_file(self, lista_ids: List[int], create_func):
        try:
            pasta = self._choose_folder()
            filename = create_func(pasta, lista_ids)
            self.view.show_message(f"✅ {os.path.basename(filename)} salvo!")
        except Exception as e:
            self.view.show_message(f"❌ Erro: {str(e)}")
    
    def _choose_folder(self) -> str:
        """Escolha de pasta (simplificado)"""
        try:
            from plyer import filechooser
            result = filechooser.open_directory()
            return result[0] if result else os.getcwd()
        except:
            return os.getcwd()
    
    def _create_excel(self, pasta: str, lista_ids: List[int]) -> str:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(["Lista", "Item", "Qtd", "Preço", "Comprado", "Subtotal"])
        
        total = 0
        for lista_id in lista_ids:
            nome_lista = db.get_lista_nome(lista_id)
            for item in db.get_itens(lista_id):
                _, nome, qtd, preco, comprado = item
                subtotal = qtd * preco if comprado else 0
                if comprado: total += subtotal
                ws.append([nome_lista, nome, qtd, f"R${preco:.2f}", 
                          "Sim" if comprado else "Não", f"R${subtotal:.2f}"])
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(pasta, f"lista_compras_{timestamp}.xlsx")
        wb.save(filename)
        return filename
    
    def _create_pdf(self, pasta: str, lista_ids: List[int]) -> str:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(pasta, f"lista_compras_{timestamp}.pdf")
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("🛒 Lista de Compras", styles['Title']))
        total = 0
        
        for lista_id in lista_ids:
            nome_lista = db.get_lista_nome(lista_id)
            itens = db.get_itens(lista_id)
            if itens:
                story.append(Paragraph(nome_lista, styles['Heading2']))
                data = [["Item", "Qtd", "Preço", "Status", "Total"]]
                for _, nome, qtd, preco, comprado in itens:
                    subtotal = qtd * preco if comprado else 0
                    if comprado: total += subtotal
                    data.append([nome, f"{qtd:.1f}", f"R${preco:.2f}", 
                               "✅" if comprado else "❌", f"R${subtotal:.2f}"])
                
                t = Table(data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.grey),
                    ('GRID', (0,0), (-1,-1), 1, colors.black)
                ]))
                story.append(t)
        
        story.append(Paragraph(f"Total: R$ {total:.2f}", styles['Heading3']))
        doc.build(story)
        return filename
    
    def confirm_delete_lista(self, lista_id: int):
        def on_confirm(dialog):
            db.delete_lista(lista_id)
            if lista_id in self.selecionadas:
                self.selecionadas.discard(lista_id)
            self.refresh_listas()
            dialog.dismiss()
        self.view.show_confirm_dialog("Excluir Lista?", "Todos os itens serão removidos.", on_confirm)
    
    def open_lista(self, lista_id: int):
        """Navega para tela de itens"""
        print(f"🚀 Abrindo lista ID: {lista_id}")  # DEBUG
        self.lista_controller.show_lista(lista_id)
        self.view.sm.current = 'lista'  # ✅ MUDA PARA TELA DE ITENS
