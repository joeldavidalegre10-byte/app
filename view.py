# view.py
import flet as ft
import random
import math

# ============================================================================
# COMPONENTES REUTILIZABLES (Nuevo Estilo Profesional Oscuro)
# ============================================================================

# --- Colores del Tema (Profesional Oscuro) ---
BG_COLOR = ft.Colors.BLACK                 # Fondo negro
CONTAINER_COLOR = ft.Colors.GREY_900       # Contenedores gris muy oscuro
BORDER_COLOR = ft.Colors.GREY_800          # Borde sutil
BUTTON_COLOR = ft.Colors.BLUE_700          # Acento de color azul profesional
BUTTON_BORDER_COLOR = ft.Colors.BLUE_600   # Borde de botón
TEXT_FIELD_BG_COLOR = ft.Colors.GREY_800   # Fondo de campos de texto
TEXT_FIELD_BORDER_COLOR = ft.Colors.GREY_700 # Borde de campos de texto

def create_solid_background():
    """Crea un fondo sólido de color negro."""
    return ft.Container(
        expand=True,
        bgcolor=BG_COLOR,
    )

def create_styled_container(content, padding=16, border_radius=12, on_click=None, expand=False, gradient=None, bgcolor=CONTAINER_COLOR, border_color=BORDER_COLOR):
    """Crea un contenedor con el nuevo estilo sólido oscuro."""
    return ft.Container(
        content=content,
        padding=padding,
        border_radius=border_radius,
        bgcolor=bgcolor,
        border=ft.border.all(1.5, border_color),
        gradient=gradient,
        on_click=on_click,
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        ink=True,
        expand=expand
    )

def create_gradient_container(content, gradient_colors, padding=16, border_radius=12, on_click=None, border_color=None, expand=False):
    """Crea un contenedor con un gradiente sólido (usado para tarjetas de estadísticas)."""
    solid_gradient = ft.LinearGradient(
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
        colors=[
            gradient_colors[0],
            gradient_colors[1]
        ]
    )
    use_border_color = border_color if border_color else gradient_colors[0]
    
    return create_styled_container(
        content,
        padding=padding,
        border_radius=border_radius,
        on_click=on_click,
        expand=expand,
        gradient=solid_gradient,
        bgcolor=None,
        border_color=use_border_color
    )

def create_action_button(text, icon, on_click, gradient_colors=None, width=None, disabled=False):
    """Botón de acción con estilo sólido."""
    content = ft.Row(
        [ft.Icon(icon, color=ft.Colors.WHITE, size=18), ft.Text(text, color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.W_500)],
        alignment=ft.MainAxisAlignment.CENTER, spacing=8, tight=True,
    )

    solid_gradient = None
    button_bgcolor = BUTTON_COLOR
    button_border = ft.border.all(1.5, BUTTON_BORDER_COLOR)

    if gradient_colors:
        solid_gradient = ft.LinearGradient(
            colors=[gradient_colors[0], gradient_colors[1]]
        )
        button_bgcolor = None
        button_border = ft.border.all(1.5, gradient_colors[0])

    return ft.Container(
        content=content,
        width=width,
        padding=ft.padding.symmetric(horizontal=20, vertical=14),
        border_radius=10,
        bgcolor=button_bgcolor,
        border=button_border,
        gradient=solid_gradient,
        on_click=on_click if not disabled else None,
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        ink=True,
        opacity=1.0 if not disabled else 0.5
    )


def create_stats_card(title, value, subtitle, icon, gradient_color, expand=True):
    icon_bg_color = ft.Colors.with_opacity(0.1, gradient_color)
    card_bgcolor = ft.Colors.with_opacity(0.15, gradient_color)
    card_border_color = ft.Colors.with_opacity(0.3, gradient_color)

    return create_styled_container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Icon(icon, color=gradient_color, size=20),
                    width=40, height=40,
                    border_radius=10, 
                    bgcolor=icon_bg_color,
                ),
                ft.Text(str(value), size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text(title, size=11, color=ft.Colors.WHITE70),
                ft.Text(subtitle, size=10, color=ft.Colors.WHITE54),
            ],
            spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True,
        ),
        padding=12, border_radius=14,
        expand=expand,
        bgcolor=card_bgcolor,
        border_color=card_border_color,
    )

