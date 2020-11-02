from flask import Flask, Response, request
from urllib import parse
import requests
from xml.dom import minidom as DOM
app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def date(path):
    class Item():
        '''能够根据指定属性判断item重复'''

        def __init__(self, node, diff="guid"):
            self._node = node
            self.diff = diff
            diff = self._node.getElementsByTagName(self.diff)
            if diff:
                diff = diff[0]
                for node in diff.childNodes:
                    if node.nodeName == "#text":
                        diff = node
                        break
                if diff:
                    self.id = diff.data

        def __eq__(self, other):
            return self.id == other.id

    def get_rss_xml(url: str):
        ''':param url: rss url\n
        :return: xml string'''
        res = requests.get(url)
        return res.text

    def get_dom(xml: str):
        tree = DOM.parseString(xml)
        return tree

    def get_items_from_xml(tree):
        ''':param xml: xml string\n
        :return: items list'''
        root = tree.documentElement
        channel = root.getElementsByTagName("channel")
        if channel:
            channel = channel[0]
            items = channel.getElementsByTagName("item")
        return items if items else None

    query = parse.parse_qs(parse.urlsplit(request.full_path).query)
    items = []
    first = None
    # 获取模板rss与items
    if "rss" in query:
        urls = query["rss"]
        first = get_dom(get_rss_xml(urls[0]))
        items = [item for item in get_items_from_xml(first)]
        items_first = items.copy()
        items = [Item(item) for item in items]
        for url in urls[1:]:
            xml = get_rss_xml(url)
            tree = get_dom(xml)
            tree_item = get_items_from_xml(tree)
            for item in tree_item:
                item = Item(item)
                if item not in items:
                    items.append(item)
    if items:
        items = [item._node for item in items]
        root = first.documentElement
        channel = root.getElementsByTagName("channel")
        if channel:
            channel = channel[0]
            for item in items_first:
                channel.removeChild(item)
            for item in items:
                channel.appendChild(item)
    res = first.toprettyxml(encoding="utf-8") if first else None
    return Response(res, mimetype='application/xml')


if __name__ == '__main__':
    app.run(debug=True)
