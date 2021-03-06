# -*- coding: utf-8 -*-

__all__ = ['URL']

import urllib
from webob.multidict import MultiDict
from .url_templates import urlquote


def construct_url(path, query, host, port, schema):
    query = ('?' + '&'.join(['%s=%s' % (urlquote(k), urlquote(v)) \
                            for k,v in query.iteritems()])  \
             if query else '')

    path = path
    if host:
        host = host.encode('idna')
        port = ':' + port if port else ''
        return ''.join((schema, '://', host, port, path,  query))
    else:
        return path + query


class URL(str):
    def __new__(cls, path, query=None, host=None, port=None, schema=None, show_host=True):
        '''
        path - urlencoded string or unicode object (not encoded at all)
        '''
        path = path if isinstance(path, str) else urlquote(path)
        query = MultiDict(query) if query else MultiDict()
        host = host or ''
        port = port or ''
        schema = schema or 'http'
        self = str.__new__(cls, construct_url(path, query, host if show_host else '', port,schema))
        self.path = path
        self.query = query
        self.host = host
        self.port = port
        self.schema = schema
        self.show_host = show_host
        return self

    def _copy(self, **kwargs):
        path = kwargs.pop('path', self.path)
        kw = dict(query=self.query, host=self.host, 
                  port=self.port, schema=self.schema,
                  show_host=self.show_host)
        kw.update(kwargs)
        return self.__class__(path, **kw)

    def qs_set(self, *args, **kwargs):
        if args and kwargs:
            raise TypeError('Use positional args or keyword args not both')
        query = self.query.copy()
        if args:
            mdict = MultiDict(args[0])
            for k in mdict.keys():
                if k in query:
                    del query[k]
            for k, v in mdict.items():
                query.add(k, v)
        else:
            for k, v in kwargs.items():
                query[k] = v
        return self._copy(query=query)

    def qs_add(self, *args, **kwargs):
        query = self.query.copy()
        if args:
            mdict = MultiDict(args[0])
            for k, v in mdict.items():
                query.add(k, v)
        for k, v in kwargs.items():
            query.add(k, v)
        return self._copy(query=query)

    def with_host(self):
        return self._copy(show_host=True)

    def qs_delete(self, key):
        query = self.query.copy()
        try:
            del query[key]
        except KeyError:
            pass
        return self._copy(query=query)

    def qs_get(self, key, default=None):
        return self.query.get(key, default=default)

    def qs_getall(self, key):
        return self.query.getall(key)

    def qs_getone(self, key):
        return self.query.getone(key)

    def get_readable(self):
        '''Gets human-readable representation of the url'''
        query = (u'?' + u'&'.join([u'%s=%s' % (k,v) for k, v in self.query.iteritems()]) \
                 if self.query else '')

        path = urllib.unquote(self.path).decode('utf-8')
        if self.host:
            port = u':' + self.port if self.port else u''
            return u''.join((self.schema, '://', self.host, port, path,  query))
        else:
            return path + query

    def __repr__(self):
        return '<URL %r>' % str.__repr__(self)
