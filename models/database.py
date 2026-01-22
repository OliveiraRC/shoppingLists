"""
MODELO - Camada de Dados (MVC)
Responsável apenas por CRUD e banco SQLite
Sem UI, sem lógica de negócio
"""
import sqlite3
from typing import List, Tuple, Optional


class Database:
    """Gerenciador completo do banco SQLite"""
    
    def __init__(self, db_path: str = 'compras.db'):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self) -> None:
        """Cria estrutura do banco se não existir"""
        with self._conn:
            self._conn.execute('''CREATE TABLE IF NOT EXISTS listas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL
            )''')
            self._conn.execute('''CREATE TABLE IF NOT EXISTS itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lista_id INTEGER,
                nome TEXT,
                quantidade REAL,
                preco_unit REAL,
                comprado INTEGER DEFAULT 0,
                FOREIGN KEY(lista_id) REFERENCES listas(id)
            )''')
    
    # ===== LISTAS =====
    def create_lista(self, nome: str) -> int:
        """Cria lista e retorna ID"""
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("INSERT INTO listas (nome) VALUES (?)", (nome,))
            return cursor.lastrowid
    
    def delete_lista(self, lista_id: int) -> None:
        """Remove lista e todos seus itens"""
        with self._conn:
            self._conn.execute("DELETE FROM itens WHERE lista_id=?", (lista_id,))
            self._conn.execute("DELETE FROM listas WHERE id=?", (lista_id,))
    
    def get_listas(self, filtro: str = "") -> List[Tuple[int, str]]:
        """Lista todas ou filtradas por nome"""
        with self._conn:
            cursor = self._conn.cursor()
            if filtro:
                cursor.execute(
                    "SELECT id, nome FROM listas WHERE nome LIKE ? ORDER BY id DESC",
                    (f'%{filtro}%',)
                )
            else:
                cursor.execute("SELECT id, nome FROM listas ORDER BY id DESC")
            return cursor.fetchall()
    
    def get_lista_nome(self, lista_id: int) -> str:
        """Nome da lista por ID"""
        cursor = self._conn.cursor()
        cursor.execute("SELECT nome FROM listas WHERE id=?", (lista_id,))
        result = cursor.fetchone()
        return result[0] if result else f"Lista {lista_id}"
    
    # ===== ITENS =====
    def create_item(self, lista_id: int, nome: str, qtd: float, preco: float) -> None:
        """Adiciona item à lista"""
        with self._conn:
            self._conn.execute(
                "INSERT INTO itens (lista_id, nome, quantidade, preco_unit) VALUES (?, ?, ?, ?)",
                (lista_id, nome, qtd, preco)
            )
    
    def delete_item(self, item_id: int) -> None:
        """Remove item específico"""
        with self._conn:
            self._conn.execute("DELETE FROM itens WHERE id=?", (item_id,))
    
    def toggle_item(self, item_id: int, comprado: bool) -> None:
        """Marca/desmarca como comprado"""
        with self._conn:
            self._conn.execute(
                "UPDATE itens SET comprado=? WHERE id=?", (int(comprado), item_id)
            )
    
    def get_itens(self, lista_id: int, filtro: str = "") -> List[Tuple[int, str, float, float, int]]:
        """Itens da lista com filtro opcional"""
        cursor = self._conn.cursor()
        if filtro:
            cursor.execute(
                "SELECT id, nome, quantidade, preco_unit, comprado FROM itens "
                "WHERE lista_id=? AND nome LIKE ? ORDER BY id",
                (lista_id, f'%{filtro}%')
            )
        else:
            cursor.execute(
                "SELECT id, nome, quantidade, preco_unit, comprado FROM itens "
                "WHERE lista_id=? ORDER BY id", (lista_id,)
            )
        return cursor.fetchall()
    
    def get_total_comprados(self, lista_id: int) -> float:
        """Calcula total apenas de itens comprados"""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT SUM(quantidade * preco_unit) FROM itens 
            WHERE lista_id=? AND comprado=1
        """, (lista_id,))
        result = cursor.fetchone()[0]
        return result or 0.0

# Instância global singleton
db = Database()
