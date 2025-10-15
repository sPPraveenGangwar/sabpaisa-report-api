"""
Multi-database routing for SabPaisa Reports API
"""

class MultiDatabaseRouter:
    """
    A router to control all database operations on models for the
    auth, transaction, and user management applications.
    """
    route_app_labels = {
        'authentication': 'user_management',
        'contenttypes': 'default',
        'sessions': 'default',
        'admin': 'default',
        'auth': 'user_management',
    }

    def db_for_read(self, model, **hints):
        """Suggest the database should be used to read the model."""
        # Route specific models to their databases
        if model._meta.app_label == 'authentication':
            return 'user_management'
        elif model._meta.app_label == 'transactions':
            # Check if it's a legacy model
            if hasattr(model, 'USE_LEGACY_DB') and model.USE_LEGACY_DB:
                return 'legacy'
            return 'default'
        elif model._meta.app_label == 'settlements':
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        """Suggest the database should be used for writes of model."""
        # Route specific models to their databases
        if model._meta.app_label == 'authentication':
            return 'user_management'
        elif model._meta.app_label == 'transactions':
            # Check if it's a legacy model
            if hasattr(model, 'USE_LEGACY_DB') and model.USE_LEGACY_DB:
                return 'legacy'
            return 'default'
        elif model._meta.app_label == 'settlements':
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same app label."""
        db_set = {'default', 'legacy', 'user_management'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps only migrate to the appropriate databases."""
        if app_label == 'authentication':
            return db == 'user_management'
        elif app_label in ['transactions', 'settlements']:
            if db == 'legacy':
                return False  # Don't create new tables in legacy DB
            return db == 'default'
        elif db == 'user_management':
            return app_label == 'authentication'
        elif db == 'legacy':
            return False  # No migrations on legacy database
        return db == 'default'