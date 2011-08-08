# Copyright (c) J. A. Zanardo Jr. <zanardo@gmail.com>
# Please refer to COPYING for license details

import re
import os
import os.path
import tempfile
import bottle
import rrdtool

__VERSION__ = '0.3'

app = bottle.Bottle()

DIR = os.path.realpath(os.path.curdir)

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
        for line in fp:
            line = line.strip()
            if re.match('^#', line):
                continue
            graph_params.append(line)
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

if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(reloader=True, app=app, host='0.0.0.0')
