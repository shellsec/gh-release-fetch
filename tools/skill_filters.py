"""Purpose filters for the desktop Agent Skills catalog."""

STAGES = {
    "选题与调研": ("panniantong/agent-reach", "mvanhorn/last30days-skill", "sansan0/trendradar"),
    "脚本与分镜": ("zenstory-ai/drama-skills", "vincentwei1021/video-shotcraft",
                 "vincentwei1021/anything2explainer", "lixiaoxiao9888-create/manju-laoli-skill"),
    "素材准备": ("yt-dlp/yt-dlp", "comfy-org/comfyui", "joeseesun/qiaomu-cut-skill"),
    "录音与配音": ("hexgrad/kokoro", "rhasspy/piper", "ohf-voice/piper1-gpl", "qwenaudio/cosyvoice"),
    "粗剪": ("breakthrough/pyscenedetect", "wyattblue/auto-editor", "kajisho5/ffmpeg-skill",
           "agentchengfeng/chengfeng-videocut-skills", "0xsline/openchatcut"),
    "字幕与精剪": ("systran/faster-whisper", "m-bain/whisperx", "tkarabela/pysubs2",
                  "kajisho5/ffmpeg-skill", "0xsline/openchatcut", "nateherkai/herk-edit-kit",
                  "remotion-dev/skills", "vincentwei1021/anything2explainer", "openfilm/openfilm"),
    "审片与导出": ("remotion-dev/skills", "kajisho5/ffmpeg-skill", "0xsline/openchatcut",
                  "nateherkai/herk-edit-kit", "vincentwei1021/anything2explainer", "openfilm/openfilm"),
    "封面与发布": ("jimliu/baoyu-skills", "joeseesun/qiaomu-mondo-poster-design",
                  "joeseesun/qiaomu-codex-imagegen", "comfy-org/comfyui", "dreammis/social-auto-upload"),
}
FULL_WORKFLOWS = {
    "njrhts2kvv-star/fredtalk": ("脚本与分镜", "粗剪", "字幕与精剪", "审片与导出"),
    "openmontageinc/openmontage": ("脚本与分镜", "素材准备", "录音与配音", "粗剪", "字幕与精剪", "审片与导出"),
    "calesthio/openmontage": ("脚本与分镜", "素材准备", "录音与配音", "粗剪", "字幕与精剪", "审片与导出"),
    "joeseesun/qiaomu-cut-skill": ("粗剪", "字幕与精剪", "审片与导出"),
}


def stages_for(app):
    repo = (app.get("repo_path") or "").casefold()
    explicit = app.get("视频流程")
    if isinstance(explicit, list):
        return {stage for stage in STAGES if stage in explicit}
    return {stage for stage, repos in STAGES.items() if repo in repos} | set(FULL_WORKFLOWS.get(repo, ()))


SKILL_FILTERS = {
    "办公与知识管理": {
        "客户与交付": (),
    },
    "增长与运营": {
        "调研与定位": ("marketing", "founder-skills", "opc-skills"),
        "搜索增长（SEO / GEO / AEO）": ("marketing", "seo-workflows", "open-source-growth"),
        "内容与渠道运营": ("marketing", "founder-skills", "opc-skills", "open-source-growth"),
        "转化与留存": ("marketing", "founder-skills", "opc-skills"),
        "数据与复盘": ("marketing",),
    },
    "开发与测试": {
        "开发工作流": (
            "superpowers", "addy-osmani", "matt-pocock", "karpathy", "claude-practices", "github-copilot-catalog",
            "ponytail", "graphify", "caveman", "understand-anything", "archify", "aegis", "elephant-goldfish-model",
            "qiaomu-goal-meta-skill", "creator", "anthropic-mcp-builder", "supabase",
        ),
        "前端与界面": (
            "vercel", "web-quality", "ui-ux-pro-max", "impeccable", "anthropic-frontend-design",
            "platform-design-skills", "expo-official", "modern-web-guidance-src", "stitch-skills",
        ),
        "测试与调试": ("superpowers", "playwright", "sentry", "agent-browser", "browser-skill", "web-quality", "aegis"),
        "代码与安全审查": ("superpowers", "addy-osmani", "aegis", "skillspector", "cloudflare-security-audit",
                            "elephant-goldfish-model"),
    },
    "发现技能": {
        "官方技能库": ("openai-catalog", "anthropic-catalog", "openai-plugins", "vercel-cli"),
        "搜索与目录": (
            "yunshu", "clawhub", "tencent-skillhub", "skills-sh", "skillsmp", "smithery-skills",
            "lobehub-skills", "buildwithclaude", "claude-code-templates", "iflytek-skillhub", "skill-fetch",
        ),
        "精选合集": (
            "voltagent", "awesome-claude-skills", "android-skill-index", "motion-skill-index",
            "seo-skill-index", "claude-skills-zh", "codex-community-index", "video-skill-index",
            "awesome-design-skills",
        ),
    },
    "写作与视觉创作": {
        "写作与改稿": (
            "baoyu", "nuwa", "patent-disclosure", "agency-creative", "lieflat-less-ai-tone", "humanizer",
            "humanizer-zh", "avoid-ai-writing", "qu-ai-wei", "humanize-chinese", "shuorenhua",
        ),
        "插画与生图": ("baoyu", "vane-gpt-image", "agency-creative", "pixelfx", "pixel-splats"),
        "海报与排版": (
            "baoyu", "agency-creative", "luobo-gzh-design", "luobo-ppt", "taste-skill", "huashu-design",
            "mengto", "scroll-world", "emil-design", "hallmark",
        ),
    },
}


def filter_options(category):
    if category == "视频与自媒体":
        return STAGES
    return SKILL_FILTERS.get(category, {})


def matches_filter(category, value, app):
    if category == "视频与自媒体":
        return value in stages_for(app)
    explicit = app.get("用途标签")
    if isinstance(explicit, list):
        return value in explicit or (
            category == "增长与运营"
            and value == "搜索增长（SEO / GEO / AEO）"
            and any(tag in explicit for tag in ("SEO", "GEO", "AEO"))
        )
    identifier = app["id"].removeprefix("agent-skill-")
    return identifier in filter_options(category).get(value, ())
