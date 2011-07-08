# -*- coding: utf-8 -*-

__all__ = ['Reverse', 'URL']

import urllib
from webob.multidict import MultiDict
from .url import urlquote


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
    def __new__(cls, path, query=None, host=None, port=None, schema=None):
        '''
        path - urlencoded string or unicode object (not encoded at all)
        '''
        path = path if isinstance(path, str) else urlquote(path)
        query = MultiDict(query) if query else MultiDict()
        host = host or ''
        port = port or ''
        schema = schema or 'http'
        self = str.__new__(cls, construct_url(path, query, host, port,schema))
        self.path = path
        self.query = query
        self.host = host
        self.port = port
        self.schema = schema
        return self

    def _copy(self, **kwargs):
        path = kwargs.pop('path', self.path)
        kw = dict(query=self.query, host=self.host, 
                  port=self.port, schema=self.schema)
        kw.update(kwargs)
        return self.__class__(path, **kw)

    def qs_set(self, **kwargs):
        query = self.query.copy()
        for k, v in kwargs.items():
            query[k] = v
        return self._copy(query=query)

    def qs_add(self, **kwargs):
        query = self.query.copy()
        for k, v in kwargs.items():
            query.add(k, v)
        return self._copy(query=query)

    def qs_delete(self, key):
        query = self.query.copy()
        del query[key]
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


class Location(object):
    def __init__(self, *builders):
        self.builders = list(builders)
        self.subdomains = []

    @property
    def need_arguments(self):
        for b in self.builders:
            if b._url_params:
                return True
        return False

    def build_path(self, **kwargs):
        result = []
        for b in self.builders:
            result.append(b(**kwargs))
        return ''.join(result)

    def build_subdomians(self):
        return u'.'.join(self.subdomains)

    def __eq__(self, other):
        return self.builders == other.builders and self.subdomains == other.subdomains


class Reverse(object):
    def __init__(self, scope, location=None, path='', host='', ready=False):
        self._location = location
        self._scope = scope
        self._ready = ready
        self._path = path
        self._host = host
        self._is_endpoint = (not self._scope) or ('' in self._scope)
        self._is_scope = bool(self._scope)

    def __call__(self, **kwargs):
        if self._is_endpoint:
            location = self._scope[''][0] if self._is_scope else self._location
            host = self._host + location.build_subdomians()
            path = location.build_path(**kwargs)
            return self.__class__(self._scope, self._location, path=path, host=host, ready=True)
        raise Exception('Not Endpoint')

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        if self._is_scope and name in self._scope:
            location, scope = self._scope[name]
            path = self._path
            host = self._host
            ready = False
            if not location.need_arguments:
                path = location.build_path()
                host += location.build_subdomians()
                ready = True
            return self.__class__(scope, location, path, host, ready=ready)
        raise AttributeError(name)

    @property
    def as_url(self):
        if self._ready:
            return URL(self._path, host=self._host)
        raise Exception('Not ready')

    @classmethod
    def from_handler(cls, handler, env=None):
        from .core import locations
        return cls(locations(handler))
