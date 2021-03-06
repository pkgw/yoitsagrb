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


class SetConfig (webapp2.RequestHandler):
    """TODO: multiple calls to this handler will create multiple records in the
    config database, which leads to unpredictable results. Right now we fix
    this manually by logging in to the Developer Console web UI and cleaning
    things out, but this function should really clear existing records with
    the same name.

    This handler can only be called by administrators, so we don't
    sanity-check the input or the output. Also, it should really be a POST,
    not GET, since it changes the server's state. For our simple uses, the
    current implementation is good enough, though.

    """
    def get (self):
        from cgi import escape

        name = self.request.get ('name')
        value = self.request.get ('value')

        self.response.out.write ('set "%s" to "%s"' %
                                 (escape (name), escape (value)))
        ConfigRecord (name=name, value=value).put ()


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
ALLOWED_SENDERS = [
    'vxw@capella2.gsfc.nasa.gov',
]

class GRB (InboundMailHandler):
    def receive (self, mail_message):
        # The precise destination email address that we accept is a random
        # string, so that random people can't just trigger GRB alerts. Ignore
        # any emails that don't come to the right address.

        logging.info ('Received a message from: ' + mail_message.sender)
        for sender in ALLOWED_SENDERS:
            if sender in mail_message.sender:
                break
        else:
            # this branch is taken if nothing matches
            logging.info ('discarding due to unrecognized sender address')
            return

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
    ('/admin/setconfig', SetConfig),
    ('/admin/subcount', CountSubscribers),
]

app = webapp2.WSGIApplication (handlers)
