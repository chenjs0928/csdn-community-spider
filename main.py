import base64
import hmac
from hashlib import sha256
from urllib.parse import urlparse, urlencode, unquote

import requests


def url_params_dict_to_str(params, doseq=True, is_unquote=True):
    """
    将一个字典类型的参数转换成查询字符串
    :param params:
    :param is_unquote: 是否需要解码
    :param doseq: 如果doseq为True，则将多个值的查询字符串合并到一个参数中，否则每个值都分别转换为独立的参数
    :return:
    """
    params_str = urlencode(params, doseq=doseq)
    if is_unquote:
        params_str = unquote(params_str)
    return params_str


def get_url_path(url):
    """
    获取请求路径
    :param url: 完整的请求URL
    :return:
    """
    return urlparse(url).path


def get_signature(key, data):
    """
    使用HmacSHA256并用base64加密
    :param key:
    :param data:
    :return:
    """
    key = key.encode('utf-8')
    data = data.encode('utf-8')
    signature = base64.b64encode(hmac.new(key, data, digestmod=sha256).digest())
    signature = str(signature, 'utf-8')
    return signature


def get_signature_data(url, params, headers, request_method="GET"):
    """
    获取需要加密的数据
    :param url: 请求的URL
    :param params: 查询字符串
    :param headers: 请求头
    :param request_method: 请求方法,默认是GET
    :return:
    """
    accept = headers['accept']
    x_ca_key = "x-ca-key:" + headers['x-ca-key']
    x_ca_nonce = headers.get('x-ca-nonce') if headers.get('x-ca-nonce') else ''
    x_ca_nonce = "x-ca-nonce:" + x_ca_nonce
    url_path = get_url_path(url)
    params_str = url_params_dict_to_str(params)

    return f"{request_method}\n{accept}\n\n\n\n{x_ca_key}\n{x_ca_nonce}\n{url_path}?{params_str}"


def get_page_community_data(page, r_type):
    """
    获取CSDN社区数据
    :param page: 页数
    :param r_type: 类型, 1:最新发布, 2:最新回复, 3:有活动, 4:有红包, 5:最热, 6:与我相关
    :return:
    """
    headers = {
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'x-ca-key': '203899271',
        'x-ca-signature': '',
        'x-ca-signature-headers': 'x-ca-key,x-ca-nonce',
    }
    url = "https://bizapi.csdn.net/community-cloud/v1/new/home/recent"
    key = "bK9jk5dBEtjauy6gXL7vZCPJ1fOy076H"
    params = {
        'pageNum': page,
        'type': r_type,
    }
    signature_data = get_signature_data(url, params, headers)
    headers['x-ca-signature'] = get_signature(key, signature_data)
    res = requests.get(url, params=params, headers=headers)
    return res.json()


res_data = get_page_community_data(21, 1)
print(res_data)
print(res_data['data'])
print(len(res_data['data']['list']))
for item in res_data['data']['list']:
    communityName = item.get('communityName')
    topicTitle = item.get('content').get('topicTitle')
    print("communityName:" + communityName)
    print("topicTitle:" + topicTitle)
