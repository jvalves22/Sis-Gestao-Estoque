#!/usr/bin/env python3
from menu import MenuManager

def main():
    """
    Função principal que inicia a aplicação
    Trata exceções e garante uma saída graciosa
    """
    try:
        # Cria e inicia o gerenciador de menus
        app = MenuManager()
        app.main_menu()
        print("\nObrigado por usar o Sistema de Gestão de Estoque!")
    except KeyboardInterrupt:
        # Trata interrupção por Ctrl+C
        print("\nPrograma interrompido pelo usuário")
    except Exception as e:
        # Trata erros inesperados
        print(f"\nErro: {e}")

if __name__ == "__main__":
    # Ponto de entrada da aplicação
    main()