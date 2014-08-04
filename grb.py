# -*- python -*-

import cgi, cookielib, datetime, logging, urllib2, webapp2
#from google.appengine.ext import db
#from google.appengine.api import taskqueue, urlfetch

class GetFeed (webapp2.RequestHandler):
    def get (self):
        self.response.out.write ("Hello, world!")


handlers = [
    ('/hello.txt', GetFeed)

]

app = webapp2.WSGIApplication (handlers)
