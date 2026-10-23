# Switch 整合包组件对照

核查日期：2026-10-19。按提供的 SW 23.0.1 / Atmosphere 1.12.1 / Hekate 6.5.4 参考组合整理；具体插件的兼容范围以各自发布说明为准。

清单默认跟随最新稳定 Release，不将所有工具固定在参考组合的旧版本。仅有预发布的条目固定到已核查标签。所有操作仅下载或打开页面，不安装、不解压、不修改 SD 卡、不刷写。

## 1. 大气层三件套与补丁

| 组件 | 清单 ID | 说明 |
|---|---|---|
| Atmosphere 本体 | `atmosphere` | 本次核查 1.12.1；完整包包含 hbl/hbmenu，fusee.bin 单独在发布页获取 |
| Hekate + Nyx 原版 | `hekate` | 本次核查 6.5.4 / Nyx 1.9.4 完整 ZIP |
| easyworld 汉化 | `hekate-easyworld` | 默认简体 _sc.zip；繁体 _tc.zip 同页，勿与其他汉化方案同时覆盖 |
| zdm 汉化 Nyx | `hekate-zdm` | 独立 nyx.bin；本次 latest 标签 v6.5.3-CN，使用前与引导版本核对 |
| Sigpatch 发布帖 | `sigpatch-downloads` | GBAtemp 页面入口，附件手动选择 |
| 签名补丁 Python 制作脚本 | `sigpatch-scripts` | make_patches.py 源文件页面，不自动执行 |
| 补丁数据库 | `sigpatch-database` | patch_database/ 目录页面 |
| IPS Patch Creator | `ips-patch-creator` | 电脑端工具页面 |
| sys-patch 系统模块 | `sys-patch` | 与 IPS 形式补丁分开收录，按模块说明部署 |

Hekate 汉化按所选包说明处理 `bootloader/sys/nyx.bin`。不要把用户参考文件名或某个分支的 latest 标签等同于所有版本均可互换；是否保留英文备份文件以实际整合包内容为准。

## 2. Tesla / Ultrahand 汉化组件

| 组件 | 清单 ID | 下载内容 |
|---|---|---|
| zdm overlay 加载器 | `nx-ovlloader-zdm` | nx-ovlloader.zip |
| zdm Ultrahand 菜单 | `ultrahand-zdm` | Ultrahand.zip |
| 系统模块管理 | `ovl-sysmodules-zdm` | ovl-sysmodules.zip |
| EdiZon 汉化套件 | `edizon-overlay-zdm` | EdiZon.zip，NRO/OVL 按包内实际内容放置 |
| sys-clk 汉化套件 | `sys-clk-zdm` | sys-clk.zip |
| 状态监控汉化套件 | `status-monitor-zdm` | StatusMonitor.zip |

原版 `tesla-menu`、`nx-ovlloader`、`ultrahand-overlay`、`sys-clk`、`status-monitor-overlay` 仍分别保留。它们与汉化分支是不同来源，菜单同名文件不可按“全选下载后全覆盖”理解；本工具只下载供选择。模块、OVL 以及资源按包内布局和分支说明放置。

## 3. 相册 / hbmenu 主机端应用

| 工具 | 清单 ID | 说明 |
|---|---|---|
| Awoo Installer | `awoo-installer` | 主机端 ZIP |
| NS-USBloader | `ns-usbloader` | 电脑端配套页面，选择对应系统/Java 文件；不作为 Switch NRO |
| Checkpoint | `checkpoint` | 已改为 BernardoGiordano/Checkpoint 的当前来源；5.3.0 的 Switch NRO |
| DBI 原版 | `dbi` | rashevskyv/dbi 原始分发 |
| DBI 外置翻译版 | `dbipatcher` | rashevskyv/DBIPatcher 同页提供的兼容 DBI.nro |
| DBI 简体中文文件 | `dbi-translation-zhcn` | translation_zhcn.bin，手动改名 translation.bin，与同版本 DBIPatcher DBI.nro 放在同一 SD 目录；不可混用原版/其他版本 |
| Ascent Toolbox | `ascent-toolbox` | Ascent-Toolbox.nro；与 DeepSea 分支分别保留 |
| DeepSea Toolbox | `deepsea-toolbox` | 原 DeepSea 分支，实际附件名 DeepSeaToolbox.nro |
| EdiZon SE | `edizon-se` | edizon.zip 标准包；汉化套件另见 edizon-overlay-zdm |
| Goldleaf | `goldleaf` | Goldleaf.nro |
| JKSV | `jksv` | JKSV.nro |
| Linkalho | `linkalho` | linkalho 完整 ZIP |
| N-Xplorer | `n-xplorer` | 预发布 NRO，固定 0.7.1-crash-fix 标签 |
| NX Activity Log 汉化 | `nx-activity-log-zdm` | NX-Activity-Log.nro |
| Sphaira | `sphaira` | sphaira.zip 完整包 |
| Switch Time | `switch-time` | switch-time.nro |
| Tencent Switcher GUI | `tencent-switcher-gui` | 本次 latest 为 0.1.1，与参考清单中的 0.1.2 有差异 |
| TinWoo | `tinwoo` | Tinwoo-Installer.zip |
| wiliwili | `wiliwili` | 选择 NintendoSwitch ZIP，排除 Windows/Linux 等平台文件 |

NRO 通常通过 hbmenu 启动，但完整内存模式、联网、系统校时和配套文件要求需看各项目说明；本次未验证实机运行。不同来源中的同名 NRO 是可选版本，不自动混装。

## 4. Hekate 载荷与芯片固件

| 工具 | 清单 ID | 放置/选择说明 |
|---|---|---|
| CommonProblemResolver | `commonproblemresolver` | .bin 载荷，手动放入 bootloader/payloads/ |
| Lockpick RCM | `lockpick-rcm` | 默认 _Hekate.zip，按包内说明取用载荷 |
| TegraExplorer Ext | `tegraexplorer-ext` | 完整 ZIP，额外 TE 脚本按项目说明放置 |
| HWFLY Toolbox | `hwfly-toolbox` | hwfly_toolbox.bin 载荷 |
| HWFLY 固件 / SDLoader | `hwfly-firmware` | release_072.zip，按具体芯片与包内说明选择文件 |
| Picofly 工具箱与固件目录 | `picofly-firmwares` | 仓库 Firmwares/ 页面入口，手动选择对应文件 |
| rehius Picofly 固件 | `picofly-usk` | 选择 update.bin；firmware.uf2 在同一发布页，按其说明选择烧录方式 |
| DowngradeFixer | `downgradefixer` | ZIP 载荷包 |
| Warmboot Extractor | `warmboot-extractor` | ZIP 载荷包，适用机型与提取前提查看 README |

裸 .bin 载荷与 update.bin、translation_zhcn.bin 都使用同一扩展名，但用途完全不同；分类和每条下载规则已分别指定文件，不按 .bin 通配下载，也不会自动复制或执行。HWFLY、Picofly 固件的硬件对应关系以各自项目说明为准。

## 查询示例

```bat
lookup_switch.bat 汉化
lookup_switch.bat 深海工具箱
lookup_switch.bat DBI汉化
lookup_switch.bat 载荷
lookup_switch.bat 签名补丁
python auto_update.py --apps-dir apps-switch --platform switch dbipatcher dbi-translation-zhcn
```

下载后的本机文件仍按原附件名保存在 `switch/<id>/`；本文中的 SD 卡路径是手动部署参考，不是本工具的本机下载路径。
