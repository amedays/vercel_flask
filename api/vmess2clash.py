from flask import Flask, Response, request, jsonify
from urllib import parse
import base64
import requests
app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def vmess2clash(path):
    query = parse.parse_qs(parse.urlsplit(request.full_path).query)
    clash = {}
    if "vmess" in query:
        vmess_content = query["vmess"][0].split("vmess://")[-1]
        # length = len(vmess_content)
        # remainder = length % 3
        # if remainder != 0:
        #     vmess_content = vmess_content + "=" * (3 - remainder)
        if vmess_content[-2:] != '==' and vmess_content[-1] != '=':
            vmess_content = vmess_content + '=='
        elif vmess_content[-1] == '=' and vmess_content[-2:] != '==':
            vmess_content = vmess_content + '='
        # +(加号)会被替换成空格
        vmess_content = vmess_content.replace(' ', '+')
        clash = base64.b64decode(vmess_content)
        clash = clash.decode('utf-8')
    # return clash
    return Response(clash, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
