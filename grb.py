# -*- python -*-

import logging, urllib, urllib2, webapp2
from google.appengine.ext import db
from google.appengine.api import urlfetch


class ConfigRecord (db.Model):
    name = db.StringProperty (required=True)
    value = db.StringProperty (required=True)


class SetKey (webapp2.RequestHandler):
    def get (self):
        key = self.request.get ('key')
        self.response.out.write('set key to : ' + key)
        ConfigRecord (name='api-key', value = key).put ()


class SetEmail (webapp2.RequestHandler):
    def get (self):
        email = self.request.get ('email')
        self.response.out.write('set email to : ' + email)
        ConfigRecord (name='email', value = email).put ()


class GRB (webapp2.RequestHandler):
    def post (self):
        keys = list (db.GqlQuery ('SELECT * FROM ConfigRecord where name = \'api-key\''))
        key = keys[0]

        emails = list (db.GqlQuery ('SELECT * FROM ConfigRecord where name = \'email\''))
        email = emails[0]

        if not self.request.path.startswith('/_ah/mail/' + email.value + '@'):
            logging.warn ('Suspicious e-mail to ' + self.request.path)
            return

        logging.info ('GRB Yo! sent.')

        form_fields = {
          "api_token": key.value,
        }
        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url="http://api.justyo.co/yoall/",
            payload=form_data,
            method=urlfetch.POST,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})

handlers = [
    ('/_ah/mail/.+', GRB),
    ('/admin/setkey', SetKey),
    ('/admin/setemail', SetEmail)
]

app = webapp2.WSGIApplication (handlers)
