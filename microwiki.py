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
    dn = os.path.dirname(page) or '.'
    for f in os.listdir(dn):
        if os.path.isdir(f):
            f = f+'/index.md'
        if f.endswith('.md'):
            md += "* [%s]\n" % (f[:-3])

    return md


def replacelink(link, orig):
    path = link[2]
    title = get_title(os.path.join(os.path.dirname(orig), path))
    pre = link[1]

    return "%s[%s](%s)" % (pre, title, path)


link_re = re.compile(r'([^\)])\[(.*?)\]')


def render_page(page):
    pagedata = find_page(page)

    if '[[index]]' in pagedata:
        pagedata = pagedata.replace('[[index]]', dirindex(page))

    pagedata = link_re.sub(lambda x: replacelink(x, page), pagedata)

    md = markdown.markdown(pagedata)

    return template.render({
        "page": page,
        "title": get_title(page),
        "body": md
    })


@app.route('/<path:path>')
def page(path):
    return render_page(path)
