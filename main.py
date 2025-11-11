
import flet as ft
from model import AppModel
from view import AppView

class AppController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.model = AppModel()
        self.view = AppView(self)
        

        self.is_logged_in = False
        self.current_user_role = None 
        self.current_section = None
        self.search_query = ""
        self.active_filter = "all"
        self.active_earnings_tab = "week" 

    def start(self):
        """Inicia y renderiza la vista inicial de la aplicación."""
        self.page.on_resize = self.handle_resize
        self.render()

    def handle_resize(self, e):
        """Maneja el redimensionamiento de la ventana y vuelve a renderizar."""
        self.render()

    def handle_login(self, username, password):
        """Manejador para el evento de inicio de sesión."""
        
        self.view.clear_login_error() 
        user_role = self.model.authenticate(username, password)
        
        if user_role:
            self.is_logged_in = True
            self.current_user_role = user_role
            self.render()
        else:
            print(f"Intento de login fallido para: {username}")
            self.view.show_login_error("Usuario o contraseña incorrectos.")

    def handle_logout(self, e):
        """Manejador para el evento de cierre de sesión."""
        self.is_logged_in = False
        self.current_user_role = None 
        self.current_section = None
        self.render()

    def handle_select_section(self, section_name):
        """Manejador para la selección de una sección del dashboard."""
        self.current_section = section_name
        self.active_filter = "all"
        self.search_query = ""
        self.active_earnings_tab = "week"
        self.render()

    def handle_back(self, e):
        """Manejador para el botón de 'volver'."""
        self.current_section = None
        self.render()

    def handle_search(self, section, query):
        """Manejador para los cambios en las barras de búsqueda."""
        self.search_query = query.lower()
        self.update_dynamic_list(section)

    # --- ¡ARREGLO AQUÍ! ---
    def handle_filter_change(self, section, filter_type):
        """
        Manejador para los clics en los botones de filtro.
        """
        self.active_filter = filter_type
        self.render()


    def handle_earnings_tab_change(self, tab_name):
        """
        Manejador para cambiar entre 'semana' y 'mes' en ganancias.
        """
        self.active_earnings_tab = tab_name
        self.render()

    def update_dynamic_list(self, section):
        """
        Pide datos filtrados al modelo y le dice a la vista que
        actualice solo la lista de elementos.
        (Esta función se usa ahora SOLO para la búsqueda)
        """
        if section == 'cashiers':
            data = self.model.get_cashiers(self.active_filter, self.search_query)
            self.view.update_cashier_list(data)
        elif section == 'maintenance':
            data = self.model.get_maintenance_tasks(self.search_query)
            self.view.update_maintenance_list(data)
        elif section == 'inventory':
            data = self.model.get_inventory(self.active_filter, self.search_query)
            self.view.update_inventory_list(data)
        elif section == 'sales':
            data = self.model.get_sales(self.active_filter, self.search_query)
            self.view.update_sales_list(data)

    def render(self):
        """
        Lógica principal de renderizado. Limpia la página y construye la
        vista adecuada basándose en el estado actual de la aplicación.
        """
        self.page.controls.clear()
        view_to_render = None

        if not self.is_logged_in:
            view_to_render = self.view.build_login_screen()
        else:
            section = self.current_section
            if section is None:
                stats = self.model.get_dashboard_stats()
                view_to_render = self.view.build_dashboard(stats)
            
            elif section == "cashiers":
                stats = self.model.get_cashier_stats()
                # Al llamar a render(), los datos se obtienen aquí
                data = self.model.get_cashiers(self.active_filter, self.search_query)
                view_to_render = self.view.build_cashier_section(data, stats, self.active_filter)
            
            elif section == "maintenance":
                if self.current_user_role == 'admin':
                    stats = self.model.get_maintenance_stats()
                    data = self.model.get_maintenance_tasks(self.search_query)
                    view_to_render = self.view.build_maintenance_section(data, stats)
                else:
                    self.current_section = None 
                    stats = self.model.get_dashboard_stats()
                    view_to_render = self.view.build_dashboard(stats)
            
            elif section == "inventory":
                stats = self.model.get_inventory_stats()
                data = self.model.get_inventory(self.active_filter, self.search_query)
                view_to_render = self.view.build_inventory_section(data, stats, self.active_filter)
            
            elif section == "sales":
                stats = self.model.get_sales_stats()
                data = self.model.get_sales(self.active_filter, self.search_query)
                view_to_render = self.view.build_sales_section(data, stats, self.active_filter)

            elif section == "earnings":
                if self.current_user_role == 'admin':
                    data = self.model.get_earnings_data()
                    view_to_render = self.view.build_earnings_section(data, self.active_earnings_tab)
                else:
                    self.current_section = None 
                    stats = self.model.get_dashboard_stats()
                    view_to_render = self.view.build_dashboard(stats)

        if view_to_render:
            self.page.add(view_to_render)
        self.page.update()

def main(page: ft.Page):
    """Función de entrada de la aplicación Flet."""
    page.title = "SuperMarket Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000" 
    page.padding = 0
      
    page.window_width = 393
    page.window_height = 852 
    page.window_resizable = False
    page.update() 
    
    app = AppController(page)
    app.start()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)