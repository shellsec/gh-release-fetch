# -*- coding: utf-8 -*-
"""Lookup 交互界面的语言。加语言只加下面的字符串行。"""
from __future__ import annotations

import os

LANG_ENV = "GH_RELEASE_FETCH_LANG"
SUPPORTED = ("zh-CN", "zh-TW", "en", "ja", "ko")
_MISSING = object()

# key, zh-CN, zh-TW, en, ja, ko
_ROWS = (
    ("common.cancelled", "已取消。", "已取消。", "Cancelled.", "キャンセルしました。", "취소했습니다."),
    ("common.warn_skip", "[WARN] 跳过 %s: %s", "[WARN] 略過 %s: %s", "[WARN] skipped %s: %s", "[WARN] スキップ %s: %s", "[WARN] 건너뜀 %s: %s"),
    ("common.quit", "已退出。", "已結束。", "Quit.", "終了しました。", "종료했습니다."),
    ("common.invalid_input", "无效输入: %r", "無效輸入: %r", "Invalid input: %r", "無効な入力: %r", "잘못된 입력: %r"),
    ("common.invalid_text", "无效输入: %s", "無效輸入: %s", "Invalid input: %s", "無効な入力: %s", "잘못된 입력: %s"),
    ("common.index_range", "序号超出范围: %d", "編號超出範圍: %d", "Number out of range: %d", "番号が範囲外です: %d", "번호가 범위를 벗어났습니다: %d"),
    ("common.invalid_choice", "无效选择。", "無效選擇。", "Invalid choice.", "無効な選択です。", "잘못된 선택입니다."),
    ("sep.list", "、", "、", ", ", "、", ", "),
    ("sep.semi", "；", "；", "; ", "；", "; "),
    ("hits.count", "共 %d 条匹配：", "共 %d 項相符：", "%d matches:", "一致 %d 件:", "일치 %d건:"),
    ("hits.yes", "是", "是", "yes", "はい", "예"),
    ("hits.no", "否", "否", "no", "いいえ", "아니요"),
    ("hits.downloadable", "可下载", "可下載", "downloadable", "ダウンロード可", "다운로드 가능"),
    ("hits.page_only", "仅页面", "僅頁面", "page only", "ページのみ", "페이지만"),
    ("hits.shard", "    分片: %s", "    分片: %s", "    shard: %s", "    シャード: %s", "    샤드: %s"),
    ("hits.category", "    分类: %s", "    分類: %s", "    category: %s", "    分類: %s", "    분류: %s"),
    ("hits.repo", "    仓库: %s", "    倉庫: %s", "    repo: %s", "    リポジトリ: %s", "    저장소: %s"),
    ("hits.page", "    页面: %s", "    頁面: %s", "    page: %s", "    ページ: %s", "    페이지: %s"),
    ("hits.brief", "    简介: %s", "    簡介: %s", "    summary: %s", "    概要: %s", "    소개: %s"),
    ("choose.title", "请选择要操作的条目：", "請選擇要操作的項目：", "Select entries:", "操作する項目を選んでください:", "작업할 항목을 선택하세요:"),
    ("choose.hint", "  输入序号（如 1 或 1,3）| a=全部 | b/回车=返回 | q=退出", "  輸入編號（如 1 或 1,3）| a=全部 | b/Enter=返回 | q=結束", "  Enter numbers (e.g. 1 or 1,3) | a=all | b/Enter=back | q=quit", "  番号を入力（例: 1 または 1,3）| a=すべて | b/Enter=戻る | q=終了", "  번호 입력(예: 1 또는 1,3) | a=전체 | b/Enter=뒤로 | q=종료"),
    ("enable.skip", "[跳过] %s / %s 已是开启状态", "[略過] %s / %s 已是啟用狀態", "[skip] %s / %s is already enabled", "[スキップ] %s / %s はすでに有効です", "[건너뜀] %s / %s 은(는) 이미 켜져 있습니다"),
    ("enable.dry", "[dry-run] 将开启 %s / %s → %s", "[dry-run] 將啟用 %s / %s → %s", "[dry-run] would enable %s / %s → %s", "[dry-run] %s / %s を有効化します → %s", "[dry-run] %s / %s 을(를) 켭니다 → %s"),
    ("enable.done", "[已开启] %s / %s → %s", "[已啟用] %s / %s → %s", "[enabled] %s / %s → %s", "[有効化] %s / %s → %s", "[켬] %s / %s → %s"),
    ("enable.missing", "[失败] 未在 %s 中找到 id=%s", "[失敗] 未在 %s 中找到 id=%s", "[failed] not found in %s: id=%s", "[失敗] %s に id=%s が見つかりません", "[실패] %s 에서 id=%s 을(를) 찾지 못했습니다"),
    ("enable.total", "共开启 %d 条。", "共啟用 %d 項。", "Enabled %d entries.", "%d 件を有効にしました。", "%d개 항목을 켰습니다."),
    ("enable.total_nl", "\n共开启 %d 条。", "\n共啟用 %d 項。", "\nEnabled %d entries.", "\n%d 件を有効にしました。", "\n%d개 항목을 켰습니다."),
    ("enable.already", "所选条目均已 enabled=true。", "所選項目均已 enabled=true。", "Selected entries are already enabled=true.", "選択した項目はすべて enabled=true です。", "선택한 항목은 모두 enabled=true 입니다."),
    ("save.ask", "是否加入到更新列表 %s ？", "是否加入更新清單 %s ？", "Add to the update list %s?", "更新リスト %s に追加しますか？", "업데이트 목록 %s 에 추가할까요?"),
    ("save.hint", "（之后可运行 run_saved_apps.bat 一键开启并更新）", "（之後可執行 run_saved_apps.bat 一鍵啟用並更新）", "(Later, run_saved_apps.bat can enable and update them together)", "（後で run_saved_apps.bat を実行すると一括で有効化して更新できます）", "(나중에 run_saved_apps.bat 으로 한 번에 켜고 업데이트할 수 있습니다)"),
    ("save.skip", "未加入列表。", "未加入清單。", "Not added to the list.", "リストには追加しませんでした。", "목록에 추가하지 않았습니다."),
    ("save.dry", "[dry-run] 将加入列表 %s / %s", "[dry-run] 將加入清單 %s / %s", "[dry-run] would add %s / %s to the list", "[dry-run] リストに追加します %s / %s", "[dry-run] 목록에 추가합니다 %s / %s"),
    ("action.title", "请选择操作：", "請選擇操作：", "Choose an action:", "操作を選んでください:", "작업을 선택하세요:"),
    ("action.1", "  1 = 立刻下载（无安装包则自动打开页面；不修改 enabled）", "  1 = 立即下載（無安裝包則自動開啟頁面；不修改 enabled）", "  1 = Download now (open the page if there is no installer; do not change enabled)", "  1 = 今すぐダウンロード（インストール包がなければページを開く。enabled は変えない）", "  1 = 즉시 다운로드(설치 파일이 없으면 페이지를 엽니다. enabled 는 바꾸지 않음)"),
    ("action.2", "  2 = 加入更新列表并立刻下载", "  2 = 加入更新清單並立即下載", "  2 = Add to the update list and download now", "  2 = 更新リストに追加して今すぐダウンロード", "  2 = 업데이트 목록에 추가하고 즉시 다운로드"),
    ("action.3", "  3 = 加入更新列表 saved_apps_<平台>.json", "  3 = 加入更新清單 saved_apps_<平台>.json", "  3 = Add to update list saved_apps_<platform>.json", "  3 = 更新リスト saved_apps_<プラットフォーム>.json に追加", "  3 = 업데이트 목록 saved_apps_<플랫폼>.json 에 추가"),
    ("action.4", "  4 = 设为 enabled=true", "  4 = 設為 enabled=true", "  4 = Set enabled=true", "  4 = enabled=true にする", "  4 = enabled=true 로 설정"),
    ("action.5", "  5 = 打开页面（官网 / GitHub Releases）", "  5 = 開啟頁面（官網 / GitHub Releases）", "  5 = Open page (website / GitHub Releases)", "  5 = ページを開く（公式サイト / GitHub Releases）", "  5 = 페이지 열기(공식 사이트 / GitHub Releases)"),
    ("action.nav", "  b/回车 = 返回    q = 退出", "  b/Enter = 返回    q = 結束", "  b/Enter = back    q = quit", "  b/Enter = 戻る    q = 終了", "  b/Enter = 뒤로    q = 종료"),
    ("action.invalid", "无效输入: %r（请输入 1-5，b 返回，q 退出）", "無效輸入: %r（請輸入 1-5，b 返回，q 結束）", "Invalid input: %r (enter 1-5, b to go back, q to quit)", "無効な入力: %r（1-5、戻るは b、終了は q）", "잘못된 입력: %r (1-5, 뒤로=b, 종료=q)"),
    ("action.selected", "\n已选 %d 条。", "\n已選 %d 項。", "\nSelected %d.", "\n%d 件を選択しました。", "\n%d개를 선택했습니다."),
    ("action.download_flag", "操作: 1（--download 立刻下载）", "操作: 1（--download 立即下載）", "Action: 1 (--download now)", "操作: 1（--download で今すぐダウンロード）", "작업: 1(--download 즉시 다운로드)"),
    ("open.skip", "[跳过] %s / %s：无可用页面 URL", "[略過] %s / %s：無可用頁面 URL", "[skip] %s / %s: no page URL", "[スキップ] %s / %s：開けるページ URL がありません", "[건너뜀] %s / %s: 열 수 있는 페이지 URL이 없습니다"),
    ("open.dry", "[dry-run] 将打开: %s  (%s / %s)", "[dry-run] 將開啟: %s  (%s / %s)", "[dry-run] would open: %s  (%s / %s)", "[dry-run] 開きます: %s  (%s / %s)", "[dry-run] 엽니다: %s  (%s / %s)"),
    ("open.done", "[已打开] %s / %s → %s", "[已開啟] %s / %s → %s", "[opened] %s / %s → %s", "[開いた] %s / %s → %s", "[열림] %s / %s → %s"),
    ("open.fail", "[失败] 无法打开浏览器: %s", "[失敗] 無法開啟瀏覽器: %s", "[failed] could not open the browser: %s", "[失敗] ブラウザーを開けません: %s", "[실패] 브라우저를 열 수 없습니다: %s"),
    ("download.page_only", "[提示] %d 条无安装包，将打开页面。", "[提示] %d 項無安裝包，將開啟頁面。", "[note] %d entries have no installer; opening the page.", "[案内] %d 件はインストール包がないためページを開きます。", "[안내] %d개 항목은 설치 파일이 없어 페이지를 엽니다."),
    ("download.none", "没有可下载的条目。", "沒有可下載的項目。", "Nothing to download.", "ダウンロードできる項目がありません。", "다운로드할 항목이 없습니다."),
    ("download.banner", "[下载] 平台 %s：%s", "[下載] 平台 %s：%s", "[download] platform %s: %s", "[ダウンロード] プラットフォーム %s：%s", "[다운로드] 플랫폼 %s: %s"),
    ("download.dry", "[dry-run] 将执行: %s", "[dry-run] 將執行: %s", "[dry-run] would run: %s", "[dry-run] 実行します: %s", "[dry-run] 실행합니다: %s"),
    ("usage.1", "用法: lookup_app [选项与关键词...]", "用法: lookup_app [選項與關鍵字...]", "Usage: lookup_app [options and keywords...]", "使い方: lookup_app [オプションとキーワード...]", "사용법: lookup_app [옵션과 키워드...]"),
    ("usage.2", "示例: lookup_app drawio", "範例: lookup_app drawio", "Example: lookup_app drawio", "例: lookup_app drawio", "예: lookup_app drawio"),
    ("usage.3", "      lookup_mobile.bat termux", "      lookup_mobile.bat termux", "      lookup_mobile.bat termux", "      lookup_mobile.bat termux", "      lookup_mobile.bat termux"),
    ("usage.4", "      lookup_ios.bat 微信", "      lookup_ios.bat 微信", "      lookup_ios.bat 微信", "      lookup_ios.bat 微信", "      lookup_ios.bat 微信"),
    ("usage.5", "交互选条目: 1=下载(无包则开页)  2=加入并下载  3=加入列表  4=启用  5=打开页面；b/回车=返回，q=退出", "互動選項目: 1=下載(無包則開頁)  2=加入並下載  3=加入清單  4=啟用  5=開啟頁面；b/Enter=返回，q=結束", "Interactive: 1=download (open page if none)  2=add and download  3=add to list  4=enable  5=open page; b/Enter=back, q=quit", "対話で項目選択: 1=ダウンロード（無ければページ）  2=追加してダウンロード  3=リストへ追加  4=有効化  5=ページを開く；b/Enter=戻る、q=終了", "대화형 선택: 1=다운로드(없으면 페이지)  2=추가 후 다운로드  3=목록에 추가  4=사용  5=페이지 열기; b/Enter=뒤로, q=종료"),
    ("usage.6", "直接下载: lookup_app -y --download drawio", "直接下載: lookup_app -y --download drawio", "Download directly: lookup_app -y --download drawio", "直接ダウンロード: lookup_app -y --download drawio", "바로 다운로드: lookup_app -y --download drawio"),
    ("usage.7", "打开页面: lookup_app chatbox --open", "開啟頁面: lookup_app chatbox --open", "Open page: lookup_app chatbox --open", "ページを開く: lookup_app chatbox --open", "페이지 열기: lookup_app chatbox --open"),
    ("catalog.which", "搜哪个清单?", "搜尋哪個清單?", "Which catalog?", "どのカタログを検索しますか?", "어떤 목록을 검색할까요?"),
    ("catalog.prompt", "请选择 (1-%d，回车=Windows，q=退出): ", "請選擇 (1-%d，Enter=Windows，q=結束): ", "Choose (1-%d, Enter=Windows, q=quit): ", "選択 (1-%d、Enter=Windows、q=終了): ", "선택 (1-%d, Enter=Windows, q=종료): "),
    ("catalog.chosen", "清单: %s", "清單: %s", "Catalog: %s", "カタログ: %s", "목록: %s"),
    ("catalog.keyword", "请输入关键词（回车=返回清单）: ", "請輸入關鍵字（Enter=返回清單）: ", "Enter a keyword (Enter=back to catalogs): ", "キーワードを入力（Enter=カタログに戻る）: ", "키워드 입력(Enter=목록으로 돌아가기): "),
    ("catalog.hint_back", "回车=返回清单", "Enter=返回清單", "Enter=back to catalogs", "Enter=カタログに戻る", "Enter=목록으로 돌아가기"),
    ("catalog.hint_quit", "回车=退出", "Enter=結束", "Enter=quit", "Enter=終了", "Enter=종료"),
    ("catalog.keyword_again", "请输入关键词（%s）:", "請輸入關鍵字（%s）:", "Enter a keyword (%s):", "キーワードを入力（%s）:", "키워드 입력(%s):"),
    ("catalog.back_search", "返回重新搜索。", "返回重新搜尋。", "Back to search again.", "検索に戻ります。", "다시 검색으로 돌아갑니다."),
    ("catalog.query_prompt", "请输入搜索关键词: ", "請輸入搜尋關鍵字: ", "Enter a search keyword: ", "検索キーワードを入力: ", "검색 키워드를 입력하세요: "),
    ("catalog.err_query", "[ERROR] 需要至少一个关键词。", "[ERROR] 需要至少一個關鍵字。", "[ERROR] At least one keyword is required.", "[ERROR] キーワードが少なくとも1つ必要です。", "[ERROR] 키워드가 하나 이상 필요합니다."),
    ("catalog.err_dir", "[ERROR] 目录不存在: %s", "[ERROR] 目錄不存在: %s", "[ERROR] Directory does not exist: %s", "[ERROR] ディレクトリがありません: %s", "[ERROR] 디렉터리가 없습니다: %s"),
    ("catalog.searching", "检索: %r  （清单: %s）", "搜尋: %r  （清單: %s）", "Search: %r  (catalog: %s)", "検索: %r  （カタログ: %s）", "검색: %r  (목록: %s)"),
    ("catalog.all_platforms", "全部平台", "全部平台", "all platforms", "すべてのプラットフォーム", "모든 플랫폼"),
    ("catalog.custom_miss", "自定义清单中未找到匹配项。请在「自定义清单 → 添加软件」中收录，或使用 --custom-add。", "自訂清單中找不到相符項目。請在「自訂清單 → 新增軟體」中收錄，或使用 --custom-add。", "No match in the custom catalog. Add it under Custom catalog → Add an app, or use --custom-add.", "カスタムカタログに一致がありません。「カスタムカタログ → ソフトを追加」で登録するか、--custom-add を使ってください。", "사용자 목록에서 찾지 못했습니다. 「사용자 목록 → 소프트웨어 추가」에서 넣거나 --custom-add 를 사용하세요."),
    ("catalog.custom", "自定义清单", "自訂清單", "Custom catalog", "カスタムカタログ", "사용자 목록"),
    ("catalog.all", "搜全部清单", "搜尋全部清單", "Search all catalogs", "すべてのカタログを検索", "모든 목록 검색"),
    ("catalog.handheld", "Linux掌机", "Linux 掌機", "Linux handheld", "Linux 携帯ゲーム機", "Linux 휴대용 기기"),
    ("gh.skip_write", "[跳过写入] 平台 %s 已有相同 id 或仓库（%s），不重复追加。", "[略過寫入] 平台 %s 已有相同 id 或倉庫（%s），不重複追加。", "[skip write] platform %s already has the same id or repo (%s); not appending again.", "[書き込みスキップ] プラットフォーム %s には同じ id またはリポジトリ（%s）があるため追加しません。", "[기록 건너뜀] 플랫폼 %s 에 같은 id 또는 저장소(%s)가 있어 다시 넣지 않습니다."),
    ("gh.dry_append", "[dry-run] 将追加 enabled=false 到 %s（id=%s），本次不写文件。", "[dry-run] 將追加 enabled=false 到 %s（id=%s），本次不寫檔案。", "[dry-run] would append enabled=false to %s (id=%s); not writing.", "[dry-run] enabled=false を %s に追加します（id=%s）。今回は書き込みません。", "[dry-run] enabled=false 를 %s 에 추가합니다(id=%s). 이번에는 쓰지 않습니다."),
    ("gh.wrote", "[已写入] %s  id=%s  enabled=false", "[已寫入] %s  id=%s  enabled=false", "[wrote] %s  id=%s  enabled=false", "[書き込み] %s  id=%s  enabled=false", "[기록함] %s  id=%s  enabled=false"),
    ("gh.choice", "%s仓库: %s    版本: %s    文件: %s    大小: %s    star: %d", "%s倉庫: %s    版本: %s    檔案: %s    大小: %s    star: %d", "%srepo: %s    version: %s    file: %s    size: %s    stars: %d", "%sリポジトリ: %s    バージョン: %s    ファイル: %s    サイズ: %s    star: %d", "%s저장소: %s    버전: %s    파일: %s    크기: %s    star: %d"),
    ("gh.platform_line", "    平台: %s", "    平台: %s", "    platform: %s", "    プラットフォーム: %s", "    플랫폼: %s"),
    ("gh.enter", "回车下载，其它键取消", "Enter 下載，其它鍵取消", "Enter to download, any other key to cancel", "Enter でダウンロード、それ以外でキャンセル", "Enter 는 다운로드, 다른 키는 취소"),
    ("gh.not_tty", "当前不是交互终端，已取消。可加 --no-prompt（仅仓库名一致且只有一个合格包时会下载）。", "目前不是互動終端，已取消。可加 --no-prompt（僅倉庫名一致且只有一個合格包時會下載）。", "This is not an interactive terminal, so it was cancelled. Add --no-prompt (downloads only when the repo name matches and there is one qualified package).", "対話端末ではないためキャンセルしました。--no-prompt を付けると、リポジトリ名が一致し合格パッケージが1つだけのときだけダウンロードします。", "대화형 터미널이 아니어서 취소했습니다. --no-prompt 를 주면 저장소 이름이 일치하고 적합한 패키지가 하나일 때만 다운로드합니다."),
    ("gh.pick", "请输入编号（回车取消）", "請輸入編號（Enter 取消）", "Enter a number (Enter to cancel)", "番号を入力（Enter でキャンセル）", "번호를 입력하세요(Enter 취소)"),
    ("gh.bad_index", "无效编号，已取消。", "無效編號，已取消。", "Invalid number, cancelled.", "無効な番号のためキャンセルしました。", "잘못된 번호라서 취소했습니다."),
    ("gh.fail", "[失败] 下载未完成：%s", "[失敗] 下載未完成：%s", "[failed] download did not finish: %s", "[失敗] ダウンロードが完了しませんでした：%s", "[실패] 다운로드가 끝나지 않았습니다: %s"),
    ("gh.saved", "[已下载] %s", "[已下載] %s", "[downloaded] %s", "[ダウンロード済み] %s", "[다운로드됨] %s"),
    ("gh.fallback", "本地清单未命中，改为 GitHub 仓库搜索（平台: %s）。", "本地清單未命中，改為 GitHub 倉庫搜尋（平台: %s）。", "No local catalog hit. Searching GitHub repositories (platform: %s).", "ローカルカタログにないため、GitHub リポジトリを検索します（プラットフォーム: %s）。", "로컬 목록에 없어 GitHub 저장소를 검색합니다(플랫폼: %s)."),
    ("gh.bad_platform", "GitHub 补搜只挑选 Windows / macOS / Linux 安装包，当前平台为 %s，已停止。", "GitHub 補搜只挑選 Windows / macOS / Linux 安裝包，目前平台為 %s，已停止。", "GitHub fallback only picks Windows / macOS / Linux installers. Current platform is %s, so it stopped.", "GitHub 補完検索は Windows / macOS / Linux のインストール包だけを選びます。現在のプラットフォームは %s のため停止しました。", "GitHub 추가 검색은 Windows / macOS / Linux 설치 파일만 고릅니다. 현재 플랫폼이 %s 라서 멈췄습니다."),
    ("gh.no_repo", "GitHub 上没有与 %r 相匹配的公开仓库，已停止。", "GitHub 上沒有與 %r 相符的公開倉庫，已停止。", "No public GitHub repository matches %r. Stopped.", "GitHub に %r と一致する公開リポジトリがありません。停止しました。", "GitHub 에 %r 와(과) 맞는 공개 저장소가 없습니다. 멈췄습니다."),
    ("gh.exact_cracked", "仓库名对得上的结果像破解或改包，已停止，不下载：%s", "倉庫名對得上的結果像破解或改包，已停止，不下載：%s", "Name matches look like cracked or repacked builds. Stopped, not downloading: %s", "名前が一致する結果はクラック版または改変包のようです。停止し、ダウンロードしません：%s", "이름이 맞는 결과가 크랙 또는 개조판으로 보입니다. 멈추고 다운로드하지 않습니다: %s"),
    ("gh.near_cracked", "接近的仓库像破解或改包，已停止，不下载：%s", "接近的倉庫像破解或改包，已停止，不下載：%s", "Close repositories look like cracked or repacked builds. Stopped, not downloading: %s", "近いリポジトリはクラック版または改変包のようです。停止し、ダウンロードしません：%s", "비슷한 저장소가 크랙 또는 개조판으로 보입니다. 멈추고 다운로드하지 않습니다: %s"),
    ("gh.no_match", "没有仓库名与 %r 几乎一致（已忽略大小写、-、_、空格），已停止，不下载。", "沒有倉庫名與 %r 幾乎一致（已忽略大小寫、-、_、空格），已停止，不下載。", "No repository name is nearly identical to %r (ignoring case, -, _, and spaces). Stopped, not downloading.", "%r とほぼ同じリポジトリ名がありません（大文字小文字、-、_、空白は無視）。停止し、ダウンロードしません。", "%r 와(과) 거의 같은 저장소 이름이 없습니다(대소문자, -, _, 공백은 무시). 멈추고 다운로드하지 않습니다."),
    ("gh.nearest", "最接近的是：%s", "最接近的是：%s", "Closest: %s", "最も近いもの：%s", "가장 가까운 항목: %s"),
    ("gh.no_asset", "没有合格安装包，已停止，不下载。", "沒有合格安裝包，已停止，不下載。", "No qualified installer. Stopped, not downloading.", "合格するインストール包がないため停止し、ダウンロードしません。", "적합한 설치 파일이 없어 멈추고 다운로드하지 않습니다."),
    ("gh.suggest", "建议：", "建議：", "Suggestion:", "候補：", "제안:"),
    ("gh.one_repo", "仓库 %s 有 %d 个合格安装包，请编号选择，不会自动猜：", "倉庫 %s 有 %d 個合格安裝包，請編號選擇，不會自動猜：", "Repository %s has %d qualified installers. Pick a number; nothing is guessed:", "リポジトリ %s には合格インストール包が %d 個あります。番号で選んでください。自動では選びません：", "저장소 %s 에 적합한 설치 파일이 %d개 있습니다. 번호로 고르세요. 자동으로 고르지 않습니다:"),
    ("gh.multi", "有 %d 个同样接近的结果，请编号选择，不会自动猜：", "有 %d 個同樣接近的結果，請編號選擇，不會自動猜：", "%d results are equally close. Pick a number; nothing is guessed:", "同じ近さの結果が %d 件あります。番号で選んでください。自動では選びません：", "똑같이 가까운 결과가 %d개 있습니다. 번호로 고르세요. 자동으로 고르지 않습니다:"),
    ("gh.dry_ambiguous", "[dry-run] 没有唯一文件，不下载。", "[dry-run] 沒有唯一檔案，不下載。", "[dry-run] there is no single file, so nothing is downloaded.", "[dry-run] ファイルが一つに定まらないためダウンロードしません。", "[dry-run] 파일이 하나로 정해지지 않아 다운로드하지 않습니다."),
    ("gh.dry_would", "[dry-run] 将下载 %s 的 %s，本次不下载。", "[dry-run] 將下載 %s 的 %s，本次不下載。", "[dry-run] would download %s's %s; not downloading now.", "[dry-run] %s の %s をダウンロードします。今回はダウンロードしません。", "[dry-run] %s 의 %s 을(를) 다운로드합니다. 이번에는 받지 않습니다."),
    ("gh.noprompt_name", "未自动下载：仓库名与输入不是完全一致（%s）。--no-prompt 不会猜。", "未自動下載：倉庫名與輸入不是完全一致（%s）。--no-prompt 不會猜。", "Not downloaded automatically: the repo name is not an exact match (%s). --no-prompt does not guess.", "自動ダウンロードしません：リポジトリ名が入力と完全一致しません（%s）。--no-prompt は推測しません。", "자동으로 받지 않습니다. 저장소 이름이 입력과 완전히 같지 않습니다(%s). --no-prompt 는 추측하지 않습니다."),
    ("gh.noprompt_unique", "未自动下载：没有唯一的「仓库名一致且只有一个合格安装包」。--no-prompt 不会猜。", "未自動下載：沒有唯一的「倉庫名一致且只有一個合格安裝包」。--no-prompt 不會猜。", "Not downloaded automatically: there is no single case of “exact repo name and one qualified installer”. --no-prompt does not guess.", "自動ダウンロードしません：「リポジトリ名が一致し、合格インストール包が1つだけ」という条件を満たす唯一の候補がありません。--no-prompt は推測しません。", "자동으로 받지 않습니다. 「저장소 이름이 일치하고 적합한 설치 파일이 하나뿐」인 유일한 경우가 없습니다. --no-prompt 는 추측하지 않습니다."),
    ("gh.too_many", "同一相似度的仓库超过 5 个，只检查了星标较高的 5 个。", "同一相似度的倉庫超過 5 個，只檢查了星標較高的 5 個。", "More than 5 repositories share this similarity; only the 5 with more stars were checked.", "同じ類似度のリポジトリが 5 件を超えたため、スターが多い 5 件だけ確認しました。", "같은 유사도의 저장소가 5개를 넘어, 스타가 많은 5개만 확인했습니다."),
    ("gh.no_release", "%s：没有可用 Release。", "%s：沒有可用 Release。", "%s: no usable Release.", "%s：使える Release がありません。", "%s: 사용할 수 있는 Release 가 없습니다."),
    ("gh.note", "%s：%s", "%s：%s", "%s: %s", "%s：%s", "%s: %s"),
    ("gh.version", "版本 %s：%s", "版本 %s：%s", "Version %s: %s", "バージョン %s：%s", "버전 %s: %s"),
    ("gh.size_unknown", "大小未知", "大小未知", "unknown size", "サイズ不明", "크기 알 수 없음"),
    ("gh.reason_win", "没有合格的 Windows x64 安装包（exe/msi；旁边有安装包时不选便携 zip，源码包和校验文件已丢弃）", "沒有合格的 Windows x64 安裝包（exe/msi；旁邊有安裝包時不選便攜 zip，原始碼包和校驗檔已丟棄）", "No qualified Windows x64 installer (exe/msi; a portable zip is skipped when an installer is present, and source or checksum files are ignored)", "合格する Windows x64 インストール包がありません（exe/msi。インストール包があるときはポータブル zip を選ばず、ソースとチェックサムは捨てます）", "적합한 Windows x64 설치 파일이 없습니다(exe/msi. 설치 파일이 있으면 포터블 zip 은 고르지 않고, 소스와 체크섬은 버립니다)"),
    ("gh.reason_mac", "没有合格的 macOS 安装包（只要 arm64 或 universal dmg；仅有 Intel dmg 时不选）", "沒有合格的 macOS 安裝包（只要 arm64 或 universal dmg；僅有 Intel dmg 時不選）", "No qualified macOS installer (only arm64 or universal dmg; Intel-only dmg is not chosen)", "合格する macOS インストール包がありません（arm64 または universal の dmg のみ。Intel だけの dmg は選びません）", "적합한 macOS 설치 파일이 없습니다(arm64 또는 universal dmg 만. Intel 전용 dmg 는 고르지 않습니다)"),
    ("gh.reason_linux", "没有合格的 Linux x64 安装包（只要 AppImage 或 deb）", "沒有合格的 Linux x64 安裝包（只要 AppImage 或 deb）", "No qualified Linux x64 installer (AppImage or deb only)", "合格する Linux x64 インストール包がありません（AppImage または deb のみ）", "적합한 Linux x64 설치 파일이 없습니다(AppImage 또는 deb 만)"),
    ("gh.reason_other", "GitHub 补搜只按 Windows / macOS / Linux 安装包挑选", "GitHub 補搜只按 Windows / macOS / Linux 安裝包挑選", "GitHub fallback only selects Windows / macOS / Linux installers", "GitHub 補完検索は Windows / macOS / Linux のインストール包だけを選びます", "GitHub 추가 검색은 Windows / macOS / Linux 설치 파일만 고릅니다"),
    ("gh.no_files", "（无附件）", "（無附件）", "(no assets)", "（添付なし）", "(첨부 없음)"),
    ("gh.file_count", "（共 %d 个）", "（共 %d 個）", " (%d total)", "（全 %d 個）", " (총 %d개)"),
    ("gh.files_now", "%s。现有文件：%s", "%s。現有檔案：%s", "%s. Existing files: %s", "%s。現在のファイル：%s", "%s. 현재 파일: %s"),
    ("gh.rate", "GitHub API 未登录额度已用完（搜索约 10 次/分钟）。请稍后再试，或设置环境变量 GITHUB_TOKEN / GH_TOKEN 后重试。\n%s", "GitHub API 未登入額度已用完（搜尋約 10 次/分鐘）。請稍後再試，或設定環境變數 GITHUB_TOKEN / GH_TOKEN 後重試。\n%s", "The unauthenticated GitHub API limit is used up (search is about 10 times per minute). Try again later, or set GITHUB_TOKEN / GH_TOKEN and retry.\n%s", "未ログインの GitHub API 上限に達しました（検索は約 10 回/分）。しばらくしてから再試行するか、環境変数 GITHUB_TOKEN / GH_TOKEN を設定してください。\n%s", "로그인하지 않은 GitHub API 한도를 모두 썼습니다(검색은 분당 약 10회). 나중에 다시 시도하거나 환경 변수 GITHUB_TOKEN / GH_TOKEN 을 설정하세요.\n%s"),
    ("gh.stage_fail", "%s失败，未继续下载。\n%s", "%s失敗，未繼續下載。\n%s", "%s failed. Download was not started.\n%s", "%sに失敗したため、ダウンロードを続けていません。\n%s", "%s에 실패하여 다운로드를 계속하지 않았습니다.\n%s"),
    ("gh.no_address", "无可用地址", "無可用位址", "No usable address", "使えるアドレスがありません", "사용할 주소가 없습니다"),
    ("gh.rate_line", "%s -> HTTP %s 限流", "%s -> HTTP %s 限流", "%s -> HTTP %s rate limited", "%s -> HTTP %s レート制限", "%s -> HTTP %s 요청 제한"),
    ("gh.not_json", "%s -> 响应不是 JSON", "%s -> 回應不是 JSON", "%s -> response is not JSON", "%s -> 応答が JSON ではありません", "%s -> 응답이 JSON이 아닙니다"),
    ("gh.stage_search", "GitHub 仓库搜索", "GitHub 倉庫搜尋", "GitHub repository search", "GitHub リポジトリ検索", "GitHub 저장소 검색"),
    ("gh.stage_release", "读取 %s 的 Release", "讀取 %s 的 Release", "Read Release for %s", "%s の Release を読み取り", "%s 의 Release 읽기"),
    ("gh.stage_release_list", "读取 %s 的 Release 列表", "讀取 %s 的 Release 清單", "Read the Release list for %s", "%s の Release 一覧を読み取り", "%s 의 Release 목록 읽기"),
    ("gh.stage_repo", "读取仓库信息", "讀取倉庫資訊", "Read repository info", "リポジトリ情報を読み取り", "저장소 정보 읽기"),
    ("gh.stage_release_one", "读取 Release", "讀取 Release", "Read Release", "Release を読み取り", "Release 읽기"),
    ("cc.pick_platform", "请选择 %s 的适用平台（不能仅凭附件判断）：", "請選擇 %s 的適用平台（不能只憑附件判斷）：", "Choose platforms for %s (the asset name alone is not enough):", "%s の対象プラットフォームを選んでください（添付名だけでは判断できません）：", "%s 의 해당 플랫폼을 선택하세요(첨부 이름만으로는 판단할 수 없습니다):"),
    ("cc.platform_prompt", "平台序号（多选用逗号，0=取消%s）: ", "平台編號（多選用逗號，0=取消%s）: ", "Platform numbers (comma for multiple, 0=cancel%s): ", "プラットフォーム番号（複数はコンマ、0=キャンセル%s）: ", "플랫폼 번호(여러 개는 쉼표, 0=취소%s): "),
    ("cc.enter_default", "，回车=%s", "，Enter=%s", ", Enter=%s", "、Enter=%s", ", Enter=%s"),
    ("cc.pick_repo", "选择仓库序号（0=取消）: ", "選擇倉庫編號（0=取消）: ", "Repository number (0=cancel): ", "リポジトリ番号（0=キャンセル）: ", "저장소 번호(0=취소): "),
    ("cc.filename", "安装包文件名（含扩展名，回车取消）: ", "安裝包檔名（含副檔名，Enter 取消）: ", "Installer file name, including extension (Enter to cancel): ", "インストール包のファイル名（拡張子を含む、Enter でキャンセル）: ", "설치 파일 이름(확장자 포함, Enter 취소): "),
    ("cc.asset_line", "  %d  %s  [%s · %s · %s%s]", "  %d  %s  [%s · %s · %s%s]", "  %d  %s  [%s · %s · %s%s]", "  %d  %s  [%s · %s · %s%s]", "  %d  %s  [%s · %s · %s%s]"),
    ("cc.asset_prompt", "选择安装包（多选用逗号，a=全部，0=取消%s）: ", "選擇安裝包（多選用逗號，a=全部，0=取消%s）: ", "Choose installers (comma for multiple, a=all, 0=cancel%s): ", "インストール包を選択（複数はコンマ、a=すべて、0=キャンセル%s）: ", "설치 파일 선택(여러 개는 쉼표, a=전체, 0=취소%s): "),
    ("cc.name", "软件名称（回车=%s）: ", "軟體名稱（Enter=%s）: ", "App name (Enter=%s): ", "ソフト名（Enter=%s）: ", "소프트웨어 이름(Enter=%s): "),
    ("cc.category", "分类（回车=%s）: ", "分類（Enter=%s）: ", "Category (Enter=%s): ", "分類（Enter=%s）: ", "분류(Enter=%s): "),
    ("cc.preview", "\n收录预览：", "\n收錄預覽：", "\nImport preview:", "\n登録プレビュー：", "\n수록 미리보기:"),
    ("cc.preview_item", "  %s · %s · %s %s\n  安装包: %s\n  更新: %s", "  %s · %s · %s %s\n  安裝包: %s\n  更新: %s", "  %s · %s · %s %s\n  installer: %s\n  updates: %s", "  %s · %s · %s %s\n  インストール包: %s\n  更新: %s", "  %s · %s · %s %s\n  설치 파일: %s\n  업데이트: %s"),
    ("cc.duplicate", "（更新已有条目）", "（更新已有項目）", "(updates an existing entry)", "（既存の項目を更新）", "(기존 항목 업데이트)"),
    ("cc.mode_github", "跟随 GitHub 最新稳定 Release", "跟隨 GitHub 最新穩定 Release", "Follow the latest stable GitHub Release", "GitHub の最新安定 Release に従う", "GitHub 최신 안정 Release 를 따라감"),
    ("cc.mode_fixed", "固定链接，不检测新版本", "固定連結，不偵測新版本", "Fixed link, no new-version check", "固定リンク。新しいバージョンは調べません", "고정 링크, 새 버전을 확인하지 않음"),
    ("cc.source", "  来源: %s", "  來源: %s", "  source: %s", "  入手元: %s", "  출처: %s"),
    ("cc.tag", "  当前读取版本: %s", "  目前讀取版本: %s", "  version read now: %s", "  現在読み取ったバージョン: %s", "  지금 읽은 버전: %s"),
    ("cc.confirm", "1=确认仅保存  2=确认保存并下载  0/回车=取消: ", "1=確認僅儲存  2=確認儲存並下載  0/Enter=取消: ", "1=save only  2=save and download  0/Enter=cancel: ", "1=保存のみ  2=保存してダウンロード  0/Enter=キャンセル: ", "1=저장만  2=저장 후 다운로드  0/Enter=취소: "),
    ("cc.cancel_keep", "已取消，未修改清单。", "已取消，未修改清單。", "Cancelled. The catalog was not changed.", "キャンセルしました。カタログは変更していません。", "취소했습니다. 목록은 바꾸지 않았습니다."),
    ("cc.dry_save", "[dry-run] 将保存 %d 条；本次不写入、不下载。", "[dry-run] 將儲存 %d 項；本次不寫入、不下載。", "[dry-run] would save %d entries; not writing or downloading.", "[dry-run] %d 件を保存します。今回は書き込まず、ダウンロードもしません。", "[dry-run] %d개를 저장합니다. 이번에는 쓰지도 다운로드하지도 않습니다."),
    ("cc.saved", "已保存 %d 条到自定义清单。", "已儲存 %d 項到自訂清單。", "Saved %d entries to the custom catalog.", "カスタムカタログに %d 件保存しました。", "사용자 목록에 %d개를 저장했습니다."),
    ("cc.paste", "粘贴 GitHub 仓库 / Release / 下载链接，或输入软件名（回车取消）: ", "貼上 GitHub 倉庫 / Release / 下載連結，或輸入軟體名稱（Enter 取消）: ", "Paste a GitHub repo / Release / download link, or type an app name (Enter to cancel): ", "GitHub リポジトリ / Release / ダウンロードリンクを貼るか、ソフト名を入力（Enter でキャンセル）: ", "GitHub 저장소 / Release / 다운로드 링크를 붙이거나 소프트웨어 이름을 입력(Enter 취소): "),
    ("cc.not_saved", "[未保存] %s", "[未儲存] %s", "[not saved] %s", "[未保存] %s", "[저장 안 됨] %s"),
    ("cc.batch_intro", "每行粘贴一个仓库或下载地址，空行结束输入；输入 0 取消。", "每行貼上一個倉庫或下載位址，空行結束輸入；輸入 0 取消。", "Paste one repository or download address per line. A blank line finishes; 0 cancels.", "1行に1つのリポジトリまたはダウンロードアドレスを貼り付けます。空行で終了、0 でキャンセル。", "한 줄에 저장소 또는 다운로드 주소를 하나씩 붙이세요. 빈 줄은 종료, 0 은 취소입니다."),
    ("cc.recognized", "\n识别: %s", "\n識別: %s", "\nRecognized: %s", "\n認識: %s", "\n인식: %s"),
    ("cc.batch_cancel", "\n已取消，本批未保存。", "\n已取消，本批未儲存。", "\nCancelled. This batch was not saved.", "\nキャンセルしました。このバッチは保存していません。", "\n취소했습니다. 이 묶음은 저장하지 않았습니다."),
    ("cc.batch_fail", "[本批未保存] %s", "[本批未儲存] %s", "[batch not saved] %s", "[このバッチは未保存] %s", "[이 묶음은 저장 안 됨] %s"),
    ("cc.transfer", "1=导入 JSON 清单  2=导出 JSON 清单  0=返回: ", "1=匯入 JSON 清單  2=匯出 JSON 清單  0=返回: ", "1=import JSON catalog  2=export JSON catalog  0=back: ", "1=JSON カタログをインポート  2=JSON カタログをエクスポート  0=戻る: ", "1=JSON 목록 가져오기  2=JSON 목록 내보내기  0=뒤로: "),
    ("cc.import_path", "导入文件路径（回车取消）: ", "匯入檔案路徑（Enter 取消）: ", "Import file path (Enter to cancel): ", "インポートするファイルパス（Enter でキャンセル）: ", "가져올 파일 경로(Enter 취소): "),
    ("cc.export_path", "导出文件路径（回车=%s）: ", "匯出檔案路徑（Enter=%s）: ", "Export file path (Enter=%s): ", "エクスポートするファイルパス（Enter=%s）: ", "내보낼 파일 경로(Enter=%s): "),
    ("cc.overwrite", "文件已存在，确认覆盖？y=确认: ", "檔案已存在，確認覆蓋？y=確認: ", "File already exists. Overwrite? y=confirm: ", "ファイルが既にあります。上書きしますか？ y=確認: ", "파일이 이미 있습니다. 덮어쓸까요? y=확인: "),
    ("cc.dry_nowrite", "[dry-run] 未写入。", "[dry-run] 未寫入。", "[dry-run] not written.", "[dry-run] 書き込んでいません。", "[dry-run] 쓰지 않았습니다."),
    ("cc.exported", "已导出 %d 条 → %s", "已匯出 %d 項 → %s", "Exported %d entries → %s", "%d 件を書き出しました → %s", "%d개를 내보냈습니다 → %s"),
    ("cc.transfer_fail", "[未导入/导出] %s", "[未匯入/匯出] %s", "[not imported/exported] %s", "[未インポート/未エクスポート] %s", "[가져오기/내보내기 안 됨] %s"),
    ("cc.prefs", "当前偏好: %s", "目前偏好: %s", "Current preferences: %s", "現在の設定: %s", "현재 선호: %s"),
    ("cc.prefs_unset", "未设置；成功添加后自动记住选择", "未設定；成功新增後自動記住選擇", "Not set; a successful add remembers the choice", "未設定。追加に成功すると選択を覚えています", "설정되지 않음. 추가에 성공하면 선택을 기억합니다"),
    ("cc.prefs_menu", "1=修改偏好  2=清除偏好  0=返回: ", "1=修改偏好  2=清除偏好  0=返回: ", "1=edit preferences  2=clear preferences  0=back: ", "1=設定を変更  2=設定を消去  0=戻る: ", "1=선호 수정  2=선호 지우기  0=뒤로: "),
    ("cc.prefs_platform", "默认平台序号（0=取消）: ", "預設平台編號（0=取消）: ", "Default platform number (0=cancel): ", "既定プラットフォーム番号（0=キャンセル）: ", "기본 플랫폼 번호(0=취소): "),
    ("cc.arch_prefix", "架构: ", "架構: ", "Architecture: ", "アーキテクチャ: ", "아키텍처: "),
    ("cc.prefs_arch", "架构序号（回车不限）: ", "架構編號（Enter 不限）: ", "Architecture number (Enter=any): ", "アーキテクチャ番号（Enter で制限なし）: ", "아키텍처 번호(Enter=제한 없음): "),
    ("cc.prefs_kind", "版本类型: 1=%s  2=%s  回车=不限: ", "版本類型: 1=%s  2=%s  Enter=不限: ", "Package type: 1=%s  2=%s  Enter=any: ", "種類: 1=%s  2=%s  Enter=制限なし: ", "버전 유형: 1=%s  2=%s  Enter=제한 없음: "),
    ("cc.prefs_saved", "偏好已保存；只影响推荐，仍需预览确认。", "偏好已儲存；只影響推薦，仍需預覽確認。", "Preferences saved. They only affect suggestions and still need a preview confirmation.", "設定を保存しました。おすすめだけに影響し、プレビューでの確認は必要です。", "선호를 저장했습니다. 추천에만 영향을 주며, 미리보기 확인은 그대로 필요합니다."),
    ("cc.empty", "自定义清单为空，请先添加软件。", "自訂清單是空的，請先新增軟體。", "The custom catalog is empty. Add an app first.", "カスタムカタログは空です。先にソフトを追加してください。", "사용자 목록이 비어 있습니다. 먼저 소프트웨어를 추가하세요."),
    ("cc.manage_pick", "选择管理的条目（0=返回）: ", "選擇管理的項目（0=返回）: ", "Entry to manage (0=back): ", "管理する項目（0=戻る）: ", "관리할 항목(0=뒤로): "),
    ("cc.manage_action", "1=修改名称/分类  2=修改来源/安装包  3=删除  0=返回: ", "1=修改名稱/分類  2=修改來源/安裝包  3=刪除  0=返回: ", "1=edit name/category  2=edit source/installer  3=delete  0=back: ", "1=名前/分類を変更  2=入手元/インストール包を変更  3=削除  0=戻る: ", "1=이름/분류 수정  2=출처/설치 파일 수정  3=삭제  0=뒤로: "),
    ("cc.new_source", "新地址或软件名（回车=%s）: ", "新位址或軟體名稱（Enter=%s）: ", "New address or app name (Enter=%s): ", "新しいアドレスまたはソフト名（Enter=%s）: ", "새 주소 또는 소프트웨어 이름(Enter=%s): "),
    ("cc.keep_name", "名称（回车保留）: ", "名稱（Enter 保留）: ", "Name (Enter to keep): ", "名前（Enter で維持）: ", "이름(Enter 유지): "),
    ("cc.keep_category", "分类（回车保留）: ", "分類（Enter 保留）: ", "Category (Enter to keep): ", "分類（Enter で維持）: ", "분류(Enter 유지): "),
    ("cc.will_edit", "将修改为：%s · %s · %s", "將修改為：%s · %s · %s", "Will change to: %s · %s · %s", "次のように変更します：%s · %s · %s", "다음으로 바꿉니다: %s · %s · %s"),
    ("cc.confirm_edit", "确认修改？y=确认，其它=取消: ", "確認修改？y=確認，其它=取消: ", "Apply this change? y=confirm, anything else=cancel: ", "変更しますか？ y=確認、それ以外=キャンセル: ", "수정할까요? y=확인, 그 외=취소: "),
    ("cc.edited", "已修改。", "已修改。", "Updated.", "変更しました。", "수정했습니다."),
    ("cc.will_delete", "将从自定义清单删除：%s；安装包和其它清单不会删除。", "將從自訂清單刪除：%s；安裝包和其它清單不會刪除。", "This will remove %s from the custom catalog. Installers and other catalogs stay.", "カスタムカタログから削除します：%s。インストール包と他のカタログは削除しません。", "사용자 목록에서 삭제합니다: %s. 설치 파일과 다른 목록은 지우지 않습니다."),
    ("cc.confirm_delete", "确认删除？y=确认，其它=取消: ", "確認刪除？y=確認，其它=取消: ", "Delete? y=confirm, anything else=cancel: ", "削除しますか？ y=確認、それ以外=キャンセル: ", "삭제할까요? y=확인, 그 외=취소: "),
    ("cc.dry_nodelete", "[dry-run] 未删除。", "[dry-run] 未刪除。", "[dry-run] not deleted.", "[dry-run] 削除していません。", "[dry-run] 삭제하지 않았습니다."),
    ("cc.deleted", "已删除。", "已刪除。", "Deleted.", "削除しました。", "삭제했습니다."),
    ("cc.not_modified", "[未修改] %s", "[未修改] %s", "[not changed] %s", "[未変更] %s", "[변경 안 됨] %s"),
    ("cc.menu", "\n自定义软件\n  1  搜索已添加的软件\n  2  添加软件\n  3  管理软件（修改 / 删除）\n  4  批量添加\n  5  导入 / 导出清单\n  6  撤销上一次清单修改\n  7  平台 / 架构 / 版本类型偏好\n  0  返回    q  退出", "\n自訂軟體\n  1  搜尋已新增的軟體\n  2  新增軟體\n  3  管理軟體（修改 / 刪除）\n  4  批量新增\n  5  匯入 / 匯出清單\n  6  復原上一次清單修改\n  7  平台 / 架構 / 版本類型偏好\n  0  返回    q  結束", "\nCustom apps\n  1  Search added apps\n  2  Add an app\n  3  Manage apps (edit / delete)\n  4  Batch add\n  5  Import / export catalog\n  6  Undo the last catalog change\n  7  Platform / architecture / package preferences\n  0  back    q  quit", "\nカスタムソフト\n  1  追加済みを検索\n  2  ソフトを追加\n  3  ソフトを管理（変更 / 削除）\n  4  まとめて追加\n  5  カタログのインポート / エクスポート\n  6  直前のカタログ変更を元に戻す\n  7  プラットフォーム / アーキテクチャ / 種類の設定\n  0  戻る    q  終了", "\n사용자 소프트웨어\n  1  추가된 소프트웨어 검색\n  2  소프트웨어 추가\n  3  소프트웨어 관리(수정 / 삭제)\n  4  일괄 추가\n  5  목록 가져오기 / 내보내기\n  6  마지막 목록 변경 실행 취소\n  7  플랫폼 / 아키텍처 / 버전 유형 선호\n  0  뒤로    q  종료"),
    ("cc.choose", "请选择: ", "請選擇: ", "Choose: ", "選択: ", "선택: "),
    ("cc.keyword_cancel", "请输入关键词（回车取消）: ", "請輸入關鍵字（Enter 取消）: ", "Enter a keyword (Enter to cancel): ", "キーワードを入力（Enter でキャンセル）: ", "키워드 입력(Enter 취소): "),
    ("cc.undo_ask", "撤销最近一次添加、修改或删除？y=确认: ", "復原最近一次新增、修改或刪除？y=確認: ", "Undo the latest add, edit, or delete? y=confirm: ", "直前の追加、変更、削除を元に戻しますか？ y=確認: ", "최근 추가, 수정 또는 삭제를 되돌릴까요? y=확인: "),
    ("cc.dry_noundo", "[dry-run] 未恢复。", "[dry-run] 未復原。", "[dry-run] not restored.", "[dry-run] 元に戻していません。", "[dry-run] 되돌리지 않았습니다."),
    ("cc.restored", "已恢复。", "已復原。", "Restored.", "元に戻しました。", "되돌렸습니다."),
    ("cc.nothing_undo", "没有可撤销的修改。", "沒有可復原的修改。", "Nothing to undo.", "元に戻せる変更がありません。", "되돌릴 변경이 없습니다."),
    ("cc.last_pref", " · 上次偏好", " · 上次偏好", " · last preference", " · 前回の設定", " · 지난 선호"),
    ("kind.portable", "绿色/便携版", "綠色/便攜版", "portable", "ポータブル版", "포터블"),
    ("kind.installer", "安装版", "安裝版", "installer", "インストール版", "설치판"),
    ("kind.release", "发布附件", "發布附件", "release asset", "リリース添付", "릴리스 첨부"),
    ("arch.universal", "通用", "通用", "universal", "汎用", "범용"),
    ("arch.unspecified", "未标明", "未標明", "unspecified", "未指定", "미표시"),
    ("platform.unset", "平台待选", "平台待選", "platform not chosen", "プラットフォーム未選択", "플랫폼 미선택"),
    ("err.need_source", "请输入仓库地址、下载链接或软件名。", "請輸入倉庫位址、下載連結或軟體名稱。", "Enter a repository address, download link, or app name.", "リポジトリのアドレス、ダウンロードリンク、またはソフト名を入力してください。", "저장소 주소, 다운로드 링크 또는 소프트웨어 이름을 입력하세요."),
    ("err.http_only", "只支持不含用户名和密码的 HTTP / HTTPS 地址。", "只支援不含使用者名稱和密碼的 HTTP / HTTPS 位址。", "Only HTTP / HTTPS addresses without a username or password are supported.", "ユーザー名とパスワードを含まない HTTP / HTTPS アドレスだけに対応しています。", "사용자 이름과 비밀번호가 없는 HTTP / HTTPS 주소만 지원합니다."),
    ("err.need_owner", "GitHub 地址需要包含 owner/repo。", "GitHub 位址需要包含 owner/repo。", "A GitHub address must include owner/repo.", "GitHub アドレスには owner/repo が必要です。", "GitHub 주소에는 owner/repo 가 필요합니다."),
    ("err.need_release_url", "请提供 GitHub 仓库或 Release 地址。", "請提供 GitHub 倉庫或 Release 位址。", "Provide a GitHub repository or Release address.", "GitHub リポジトリまたは Release のアドレスを指定してください。", "GitHub 저장소 또는 Release 주소를 입력하세요."),
    ("err.name_empty", "名称不能为空。", "名稱不能為空。", "The name cannot be empty.", "名前は空にできません。", "이름은 비울 수 없습니다."),
    ("err.category_text", "分类必须是文字。", "分類必須是文字。", "The category must be text.", "分類は文字である必要があります。", "분류는 텍스트여야 합니다."),
    ("err.github_asset", "GitHub 地址应使用 Release 附件识别。", "GitHub 位址應使用 Release 附件識別。", "A GitHub address should be recognized from a Release asset.", "GitHub アドレスは Release の添付から識別してください。", "GitHub 주소는 Release 첨부로 식별해야 합니다."),
    ("err.bad_filename", "请填写有效的安装包文件名。", "請填寫有效的安裝包檔名。", "Enter a valid installer file name.", "有効なインストール包のファイル名を入力してください。", "올바른 설치 파일 이름을 입력하세요."),
    ("err.read_catalog", "无法读取自定义清单 %s：%s", "無法讀取自訂清單 %s：%s", "Could not read custom catalog %s: %s", "カスタムカタログ %s を読めません：%s", "사용자 목록 %s 을(를) 읽을 수 없습니다: %s"),
    ("err.bad_shard", "自定义分片必须是含 id 的条目数组：%s", "自訂分片必須是含 id 的項目陣列：%s", "A custom shard must be an array of entries with id: %s", "カスタムシャードは id を持つ項目の配列である必要があります：%s", "사용자 샤드는 id 가 있는 항목 배열이어야 합니다: %s"),
    ("err.bad_backup", "备份格式不正确，未恢复。", "備份格式不正確，未復原。", "The backup format is invalid, so nothing was restored.", "バックアップ形式が正しくないため、元に戻していません。", "백업 형식이 올바르지 않아 되돌리지 않았습니다."),
    ("err.bad_backup_path", "备份包含无效路径，未恢复。", "備份包含無效路徑，未復原。", "The backup contains an invalid path, so nothing was restored.", "バックアップに無効なパスがあるため、元に戻していません。", "백업에 잘못된 경로가 있어 되돌리지 않았습니다."),
    ("err.bad_export", "不是有效的自定义清单导出文件。", "不是有效的自訂清單匯出檔案。", "This is not a valid custom-catalog export.", "有効なカスタムカタログの書き出しファイルではありません。", "올바른 사용자 목록 내보내기 파일이 아닙니다."),
    ("err.bad_import_entry", "导入文件的条目格式无效。", "匯入檔案的項目格式無效。", "An entry in the import file is invalid.", "インポートファイルの項目形式が無効です。", "가져오기 파일의 항목 형식이 잘못되었습니다."),
    ("err.bad_import_platform", "导入文件包含无效的平台或条目。", "匯入檔案包含無效的平台或項目。", "The import file contains an invalid platform or entry.", "インポートファイルに無効なプラットフォームまたは項目があります。", "가져오기 파일에 잘못된 플랫폼 또는 항목이 있습니다."),
    ("err.import_missing", "导入条目缺少有效仓库或附件名。", "匯入項目缺少有效倉庫或附件名。", "An imported entry is missing a valid repository or asset name.", "インポート項目に有効なリポジトリまたは添付名がありません。", "가져온 항목에 올바른 저장소 또는 첨부 이름이 없습니다."),
    ("err.bad_id", "无效的平台或条目 id。", "無效的平台或項目 id。", "Invalid platform or entry id.", "無効なプラットフォームまたは項目 id です。", "잘못된 플랫폼 또는 항목 id 입니다."),
    ("err.duplicate_add", "同一次添加中选择了重复条目。", "同一次新增中選擇了重複項目。", "The same entry was selected more than once in this add.", "同じ追加の中で重複する項目が選ばれています。", "같은 추가에서 중복 항목을 선택했습니다."),
    ("err.exists", "条目已存在，请确认替换：%s / %s", "項目已存在，請確認取代：%s / %s", "The entry already exists. Confirm replacement: %s / %s", "項目が既にあります。置き換えるか確認してください：%s / %s", "항목이 이미 있습니다. 바꿀지 확인하세요: %s / %s"),
    ("err.missing_entry", "条目不存在。", "項目不存在。", "The entry does not exist.", "項目がありません。", "항목이 없습니다."),
    ("err.bad_index", "请输入有效序号，可用逗号分隔。", "請輸入有效編號，可用逗號分隔。", "Enter valid numbers, separated by commas.", "有効な番号を、コンマ区切りで入力してください。", "올바른 번호를 쉼표로 구분해 입력하세요."),
    ("err.index_range", "序号超出范围。", "編號超出範圍。", "A number is out of range.", "番号が範囲外です。", "번호가 범위를 벗어났습니다."),
    ("err.no_github", "GitHub 未找到匹配的公开仓库。", "GitHub 未找到相符的公開倉庫。", "GitHub found no matching public repository.", "GitHub で一致する公開リポジトリが見つかりません。", "GitHub 에서 맞는 공개 저장소를 찾지 못했습니다."),
    ("err.one_repo", "请一次选择一个仓库。", "請一次選擇一個倉庫。", "Select one repository at a time.", "リポジトリは一度に一つ選んでください。", "저장소는 한 번에 하나만 선택하세요."),
    ("err.repo_unavailable", "仓库不存在或当前不可访问。", "倉庫不存在或目前無法存取。", "The repository does not exist or cannot be reached.", "リポジトリが存在しないか、現在アクセスできません。", "저장소가 없거나 지금 접근할 수 없습니다."),
    ("err.no_release", "没有可读取的 Release；可粘贴具体 Release 地址重试。", "沒有可讀取的 Release；可貼上具體 Release 位址重試。", "No Release could be read. Paste a specific Release address and try again.", "読み取れる Release がありません。具体的な Release アドレスを貼って再試行できます。", "읽을 수 있는 Release 가 없습니다. 구체적인 Release 주소를 붙여 다시 시도하세요."),
    ("err.no_known_asset", "这个 Release 没有可识别的安装包或附件。", "這個 Release 沒有可識別的安裝包或附件。", "This Release has no recognized installer or asset.", "この Release には識別できるインストール包または添付がありません。", "이 Release 에는 알아볼 수 있는 설치 파일이나 첨부가 없습니다."),
    ("err.unknown_format", "未识别到支持的安装包格式。", "未識別到支援的安裝包格式。", "No supported installer format was recognized.", "対応しているインストール包形式を識別できませんでした。", "지원하는 설치 파일 형식을 알아보지 못했습니다."),
    ("err.one_platform", "修改已有条目时请只选择一个平台和安装包。", "修改已有項目時請只選擇一個平台和安裝包。", "When editing an existing entry, choose only one platform and one installer.", "既存の項目を変更するときは、プラットフォームとインストール包を一つずつ選んでください。", "기존 항목을 수정할 때는 플랫폼과 설치 파일을 하나씩만 선택하세요."),
)


