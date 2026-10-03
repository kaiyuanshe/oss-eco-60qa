# 开源生态60问

《解码开源：开源生态60问》阅读网站与带来源问答。原书作者：庄表伟。

正式入口：https://oss-eco-60qa.netlify.app/
思维导图：https://mapify.so/share-link/3X7HCA3OGN

## 目录

- `web/`：2026-10-03已部署的简繁静态网页，包含60问正文和图表。
- `dify/workflow.yml`：用户2026-10-03导出的最新工作流；`nodes/`和`prompts/`是其中代码与提示词的可读副本。
- `full-library/`：网站正文结构数据、60问Markdown与图表。
- `output/opensource60-clean/`：问答使用的550个清洗片段、导入文本与页码映射。
- `full-work/`：历史正文/图表提取与网站导出脚本。
- `project_sources/`：用户提供的原书PDF和思维导图图片。
- `output/20261003-json-citation-fix/`：当前校验节点回归测试与必要样例。

## 部署

将`web`文件夹上传到现有Netlify项目`oss-eco-60qa`的Deploys页面；必须同时包含index.html和zh-hant.html。无需新建v2项目。

Dify导入workflow.yml后，需自行配置供应商凭据与知识库，并将检索节点绑定到导入knowledge-import.txt的知识库。DSL中的知识库ID属于原工作区，不能假设在另一个工作区可用。网页的问答入口目前连接已发布Gh62GiucZvMTdflH应用；迁移后须修改两页外链和iframe。

## 验证

Python 3环境安装requirements.txt依赖，然后运行：

```sh
python output/20261003-json-citation-fix/test_classification.py
```

48项本地检查及代表性线上题目已通过。原网址已核实接入新版问答。手机反馈：排版、全文阅读、问答三项暂看正常，简繁搜索仍有问题，尚未关闭。此次未完成全部60问语义验收或长期稳定性证明。

## 数据与维护说明

网站正文数据与问答清洗片段来自同一原书，但目前是不同生成产物，
尚未统一为一个自动构建数据管线。历史 `export_site.py` 不直接重建
当前简繁成品；本次发布以 `web/index.html` 和 `web/zh-hant.html`
为准。原书内容、编辑摘要和图示说明的标注保留在网页中。

代码与书籍内容分别适用下方“许可证”章节所说明的许可，
具体范围详见 `LICENSE` 与 `LICENSE-CONTENT.md`。
资料提取、清洗、格式转换或嵌入网页，不改变其适用的许可；
第三方代码、素材及标志遵循各自的授权说明。

账单、凭据与完整聊天／工作区日志不在公开归档范围。

## 许可证

本项目分别对代码和书籍内容采用不同许可证。

### 代码
本项目原创程序代码采用 Apache License 2.0，
详见 LICENSE 文件。第三方代码遵循其原有许可证。

### 书籍内容
经相关权利人授权，《解码开源：开源生态60问》
（庄表伟著）的原文 PDF，以及授权范围内的正文摘录、
内容分块和改编资料，采用 CC BY-NC-SA 4.0。

协议：https://creativecommons.org/licenses/by-nc-sa/4.0/
具体范围、署名及例外详见 LICENSE-CONTENT.md。

网页、Markdown、JSON 和知识库文件中包含的上述书籍内容，
同样适用内容许可，不因文件格式改变而改用代码许可。

### 例外
第三方素材及标志另行标注；
上述许可不授予商标使用权。
