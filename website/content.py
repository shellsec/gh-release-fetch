"""Editorial content. Platform lists are intentional, not inferred from sibling shards."""

PLATFORMS = {
    'windows': ('Windows', '适合新电脑的日常工具，从解压、截图到办公和备份。', '电脑'),
    'darwin': ('macOS', '为 Mac 补齐日常所需，获取前请确认 Apple Silicon 或 Intel。', '电脑'),
    'linux': ('Linux', '办公、开发与桌面工具。请按发行版选择官方支持的安装方式。', '电脑'),
    'android': ('Android', '文件互传、阅读、笔记与开源应用，按需要丰富你的手机。', '手机与平板'),
    'ios': ('iPhone / iPad', '通过官方商店获取工具，留意商店地区、系统要求与 iPad 适配。', '手机与平板'),
    'android_tv': ('Android TV', '为大屏与遥控操作选择应用，安装前确认电视适配。', '电视与游戏设备'),
    'linux_handheld': ('Linux 掌机', '掌机扩展、游戏串流与设备工具，先阅读各项目的安装条件。', '电视与游戏设备'),
    'switch': ('Switch', '设备工具与项目资料，使用前核对机型、系统和项目说明。', '电视与游戏设备'),
    'ps4': ('PS4', '设备配套项目与资料入口，兼容性以项目说明为准。', '电视与游戏设备'),
    'ps5': ('PS5', '设备工具与社区项目，获取前核对系统版本和前置条件。', '电视与游戏设备'),
    'vita': ('PS Vita', '文件管理与设备项目，按官方项目说明确认适用条件。', '电视与游戏设备'),
    'xbox': ('Xbox', '不同代际 Xbox 的设备工具，使用前确认具体硬件型号。', '电视与游戏设备'),
}

# id, title, description, symbol, legacy categories, search terms
CATEGORIES = [
    ('browser', '浏览器与上网', '浏览网页、整理书签，找到习惯的上网方式。', '◎', ['浏览器'], '上网 浏览器 网页 书签'),
    ('files', '文件与解压', '解压安装包、查找文件，把资料整理得井井有条。', '▣', ['文件管理', '压缩'], '解压 压缩 文件 搜索 查找'),
    ('transfer', '下载与传输', '下载大文件，在手机和电脑之间轻松互传。', '⇄', ['下载', '局域网文件共享'], '下载 互传 传照片 传文件 局域网'),
    ('office', '办公与 PDF', '处理文档、表格、演示和 PDF，完成每天的工作。', '▤', ['办公', '办公与设计'], '办公 文档 表格 演示 pdf'),
    ('notes', '笔记与写作', '记下灵感、整理知识，让下一次查找更容易。', '✎', ['笔记', '写作'], '笔记 写作 知识库 markdown'),
    ('capture', '截图与录屏', '截图标注、录制教程，清楚表达屏幕上的内容。', '▧', ['截图'], '截图 录屏 录课 直播 标注'),
    ('design', '图片与设计', '修照片、画插画、做矢量图和流程图。', '◇', ['设计', '多媒体与设计'], '修图 绘画 图片 设计 流程图'),
    ('media', '影音与阅读', '播放影音、管理媒体库，读完一本好书。', '▷', ['多媒体', '音视频', '阅读'], '播放器 视频 音乐 阅读 电子书'),
    ('editing', '剪辑与转码', '剪视频、编辑音频，转换和压缩媒体文件。', '✂', ['剪辑'], '剪辑 转码 音频 压缩视频'),
    ('backup', '备份与同步', '备份重要资料，让多台设备的文件保持一致。', '↻', ['备份'], '备份 同步 恢复 存档'),
    ('security', '密码与安全', '管理密码、检查文件，照顾好自己的数据。', '♧', ['安全'], '密码 安全 密码库 加密'),
    ('remote', '远程与协作', '远程协助另一台电脑，让手机与电脑协同工作。', '⌘', ['远程与协作', '网络与协作', '网络与通讯'], '远程 协作 控制 手机电脑'),
    ('system', '系统与效率', '管理窗口、剪贴板与磁盘，减少重复操作。', '⊞', ['系统', '效率', '工具'], '系统 效率 窗口 清理 剪贴板'),
    ('ai', 'AI 工具', '对话、辅助编程与本地模型，按任务和硬件选择。', '✳', ['AI'], 'ai 人工智能 对话 大模型 编程'),
    ('development', '开发工具', '从编辑器、终端到版本管理，搭建开发环境。', '⌨', ['开发', '命令行', '终端', '编辑器'], '开发 代码 编程 git 终端 编辑器'),
    ('data', '数据与运维', '管理数据库、容器和服务，观察系统运行状态。', '▥', ['数据库', '云原生', '可观测'], '数据库 容器 运维 监控'),
    ('gaming', '游戏与设备', '发现游戏启动、串流与设备配套工具。', '♙', ['游戏', '系统工具'], '游戏 掌机 串流 控制器'),
    ('more', '更多工具', '网络进阶、专业用途与其他收录工具。', '⋯', [], '网络 专业 工具'),
]

