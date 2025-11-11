El proyecto es una aplicación de gestión de supermercado creada con Python y la biblioteca Flet. Utiliza una arquitectura muy organizada llamada Modelo-Vista-Controlador (MVC) para separar las responsabilidades:

El Modelo (El Cerebro): Es la parte que maneja todos los datos y la lógica de negocio.

Se conecta a una base de datos SQLite (un archivo que contiene todas las tablas).

Define cómo autenticar usuarios. Compara la contraseña que escribes con una versión segura (un "hash") guardada en la base de datos para ver si coincide.

Sabe si un usuario es 'admin' o 'user'.

Tiene funciones para obtener datos (ej. get_cashiers, get_inventory) y puede filtrarlos (ej. mostrar solo cajas "abiertas" o productos con "stock bajo") y buscarlos.

La Vista (La Cara): Es todo lo que el usuario ve y con lo que interactúa.

Está construida 100% con Flet.

Utiliza un tema oscuro profesional y define componentes reutilizables (como tarjetas, botones y cabeceras).

Tiene funciones para "construir" cada pantalla: la de inicio de sesión, el panel principal (dashboard) y una pantalla para cada sección (Cajas, Ventas, Inventario, etc.).

Es dinámica: Por ejemplo, en el dashboard, comprueba el rol del usuario. Si el usuario es "admin", le muestra los botones de "Mantenimiento" y "Ganancias"; si es un "user" normal, esos botones se ocultan.

El Controlador (El Coordinador): Es la pieza central que une todo.

Mantiene el "estado" de la aplicación (quién ha iniciado sesión, qué rol tiene, qué pantalla está viendo, qué filtro está activo).

Actúa como el intermediario: la Vista nunca habla directamente con el Modelo, y viceversa.

Maneja todas las acciones del usuario.

Flujo de Funcionamiento Paso a Paso
Así es como funciona todo junto cuando usas la aplicación:

Inicio y Login:

Inicias la aplicación. El Controlador ve que nadie ha iniciado sesión (is_logged_in es False).

Le dice a la Vista que construya y muestre la build_login_screen.

Intento de Login:

Escribes "admin_root" y tu contraseña. Haces clic en "Iniciar Sesión".

La Vista le dice al Controlador: "¡El usuario hizo clic en login con estos datos!".

El Controlador toma esos datos y le pregunta al Modelo: "Por favor, autentica a este usuario".

El Modelo busca en la base de datos, hashea la contraseña que escribiste, la compara y responde al Controlador: "Éxito. El rol es 'admin'".

Renderizado del Dashboard:

El Controlador actualiza su estado: is_logged_in = True y current_user_role = 'admin'.

Inmediatamente llama a su función principal render().

La función render() ve que el usuario está logueado pero no ha elegido sección (current_section es None).

Le pide al Modelo las estadísticas para el dashboard (ej. get_dashboard_stats()).

Luego, le dice a la Vista: "Construye el build_dashboard con estas estadísticas".

La Vista construye el dashboard. Al hacerlo, pregunta al Controlador por el rol del usuario. Como es 'admin', muestra todos los botones.

Navegación a una Sección:

Haces clic en el botón "Inventario".

La Vista le dice al Controlador: "¡El usuario seleccionó la sección 'inventory'!".

El Controlador actualiza su estado: current_section = 'inventory' y vuelve a llamar a render().

Renderizado de Sección (Ej. Inventario):

La función render() ve que current_section es 'inventory'.

Le pide al Modelo las estadísticas de inventario (get_inventory_stats()).

Le pide al Modelo la lista de productos, usando el filtro y la búsqueda actuales (ej. get_inventory(active_filter, search_query)).

Le pasa todos esos datos a la Vista y le dice: "Construye la build_inventory_section con estos datos".

Uso de Filtros y Búsqueda:

Si haces clic en un filtro (ej. "Stock Bajo"): El Controlador actualiza active_filter = 'low' y llama a render(). Esto recarga toda la sección (paso 5) pero ahora el Modelo devuelve solo productos con stock bajo.

Si escribes en la barra de búsqueda: El Controlador NO recarga todo. Llama a una función update_dynamic_list(). Esta función solo le pide al Modelo los nuevos datos filtrados por la búsqueda y le dice a la Vista que solo actualice la lista de productos, lo cual es mucho más rápido.

Además de esto, tienes un script separado de configuración (database_setup.py) cuyo único propósito es crear el archivo de la base de datos desde cero y llenarlo con todos los datos de ejemplo (cajas, usuarios, productos, etc.) para que la aplicación tenga algo que mostr
