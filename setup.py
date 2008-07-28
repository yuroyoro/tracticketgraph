from setuptools import setup

PACKAGE = 'TracTicketGraph'
VERSION = '0.6'

setup(name=PACKAGE,
version=VERSION,
packages=['ticketgraph'],
entry_points={'trac.plugins': '%s = ticketgraph' % PACKAGE},
package_data={'ticketgraph': ['templates/*.cs', 'htdocs/*.css','htdocs/FusionChartsFree/Charts/*' ,'htdocs/FusionChartsFree/JSClass/*']},
author = "Tomohito Ozaki",
author_email = "ozaki@yuroyoro.com",
description = "This is a Ticket Timeline Chart Graph creation plugin for Trac.",
url = "http://d.hatena.ne.jp/yuroyoro/",
)
