# -*- python -*-
#
# Copyright 2014 Philip Cowperthwaite and collaborators. Licensed under the
# MIT License.

import logging, urllib, urllib2, webapp2
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler


class ConfigRecord (db.Model):
    name = db.StringProperty (required=True)
    value = db.StringProperty (required=True)


class SetKey (webapp2.RequestHandler):
    """TODO: multiple calls to this will create multiple entires in the database,
    which leads to unpredictable results. Right now we fix this by logging in
    to the Developer Console web UI and cleaning things out, but this function
    should really clear existing database keys.

    """
    def get (self):
        key = self.request.get ('key')
        self.response.out.write ('set key to : ' + key)
        ConfigRecord (name='api-key', value=key).put ()


class SetEmail (webapp2.RequestHandler):
    """TODO: see comment in SetKey handler."""

    def get (self):
        email = self.request.get ('email')
        self.response.out.write ('set email to : ' + email)
        ConfigRecord (name='email', value=email).put ()


def get_config (name):
    results = list (db.GqlQuery ('SELECT * FROM ConfigRecord where name = :1', name))

    if len (results) > 1:
        logging.warn ('multiple results for config record "%s"' % name)
    if len (results) == 0:
        raise Exception ('missing needed config record "%s"' % name)

    return results[0].value


class CountSubscribers (webapp2.RequestHandler):
    def get (self):
        from cgi import escape

        key = get_config ('api-key')
        url = 'https://api.justyo.co/subscribers_count?api_token=' + urllib.quote (key)
        result = urlfetch.fetch (url=url, method=urlfetch.GET)

        self.response.out.write ('<!DOCTYPE html><html><head></head><body>')
        self.response.out.write ('<p>Response status code: %s</p>' % result.status_code)
        self.response.out.write ('<pre>')
        self.response.out.write (escape (result.content))
        self.response.out.write ('</pre></body></html>')


FERMI_DUR_THRESHOLD = 0.5 # seconds

class GRB (InboundMailHandler):
    def receive (self, mail_message):
        # The precise destination email address that we accept is a random
        # string, so that random people can't just trigger GRB alerts. Ignore
        # any emails that don't come to the right address.

        logging.info ('Received a message from: ' + mail_message.sender)
        mailtext = mail_message.original.as_string ()
        logging.info ('Mail content: ' + mailtext)

        email = get_config ('email')
        if not self.request.path.startswith('/_ah/mail/' + email + '@'):
            logging.warn ('Suspicious e-mail to ' + self.request.path)
            return

        # Filter out low-significant Fermi alerts, since they're quite common.
        reject_this_one = False

        for line in mailtext.splitlines ():
            if 'TRIGGER_DUR:' in line:
                try:
                    q = float (line.split ()[1])
                except Exception as e:
                    logging.warn ('failed to parse TRIGGER_DUR line: ' + str (e))
                else:
                    if q < FERMI_DUR_THRESHOLD:
                        reject_this_one = True

        if reject_this_one:
            logging.info ('rejected this event due to low significance')
            return

        # OK to go!
        logging.info ('Sending GRB Yo!')

        form_fields = {'api_token': get_config ('api-key')}
        result = urlfetch.fetch (url='http://api.justyo.co/yoall/',
                                 payload=urllib.urlencode (form_fields),
                                 method=urlfetch.POST,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})

handlers = [
    ('/_ah/mail/.+', GRB),
    ('/admin/setkey', SetKey),
    ('/admin/setemail', SetEmail),
    ('/admin/subcount', CountSubscribers),
]

app = webapp2.WSGIApplication (handlers)
