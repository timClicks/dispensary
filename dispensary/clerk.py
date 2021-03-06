#! /usr/bin/env python
# -*- encoding: latin-1 -*-

try:
    import cPickle as pickle
except ImportError:
    import pickle
from datetime import datetime, timedelta
import feedparser as fp
import time

class Feed(object):
    """
    Provides tools to download & cache a 
    feed. Works with nearly every feed standard.
    
    TODO:
       - implement the "borg" pattern, 
         from Alex Martelli
         http://code.google.com/edu/languages/index.html#_python_patterns
    """

    def __init__(self, url):
        self.url = url
        self.contents = self.load(url)

    def load(self, url):
        try:
            feed = pickle.load(open('%s.pkl' % url))
            new = get_new(url, stale_feed)
            if new.has_key('entries'):
                feed = new
        except IOError:
            feed = retrieve_feed(url)
        finally:
            pickle.dumps(open('%s.pkl' % url, 'w+b'))
            
        return feed

    def get_new(self, url, stale_feed):
        new = None
        try:
            new = _new_with_etag(url, stale_feed)
        except AttributeError:
            try:
                new = _new_with_last_modified(url, stale_feed)
            except AttributeError:
                try:
                    new = _new_with_cache_control(url, stale_feed)
                except AttributeError, KeyError, ValueError:
                    try:
                        new = _new_with_headers_expires(url, stale_feed)
                    except:
                        pass
        return new or stale_feed

    def _new_with_etag(self, url, stale_feed):
        return retrieve_feed(self, url, etag=stale_feed.etag)

    def _new_with_last_modified(self, url, stale_feed):
        return retrieve_feed(self, url, last_modified=stale_feed.modified)

    def _new_with_cache_control(self, url, stale_feed):
        """
        >>> cant_cache = {'headers':{'cache-control': 'private'}}
        >>> _new_with_cache_control(cant_cache)
        Traceback (most recent call last):
        ...
        ValueError
        """
        if not 'public' in stale_feed['headers']['cache-control']:
            exp = stale_feed['headers']['cache-control'].split("=")[-1]
            now = datetime.utcnow()
            if datetime(*stale_feed['updated'][:7]) + exp < now:
                return retrieve_feed(self, url)
        else:
            raise ValueError

    def _new_with_headers_expires(self, url, stale_feed):
        """
        >>> from datetime import datetime, timedelta
        >>> now = datetime.utcnow()
        >>> stale = {'headers': {'expires':'Wed, 18 Aug 2010 06:06:11 GMT'}}
        >>> url = 'http://feedparser.org/docs/examples/atom10.xml'
        >>> res = _new_with_headers_expires(url, stale)
        >>> res.status
        200
        >>> stale = {'headers': { 'expires':datetime.isoformat(now + timedelta(minutes=30))}}
        >>> res2 = _new_with_headers_expires(url, stale)
        >>> res == res2
        False
        """
        exp = fp._parse_date(stale_feed['headers']['expires'])
        if time.time() > exp:
            return retrieve_feed(url)

    def retrieve_feed(self, url, etag=None, last_modified=None):
        """Light-weight feed parsing
        
        This function retrieves entries from
        a given url.
        >>> retrieve_docs("http://www.example.com/doesnt/exist")
        None
        """
        feed = fp.parse(url, etag, last_modified)
        if feed['bozo'] == 0: # 200 OK
            return feed