DESKTOP = ['windows', 'darwin', 'linux']
ALL = DESKTOP + ['android', 'ios']

def tool(id, name, category, summary, reason, url, platforms, *, audience='日常使用', aliases=(), repo='', note=''):
    return dict(id=id, name=name, category=category, summary=summary, reason=reason,
                url=url, supported=platforms, audience=audience, aliases=list(aliases), repo=repo, note=note)

FEATURED = [
    tool('localsend', 'LocalSend', 'transfer', '把照片、视频和文件传到附近的手机或电脑。', '覆盖常见电脑与手机平台，适合同一局域网内互传。', 'https://localsend.org/', ALL, aliases=['传照片', '手机电脑互传', '本地发送', 'localsend_ios'], repo='localsend/localsend', note='双方需安装应用并连接可互通的局域网。'),
    tool('7zip', '7-Zip', 'files', '压缩与解压常见格式的文件。', '解压用途明确，适合作为 Windows 常用工具。', 'https://www.7-zip.org/', ['windows'], aliases=['解压', '压缩', '7z'], repo='ip7z/7zip'),
    tool('libreoffice', 'LibreOffice', 'office', '编辑文档、电子表格和演示文稿。', '一个套件覆盖常见桌面办公任务。', 'https://www.libreoffice.org/download/', DESKTOP, aliases=['office', '文档', '表格'], note='复杂 Office 文档请先检查排版与宏兼容性。'),
    tool('vlc', 'VLC', 'media', '播放本地视频、音乐和网络媒体。', '常见平台都有官方入口，适合日常影音播放。', 'https://www.videolan.org/vlc/', ALL, aliases=['播放器', 'vlc_android', 'vlc_ios']),
    tool('keepassxc', 'KeePassXC', 'security', '用本地密码库保存和管理账号密码。', '适合希望自己保管密码库的电脑用户。', 'https://keepassxc.org/download/', DESKTOP, aliases=['密码管理', '密码库'], repo='keepassxreboot/keepassxc', note='请妥善保存主密码并备份密码库。'),
    tool('obs', 'OBS Studio', 'capture', '录制屏幕、制作课程和进行直播。', '支持多场景与音频控制，适合较完整的录制工作。', 'https://obsproject.com/', DESKTOP, aliases=['obs studio', '录屏', '直播', '录课'], repo='obsproject/obs-studio', audience='录课与直播'),
    tool('firefox', 'Firefox', 'browser', '浏览网页，使用标签、书签和扩展。', '为电脑与手机提供一致的浏览器选择。', 'https://www.mozilla.org/firefox/browsers/', ALL, aliases=['火狐', 'firefox_ios']),
    tool('joplin', 'Joplin', 'notes', '整理笔记、待办和 Markdown 文档。', '适合需要跨设备整理文字与附件的人。', 'https://joplinapp.org/', ALL, aliases=['笔记', 'joplin_ios'], repo='laurent22/joplin', note='同步需自行选择并配置服务。'),
    tool('rustdesk', 'RustDesk', 'remote', '远程访问电脑，协助处理另一台设备的问题。', '提供远程桌面和自建服务选项。', 'https://rustdesk.com/', ALL, aliases=['远程控制', 'rustdesk_ios'], repo='rustdesk/rustdesk', note='各平台控制能力不同，iOS 不支持作为普通被控桌面。'),
    tool('gopeed', 'Gopeed', 'transfer', '集中管理常见协议的下载任务。', '适合需要独立下载管理界面的用户。', 'https://gopeed.com/', DESKTOP + ['android'], aliases=['下载器'], repo='GopeedLab/gopeed'),
    tool('drawio', 'draw.io', 'design', '画流程图、架构图和思维导图。', '适合把工作流程与技术结构画清楚。', 'https://www.drawio.com/', DESKTOP, aliases=['流程图', 'diagrams', '架构图'], repo='jgraph/drawio-desktop'),
    tool('pixpin', 'PixPin', 'capture', '截图、标注和固定屏幕上的参考内容。', '适合经常截图沟通、整理屏幕资料的人。', 'https://pixpin.cn/', ['windows', 'darwin'], aliases=['截图', '贴图', '长截图']),
    tool('powertoys', 'PowerToys', 'system', '管理窗口、快捷启动和日常系统操作。', '把多种 Windows 效率功能集中到一个工具中。', 'https://learn.microsoft.com/windows/powertoys/', ['windows'], aliases=['微软工具箱', '窗口管理'], repo='microsoft/PowerToys'),
    tool('obsidian', 'Obsidian', 'notes', '用本地 Markdown 文件组织个人知识库。', '适合重视双向链接和本地文档的人。', 'https://obsidian.md/download', ALL, aliases=['双链笔记', 'obsidian_ios'], note='同步、发布等附加服务的费用以官网为准。'),
    tool('bitwarden', 'Bitwarden', 'security', '跨设备保存和自动填充账号密码。', '适合需要手机与电脑共同使用密码管理的人。', 'https://bitwarden.com/download/', ALL, aliases=['bitwarden_desktop', 'bitwarden_android', 'bitwarden_ios', '密码'], note='服务、订阅和自托管选项请查看官方说明。'),
    tool('syncthing', 'Syncthing', 'backup', '在自己的电脑之间同步文件夹。', '适合管理多台电脑上的工作资料。', 'https://syncthing.net/', DESKTOP, aliases=['文件同步'], repo='syncthing/syncthing', note='同步不等于独立备份，删除操作也可能传播。'),
    tool('kdeconnect', 'KDE Connect', 'remote', '连接手机和电脑，分享文件与设备操作。', '适合希望手机电脑联动的用户。', 'https://kdeconnect.kde.org/', ['windows', 'darwin', 'linux', 'android', 'ios'], aliases=['设备互联', 'kde connect'], note='通知、剪贴板等能力取决于平台与权限。'),
    tool('gimp', 'GIMP', 'design', '编辑照片、合成图片和处理图像。', '适合需要多图层图像编辑的用户。', 'https://www.gimp.org/downloads/', DESKTOP, aliases=['修图', '图片处理']),
    tool('krita', 'Krita', 'design', '绘制插画、概念图和数字作品。', '围绕画笔和绘画工作流组织功能。', 'https://krita.org/en/download/', DESKTOP, aliases=['绘画', '插画']),
    tool('inkscape', 'Inkscape', 'design', '绘制和编辑 SVG 矢量图。', '适合图标、示意图和可缩放图形制作。', 'https://inkscape.org/release/', DESKTOP, aliases=['矢量', 'svg']),
    tool('handbrake', 'HandBrake', 'editing', '转换视频格式，调整尺寸和文件大小。', '适合处理视频兼容性与存储空间。', 'https://handbrake.fr/downloads.php', DESKTOP, aliases=['视频压缩', '转码']),
    tool('shotcut', 'Shotcut', 'editing', '剪辑视频、排列片段并添加基础效果。', '适合从时间线剪辑开始制作视频。', 'https://shotcut.org/download/', DESKTOP, aliases=['视频剪辑']),
    tool('audacity', 'Audacity', 'editing', '录制、剪切和编辑音频。', '适合配音、录音整理和基础音频处理。', 'https://www.audacityteam.org/download/', DESKTOP, aliases=['录音', '音频剪辑']),
    tool('calibre', 'calibre', 'media', '管理电子书，整理书库和转换格式。', '适合有较多本地电子书的读者。', 'https://calibre-ebook.com/download', DESKTOP, aliases=['电子书', '书库']),
    tool('vscode', 'Visual Studio Code', 'development', '编写代码，配合扩展调试和管理项目。', '适合多种语言与项目的日常开发。', 'https://code.visualstudio.com/download', DESKTOP, aliases=['vsc', '代码', '编辑器']),
    tool('git', 'Git', 'development', '记录代码变更，管理项目版本。', '为开发项目建立可回溯的版本历史。', 'https://git-scm.com/downloads', DESKTOP, aliases=['git_windows', 'git_for_windows', '版本管理'], audience='开发者'),
    tool('github_desktop', 'GitHub Desktop', 'development', '通过图形界面提交代码和查看变更。', '适合从可视化界面开始学习 Git 工作流。', 'https://desktop.github.com/download/', ['windows', 'darwin'], aliases=['git 图形界面']),
    tool('github_cli', 'GitHub CLI', 'development', '在终端操作仓库、Issue 和 Pull Request。', '适合已经习惯命令行的开发者。', 'https://cli.github.com/', DESKTOP, aliases=['gh', 'github 命令行'], repo='cli/cli', audience='开发者'),
    tool('windows_terminal', 'Windows Terminal', 'development', '在一个窗口管理多个命令行会话。', '适合同时使用 PowerShell、命令提示符与 WSL。', 'https://github.com/microsoft/terminal', ['windows'], aliases=['terminal', '终端'], repo='microsoft/terminal'),
    tool('ollama', 'Ollama', 'ai', '在自己的电脑上运行和调用语言模型。', '适合愿意配置模型、关注本地运行的用户。', 'https://ollama.com/download', DESKTOP, aliases=['本地模型', '本地ai'], repo='ollama/ollama', note='需要下载模型，内存和显存需求随模型而变。'),
    tool('lm_studio', 'LM Studio', 'ai', '通过桌面界面尝试本地语言模型。', '适合希望用图形界面探索本地模型的人。', 'https://lmstudio.ai/download', DESKTOP, aliases=['lmstudio', '本地模型'], note='运行要求与模型许可请分别查看官方说明。'),
    tool('chatbox', 'Chatbox', 'ai', '用一个客户端组织 AI 对话。', '适合希望集中管理对话和模型连接的人。', 'https://chatboxai.app/', ALL, aliases=['ai聊天', '对话'], repo='chatboxai/chatbox', note='模型服务、API 密钥或订阅可能需要单独配置。'),
    tool('dbeaver', 'DBeaver Community', 'data', '连接数据库，查看数据并执行 SQL。', '适合需要可视化数据库客户端的开发者。', 'https://dbeaver.io/download/', DESKTOP, aliases=['数据库', 'sql']),
    tool('fdroid', 'F-Droid', 'system', '发现和获取 Android 开源应用。', '为寻找开源手机工具提供独立入口。', 'https://f-droid.org/', ['android'], aliases=['f-droid', '开源商店'], note='不同分发渠道的签名可能不同，请按官方说明更新。'),
    tool('kodi', 'Kodi', 'media', '用大屏界面组织和播放自己的媒体。', '适合家庭影音与电视播放场景。', 'https://kodi.tv/download/', DESKTOP + ['android', 'android_tv'], aliases=['家庭影院', '媒体中心']),
    tool('jellyfin', 'Jellyfin', 'media', '搭建自己的媒体库并连接播放客户端。', '适合愿意维护家庭媒体服务器的用户。', 'https://jellyfin.org/downloads/', DESKTOP + ['android', 'ios', 'android_tv'], aliases=['jellyfin_server', 'jellyfin_media_player', 'jellyfin_android', '媒体库'], note='需要区分服务端与客户端，先按官方指南配置媒体服务器。'),
    tool('moonlight', 'Moonlight', 'gaming', '把电脑画面串流到另一台设备上游玩。', '适合已有兼容串流主机与稳定局域网的用户。', 'https://moonlight-stream.org/', ALL + ['android_tv', 'linux_handheld'], aliases=['moonlight_qt', 'moonlight_android', '游戏串流'], note='需配置兼容的串流服务端，体验取决于网络和硬件。'),
    tool('steam', 'Steam', 'gaming', '管理游戏库，安装并启动支持的游戏。', '适合集中管理电脑游戏与掌机游戏库。', 'https://store.steampowered.com/about/', DESKTOP + ['linux_handheld'], aliases=['游戏库'], note='游戏价格与平台兼容性需逐项确认。'),
    tool('flameshot', 'Flameshot', 'capture', '截图后直接添加箭头、文字和标注。', '适合日常沟通与文档截图标注。', 'https://flameshot.org/', DESKTOP, aliases=['截图标注'], repo='flameshot-org/flameshot'),
    tool('restic', 'restic', 'backup', '通过命令行备份文件到多种存储位置。', '适合需要脚本化备份与恢复流程的人。', 'https://restic.net/', DESKTOP, aliases=['备份'], audience='进阶用户', note='请先配置备份目标并验证恢复流程。'),
    tool('sumatrapdf', 'SumatraPDF', 'office', '阅读 PDF、电子书和常见文档格式。', '适合主要需要打开和阅读文档的 Windows 用户。', 'https://www.sumatrapdfreader.org/free-pdf-reader', ['windows'], aliases=['sumatra_pdf', 'pdf阅读']),
    tool('localsend_tv_guide', '电视文件传输指南', 'transfer', '在电视安装应用前，先确认设备支持的传输方式。', '按电视型号和系统确认可用入口。', 'https://localsend.org/', [], note='资料入口，不作为已确认的电视适配应用。'),
]
FEATURED = [p for p in FEATURED if p['supported']]

