# -*- coding: utf-8 -*-
# Copyright (c) J. A. Zanardo Jr. <zanardo@gmail.com>
# Please refer to COPYING for license details

import re
import os
import os.path
import tempfile
import bottle
import rrdtool
import time

__VERSION__ = '0.3'

app = bottle.Bottle()

DIR = os.path.realpath(os.path.curdir)

PERIODS = [ ('Horário', 7200), ('Diário', 86400), ('Semanal', 604800),
           ('Mensal', 1814400), ('Anual', 21772800) ]

@app.route('/render-graph/:name#[a-z0-9\-]+#/:width#\d+#/:height#\d+#/:offset#\d+#')
def render_graph(name, width, height, offset):

    img = ''

    graph_params = [
        "-E",
        "--end=now",
        "--start=end-%s" % offset,
        "--width=%s" % width,
        "--height=%s" % height,
        "--font=AXIS:6",
        "--font=LEGEND:7",
        "--font=TITLE:7",
        "--color=BACK#FFFFFF",
        "--color=SHADEA#FFFFFF",
        "--color=SHADEB#FFFFFF"
    ]

    # Loading graph definition
    try:
        os.chdir(DIR)
        fp = open('./conf-graph/%s' % name)
        graph_params.extend(
            [ line.strip() for line in fp.readlines() if not re.match('^#', line) ]
        )
        fp.close()
    except Exception, err:
        return err

    # Generating graph
    try:
        os.chdir('./data')
        fp, path = tempfile.mkstemp('.png')
        rrdtool.graph(path, graph_params)
        fptmp = open(path)
        chunk = fptmp.read(4096)
        while chunk:
            img += chunk
            chunk = fptmp.read(4096)
        fptmp.close()
    except Exception, err:
        return err

    bottle.response.headers['Content-Type'] = 'image/png'
    return img

@app.route('/list-graph-all-periods/:name#[a-z0-9\-]+#')
def list_graph_all_periods(name):

    template = """
        <header>
            <link rel="stylesheet" type="text/css" href="/styles.css">
            <title>Gráficos RRD - {{ name }}</title>
        </header>
        <h1>Gráficos RRD - {{ name }}</h1>
        %for period in periods:
            <h3>{{ period[0] }}</h3>
            <img src="/render-graph/{{ name }}/650/200/{{ period[1] }}">
        %end
        {{!footer}}
    """

    return bottle.template(template, name=name, periods=PERIODS,
                           footer=page_footer())

def filter_graphs(filter_re):
    filter_re_compiled = re.compile(filter_re)
    os.chdir('%s/conf-graph' % DIR)
    return [
        graph for graph in os.listdir('.') \
        if re.match('^[a-z0-9\-]+$', graph) \
            and re.search(filter_re_compiled, graph) 
    ]


@app.route('/')
def index():
    offset = bottle.request.forms.get('offset') or 86400
    filter_re = bottle.request.GET.get('re') or '!!!'
    graphs = filter_graphs(filter_re)
    all_graphs = filter_graphs('.*')
    template = """
    <head>
        <title>Gráficos RRD</title>
        <link rel="stylesheet" type="text/css" href="/styles.css">
    </head>
    <table width="100%" border="0">
    <tr>
    <td valign="top" width="500px">
    <p>
    %for graph in graphs:
        <h3>{{graph}}</h3>
        <img src="/render-graph/{{graph}}/400/100/{{offset}}">
    %end
    {{!footer}}
    </td>
    <td valign="top">
    <h1>Gráficos RRD</h1>
    <form method="get" action="/" enctype="multipart/form-data">
    <input type="text" name="re" size="10">
    <input type="submit" name="submit" value="Filtrar">
    </form>
    <p>
    <b>Período</b>
    <p>
    %for period in periods:
        <a href="/?offset={{period[1]}}">{{ period[0] }}</a><br>
    %end
    <p>
    <b>Todos</b>
    <p>
    %for graph in all_graphs:
        <a href="/list-graph-all-periods/{{graph}}">{{graph}}</a><br>
    %end
    </td>
    </tr>
    </table>
    """

    return bottle.template(template, footer=page_footer(), periods=PERIODS,
                           graphs=graphs, offset=offset, all_graphs=all_graphs)

@app.route('/styles.css')
def css():
    bottle.response.content_type = 'text/css'
    return """
        body { margin: 1em 2em 2em 2em; }
        h1, h2, h3, h4, h5, h6 {
          font-family: "Gill Sans", "Trebuchet MS", Verdana, sans-serif;
          font-weight: normal; 
        }
        img { border: none; }
        dt { font-weight: bold; }
        pre { background-color: #C0C0C0; font-weight: bold; }
        a:link { color: #0000EE; }
        a:visited { color: #0000EE; }
        a:active { color: #0000EE; }
        a:hover { color: #0000EE; }
    """

def page_footer():
    return """<p><small><i>Página gerada em %s por 
        <a href="http://zanardo.org/rrd.html">rrd %s</a></i></small>""" % \
            ( time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
             __VERSION__ )

if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(reloader=True, app=app, host='0.0.0.0')
