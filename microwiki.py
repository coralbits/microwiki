#!/usr/bin/python3
from flask import Flask
import os
import markdown
import re
from jinja2 import Environment, PackageLoader, select_autoescape
app = Flask(__name__)


jinja2_env = Environment(
    loader=PackageLoader(__name__, ''),
    autoescape=select_autoescape(['html', 'xml'])
)
template = jinja2_env.get_template('template.html')


def find_page(page):
    pages = [page+'.md', page+'/index.md']
    for filename in pages:
        if os.path.exists(filename):
            return filename
    raise Exception("not found, try %s" % pages)


def read_page(page):
    filename = find_page(page)
    with open(filename) as fd:
        return fd.read()


def get_title(page):
    try:
        return read_page(page).split('\n')[0][1:].strip() or page
    except Exception:
        return page


def replacelink(link, orig):
    path = link[2]
    title = get_title(path)
    pre = link[1]
    post = link[3]

    if path.startswith('http://') or path.startswith('https://'):
        return "%s[%s]%s" % (pre, path, post)

    return "%s[%s](/%s)%s" % (pre, title, path, post)


link_re = re.compile(r'([^\)])\[(.*?)\]([^\(])')


def breadcrumbs(url):
    current = []
    for p in url.split('/'):
        current.append(p)
        yield {"url": '/' + '/'.join(current), "label": p}


def sideindex(page):
    path = find_page(page)
    path = ('/'.join(path.split('/')[:-1]))
    if path:
        path += '/'
    for f in os.listdir('./%s' % path):
        if os.path.isdir("./%s%s" % (path, f)):
            p = "%s%s" % (path, f)
            yield {"url": '/%s' % p, "label": get_title(p)}
        if f.endswith('index.md'):
            continue
        if f.endswith('.md'):
            p = "%s%s" % (path, f[:-3])
            yield {"url": '/%s' % p, "label": get_title(p)}


def render_page(page):
    print(page)
    pagedata = read_page(page)
    pagedata = link_re.sub(lambda x: replacelink(x, page), pagedata)

    md = markdown.markdown(pagedata)

    return template.render({
        "page": page,
        "title": get_title(page),
        "body": md,
        "breadcrumbs": breadcrumbs(page),
        "index": sideindex(page),
    })


@app.route('/favicon.ico')
def favicon():
    return ""


@app.route('/')
def index():
    return render_page('index')


@app.route('/<path:path>')
def page(path):
    print(path)
    return render_page(path)


if __name__ == "__main__":
    app.run()
