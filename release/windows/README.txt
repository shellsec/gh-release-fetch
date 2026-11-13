GH Release Fetch — Windows 便携版（两个 EXE，无需安装 Python）
================================================================

解压到任意目录（路径尽量不含特殊字符），保持本文件夹结构不变。

日常用法（双击 bat，无参数时会提示输入关键词）
------------------------------------------------
  lookup_app.bat          按平台搜软件；菜单 15 获取仓库和 Chrome 扩展，16 管理个人清单，17/18 搜资讯和游戏
  lookup_mobile.bat       搜 Android APK（GitHub 包可下载；闭源打开商店页）
  lookup_ios.bat          搜 iOS 软件（打开 App Store 商店页）
  lookup_switch.bat       搜 Switch 自制工具
  lookup_ps5.bat          搜 PS5 自制工具
  open_catalog.bat        打开支持网页批量下载的本地分类目录
  search_soft_pages.bat   搜工具/频道介绍页标题（只打开网页）
  search_games.bat        搜 gamer520 游戏页（本地近期列表；无匹配时自动站内搜索，PC/Switch 混排）
  run_saved_apps.bat      按 saved_apps_windows.json 批量更新

lookup_app.exe 是主程序，auto_update.exe 是下载器。各快捷 BAT 会调用其中一个。

启动与排错
----------
  - 请完整解压后运行，保留 apps、tools 等目录；日常主入口是 lookup_app.bat / lookup_app.exe。
  - EXE 使用内置模块，同目录遗留的旧版 tools/*.py 不再覆盖程序代码。
  - 便携包内 BAT 会直接调用 EXE，不会因为电脑装过 Python 就误找缺失的源码。
  - run_saved_apps 需要先保存更新列表；auto_update 只更新已启用或明确指定的应用。
  - 直接双击 EXE 遇到错误时，窗口会保留错误信息，按回车关闭；命令行调用不等待。
  - 意外异常会写入 startup_error.log；常规下载日志是 update_log.txt。目录不可写时仍显示控制台错误。

首次建议
--------
  1. lookup_app.bat drawio  试搜，选中后按回车加入清单并下载。1 仅下载一次，3 只加入。
  2. 已经下载过的工具可在「个人更新清单」按 i，从 update_log.txt 选择导入，a 全选。
  3. 在「个人更新清单」按 a 批量下载全部，或按序号查看某份清单并下载或移除条目。
     命令行也可运行 run_saved_apps.bat --manage。
  4. 批量文件按平台保存到 batch_downloads 下的本次目录，完成后统一打开总目录。
     批量只下载。安装包手动运行，便携压缩包手动解压替换。失败详情见 update_log.txt。

网页批量下载
------------
  1. 双击 open_catalog.bat，并保持启动窗口开启。
  2. 在浏览器里切换平台和用途，勾选所需条目，点击「批量下载」。
  3. 网页显示下载日志与结果。附件保存到 catalog_downloads 下的对应平台目录，
     Chrome 原版 CRX 保存到 catalog_downloads/chrome。页面条目打开官方入口。

文件说明
--------
  catalog.html            分类展示页（open_catalog.bat 打开）
  CHANGELOG.md            版本变更及各平台新增项目
  apps/                   桌面清单（Windows/macOS/Linux JSON，脚本按平台读取）
  apps-mobile/            移动清单（Android APK 下载 / iOS 占位）
  tools/soft_page_check/  search_soft_pages 的标题索引（history、list）
  auto_update.exe         下载引擎（lookup 选 1/2 时会调用）
  lookup_app.exe          软件目录、个人清单、软件资讯、游戏页面搜索和网页批量下载
  update_log.txt          运行后生成于本目录

说明
----
  - 本包不含 Python；维护脚本（monthly_check 等）请使用完整 Git 仓库。
  - 个人列表 saved_apps_windows.json 可在本目录新建，勿覆盖他人配置。
  - 单个下载时，exe/msi 是否运行取决于条目配置，7z/zip 会打开所在目录并选中文件。
  - 项目：https://github.com/shellsec/gh-release-fetch

自定义：主菜单选择 自定义清单，可添加仓库/直链、管理、批量导入导出、撤销与设置偏好。
也可运行 lookup_app.bat --custom；确认预览后保存，安装包不会自动运行。
