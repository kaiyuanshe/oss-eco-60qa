# GitHub 提交步骤（Windows）

本包约130个文件，建议使用GitHub Desktop一次提交，避免网页100文件每批的限制。

1. 用GitHub Desktop登录你有仓库管理权限的GitHub账户。密码与验证码只在官方登录界面输入。
2. File → Clone repository，选择kaiyuanshe/oss-eco-60qa，记住本地目录。
3. Fetch origin，并在需要时Pull origin，以获得最新仓库。
4. Current branch → New branch，新建release-20261003。
5. 将本包oss-eco-60qa文件夹里面的内容复制到刚克隆的仓库目录。不要把外层同名文件夹整体套进去；不要删除现有LICENSE或其他已有文件。若同名README或配置文件已存在，先对照，保留原有说明与配置，并合并本次内容。
6. 在Changes中检查变更。提交说明可用：Archive published website and Dify workflow (2026-10-03)。
7. Commit to release-20261003 → Publish branch（若已发布过则Push origin）→ Create Pull Request。
8. 在GitHub检查PR文件清单与差异后，再合并到默认分支。

本包没有完成远程仓库读取或既有文件合并；管理员身份不自动授予本助手仓库访问。不能把复制覆盖当作已完成审校。若要助手协助处理现有文件合并，需要提供仓库内容或连接GitHub。

网页可使用Add file → Upload files分批上传，每批最多100个文件、每个文件不超过25 MiB。上传解压后的源码文件，而不是仅上传整个ZIP。