def _tables() -> dict[str, dict[str, str]]:
    tables = {lang: {} for lang in SUPPORTED}
    for row in _ROWS:
        key, *values = row
        if len(values) != len(SUPPORTED):
            raise RuntimeError("ui string row %s has %d languages" % (key, len(values)))
        for lang, value in zip(SUPPORTED, values):
            if key in tables[lang]:
                raise RuntimeError("duplicate ui string %s" % key)
            tables[lang][key] = value
    return tables


STRINGS = _tables()

_CANONICAL = {
    "绿色/便携版": "kind.portable",
    "安装版": "kind.installer",
    "发布附件": "kind.release",
    "通用": "arch.universal",
    "未标明": "arch.unspecified",
}


def resolve_tag(raw: str | None) -> str | None:
    """精确区域，其次语言主标签。zh 归 zh-CN。其它非空语言归 en。空或 C/POSIX 视为无法识别。"""
    text = (raw or "").strip()
    if not text:
        return None
    text = text.split(".", 1)[0].split("@", 1)[0].replace("_", "-")
    parts = [part for part in text.split("-") if part]
    if not parts:
        return None
    lang = parts[0].lower()
    if lang in ("c", "posix"):
        return None
    region = next((part.upper() for part in parts[1:] if len(part) == 2 and part.isalpha()), "")
    exact = "%s-%s" % (lang, region) if region else lang
    if exact in STRINGS:
        return exact
    if lang == "zh":
        return "zh-CN"
    if lang in STRINGS:
        return lang
    if lang.isalpha():
        return "en"
    return None


