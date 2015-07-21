from getresults_astm.dispatchers import Dispatcher


class DmisDispatcherMixin(Dispatcher):

    def save_to_db(self, records):
        raise NotImplemented()


class OrderDispatcher(DmisDispatcherMixin, Dispatcher):
    pass
