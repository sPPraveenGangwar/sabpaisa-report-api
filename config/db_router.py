"""
Database Router for Multi-Database Support
Routes QwikForms models to qwikforms_db database
"""


class QwikFormsRouter:
    """
    A router to control all database operations on models in the
    qwikforms application.
    """
    route_app_labels = {'qwikforms'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read qwikforms models go to qwikforms_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'qwikforms_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write qwikforms models go to qwikforms_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'qwikforms_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the qwikforms apps is involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the qwikforms apps only appear in the 'qwikforms_db'
        database.
        """
        if app_label in self.route_app_labels:
            return db == 'qwikforms_db'
        return None