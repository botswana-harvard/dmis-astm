

class DmisAstmRouter(object):

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label == 'dmis_astm':
            return 'dmis_db'
        else:
            return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'dmis_astm':
            return False
        else:
            return 'default'

    def allow_migrate(self, db, model):
        try:
            if model.do_not_migrate:
                return False
        except AttributeError:
            return True
