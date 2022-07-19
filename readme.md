# bibcat

一个辅助文献管理的小工具

- 输入标题，下载链接和描述，自动下载文件，生成引用，生成笔记
- （开发中）自动翻译文档，输入标题，自动从谷歌学术、Scihub下载。

## 使用教程

安装依赖：

```powershell
pip install -r requirements.txt
```

运行`run.py`，

```
python3 run.py
```

在当前目录生成`temp.yaml`，按照`exmaple_temp.yaml`格式写入文献信息。

再次运行`run.py`，

```
python3 run.py
```

即可

### 开启百度翻译功能

开发中

### 自定义笔记格式

修改`template.md`，其中`{{description}}`将以笔记描述替代。