def _windows_ui_language() -> int | None:
    if os.name != "nt":
        return None
    try:
        import ctypes

        value = int(ctypes.windll.kernel32.GetUserDefaultUILanguage())
    except (AttributeError, OSError, ValueError):
        return None
    return value or None


def _langid_to_tag(langid: int) -> str:
    primary = langid & 0x3FF
    sub = (langid >> 10) & 0x3F
    if primary == 0x04:
        if sub == 0x01:
            return "zh-TW"
        if sub == 0x02:
            return "zh-CN"
        if sub == 0x03:
            return "zh-HK"
        if sub == 0x04:
            return "zh-SG"
        if sub == 0x05:
            return "zh-MO"
        return "zh"
    names = {0x09: "en", 0x11: "ja", 0x12: "ko"}
    if primary in names:
        return names[primary]
    if primary == 0:
        return ""
    return "und"


def detect_language(environ=None, win_langid=_MISSING) -> str:
    """GH_RELEASE_FETCH_LANG，其次 LC_ALL / LANG，再其次 Windows UI 语言。失败时为 zh-CN。"""
    env = os.environ if environ is None else environ
    override = (env.get(LANG_ENV) or "").strip()
    if override:
        return resolve_tag(override) or "zh-CN"
    for key in ("LC_ALL", "LANG"):
        resolved = resolve_tag(env.get(key) or "")
        if resolved:
            return resolved
    langid = _windows_ui_language() if win_langid is _MISSING else win_langid
    if langid:
        resolved = resolve_tag(_langid_to_tag(int(langid)))
        if resolved:
            return resolved
    return "zh-CN"


def t(key: str, *args) -> str:
    lang = detect_language()
    template = STRINGS.get(lang, {}).get(key)
    if template is None:
        template = STRINGS["zh-CN"].get(key, key)
    return template % args if args else template


def display_term(value: str) -> str:
    mapped = _CANONICAL.get(value or "")
    return t(mapped) if mapped else (value or "")


def join_items(items, *, semi: bool = False) -> str:
    return t("sep.semi" if semi else "sep.list").join(str(item) for item in items)
