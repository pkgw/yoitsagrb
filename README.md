# YO, IT’S A GRB!

[YOITSAGRB] is a web service that sends you a [Yo](http://www.justyo.co/)
whenever a [gamma-ray burst](http://en.wikipedia.org/wiki/Gamma-ray_burst)
occurs in the known universe. With our current gamma-ray observatories, humans
detect a new GRB every few days, give or take.

This page has the source code that drives the web app. See [the main
site][YOITSAGRB] for a non-programmer’s description.

[YOITSAGRB]: http://pkgw.github.io/yoitsagrb/

## How does it work under the hood?

The file `grb.py` is the main one. There’s absolutely nothing fancy: we get
[GCN](http://gcn.gsfc.nasa.gov/) email alerts, and translate them into Yos.

## Who’s responsible for this?

[Philip
Cowperthwaite](http://astronomy.fas.harvard.edu/people/philip-cowperthwaite)
and [Peter K. G. Williams](http://newton.cx/~peter/).

## Can I copy the code to start my own similar project?

Most definitely. The source files are copyright Philip Cowperthwaite and
collaborators, 2014, but they are all (including this one) licensed under the
permissive, open-source [MIT License](http://opensource.org/licenses/MIT).