COLLECTIONS = [
    dict(id='new-pc', name='新电脑，装好就用', intro='从解压、办公到文件互传，每种用途挑一个就够。系统自带功能能满足时，无需额外安装。', icon='⊞', tools=['7zip','firefox','libreoffice','vlc','localsend','keepassxc','pixpin','powertoys']),
    dict(id='office-study', name='办公学习', intro='写文档、记笔记、读资料，把每天的学习和工作接起来。', icon='▤', tools=['libreoffice','joplin','obsidian','sumatrapdf','drawio','calibre','localsend']),
    dict(id='phone-transfer', name='手机电脑互传', intro='传照片、分享文件和连接设备，先确认双方支持的平台与网络条件。', icon='⇄', tools=['localsend','kdeconnect','syncthing','rustdesk']),
    dict(id='creator', name='录课与内容创作', intro='截图、录屏、剪辑、转码，按制作步骤挑选需要的工具。', icon='▷', tools=['pixpin','flameshot','obs','shotcut','audacity','handbrake','gimp']),
    dict(id='developer', name='开发入门', intro='先准备编辑器和版本管理，再按项目需要补齐终端、数据库与 AI 工具。', icon='⌨', tools=['vscode','git','github_desktop','windows_terminal','github_cli','dbeaver','ollama']),
    dict(id='backup', name='照顾好重要文件', intro='管理密码、备份与同步。先备份，再实际验证能否恢复。', icon='↻', tools=['keepassxc','bitwarden','syncthing','restic']),
    dict(id='living-room', name='客厅影音与掌机', intro='搭建媒体库或进行游戏串流，留意服务端、客户端和设备适配。', icon='♙', tools=['vlc','kodi','jellyfin','moonlight','steam']),
]

PLATFORM_PICKS = {
    'windows': ['localsend','7zip','libreoffice','vlc','pixpin','powertoys','keepassxc','firefox','joplin','rustdesk','sumatrapdf','bitwarden'],
    'darwin': ['localsend','libreoffice','vlc','pixpin','keepassxc','firefox','joplin','obsidian','rustdesk','bitwarden','obs','calibre'],
    'linux': ['localsend','libreoffice','vlc','keepassxc','firefox','joplin','flameshot','syncthing','kdeconnect','restic','vscode','obs'],
    'android': ['localsend','vlc','joplin','bitwarden','fdroid','kdeconnect','firefox','obsidian','gopeed','rustdesk'],
    'ios': ['localsend','vlc','joplin','bitwarden','firefox','obsidian','kdeconnect','rustdesk'],
    'android_tv': ['kodi','jellyfin','moonlight'],
    'linux_handheld': ['steam','moonlight'],
}
