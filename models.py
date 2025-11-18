from db import Database

class ProductModel:
    """Classe responsável por todas as operações relacionadas a produtos"""
    
    def __init__(self):
        """Inicializa o modelo de produtos com conexão ao banco"""
        self.db = Database()
    
    def create(self, product_data):
        """
        Cria um novo produto no banco de dados
        
        Args:
            product_data (dict): Dicionário com os dados do produto
        
        Returns:
            int: ID do produto criado
        """
        query = '''
            INSERT INTO products (
                name, description, price, stock, brand
            ) VALUES (?, ?, ?, ?, ?)
        '''
        
        params = (
            product_data.get('name'),
            product_data.get('description', ''),
            product_data.get('price', 0),
            product_data.get('stock', 0),
            product_data.get('brand', '')
        )
        
        cursor = self.db.execute(query, params)
        return cursor.lastrowid
    
    def get_all(self):
        """
        Busca todos os produtos ordenados pela data de atualização
        
        Returns:
            list: Lista de todos os produtos
        """
        query = 'SELECT * FROM products ORDER BY updated_at DESC'
        return self.db.fetch_all(query)
    
    def get_by_id(self, product_id):
        """
        Busca um produto específico pelo ID
        
        Args:
            product_id (int): ID do produto
        
        Returns:
            tuple: Dados do produto ou None se não encontrado
        """
        query = 'SELECT * FROM products WHERE id = ?'
        return self.db.fetch_one(query, (product_id,))
    
    def update(self, product_id, update_data):
        """
        Atualiza os dados de um produto
        
        Args:
            product_id (int): ID do produto a ser atualizado
            update_data (dict): Dicionário com os campos a serem atualizados
        
        Returns:
            bool: True se atualizado com sucesso
        """
        set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
        query = f'UPDATE products SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
        
        params = []
        for value in update_data.values():
            params.append(value)
        params.append(product_id)
        
        self.db.execute(query, params)
        return True
    
    def delete(self, product_id):
        """
        Exclui um produto do banco de dados
        
        Args:
            product_id (int): ID do produto a ser excluído
        
        Returns:
            bool: True se excluído com sucesso
        """
        query = 'DELETE FROM products WHERE id = ?'
        self.db.execute(query, (product_id,))
        return True
    
    def update_stock(self, product_id, new_stock, change_type='manual', reason=''):
        """
        Atualiza o estoque de um produto e registra no histórico
        
        Args:
            product_id (int): ID do produto
            new_stock (int): Novo valor de estoque
            change_type (str): Tipo de alteração (manual, venda, etc.)
            reason (str): Motivo da alteração
        
        Returns:
            bool: True se atualizado com sucesso
        """
        product = self.get_by_id(product_id)
        if not product:
            return False
        
        old_stock = product[4]  # stock está na posição 4
        
        # Atualiza o estoque
        self.update(product_id, {'stock': new_stock})
        
        # Registra no histórico
        query = '''
            INSERT INTO stock_history 
            (product_id, old_stock, new_stock, change_type, reason)
            VALUES (?, ?, ?, ?, ?)
        '''
        self.db.execute(query, (product_id, old_stock, new_stock, change_type, reason))
        
        return True
    
    def search(self, search_term):
        """
        Busca produtos por nome, marca ou ID
        
        Args:
            search_term (str): Termo para busca (pode ser nome, marca ou ID)
        
        Returns:
            list: Lista de produtos que correspondem à busca
        """
        query = '''
            SELECT * FROM products 
            WHERE name LIKE ? OR brand LIKE ? OR id = ?
            ORDER BY name
        '''
        try:
            # Tenta converter para número (busca por ID)
            search_id = int(search_term)
        except ValueError:
            search_id = -1  # Se não for número, busca apenas por texto
        
        search_pattern = f'%{search_term}%'
        return self.db.fetch_all(query, (search_pattern, search_pattern, search_id))
    
    def get_low_stock(self, threshold=10):
        """
        Busca produtos com estoque baixo
        
        Args:
            threshold (int): Limite para considerar estoque baixo
        
        Returns:
            list: Produtos com estoque <= threshold
        """
        query = 'SELECT * FROM products WHERE stock <= ? ORDER BY stock ASC'
        return self.db.fetch_all(query, (threshold,))
    
    def get_out_of_stock(self):
        """
        Busca produtos sem estoque
        
        Returns:
            list: Produtos com estoque zero
        """
        query = 'SELECT * FROM products WHERE stock = 0 ORDER BY name'
        return self.db.fetch_all(query)

class StockHistoryModel:
    """Classe responsável por operações relacionadas ao histórico de estoque"""
    
    def __init__(self):
        """Inicializa o modelo de histórico com conexão ao banco"""
        self.db = Database()
    
    def get_by_product(self, product_id, limit=50):
        """
        Busca histórico de estoque de um produto específico
        
        Args:
            product_id (int): ID do produto
            limit (int): Limite de registros a retornar
        
        Returns:
            list: Histórico de movimentações do produto
        """
        query = '''
            SELECT sh.*, p.name 
            FROM stock_history sh 
            JOIN products p ON sh.product_id = p.id 
            WHERE sh.product_id = ? 
            ORDER BY sh.created_at DESC 
            LIMIT ?
        '''
        return self.db.fetch_all(query, (product_id, limit))
    
    def get_recent(self, limit=50):
        """
        Busca histórico recente de todos os produtos
        
        Args:
            limit (int): Limite de registros a retornar
        
        Returns:
            list: Histórico recente de movimentações
        """
        query = '''
            SELECT sh.*, p.name 
            FROM stock_history sh 
            JOIN products p ON sh.product_id = p.id 
            ORDER BY sh.created_at DESC 
            LIMIT ?
        '''
        return self.db.fetch_all(query, (limit,))