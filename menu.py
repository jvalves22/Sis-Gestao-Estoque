from rich.console import Console
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich import box

from models import ProductModel, StockHistoryModel

console = Console()

class MenuManager:
    """Classe principal que gerencia toda a interface do usuário"""
    
    def __init__(self):
        """Inicializa o gerenciador de menus com os modelos de dados"""
        self.product_model = ProductModel()
        self.history_model = StockHistoryModel()
    
    def clear_screen(self):
        """Limpa a tela do terminal"""
        console.clear()
    
    def show_header(self, subtitle=""):
        """
        Exibe o cabeçalho do sistema com título opcional
        
        Args:
            subtitle (str): Subtítulo opcional para a tela atual
        """
        self.clear_screen()
        title = "📦 [bold magenta]Sistema de Gestão de Estoque[/bold magenta]"
        if subtitle:
            title += f"\n[bold cyan]{subtitle}[/bold cyan]"
        console.print(Panel.fit(title, border_style="magenta"))
    
    def wait_for_enter(self):
        """Aguarda o usuário pressionar Enter para continuar"""
        Prompt.ask("\n[dim]Pressione Enter para continuar[/dim]")
    
    def select_product(self, prompt_text="Selecione o produto:"):
        """
        Mostra lista de produtos para seleção com busca interativa
        
        Args:
            prompt_text (str): Texto personalizado para o prompt
        
        Returns:
            tuple: Dados do produto selecionado ou None se voltar
        """
        while True:
            search_term = Prompt.ask(f"\n{prompt_text} (digite nome, marca ou ID)").strip()
            
            # Permite voltar a qualquer momento
            if search_term.lower() in ['voltar', '0', 'sair']:
                return None
            
            if not search_term:
                console.print("[yellow]Digite um termo para busca[/yellow]")
                continue
            
            # Busca produtos
            results = self.product_model.search(search_term)
            
            if not results:
                console.print(f"[yellow]Nenhum produto encontrado para '{search_term}'[/yellow]")
                continue
            
            # Mostrar resultados em lista numerada
            console.print(f"\n[green]✓ Encontrados {len(results)} produtos:[/green]")
            
            table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
            table.add_column("#", style="cyan", width=4)
            table.add_column("ID", style="dim", width=6)
            table.add_column("Nome", style="white")
            table.add_column("Marca", style="blue")
            table.add_column("Estoque", style="red")
            table.add_column("Preço", style="green")
            
            for i, product in enumerate(results, 1):
                stock_style = "red" if product[4] == 0 else "yellow" if product[4] <= 10 else "green"
                table.add_row(
                    str(i),
                    str(product[0]),
                    product[1][:30] + "..." if len(product[1]) > 30 else product[1],
                    product[5] or "—",
                    f"[{stock_style}]{product[4]}[/{stock_style}]",
                    f"R$ {product[3]:.2f}"
                )
            
            console.print(table)
            
            # Opções para o usuário
            console.print("\n[bold]Opções:[/bold]")
            console.print("[cyan]1-" + str(len(results)) + "[/cyan] - Selecionar produto")
            console.print("[yellow]0[/yellow] - Voltar")
            console.print("[yellow]nova busca[/yellow] - Digitar novo termo de busca")
            
            choice = Prompt.ask("\nSua escolha").strip().lower()
            
            if choice in ['0', 'voltar']:
                return None
            
            if choice in ['nova busca', 'buscar']:
                continue
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(results):
                    return results[choice_num - 1]
                else:
                    console.print("[red]Opção inválida![/red]")
            except ValueError:
                console.print("[red]Digite um número válido[/red]")
    
    def main_menu(self):
        """Menu principal do sistema - ponto de entrada da aplicação"""
        while True:
            self.show_header()
            
            # Estatísticas rápidas
            products = self.product_model.get_all()
            low_stock = self.product_model.get_low_stock()
            out_of_stock = self.product_model.get_out_of_stock()
            
            console.print(f"📊 [bold]Estatísticas:[/bold]")
            console.print(f"   Total de produtos: [cyan]{len(products)}[/cyan]")
            console.print(f"   Estoque baixo: [yellow]{len(low_stock)}[/yellow]")
            console.print(f"   Sem estoque: [red]{len(out_of_stock)}[/red]")
            
            console.print("\n[bold]Menu Principal:[/bold]")
            console.print("1. 📦 Gerenciar Produtos")
            console.print("2. 📊 Controle de Estoque")
            console.print("3. 🔍 Buscar Produtos")
            console.print("4. 📈 Histórico de Estoque")
            console.print("0. 🚪 Sair")
            
            choice = Prompt.ask("\nSelecione uma opção", choices=["0", "1", "2", "3", "4"])
            
            if choice == "1":
                self.products_menu()
            elif choice == "2":
                self.stock_menu()
            elif choice == "3":
                self.search_products()
            elif choice == "4":
                self.history_menu()
            elif choice == "0":
                if Confirm.ask("Tem certeza que deseja sair?"):
                    break
    
    def products_menu(self):
        """Menu de gerenciamento de produtos (CRUD)"""
        while True:
            self.show_header("Gerenciar Produtos")
            
            console.print("[bold]Opções:[/bold]")
            console.print("1. Listar Todos os Produtos")
            console.print("2. Adicionar Produto")
            console.print("3. Editar Produto")
            console.print("4. Excluir Produto")
            console.print("5. Ver Detalhes do Produto")
            console.print("0. ↩️  Voltar ao Menu Principal")
            
            choice = Prompt.ask("\nSelecione uma opção", choices=["0", "1", "2", "3", "4", "5"])
            
            if choice == "1":
                self.list_products()
            elif choice == "2":
                self.add_product()
            elif choice == "3":
                self.edit_product()
            elif choice == "4":
                self.delete_product()
            elif choice == "5":
                self.show_product_details()
            elif choice == "0":
                break
    
    def list_products(self):
        """Lista todos os produtos em formato de tabela"""
        self.show_header("Lista de Produtos")
        
        products = self.product_model.get_all()
        
        if not products:
            console.print("[yellow]Nenhum produto cadastrado.[/yellow]")
            self.wait_for_enter()
            return
        
        table = Table(box=box.ROUNDED)
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Nome", style="white")
        table.add_column("Marca", style="blue")
        table.add_column("Preço", style="green")
        table.add_column("Estoque", style="red")
        table.add_column("Descrição", style="dim")
        
        for product in products:
            stock_style = "red" if product[4] == 0 else "yellow" if product[4] <= 10 else "green"
            description = product[2] or "—"
            table.add_row(
                str(product[0]),
                product[1][:25] + "..." if len(product[1]) > 25 else product[1],
                product[5] or "—",
                f"R$ {product[3]:.2f}",
                f"[{stock_style}]{product[4]}[/{stock_style}]",
                description[:30] + "..." if len(description) > 30 else description
            )
        
        console.print(table)
        self.wait_for_enter()
    
    def add_product(self):
        """Interface para adicionar um novo produto"""
        self.show_header("Adicionar Produto")
        
        name = Prompt.ask("Nome do produto")
        if not name:
            console.print("[red]Nome do produto é obrigatório![/red]")
            self.wait_for_enter()
            return
        
        description = Prompt.ask("Descrição", default="")
        price = FloatPrompt.ask("Preço de venda")
        stock = IntPrompt.ask("Estoque inicial", default=0)
        brand = Prompt.ask("Marca", default="")
        
        product_data = {
            'name': name,
            'description': description,
            'price': price,
            'stock': stock,
            'brand': brand
        }
        
        if Confirm.ask("\nSalvar produto?"):
            product_id = self.product_model.create(product_data)
            console.print(f"[green]✓ Produto '{name}' criado com ID {product_id}[/green]")
        
        self.wait_for_enter()
    
    def edit_product(self):
        """Interface para editar um produto existente"""
        self.show_header("Editar Produto")
        
        product = self.select_product("Selecione o produto a editar")
        if not product:
            return
        
        console.print(f"\n[bold]Editando:[/bold] [cyan]{product[1]}[/cyan]")
        console.print(f"[bold]ID:[/bold] {product[0]}")
        
        name = Prompt.ask("Nome", default=product[1])
        description = Prompt.ask("Descrição", default=product[2] or "")
        price = FloatPrompt.ask("Preço", default=product[3])
        brand = Prompt.ask("Marca", default=product[5] or "")
        
        update_data = {
            'name': name,
            'description': description,
            'price': price,
            'brand': brand
        }
        
        if Confirm.ask("\nAtualizar produto?"):
            self.product_model.update(product[0], update_data)
            console.print("[green]✓ Produto atualizado com sucesso[/green]")
        
        self.wait_for_enter()
    
    def delete_product(self):
        """Interface para excluir um produto"""
        self.show_header("Excluir Produto")
        
        product = self.select_product("Selecione o produto a excluir")
        if not product:
            return
        
        console.print(f"\n[bold]Produto selecionado:[/bold]")
        console.print(f"ID: [cyan]{product[0]}[/cyan]")
        console.print(f"Nome: [white]{product[1]}[/white]")
        console.print(f"Marca: [blue]{product[5] or '—'}[/blue]")
        console.print(f"Estoque atual: [red]{product[4]}[/red] unidades")
        
        if Confirm.ask("\n[red]Tem certeza que deseja excluir este produto?[/red]"):
            if self.product_model.delete(product[0]):
                console.print("[green]✓ Produto excluído com sucesso[/green]")
            else:
                console.print("[red]❌ Erro ao excluir produto[/red]")
        
        self.wait_for_enter()
    
    def show_product_details(self):
        """Mostra detalhes completos de um produto específico"""
        self.show_header("Detalhes do Produto")
        
        product = self.select_product("Selecione o produto para ver detalhes")
        if not product:
            return
        
        content = f"[bold]ID:[/bold] {product[0]}\n"
        content += f"[bold]Nome:[/bold] {product[1]}\n"
        content += f"[bold]Descrição:[/bold] {product[2] or 'N/A'}\n"
        content += f"[bold]Preço:[/bold] R$ {product[3]:.2f}\n"
        content += f"[bold]Estoque:[/bold] {product[4]}\n"
        content += f"[bold]Marca:[/bold] {product[5] or 'N/A'}\n"
        content += f"[bold]Criado em:[/bold] {product[6]}\n"
        content += f"[bold]Atualizado em:[/bold] {product[7]}"
        
        console.print(Panel.fit(content, title="Detalhes do Produto", border_style="cyan"))
        self.wait_for_enter()
    
    def stock_menu(self):
        """Menu de controle de estoque"""
        while True:
            self.show_header("Controle de Estoque")
            
            console.print("[bold]Opções:[/bold]")
            console.print("1. Ajustar Estoque")
            console.print("2. Produtos com Estoque Baixo")
            console.print("3. Produtos Sem Estoque")
            console.print("0. ↩️  Voltar ao Menu Principal")
            
            choice = Prompt.ask("\nSelecione uma opção", choices=["0", "1", "2", "3"])
            
            if choice == "1":
                self.adjust_stock()
            elif choice == "2":
                self.low_stock_products()
            elif choice == "3":
                self.out_of_stock_products()
            elif choice == "0":
                break
    
    def adjust_stock(self):
        """Interface para ajustar o estoque de um produto"""
        self.show_header("Ajustar Estoque")
        
        product = self.select_product("Selecione o produto para ajustar estoque")
        if not product:
            return
        
        console.print(f"\n[bold]Produto selecionado:[/bold]")
        console.print(f"Nome: [cyan]{product[1]}[/cyan]")
        console.print(f"Estoque atual: [yellow]{product[4]}[/yellow] unidades")
        
        new_stock = IntPrompt.ask("\nNovo estoque")
        reason = Prompt.ask("Motivo do ajuste", default="Ajuste manual")
        
        if Confirm.ask(f"\nAlterar estoque de {product[4]} para {new_stock}?"):
            if self.product_model.update_stock(product[0], new_stock, 'manual', reason):
                console.print("[green]✓ Estoque atualizado com sucesso[/green]")
        
        self.wait_for_enter()
    
    def low_stock_products(self):
        """Lista produtos com estoque baixo (≤ 10 unidades)"""
        self.show_header("Produtos com Estoque Baixo (≤ 10 unidades)")
        
        low_stock_products = self.product_model.get_low_stock(10)
        
        if not low_stock_products:
            console.print("[green]✓ Nenhum produto com estoque baixo[/green]")
        else:
            table = Table(box=box.ROUNDED)
            table.add_column("ID", style="cyan")
            table.add_column("Nome", style="white")
            table.add_column("Marca", style="blue")
            table.add_column("Estoque", style="red")
            table.add_column("Preço", style="green")
            
            for product in low_stock_products:
                table.add_row(
                    str(product[0]),
                    product[1][:25] + "..." if len(product[1]) > 25 else product[1],
                    product[5] or "—",
                    f"[red]{product[4]}[/red]",
                    f"R$ {product[3]:.2f}"
                )
            
            console.print(table)
        
        self.wait_for_enter()
    
    def out_of_stock_products(self):
        """Lista produtos sem estoque"""
        self.show_header("Produtos Sem Estoque")
        
        out_of_stock_products = self.product_model.get_out_of_stock()
        
        if not out_of_stock_products:
            console.print("[green]✓ Nenhum produto sem estoque[/green]")
        else:
            table = Table(box=box.ROUNDED)
            table.add_column("ID", style="cyan")
            table.add_column("Nome", style="white")
            table.add_column("Marca", style="blue")
            table.add_column("Preço", style="green")
            table.add_column("Última atualização", style="dim")
            
            for product in out_of_stock_products:
                table.add_row(
                    str(product[0]),
                    product[1][:25] + "..." if len(product[1]) > 25 else product[1],
                    product[5] or "—",
                    f"R$ {product[3]:.2f}",
                    str(product[7])[:16]
                )
            
            console.print(table)
        
        self.wait_for_enter()
    
    def search_products(self):
        """Interface de busca de produtos por termo"""
        self.show_header("Buscar Produtos")
        
        search_term = Prompt.ask("Digite o termo de busca (nome, marca ou ID)")
        
        if not search_term:
            console.print("[yellow]Termo de busca vazio.[/yellow]")
            self.wait_for_enter()
            return
        
        results = self.product_model.search(search_term)
        
        if not results:
            console.print(f"[yellow]Nenhum produto encontrado para '{search_term}'[/yellow]")
        else:
            console.print(f"[green]✓ Encontrados {len(results)} produtos[/green]")
            
            table = Table(box=box.ROUNDED)
            table.add_column("ID", style="cyan")
            table.add_column("Nome", style="white")
            table.add_column("Marca", style="blue")
            table.add_column("Preço", style="green")
            table.add_column("Estoque", style="red")
            table.add_column("Descrição", style="dim")
            
            for product in results:
                stock_style = "red" if product[4] == 0 else "yellow" if product[4] <= 10 else "green"
                description = product[2] or "—"
                table.add_row(
                    str(product[0]),
                    product[1][:25] + "..." if len(product[1]) > 25 else product[1],
                    product[5] or "—",
                    f"R$ {product[3]:.2f}",
                    f"[{stock_style}]{product[4]}[/{stock_style}]",
                    description[:25] + "..." if len(description) > 25 else description
                )
            
            console.print(table)
        
        self.wait_for_enter()
    
    def history_menu(self):
        """Menu de histórico de movimentações de estoque"""
        while True:
            self.show_header("Histórico de Estoque")
            
            console.print("[bold]Opções:[/bold]")
            console.print("1. Histórico por Produto")
            console.print("2. Histórico Recente")
            console.print("0. ↩️  Voltar ao Menu Principal")
            
            choice = Prompt.ask("\nSelecione uma opção", choices=["0", "1", "2"])
            
            if choice == "1":
                self.product_history()
            elif choice == "2":
                self.recent_history()
            elif choice == "0":
                break
    
    def product_history(self):
        """Mostra histórico de movimentações de um produto específico"""
        self.show_header("Histórico por Produto")
        
        product = self.select_product("Selecione o produto para ver histórico")
        if not product:
            return
        
        console.print(f"\n[bold]Produto:[/bold] [cyan]{product[1]}[/cyan]")
        
        history = self.history_model.get_by_product(product[0])
        
        if not history:
            console.print("[yellow]Nenhum registro de histórico para este produto.[/yellow]")
        else:
            table = Table(box=box.ROUNDED)
            table.add_column("Data", style="cyan")
            table.add_column("Estoque Antigo", style="yellow")
            table.add_column("Estoque Novo", style="green")
            table.add_column("Variação", style="red")
            table.add_column("Tipo", style="blue")
            table.add_column("Motivo", style="white")
            
            for record in history:
                variation = record[3] - record[2]
                variation_str = f"+{variation}" if variation > 0 else str(variation)
                variation_style = "green" if variation > 0 else "red" if variation < 0 else "yellow"
                
                table.add_row(
                    str(record[6])[:16],
                    str(record[2]),
                    str(record[3]),
                    f"[{variation_style}]{variation_str}[/{variation_style}]",
                    record[4],
                    record[5] or "—"
                )
            
            console.print(table)
        
        self.wait_for_enter()
    
    def recent_history(self):
        """Mostra histórico recente de todas as movimentações"""
        self.show_header("Histórico Recente")
        
        history = self.history_model.get_recent(20)
        
        if not history:
            console.print("[yellow]Nenhum registro de histórico.[/yellow]")
        else:
            table = Table(box=box.ROUNDED)
            table.add_column("Data", style="cyan")
            table.add_column("Produto", style="white")
            table.add_column("Estoque Antigo", style="yellow")
            table.add_column("Estoque Novo", style="green")
            table.add_column("Variação", style="red")
            table.add_column("Tipo", style="blue")
            
            for record in history:
                variation = record[3] - record[2]
                variation_str = f"+{variation}" if variation > 0 else str(variation)
                variation_style = "green" if variation > 0 else "red" if variation < 0 else "yellow"
                
                table.add_row(
                    str(record[6])[:16],
                    record[7][:20] + "..." if len(record[7]) > 20 else record[7],
                    str(record[2]),
                    str(record[3]),
                    f"[{variation_style}]{variation_str}[/{variation_style}]",
                    record[4]
                )
            
            console.print(table)
        
        self.wait_for_enter()