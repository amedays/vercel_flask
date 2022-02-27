from flask import Flask, Response, request
from urllib import parse
import requests
from xml.dom import minidom as DOM
import re
app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def rss(path):
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
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'})
        return res.text
 
    def get_dom(xml: str):
        tree = DOM.parseString(xml)
        return tree

    def get_items_from_xml(tree):
        ''':param xml: xml string\n
        :return: items list'''
        items = []
        root = tree.documentElement
        channel = root.getElementsByTagName("channel")
        if channel:
            channel = channel[0]
            items = channel.getElementsByTagName("item")
        return items if items else []

    def concat_param(param: str):
        return "?{}=".format(param)

    params = ["rss"]
    params = [concat_param(param) for param in params]
    query = "?" + parse.urlsplit(request.full_path).query
    results = re.findall("\?.*?=", query)
    n = 0
    for i in range(0, len(results)):
        if results[i - n] not in params:
            del results[i - n]
            n += 1
    first = None
    i = 0
    query_dict = {}
    while not i + 1 >= len(results):
        # 依次查找
        query = re.sub("\\" + results[i], "", query, 1)
        tail = results[i + 1]
        pattern = "^.*?\{}".format(tail)
        value = re.search(pattern, query).group(0)
        value = re.sub("\\" + tail, "", value)
        if not tail[1:-1] in query_dict:
            query_dict[tail[1:-1]] = value
        elif isinstance(list, query_dict[tail[1:-1]]):
            query_dict[tail[1:-1]] = query_dict[tail[1:-1]].append(value)
        else:
            query_dict[tail[1:-1]] = [query_dict[tail[1:-1]], value]
        query = query[len(value):]
        i += 1
    query_dict[results[-1]] = re.sub("\\" + results[-1], "", query, 1)
    # 获取模板rss与items
    if "type" in query:
        # TODO: 为实现多种可能,应该使用抽象类实现转化的过程
        pass
    if "rss" in query:
        # TODO: 允许带有参数的链接(不使用库而直接使用'?rss='分割request.full_path,建立list存储?{}=格式从而分割预定的参数)
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
