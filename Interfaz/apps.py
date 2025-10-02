from django.apps import AppConfig

class InterfazConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Interfaz'

    def ready(self):
        from django.db.backends.mysql.base import DatabaseWrapper as MySQLDatabaseWrapper
        original_get_new_connection = MySQLDatabaseWrapper.get_new_connection

        def patched_get_new_connection(self, conn_params):
            conn = original_get_new_connection(self, conn_params)
            conn.query("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'")
            conn.query("SET collation_connection = 'utf8mb4_unicode_ci'")
            return conn

        MySQLDatabaseWrapper.get_new_connection = patched_get_new_connection