def create_header(title, subtitle, on_back, page_width, extra_button=None):
    header_content = [ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE70, on_click=on_back, tooltip="Volver", icon_size=22)]

    text_col = ft.Column(
        [
            ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text(subtitle, size=12, color=ft.Colors.WHITE70),
        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.START, expand=True,
    )

    if extra_button:
        header_content.append(ft.Row([text_col, extra_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True, spacing=8))
    else:
        header_content.append(text_col)

    return create_styled_container(
        content=ft.Row(header_content, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        padding=ft.padding.only(left=8, right=16, top=40, bottom=12),
        border_radius=0,
        border_color=BORDER_COLOR,
        bgcolor=CONTAINER_COLOR
    )

# ============================================================================
# CLASE DE LA VISTA
# ============================================================================

class AppView:
    def __init__(self, controller):
        self.controller = controller
        self.page = controller.page

        self.cashier_list_container = ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        self.maintenance_list_container = ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        self.inventory_list_container = ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        self.sales_list_container = ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        
        # --- Control para el error de login ---
        self.login_error_text = ft.Text(
            value="", 
            color=ft.Colors.RED_400, # 'C' Mayúscula
            size=13, 
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER,
            visible=False # Empezará oculto
        )
        
        self.background = create_solid_background() 

    def build_login_screen(self):
        # Campos de texto
        username_field = ft.TextField(label="Usuario", prefix_icon=ft.Icons.PERSON_OUTLINE, height=50, text_size=14, border_radius=10, border_color=TEXT_FIELD_BORDER_COLOR, focused_border_color=ft.Colors.BLUE_500, bgcolor=TEXT_FIELD_BG_COLOR, color=ft.Colors.WHITE)
        password_field = ft.TextField(label="Contraseña", prefix_icon=ft.Icons.LOCK_OUTLINE, password=True, can_reveal_password=True, height=50, text_size=14, border_radius=10, border_color=TEXT_FIELD_BORDER_COLOR, focused_border_color=ft.Colors.BLUE_500, bgcolor=TEXT_FIELD_BG_COLOR, color=ft.Colors.WHITE, on_submit=lambda e: self.controller.handle_login(username_field.value, password_field.value))
        
        main_icon_stack = [
            create_gradient_container(ft.Icon(ft.Icons.SHOPPING_CART, size=40, color=ft.Colors.WHITE), [ft.Colors.BLUE_500, ft.Colors.PURPLE_600], padding=20, border_radius=25), 
            ft.Container(ft.Icon(ft.Icons.AUTO_AWESOME, size=12, color=ft.Colors.WHITE), width=24, height=24, border_radius=12, gradient=ft.LinearGradient(colors=[ft.Colors.YELLOW_400, ft.Colors.ORANGE_500]), right=0, top=0, alignment=ft.alignment.center)
        ]
        main_icon = ft.Stack(main_icon_stack, width=100, height=100)
        
        login_button = create_action_button(
            "Iniciar Sesión",
            ft.Icons.ARROW_FORWARD,
            lambda e: self.controller.handle_login(username_field.value, password_field.value),
            gradient_colors=[ft.Colors.BLUE_500, ft.Colors.PURPLE_600],
            width=float("inf")
        )

        card_content = create_styled_container(
            content=ft.Column([
                ft.Column([main_icon, ft.Container(height=12), ft.Text("SuperMarket Pro", size=22, weight=ft.FontWeight.BOLD), ft.Text("Sistema de Gestión", size=13, color=ft.Colors.WHITE70)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                ft.Container(height=24),
                ft.Column([
                    username_field,
                    password_field,
                    
                    # --- Espacio para el mensaje de error ---
                    ft.Container(
                        content=self.login_error_text,
                        height=20, # Le damos un espacio fijo
                        alignment=ft.alignment.center,
                        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
                    ),
                    
                    login_button,
                    ft.Container(height=8),
                    
                    # --- Texto de ayuda actualizado ---
                    ft.Text("Bienvenido", size=11, color=ft.Colors.WHITE54, text_align=ft.TextAlign.CENTER)
                ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            padding=32, border_radius=20
        )

        return ft.Stack(
            controls=[
                self.background,
                ft.Container(
                    content=card_content,
                    alignment=ft.alignment.center,
                    padding=16,
                    expand=True
                )
            ],
            expand=True
        )

    # --- NUEVAS FUNCIONES DE LA VISTA ---
    def show_login_error(self, message):
        """Muestra un mensaje de error en la pantalla de login."""
        self.login_error_text.value = message
        self.login_error_text.visible = True
        if self.page.controls: # Asegurarse que la página ya esté cargada
            self.login_error_text.update() 

    def clear_login_error(self):
        """Oculta el mensaje de error de login."""
        if self.login_error_text.visible:
            self.login_error_text.value = ""
            self.login_error_text.visible = False
            if self.page.controls:
                self.login_error_text.update()
    # ---------------------------------------------

    def build_dashboard(self, stats):
        person_icon_glass = create_styled_container(
            content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.DEEP_PURPLE_200, size=22),
            padding=12,
            border_radius=50
        )

        # --- Muestra el rol del usuario ---
        user_role_text = "Admin" if self.controller.current_user_role == 'admin' else "Usuario"
        
        dashboard_header = create_styled_container(
            content=ft.Row(
                controls=[
                    person_icon_glass,
                    ft.Column([
                        ft.Text("Panel de Control", size=18, weight=ft.FontWeight.BOLD), 
                        ft.Text(f"Bienvenido de vuelta, {user_role_text}", size=12, color=ft.Colors.WHITE70)
                    ], spacing=2, expand=True),
                    ft.IconButton(icon=ft.Icons.LOGOUT_OUTLINED, icon_color=ft.Colors.WHITE70, tooltip="Cerrar Sesión", on_click=self.controller.handle_logout),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_radius=12
        )

        sistema_activo_banner = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.AUTO_GRAPH, color=ft.Colors.GREEN_400, size=16), ft.Text("Sistema activo", size=12, color=ft.Colors.GREEN_400)], spacing=6),
            padding=ft.padding.symmetric(horizontal=10, vertical=6), 
            border_radius=50, 
            border=ft.border.all(1, ft.Colors.with_opacity(0.5, ft.Colors.GREEN_400)),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREEN_400)
        )

        # --- Lógica de Roles para la Alerta ---
        maintenance_alert = ft.Container() # Empezar vacío
        if stats.get('maintenance_count', 0) > 0 and self.controller.current_user_role == 'admin':
            maintenance_icon_glass = create_styled_container(
                content=ft.Icon(ft.Icons.BUILD_OUTLINED, color=ft.Colors.WHITE, size=20),
                padding=12,
                border_radius=10,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ORANGE_500),
                border_color=ft.Colors.with_opacity(0.3, ft.Colors.ORANGE_500)
            )
            maintenance_alert = create_styled_container(
                content=ft.Row([
                    maintenance_icon_glass,
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.ORANGE_300, size=14), 
                            ft.Text("Cajas en Mantenimiento", size=14, color=ft.Colors.ORANGE_300, weight=ft.FontWeight.BOLD)
                        ], spacing=6),
                        ft.Text(f"{stats['maintenance_count']} cajas requieren atención. Haz clic para ver.", size=12, color=ft.Colors.WHITE, max_lines=2),
                    ], spacing=2, expand=True),
                    ft.Icon(ft.Icons.ARROW_FORWARD_IOS_ROUNDED, color=ft.Colors.WHITE30, size=16),
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
                padding=16, border_radius=12, on_click=lambda _: self.controller.handle_select_section("maintenance"),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ORANGE_500),
                border_color=ft.Colors.with_opacity(0.3, ft.Colors.ORANGE_500)
            )

        # --- Lógica de Roles para el Menú ---
        menu_items_all = [
            {"id": "cashiers", "title": "Cajas", "desc": "Estado de las cajas", "icon": ft.Icons.POINT_OF_SALE_OUTLINED, "stat": f"{stats.get('total_cashiers', 0)} activas", "color": ft.Colors.LIGHT_BLUE_400},
            {"id": "sales", "title": "Ventas", "desc": "Listado de ventas", "icon": ft.Icons.RECEIPT_LONG_OUTLINED, "stat": f"{stats.get('transactions_today', 0)} hoy", "color": ft.Colors.PURPLE_300},
            {"id": "inventory", "title": "Inventario", "desc": "Productos y stock", "icon": ft.Icons.INVENTORY_2_OUTLINED, "stat": f"{stats.get('low_stock_count', 0)} bajos", "color": ft.Colors.ORANGE_300},
            {"id": "earnings", "title": "Ganancias", "desc": "Ingresos del periodo", "icon": ft.Icons.TRENDING_UP_OUTLINED, "stat": f"+{stats.get('month_growth', 0)}% este mes", "color": ft.Colors.GREEN_400},
            {"id": "maintenance", "title": "Mantenimiento", "desc": "Tareas pendientes", "icon": ft.Icons.BUILD_OUTLINED, "stat": f"{stats.get('maintenance_count', 0)} tareas", "color": ft.Colors.RED_300}
        ]
        
        menu_items_visible = []
        if self.controller.current_user_role == 'admin':
            menu_items_visible = menu_items_all # Admin ve todo
        else:
            # User ve un subconjunto
            menu_items_visible = [item for item in menu_items_all if item['id'] in ['cashiers', 'sales', 'inventory']]

        menu_cards = []
        for item in menu_items_visible: # <-- Usar la lista filtrada
            menu_icon_glass = create_styled_container(
                content=ft.Icon(item['icon'], color=item['color'], size=24),
                padding=12,
                border_radius=50,
                bgcolor=ft.Colors.with_opacity(0.1, item['color']),
                border_color=ft.Colors.with_opacity(0.2, item['color'])
            )
            card = create_styled_container(
                content=ft.Stack([
                    ft.Column([
                        menu_icon_glass,
                        ft.Container(height=12),
                        ft.Text(item['title'], size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(item['desc'], size=12, color=ft.Colors.WHITE70),
                        ft.Container(height=10),
                        ft.Container(
                            content=ft.Text(item['stat'], size=11, weight=ft.FontWeight.W_500, color=item['color']),
                            padding=ft.padding.symmetric(horizontal=10, vertical=5), border_radius=6, 
                            bgcolor=ft.Colors.with_opacity(0.2, item['color'])
                        )
                    ], spacing=2),
                    ft.Container(
                        content=ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color=ft.Colors.WHITE30, size=18),
                        top=15,
                        right=15
                    )
                ]),
                padding=20, border_radius=16, on_click=lambda _, id=item['id']: self.controller.handle_select_section(id)
            )
            menu_cards.append(card)
        
        return ft.Stack(
            controls=[
                self.background,
                ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Column([
                                dashboard_header,
                                ft.Container(height=10),
                                sistema_activo_banner,
                            ]),
                            padding=ft.padding.only(top=40, left=20, right=20, bottom=10)
                        ),
                        
                        ft.Container(
                            content=ft.Column(
                                [
                                    maintenance_alert, # Esto estará vacío si no es admin
                                    ft.Container(height=10),
                                    ft.Column([
                                        ft.Text("¿Qué quieres gestionar hoy?", size=20, weight=ft.FontWeight.BOLD),
                                        ft.Text("Selecciona una sección para comenzar", size=13, color=ft.Colors.WHITE70),
                                    ], spacing=2),
                                    ft.Column(controls=menu_cards, spacing=12) # <-- Usa las tarjetas filtradas
                                ],
                                scroll=ft.ScrollMode.AUTO,
                                expand=True # <-- ESTE ES EL SCROLL DEL DASHBOARD
                            ),
                            padding=ft.padding.symmetric(horizontal=20),
                            expand=True
                        ),
                        
                    ],
                    spacing=0,
                    expand=True
                )
            ],
            expand=True
        )

    def _create_icon_filter_button(self, icon, count, filter_type, section, active_filter):
        is_active = active_filter == filter_type
        
        bgcolor = BUTTON_COLOR if is_active else CONTAINER_COLOR
        border = ft.border.all(1.5, BUTTON_BORDER_COLOR) if is_active else ft.border.all(1.5, BORDER_COLOR)

        return ft.Container(
            content=ft.Row([ft.Icon(icon, size=18, color=ft.Colors.WHITE if is_active else ft.Colors.WHITE70), ft.Text(str(count), size=12, color=ft.Colors.WHITE if is_active else ft.Colors.WHITE70, weight=ft.FontWeight.BOLD)], spacing=6, tight=True),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=10,
            bgcolor=bgcolor,
            border=border,
            on_click=lambda e, f_type=filter_type: self.controller.handle_filter_change(section, f_type),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            ink=True,
        )

    def build_cashier_section(self, cashiers, stats, active_filter):
        header = create_header("Estado de Cajas", f"{stats.get('open', 0)} de {stats.get('total_cashiers', 0)} abiertas", self.controller.handle_back, self.page.width)
        stats_row = ft.Row([
            create_stats_card("Abiertas", stats.get('open', 0), "Activas", ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN_500),
            create_stats_card("Cerradas", stats.get('closed', 0), "Inactivas", ft.Icons.CANCEL, ft.Colors.GREY_500),
            create_stats_card("Mantenim.", stats.get('maintenance', 0), "En Taller", ft.Icons.BUILD, ft.Colors.ORANGE_500),
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        
        filters_container = ft.Row([
            self._create_icon_filter_button(ft.Icons.SELECT_ALL, stats.get('total_cashiers', 0), "all", "cashiers", active_filter),
            self._create_icon_filter_button(ft.Icons.CHECK_CIRCLE_OUTLINE, stats.get('open', 0), "open", "cashiers", active_filter),
            self._create_icon_filter_button(ft.Icons.CANCEL_OUTLINED, stats.get('closed', 0), "closed", "cashiers", active_filter),
            self._create_icon_filter_button(ft.Icons.BUILD_OUTLINED, stats.get('maintenance', 0), "maintenance", "cashiers", active_filter),
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)

        search_bar = ft.TextField(label="Buscar por nombre o operador...", prefix_icon=ft.Icons.SEARCH, border_radius=8, height=48, text_size=12, border_color=TEXT_FIELD_BORDER_COLOR, focused_border_color=ft.Colors.BLUE_500, bgcolor=TEXT_FIELD_BG_COLOR, color=ft.Colors.WHITE, on_change=lambda e: self.controller.handle_search('cashiers', e.control.value), value=self.controller.search_query)
        self.update_cashier_list(cashiers)
        
        return ft.Stack([
            self.background,
            ft.Column([
                header,
                ft.Container(
                    content=ft.Column([
                        stats_row, filters_container, search_bar,
                        ft.Container(content=self.cashier_list_container, expand=True) 
                    ], 
                    spacing=16, 
                    scroll=ft.ScrollMode.AUTO, # <-- ESTE ES EL SCROLL DE LA SECCIÓN
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    expand=True # <-- Y ESTE EXPAND ES CLAVE
                    ),
                    padding=16,
                    expand=True
                )
            ], expand=True)
        ], expand=True)

    def update_cashier_list(self, cashiers):
        self.cashier_list_container.controls.clear()
        if not cashiers:
            self.cashier_list_container.controls.append(create_styled_container(content=ft.Text("No se encontraron cajas", text_align=ft.TextAlign.CENTER), padding=32))
        else:
            for c in cashiers:
                s_def = {'open': {'c': ft.Colors.GREEN_500, 't': 'Abierta'}, 'closed': {'c': ft.Colors.GREY_500, 't': 'Cerrada'}, 'maintenance': {'c': ft.Colors.ORANGE_500, 't': 'Mantenim.'}}
                s = s_def.get(c['status'], s_def['closed'])
                self.cashier_list_container.controls.append(create_styled_container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CIRCLE, color=s['c'], size=10),
                        ft.Column([ft.Text(c['name'], size=14, weight=ft.FontWeight.W_500), ft.Text(c['operator'] or "Sin operador", size=11, color=ft.Colors.WHITE70)], spacing=2, expand=True),
                        ft.Column([ft.Container(ft.Text(s['t'], size=10, color=s['c']), padding=ft.padding.symmetric(horizontal=8, vertical=4), border_radius=6, 
                                                bgcolor=ft.Colors.with_opacity(0.2, s['c'])), 
                                  ft.Text(f"{c['sales']} ventas", size=11, color=ft.Colors.WHITE54) if c['status'] == 'open' else ft.Container()], 
                                 spacing=4, horizontal_alignment=ft.CrossAxisAlignment.END),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=12), padding=12,
                ))
        if self.page.controls: self.page.update()

    def build_inventory_section(self, products, stats, active_filter):
        header = create_header("Inventario", f"{stats.get('total_products', 0)} productos en sistema", self.controller.handle_back, self.page.width)
        stats_row = ft.Row([
                create_stats_card("Total Prod.", stats.get('total_products', 0), "Tipos", ft.Icons.INVENTORY_2, ft.Colors.BLUE_400),
                create_stats_card("Stock Bajo", stats.get('low_stock_count', 0), "Reordenar", ft.Icons.WARNING, ft.Colors.ORANGE_400),
                create_stats_card("Valor Total", f"${stats.get('total_value', 0):,.0f}", "Estimado", ft.Icons.ATTACH_MONEY, ft.Colors.GREEN_400),
            ], spacing=10)
        filters_container = ft.Row([
            self._create_icon_filter_button(ft.Icons.INVENTORY_2_OUTLINED, stats.get('total_products', 0), "all", "inventory", active_filter),
            self._create_icon_filter_button(ft.Icons.ARROW_DOWNWARD_OUTLINED, stats.get('low_stock_count', 0), "low", "inventory", active_filter),
            self._create_icon_filter_button(ft.Icons.ARROW_UPWARD_OUTLINED, stats.get('high_stock_count', 0), "high", "inventory", active_filter),
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
        search_bar = ft.TextField(label="Buscar por nombre, SKU...", prefix_icon=ft.Icons.SEARCH, border_radius=8, height=48, text_size=12, on_change=lambda e: self.controller.handle_search('inventory', e.control.value), value=self.controller.search_query, border_color=TEXT_FIELD_BORDER_COLOR, focused_border_color=ft.Colors.BLUE_500, bgcolor=TEXT_FIELD_BG_COLOR, color=ft.Colors.WHITE)
        self.update_inventory_list(products)
        return ft.Stack([
            self.background,
            ft.Column([header, ft.Container(content=ft.Column([stats_row, filters_container, search_bar, 
                
                ft.Container(self.inventory_list_container, expand=True)
                ], 
                spacing=16, 
                scroll=ft.ScrollMode.AUTO, # <-- ESTE ES EL SCROLL DE LA SECCIÓN
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                expand=True # <-- Y ESTE EXPAND ES CLAVE
                ), padding=16, expand=True)], expand=True)
        ], expand=True)

    def update_inventory_list(self, products):
        self.inventory_list_container.controls.clear()
        if not products:
            self.inventory_list_container.controls.append(create_styled_container(content=ft.Text("No se encontraron productos", text_align=ft.TextAlign.CENTER), padding=32))
        else:
            for p in products:
                is_low = p['stock'] <= p['min_stock']
                color = ft.Colors.ORANGE_400 if is_low else ft.Colors.WHITE
                card = create_styled_container(
                    content=ft.Column([
                        ft.Row([ft.Column([ft.Text(p['name'], size=14, weight=ft.FontWeight.W_500), ft.Text(f"SKU: {p['sku']}", size=11, color=ft.Colors.WHITE54)], spacing=2, expand=True), ft.Text(f"${p['price']}", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("Stock:", size=12, color=ft.Colors.WHITE70), ft.Text(str(p['stock']), size=14, color=color, weight=ft.FontWeight.BOLD), ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=16, color=ft.Colors.ORANGE_400) if is_low else ft.Container()], spacing=6),
                    ], spacing=8), padding=12,
                )
                self.inventory_list_container.controls.append(card)
        if self.page.controls: self.page.update()

    def build_sales_section(self, sales, stats, active_filter):
        header = create_header("Ventas", f"{stats.get('total_all', 0)} ventas registradas hoy", self.controller.handle_back, self.page.width)
        stats_grid = ft.Column([
            ft.Row([create_stats_card("Ventas Totales", stats.get('total_all', 0), "Transacciones", ft.Icons.SHOPPING_CART, ft.Colors.BLUE_400), create_stats_card("Completadas", f"${stats.get('amount_completed', 0):,.0f}", f"{stats.get('total_completed', 0)} ventas", ft.Icons.CHECK, ft.Colors.GREEN_400)], spacing=10),
            ft.Row([create_stats_card("Pendientes", f"${stats.get('amount_pending', 0):,.0f}", f"{stats.get('total_pending', 0)} ventas", ft.Icons.SCHEDULE, ft.Colors.AMBER_400), create_stats_card("Reembolsos", f"${stats.get('amount_refunded', 0):,.0f}", f"{stats.get('total_refunded', 0)} ventas", ft.Icons.REMOVE_SHOPPING_CART, ft.Colors.RED_400)], spacing=10),
        ], spacing=10)
        filters_container = ft.Row([
            self._create_icon_filter_button(ft.Icons.ALL_INBOX, stats.get('total_all', 0), "all", "sales", active_filter),
            self._create_icon_filter_button(ft.Icons.CHECK, stats.get('total_completed', 0), "completed", "sales", active_filter),
            self._create_icon_filter_button(ft.Icons.SCHEDULE, stats.get('total_pending', 0), "pending", "sales", active_filter),
            self._create_icon_filter_button(ft.Icons.REMOVE_SHOPPING_CART, stats.get('total_refunded', 0), "refunded", "sales", active_filter),
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
        search_bar = ft.TextField(label="Buscar por ID, caja, cliente...", prefix_icon=ft.Icons.SEARCH, border_radius=8, height=48, text_size=12, on_change=lambda e: self.controller.handle_search('sales', e.control.value), value=self.controller.search_query, border_color=TEXT_FIELD_BORDER_COLOR, focused_border_color=ft.Colors.BLUE_500, bgcolor=TEXT_FIELD_BG_COLOR, color=ft.Colors.WHITE)
        self.update_sales_list(sales)
        return ft.Stack([
            self.background,
            ft.Column([header, ft.Container(content=ft.Column([stats_grid, filters_container, search_bar, 
                
                ft.Container(self.sales_list_container, expand=True) 
                ], 
                spacing=16, 
                scroll=ft.ScrollMode.AUTO, # <-- ESTE ES EL SCROLL DE LA SECCIÓN
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                expand=True # <-- Y ESTE EXPAND ES CLAVE
                ), padding=16, expand=True)], expand=True)
        ], expand=True)
    
    def update_sales_list(self, sales):
        self.sales_list_container.controls.clear()
        status_map = {"completed": {"c": ft.Colors.GREEN_400, "i": ft.Icons.CHECK_CIRCLE}, "pending": {"c": ft.Colors.AMBER_400, "i": ft.Icons.SCHEDULE}, "refunded": {"c": ft.Colors.RED_400, "i": ft.Icons.CANCEL}}
        if not sales:
            self.sales_list_container.controls.append(create_styled_container(content=ft.Text("No se encontraron ventas", text_align=ft.TextAlign.CENTER), padding=32))
        else:
            for s in sales:
                status = status_map.get(s['status'], {"c": ft.Colors.GREY_500, "i": ft.Icons.HELP})
                card = create_styled_container(
                    content=ft.Column([
                        ft.Row([ft.Icon(status['i'], color=status['c'], size=18), ft.Text(f"Venta #{s['id']}", size=14, weight=ft.FontWeight.W_500, expand=True), ft.Text(f"${s['amount']:,.2f}", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Text(f"Caja: {s['cashier']} | Cliente: {s['customer']}", size=11, color=ft.Colors.WHITE70),
                    ], spacing=6), padding=12,
                )
                self.sales_list_container.controls.append(card)
        if self.page.controls: self.page.update()

    # --- ¡FUNCIÓN CORREGIDA! ---
    def build_earnings_section(self, earnings_data, active_tab):
        # Esta es la línea que faltaba
        header = create_header("Ganancias", "Análisis de ingresos", self.controller.handle_back, self.page.width)
        
        # Manejar caso de datos vacíos
        week_data = earnings_data.get('week', [])
        month_data = earnings_data.get('month', {})
        
        week_total = sum(d['amount'] for d in week_data)
        month_total = month_data.get('total', 0)
        
        stats_container = ft.Row([create_stats_card("Semana", f"${week_total:,}", "Ventas", ft.Icons.CALENDAR_VIEW_WEEK, ft.Colors.BLUE_400), create_stats_card("Mes", f"${month_total:,}", "Ventas", ft.Icons.CALENDAR_MONTH, ft.Colors.GREEN_400)], spacing=10)
        
        content_container = ft.Column(spacing=12) 
        
        if active_tab == "week":
            max_amount = max((d['amount'] for d in week_data), default=1) or 1
            chart_items = [ft.Container(content=ft.Column([ft.Row([ft.Text(day['day'], size=12, weight=ft.FontWeight.W_500), ft.Text(f"${day['amount']:,}", size=13, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), 
                                                           ft.Container(ft.Container(width=f"{(day['amount']/max_amount)*100}%", height=5, border_radius=3, bgcolor=ft.Colors.BLUE_400), height=5, border_radius=3, 
                                                                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), padding=0)], 
                                                          spacing=5), 
                                         padding=10, border_radius=8, bgcolor=TEXT_FIELD_BG_COLOR)
                           for day in week_data]
            content_container.controls.append(create_styled_container(ft.Column([ft.Text("Desglose Diario", size=16, weight=ft.FontWeight.BOLD)] + chart_items, spacing=8), padding=16))
        else:
            month_weeks_data = month_data.get('weeks', [])
            max_amount = max((w['amount'] for w in month_weeks_data), default=1) or 1
            chart_items = [ft.Container(content=ft.Column([ft.Row([ft.Text(week['week'], size=12, weight=ft.FontWeight.W_500), ft.Text(f"${week['amount']:,}", size=13, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), 
                                                           ft.Container(ft.Container(width=f"{(week['amount']/max_amount)*100}%", height=5, border_radius=3, bgcolor=ft.Colors.GREEN_400), height=5, border_radius=3, 
                                                                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), padding=0)], 
                                                          spacing=5), 
                                         padding=10, border_radius=8, bgcolor=TEXT_FIELD_BG_COLOR)
                           for week in month_weeks_data]
            content_container.controls.append(create_styled_container(ft.Column([ft.Text("Desglose Semanal", size=16, weight=ft.FontWeight.BOLD)] + chart_items, spacing=8), padding=16))
        
        # --- ESTE CÓDIGO ESTABA FUERA DE LUGAR, AHORA ESTÁ DENTRO ---
        def create_tab_button(label, tab_type):
            is_active = active_tab == tab_type
            bgcolor = BUTTON_COLOR if is_active else CONTAINER_COLOR
            border_color = BUTTON_BORDER_COLOR if is_active else BORDER_COLOR

            return create_styled_container(
                content=ft.Text(label, size=13, color=ft.Colors.WHITE if is_active else ft.Colors.WHITE70, weight=ft.FontWeight.W_500),
                padding=ft.padding.symmetric(horizontal=24, vertical=10),
                border_radius=8,
                on_click=lambda e, t_type=tab_type: self.controller.handle_earnings_tab_change(t_type),
                expand=True,
                bgcolor=bgcolor,
                border_color=border_color
            )
        tabs_container = ft.Row([create_tab_button("Semana", "week"), create_tab_button("Mes", "month")], spacing=10)
        # --- FIN DEL CÓDIGO MOVIDO ---
        
        return ft.Stack([
            self.background,
            ft.Column([
                header, # <-- Ahora la variable 'header' existe
                ft.Container(
                    content=ft.Column([
                        stats_container, 
                        tabs_container, # <-- Y esta variable 'tabs_container' también
                        content_container
                    ], 
                    spacing=16, 
                    scroll=ft.ScrollMode.AUTO, # <-- ESTE ES EL SCROLL DE LA SECCIÓN
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True # <-- Y ESTE EXPAND ES CLAVE
                    ), 
                padding=16, 
                expand=True)
            ], 
            expand=True)
        ], 
        expand=True)

    def build_maintenance_section(self, tasks, stats):
        header = create_header("Mantenimiento", f"{stats.get('total', 0)} tareas pendientes", self.controller.handle_back, self.page.width)
        stats_row = ft.Row([
            create_stats_card("Total Tareas", stats.get('total', 0), "Pendientes", ft.Icons.BUILD, ft.Colors.BLUE_400),
            create_stats_card("Prioridad Alta", stats.get('high_priority', 0), "Urgentes", ft.Icons.ERROR, ft.Colors.RED_400),
            create_stats_card("T. Promedio", f"{stats.get('avg_days', 0)} días", "Estimado", ft.Icons.TIMER, ft.Colors.AMBER_400),
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        search_bar = ft.TextField(label="Buscar por caja o problema...", prefix_icon=ft.Icons.SEARCH, border_radius=8, height=48, text_size=12, on_change=lambda e: self.controller.handle_search('maintenance', e.control.value), value=self.controller.search_query, border_color=TEXT_FIELD_BORDER_COLOR, focused_border_color=ft.Colors.BLUE_500, bgcolor=TEXT_FIELD_BG_COLOR, color=ft.Colors.WHITE)
        self.update_maintenance_list(tasks)
        return ft.Stack([
            self.background,
            ft.Column([header, ft.Container(content=ft.Column([stats_row, search_bar, 
                
                ft.Container(self.maintenance_list_container, expand=True) 
                ], 
                spacing=16, 
                scroll=ft.ScrollMode.AUTO, # <-- ESTE ES EL SCROLL DE LA SECCIÓN
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                expand=True # <-- Y ESTE EXPAND ES CLAVE
                ), padding=16, expand=True)], expand=True)
        ], expand=True)

    def update_maintenance_list(self, tasks):
        self.maintenance_list_container.controls.clear()
        if not tasks:
            self.maintenance_list_container.controls.append(create_styled_container(content=ft.Text("No hay tareas de mantenimiento", text_align=ft.TextAlign.CENTER), padding=32))
        else:
            p_Colors = {'high': ft.Colors.RED_400, 'medium': ft.Colors.ORANGE_400, 'low': ft.Colors.BLUE_400}
            for task in tasks:
                card = create_styled_container(
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.CIRCLE, color=p_Colors.get(task['priority'], ft.Colors.GREY_500), size=10), ft.Text(task['name'], size=14, weight=ft.FontWeight.W_500, expand=True), ft.Text(f"~{task['estimated_days']} días", size=11, color=ft.Colors.WHITE70)]),
                        ft.Text(task['issue'], size=12, color=ft.Colors.WHITE),
                        ft.Text(task['details'], size=11, color=ft.Colors.WHITE70, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=6), padding=12,
                )
                self.maintenance_list_container.controls.append(card)
        if self.page.controls: self.page.update()