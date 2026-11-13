# 仓库下载实施计划

目标：第 15 项提供统一仓库入口，选择发布包、源码 ZIP 或 Git 克隆，保留原有软件查找流程。个人清单顺延至 16。

采用现有 Python requests 和 Git CLI，不增加运行依赖。

- [x] tools/download_engine.py：8 条候选线路、实际目标限量测速、分段并发、同线路强验证续传、换线重新下载、摘要校验和原子完成。
- [x] tools/repository_download.py：严格解析仓库短地址和完整地址，解析带斜杠的 ref，源码固定 commit，Release 附件选择，Git 完整/浅克隆及子模块/LFS 设置，任务记录和完成操作。
- [x] lookup_app.py、语言表和打包脚本接线，提供非交互 CLI；dry-run 不联网、不写文件。
- [x] 本地 HTTP 集成测试覆盖 Range/200/416/中断续传/资源变化/损坏摘要/中文路径；仓库解析、菜单、Git 和现有回归测试。
- [x] 更新中英文说明，记录公网验证结果和限制。

边界：公开 GitHub 仓库；Git 使用本机凭据和官方远程，不向第三方转发认证。源码 ZIP 不含 Git 历史。候选线路运行时检测，不承诺全部可用。没有官方摘要时只做传输和压缩包完整性检查。

## 验证结果（2026-11-08）

- 完整测试 79 项通过，含新增 18 项；本地 HTTP 测试实际下载 5 MiB 数据并核对摘要。
- GitHub octocat/Hello-World：源码直连下载、中文路径解压、自动测速选线下载、Git 浅克隆及 clean-worktree 更新均真实通过。
- GitHub cli/cli：真实下载 Release 校验清单附件，官方 SHA256 验证通过。
- 8 条候选线路实际探测：本机当次 direct、gh-proxy.com、ghfast.top 成功；其他候选出现超时、403、TLS 或 DNS 错误，已显示并自动跳过。该结果仅代表当次网络环境。
- Windows lookup_app.exe 已重建并复制到根目录；真实源码下载、ZIP 检查和解压成功。
- 修改文件按 CRLF 兼容规则执行 diff whitespace 检查通过；中文路径和 README UTF-8/UTF-16/GB18030 读取均有对应处理。
- 未运行项目代码、安装依赖或提交/发布版本。
