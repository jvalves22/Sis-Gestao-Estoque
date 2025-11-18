import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        """Inicializa a conexão com o banco de dados SQLite e cria as tabelas"""
        self.conn = sqlite3.connect('estoque.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Cria as tabelas do banco de dados se elas não existirem"""
        cursor = self.conn.cursor()
        
        # Tabela de produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                stock INTEGER,
                brand TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de histórico de estoque
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                old_stock INTEGER,
                new_stock INTEGER,
                change_type TEXT,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def execute(self, query, params=()):
        """Executa uma query SQL e retorna o cursor"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
    
    def fetch_one(self, query, params=()):
        """Executa uma query e retorna um único resultado"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def fetch_all(self, query, params=()):
        """Executa uma query e retorna todos os resultados"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()