# 多平台软件站 Implementation Plan

> **For agentic workers:** Execute tasks inline in this chat. Steps use checkbox tracking.

**Goal:** 在 website/ 实现多平台软件导航、静态详情页、搜索、下载入口和 SEO。

**Architecture:** Python 标准库读取既有平台 JSON，叠加人工精选元数据，生成独立 HTML 和浏览器搜索索引。原生 CSS/JavaScript 渐进增强，GitHub Pages 发布静态产物。

**Tech Stack:** Python 3.10+、HTML、CSS、JavaScript、unittest、GitHub Actions。

**Spec:** docs/software-directory-plan.zh-CN.md；用户补充：优化 SEO。

## Global Constraints

- 不修改既有下载器、个人文件及软件配置；输出到 dist/site/。
- 官方页面、商店、发布页分别标记；不把解析规则当作经过验证的安装包。
- 内容必须不运行 JavaScript 也可访问；正式域名通过 --site-url 注入。
- 不虚构评分、下载量、截图、免费价格或版本。

## Review Focus

- 目录中的第三方地址只允许 http/https，所有文本与内嵌 JSON 安全转义。
- 子路径部署、直接访问详情、404 页面资源路径正确。
- 无当前平台软件时提供空状态；系统识别不猜测 CPU。
- 下载解析失败时回退官方渠道，不错误标示最新版。
- 搜索结果页与低信息目录不制造大量重复索引页面。

## Tasks

- [x] 数据层：website/content.py 精选与分类，website/catalog.py 聚合平台；tests/test_website.py 验证合并、平台排除、危险 URL。
- [x] 站点：website/build.py 静态页面；website/assets/ 样式与搜索交互；验证全站内链与 SEO。
- [x] 下载：website/downloads.py 可选解析稳定 Release，平台/架构明确选择；测试源码包、预发布、架构和失败回退。
- [x] 发布：.github/workflows/website.yml、website/README.md；运行构建、测试及真实浏览器检查。

## Execution notes

- 当前仓库分支为 master，发布 workflow 据此配置。未提交、推送、部署或修改 DNS。
- 交付 41 个精选产品、12 个平台、18 个分类、7 个场景，聚合后目录为 1822 个产品；生成 82 个可索引页面。
- 验证：8 项 Python 单元/集成测试、JavaScript 语法检查、Chrome 实际交互测试、5 种屏幕宽度、无脚本访问、搜索失败回退、根路径与 /tools 子路径部署。
- SEO 验证：可索引页面标题唯一、单一 H1、描述、canonical、有效 JSON-LD、全站内链和 sitemap 一致性。
- 正式域名尚未提供，预览不写入虚构的域名或 canonical；Actions 根据 Pages 地址或 WEBSITE_SITE_URL 生成。
- 下载直接入口只覆盖可明确识别的精选 GitHub Release 安装包；其他产品提供官网/商店，不声称全量自动解析或实机验证。

## Visual direction

浅灰蓝 #f3f6fa、白 #ffffff、深墨蓝 #172b4d、蓝 #245edb、青 #087f8c、边线 #dde5ef。中文系统字体，标题 44px，正文 15px。左侧分类承担导航，主区域用紧凑的软件图标与用途介绍；精选、场景和目录具有不同密度。移动端分类改为横向入口。无外部字体和图标请求。
