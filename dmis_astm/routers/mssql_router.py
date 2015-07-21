

class DmisAstmRouter(object):

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'dmis_astm':
            return None
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        if app_label == 'dmis_astm':
            return False
        return None
