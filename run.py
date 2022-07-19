import requests
from PyPDF2 import PdfFileReader
import io
import yaml
import time
from bs4 import BeautifulSoup
import requests
import base64
import os

def get_bibtex(title):
    time.sleep(1)
    text = requests.get('https://sc.panda321.com/scholar?hl=zh-CN&as_sdt=0%2C5&q='+title,verify=False).text
    soup = BeautifulSoup(text,'lxml')
    id = soup.find_all(class_='gs_r gs_or gs_scl')[0]['data-did']
    time.sleep(1)
    text = requests.get('https://sc.panda321.com/scholar.bib?q=info:{}:scholar.google.com/&output=cite'.format(id),verify=False).text
    soup = BeautifulSoup(text,'lxml')
    link = soup.find_all('a',class_='gs_citi')[0]['href']
    time.sleep(1)
    bib = requests.get(link,verify=False).text
    with open(title+'.bib','w',encoding='UTF-8') as f:
        f.write(bib)
def handle_one(article):
    url,desc = article['u'],article['d']
    tras = article.get('t', 0) 
    bib = article.get('b', 1) 
    content = requests.get(url).content
    # https://stackoverflow.com/questions/38678377/python-3-parse-pdf-from-web
    pdf = PdfFileReader(io.BytesIO(content))
    information = pdf.getDocumentInfo()
    title0 = information.title
    title = article.get('n',title0)
    with open('template.md','r',encoding='UTF-8') as f:
        template = f.read()
        t_s = template.split('{{description}}')
    with open('{}.pdf'.format(title),'wb') as f:
        f.write(content)
    with open('{}.md'.format(title),'w',encoding='UTF-8') as f:
        f.write('---\nfrom: {}\ntitle: {}\n---\n\n{}{}{}'.format(url,title,t_s[0],desc,t_s[1]))
    if bib: get_bibtex(title)
    if tras: translate(title)
def translate(title):
    ## 获取 token
    with open('config.yaml','r',encoding='UTF-8') as f:
        s = yaml.load(f.read(), Loader=yaml.SafeLoader)
        try:
            api_key = s['API Key']
            secret_key = s['Secret Key']
        except: print('API信息缺失')
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(api_key,secret_key)
    response = requests.get(host)
    if response:
        token = response.json()['access_token']
    else:
        print('百度API认证失败')
        return 0

    ## 读取文档
    filepath = '{}.pdf'.format(title)
    with open(filepath, 'rb') as f1:
        b64 = base64.b64encode(f1.read())

    ## 调用接口，输入任务
    url = 'https://aip.baidubce.com/rpc/2.0/mt/v2/doc-translation/create?access_token=' + token
    # Build request
    headers = {'Content-Type': 'application/json'}
    # payload = {
    # "from": "en",
    # "to": "zh",
    # "input": {
    #     "content": b64,
    #     "format": "pdf",
    #     # "filename": "{}.pdf".format(title)
    #     "filename": "upload.pdf"
    # },
    # "output": {
    #     "filename_prefix": "trans",
    #     "formats": ["pdf"]
    # }
    # }
    headers = {'Content-Type': 'application/json'}
    payload = {
    "from": "en",
    "to": "zh",
    "input": {
        "content": "SSB3YW50IHRvIHBsYXkgYmFsbA==",
        "format": "txt",
        "filename": "mttest.txt"
    },
    "output": {
        "filename_prefix": "mttest_after",
        "formats": [
        "txt"
        ]
    }
    }
    # Send request
    r = requests.post(url, params=payload, headers=headers)
    print(r.json())
    task_id = r.json()['result']['id']

    ## 请求返回值
    url = 'https://aip.baidubce.com/rpc/2.0/mt/v2/doc-translation/query?access_token=' + token

    headers = {'Content-Type': 'application/json'}
    payload = {
    "id": task_id
    }
    ## 循环获取任务信息
    while True:
        time.sleep(5)
        # Send request
        r = requests.post(url, params=payload, headers=headers)
        status = r.json()['result']['data']['status']
        if status=='Succeeded':
            print('文档翻译成功')
            link = r.json()['result']['data']['output']['files'][0]['url']
            content = requests.get(link).content
            with open('{}_trans.pdf'.format(title),'wb') as f:
                f.write(content)
            break
        if status=='Failed':
            print('文档翻译失败')
            break
def handle_temp():
    with open('temp.yaml','r',encoding='UTF-8') as f:
        s = yaml.load(f.read(), Loader=yaml.SafeLoader)
        for article in s:
            handle_one(article)


if os.path.exists('temp.yaml'): 
    print('信息获取成功，解析中')
    handle_temp()
    os.remove('temp.yaml')
else: 
    open('temp.yaml','x')
    print('请将需要下载的文档信息写入 temp.yaml')
    

# translate('A Tail-Index Analysis of Stochastic Gradient Noise in Deep Neural Networks')