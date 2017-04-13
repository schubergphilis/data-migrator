class BaseEmitter(object):
    '''Base for emitters of the data_migrator'''

    def __init__(self, extension=None, manager=None):
        self.manager=manager
        self.model_class=manager.model_class
        self.meta=self.model_class._meta
        self.extension = extension or getattr(self.__class__, 'extension', '.txt')

    def emit(self, l):
        '''output the result set of an object'''
        raise NotImplementedError

    def filename(self):
        '''generate filename for this emitter'''
        _ext = self.extension
        if _ext[0] != '.':
            _ext = '.' + _ext
        _filename = self.meta.file_name or (self.meta.table_name + _ext)
        return _filename

    def preamble(self, headers=[]):
        '''generate a premable for the file to emit'''
        raise NotImplementedError
