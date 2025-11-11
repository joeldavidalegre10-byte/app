# model.py
import sqlite3
import hashlib

DB_FILE = "supermarket.db"

class AppModel:
    """
    Maneja todos los datos de la aplicación y la lógica de negocio.
    Ahora se conecta a una base de datos SQLite.
    """
    def __init__(self):
        self.db_file = DB_FILE

    def _connect_db(self):
        """
        Crea una conexión a la base de datos.
        Usamos sqlite3.Row para que los resultados se comporten como diccionarios.
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row 
            return conn
        except sqlite3.Error as e:
            print(f"Error al conectar a la BD: {e}")
            return None

    def hash_password(self, password):
        """Genera un hash SHA-256 seguro para la contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, username, password):
        """
        Lógica de autenticación real.
        Comprueba el usuario y la contraseña hasheada en la BD.
        Retorna el 'rol' (ej. 'admin' o 'user') si es exitoso.
        Retorna None si falla.
        """
        conn = self._connect_db()
        if not conn: return None
        
        try:
            user_row = conn.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,)).fetchone()
            
            if not user_row:
                return None 
                
            stored_hash = user_row["password_hash"]
            user_role = user_row["role"]
            
            input_hash = self.hash_password(password)
            
            if input_hash == stored_hash:
                return user_role 
            else:
                return None 
                
        except sqlite3.Error as e:
            print(f"Error en authenticate: {e}")
            return None
        finally:
            if conn: conn.close()

    def get_dashboard_stats(self):
        """Obtiene las estadísticas del dashboard desde la BD."""
        conn = self._connect_db()
        if not conn: return {}
        
        stats = {}
        try:
            stats["maintenance_count"] = conn.execute("SELECT COUNT(*) FROM maintenance_tasks").fetchone()[0]
            stats["total_cashiers"] = conn.execute("SELECT COUNT(*) FROM cashiers").fetchone()[0]
            stats["transactions_today"] = conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
            stats["low_stock_count"] = conn.execute("SELECT COUNT(*) FROM inventory WHERE stock <= min_stock").fetchone()[0]
            stats["month_growth"] = conn.execute("SELECT growth FROM month_stats").fetchone()["growth"]
        except sqlite3.Error as e:
            print(f"Error en get_dashboard_stats: {e}")
            return {}
        finally:
            if conn: conn.close()
            
        return stats

    def get_cashiers(self, status_filter="all", search_query=""):
        """Filtra y devuelve las cajas desde la BD."""
        conn = self._connect_db()
        if not conn: return []
        
        query = "SELECT * FROM cashiers"
        params = []
        where_clauses = []

        if status_filter != "all":
            where_clauses.append("status = ?")
            params.append(status_filter)
        
        if search_query:
            like_query = f"%{search_query.lower()}%"
            where_clauses.append("(lower(name) LIKE ? OR (operator IS NOT NULL AND lower(operator) LIKE ?))")
            params.extend([like_query, like_query])
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        try:
            data = conn.execute(query, params).fetchall()
        except sqlite3.Error as e:
            print(f"Error en get_cashiers: {e}")
            data = []
        finally:
            if conn: conn.close()
            
        return data

    def get_cashier_stats(self):
        """Calcula y devuelve estadísticas de las cajas desde la BD."""
        conn = self._connect_db()
        if not conn: return {}
        
        stats = {"open": 0, "closed": 0, "maintenance": 0}
        try:
            query = "SELECT status, COUNT(*) as count FROM cashiers GROUP BY status"
            status_counts = conn.execute(query).fetchall()
            
            for row in status_counts:
                if row["status"] in stats:
                    stats[row["status"]] = row["count"]

            stats["total_sales"] = conn.execute("SELECT SUM(sales) FROM cashiers").fetchone()[0] or 0
            stats["total_cashiers"] = sum(stats.values())
        except sqlite3.Error as e:
            print(f"Error en get_cashier_stats: {e}")
            return {}
        finally:
            if conn: conn.close()
            
        return stats
    
    def get_maintenance_tasks(self, search_query=""):
        """Filtra y devuelve las tareas de mantenimiento desde la BD."""
        conn = self._connect_db()
        if not conn: return []

        query = """
        SELECT mt.*, c.name 
        FROM maintenance_tasks mt
        JOIN cashiers c ON mt.cashier_id = c.id
        """
        params = []
        
        if search_query:
            like_query = f"%{search_query.lower()}%"
            query += """
            WHERE lower(c.name) LIKE ?
               OR lower(mt.issue) LIKE ?
               OR lower(mt.details) LIKE ?
               OR lower(mt.reported_by) LIKE ?
            """
            params.extend([like_query, like_query, like_query, like_query])
            
        try:
            data = conn.execute(query, params).fetchall()
        except sqlite3.Error as e:
            print(f"Error en get_maintenance_tasks: {e}")
            data = []
        finally:
            if conn: conn.close()
            
        return data

    def get_maintenance_stats(self):
        """Obtiene estadísticas de mantenimiento desde la BD."""
        conn = self._connect_db()
        if not conn: return {}
        
        stats = {}
        try:
            stats["total"] = conn.execute("SELECT COUNT(*) FROM maintenance_tasks").fetchone()[0]
            stats["high_priority"] = conn.execute("SELECT COUNT(*) FROM maintenance_tasks WHERE priority = 'high'").fetchone()[0]
            avg_days_result = conn.execute("SELECT AVG(estimated_days) FROM maintenance_tasks").fetchone()[0]
            stats["avg_days"] = round(avg_days_result) if avg_days_result else 0
        except sqlite3.Error as e:
            print(f"Error en get_maintenance_stats: {e}")
            return {}
        finally:
            if conn: conn.close()
            
        return stats

    def get_earnings_data(self):
        """Obtiene los datos de ganancias desde las tablas de la BD."""
        conn = self._connect_db()
        if not conn: return {}
        
        data = {}
        try:
            data["today"] = conn.execute("SELECT * FROM today_earnings").fetchone()
            data["week"] = conn.execute("SELECT * FROM daily_earnings").fetchall()
            
            month_stats = conn.execute("SELECT * FROM month_stats").fetchone()
            month_weeks = conn.execute("SELECT * FROM weekly_earnings").fetchall()
            
            data["month"] = {
                "total": month_stats["total"],
                "profit": month_stats["profit"],
                "growth": month_stats["growth"],
                "weeks": month_weeks
            }
        except sqlite3.Error as e:
            print(f"Error en get_earnings_data: {e}")
            return {}
        finally:
            if conn: conn.close()
            
        return data

    def get_inventory(self, stock_filter="all", search_query=""):
        """Filtra y devuelve los productos del inventario desde la BD."""
        conn = self._connect_db()
        if not conn: return []
        
        query = "SELECT * FROM inventory"
        params = []
        where_clauses = []

        if stock_filter == "low":
            where_clauses.append("stock <= min_stock")
        elif stock_filter == "high":
            where_clauses.append("stock > min_stock * 2")
        
        if search_query:
            like_query = f"%{search_query.lower()}%"
            where_clauses.append("(lower(name) LIKE ? OR lower(sku) LIKE ? OR lower(category) LIKE ?)")
            params.extend([like_query, like_query, like_query])
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        try:
            data = conn.execute(query, params).fetchall()
        except sqlite3.Error as e:
            print(f"Error en get_inventory: {e}")
            data = []
        finally:
            if conn: conn.close()
            
        return data

    def get_inventory_stats(self):
        """Obtiene estadísticas de inventario desde la BD."""
        conn = self._connect_db()
        if not conn: return {}
        
        stats = {}
        try:
            stats["total_products"] = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
            stats["low_stock_count"] = conn.execute("SELECT COUNT(*) FROM inventory WHERE stock <= min_stock").fetchone()[0]
            stats["high_stock_count"] = conn.execute("SELECT COUNT(*) FROM inventory WHERE stock > min_stock * 2").fetchone()[0]
            stats["total_value"] = conn.execute("SELECT SUM(stock * price) FROM inventory").fetchone()[0] or 0
            stats["total_stock_units"] = conn.execute("SELECT SUM(stock) FROM inventory").fetchone()[0] or 0
        except sqlite3.Error as e:
            print(f"Error en get_inventory_stats: {e}")
            return {}
        finally:
            if conn: conn.close()
            
        return stats

    def get_sales(self, status_filter="all", search_query=""):
        """Filtra y devuelve las ventas desde la BD."""
        conn = self._connect_db()
        if not conn: return []
        
        query = "SELECT * FROM sales"
        params = []
        where_clauses = []

        if status_filter != "all":
            where_clauses.append("status = ?")
            params.append(status_filter)
        
        if search_query:
            like_query = f"%{search_query.lower()}%"
            where_clauses.append("(lower(cashier) LIKE ? OR lower(customer) LIKE ? OR CAST(id AS TEXT) LIKE ?)")
            params.extend([like_query, like_query, like_query])
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        try:
            data = conn.execute(query, params).fetchall()
        except sqlite3.Error as e:
            print(f"Error en get_sales: {e}")
            data = []
        finally:
            if conn: conn.close()
            
        return data

    def get_sales_stats(self):
        """Obtiene estadísticas de ventas desde la BD."""
        conn = self._connect_db()
        if not conn: return {}

        stats = {
            "total_all": 0, "total_completed": 0, "total_pending": 0, "total_refunded": 0,
            "amount_completed": 0, "amount_pending": 0, "amount_refunded": 0
        }
        try:
            query = "SELECT status, COUNT(*) as count, SUM(amount) as total_amount FROM sales GROUP BY status"
            rows = conn.execute(query).fetchall()

            for row in rows:
                if row["status"] in ["completed", "pending", "refunded"]:
                    status_key = row["status"]
                    stats[f"total_{status_key}"] = row["count"]
                    stats[f"amount_{status_key}"] = row["total_amount"]
                    stats["total_all"] += row["count"]
                
        except sqlite3.Error as e:
            print(f"Error en get_sales_stats: {e}")
            return {}
        finally:
            if conn: conn.close()
            
        return stats