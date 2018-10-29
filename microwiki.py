#!/usr/bin/python3
from flask import Flask
import os
import markdown
import re
from jinja2 import Environment, PackageLoader, select_autoescape
app = Flask(__name__)


print(os.path.dirname(__file__))
jinja2_env = Environment(
    loader=PackageLoader(__name__, ''),
    autoescape=select_autoescape(['html', 'xml'])
)
template = jinja2_env.get_template('template.html')


@app.route('/favicon.ico')
def favicon():
    return ""


@app.route('/')
def index():
    return page('index')


def find_page(page):
    if '..' in page:
        raise Exception("Access denied")
    pages = [page+'.md', page+'/index.md']
    for filename in pages:
        if os.path.exists(filename):
            with open(filename) as fd:
                return fd.read()
    raise Exception("not found, try %s" % pages)


def get_title(page):
    try:
        return find_page(page).split('\n')[0][1:].strip()
    except Exception:
        return page


def dirindex(page):
    md = ""
    path = page
    if page.endswith('index'):
        path = page[:-5]
    path = path or '.'
    path += '/'
    for f in os.listdir(path):
        if os.path.isdir(f):
            md += "* [%s%s]\n" % (path, f)
        if f.endswith('index.md'):
            continue
        if f.endswith('.md'):
            md += "* [%s%s]\n" % (path, f[:-3])

    return md


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


def render_page(page):
    pagedata = find_page(page)

    if '[[index]]' in pagedata:
        pagedata = pagedata.replace('[[index]]', dirindex(page))

    pagedata = link_re.sub(lambda x: replacelink(x, page), pagedata)

    md = markdown.markdown(pagedata)

    return template.render({
        "page": page,
        "title": get_title(page),
        "body": md,
        "breadcrumbs": breadcrumbs(page)
    })


@app.route('/<path:path>')
def page(path):
    return render_page(path)
