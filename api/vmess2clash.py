from flask import Flask, Response, request, jsonify
from urllib import parse
import base64
import requests
import json
app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def vmess2clash(path):
    def to_json(vmess_content):
        if vmess_content[-2:] != '==' and vmess_content[-1] != '=':
            vmess_content = vmess_content + '=='
        elif vmess_content[-1] == '=' and vmess_content[-2:] != '==':
            vmess_content = vmess_content + '='
        # +(加号)会被替换成空格
        vmess_content = vmess_content.replace(' ', '+')
        vmess = base64.b64decode(vmess_content)
        vmess = vmess.decode('utf-8')
        return json.loads(vmess)

    def to_clash(vmess: dict):
        clash = {
            "name": vmess["ps"],
            "type": "vmess",
            "server": vmess["add"],
            "port": int(vmess["port"]),
            "uuid": vmess["id"],
            "alterId": int(vmess["aid"]),
            "cipher": "auto",
            "network": vmess["net"],
            "ws-path": vmess["path"],
            "tls": True if vmess["tls"] == "tls" else False,
            "ws-headers": {} if "ws-headers" not in vmess else vmess["ws-headers"]
        }
        return clash
    query = parse.parse_qs(parse.urlsplit(request.full_path).query)
    clash = {}
    if "vmess" in query:
        vmess_content = query["vmess"][0].split("vmess://")[-1]
        # length = len(vmess_content)
        # remainder = length % 3
        # if remainder != 0:
        #     vmess_content = vmess_content + "=" * (3 - remainder)
        clash = to_clash(to_json(vmess_content))
    # return clash
    clash = json.dumps(clash, ensure_ascii=False)
    return Response(clash, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
