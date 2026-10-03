<div align="center">

# 🏢 Malan Skills for Office Efficiency

**码岚办公提效 Skill 集 · 面向办公与组织效率提升的 Agent Skill 集合**

把办公室里**重复、耗时、易错**的工作流封装成可复用的 Agent Skill：批量筛简历、产出会议纪要与行动项、生成周报与数据分析、沉淀 SOP 与入职流程。

[![skills](https://img.shields.io/badge/skills-1-blueviolet?style=flat-square)](#sec-1)
[![roadmap](https://img.shields.io/badge/roadmap-7%20planned-lightgrey?style=flat-square)](#sec-5)
[![license](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![python](https://img.shields.io/badge/python-%3E%3D3.9-blue?style=flat-square)](#sec-7)
[![validate](actions/workflows/validate-skills.yml/badge.svg)](actions/workflows/validate-skills.yml)
[![spec](https://img.shields.io/badge/spec-Agent%20Skills-ff69b4?style=flat-square)](https://agentskills.io/specification)
[![plugin](https://img.shields.io/badge/plugin-Claude%20Code-8a5cf5?style=flat-square)](#sec-2)

</div>

> 本仓库收录**办公与组织效率**方向上成熟的 Agent Skill，同时是一个 **[Claude Code 插件](https://code.claude.com/docs/en/plugins)** 和一个 **[Agent Skills](https://agentskills.io/specification) 集合**：一个 Skill = 一个独立目录（`SKILL.md` + 可选 `scripts/` `references/` `assets/`），装上即用，也可被单独发现、单独安装。
>
> An open-source collection of Agent Skills for office and organizational productivity, shipped as a Claude Code plugin. Each skill is a self-contained directory with a `SKILL.md` manifest plus runnable scripts and references, and is installable on its own.

---

## 目录 / Contents

| # | 章节 | 内容 |
|---|---|---|
| 1 | [工程内容与分布](#sec-1) | 仓库里有什么、各文件职责、Skill 清单与分类 |
| 2 | [安装与使用](#sec-2) | 插件安装、单独安装、使用示例 |
| 3 | [工程结构](#sec-3) | 目录树与组织约定 |
| 4 | [Skill 编写规范](#sec-4) | frontmatter、自包含约定、文件预算、命名与分类 |
| 5 | [能力地图与规划](#sec-5) | 四大域、已完成与规划中 |
| 6 | [新增一个 Skill](#sec-6) | 7 步流程与校验清单 |
| 7 | [质量校验](#sec-7) | 本地校验命令与当前状态 |
| 8 | [FAQ](#sec-8) | 能力边界与常见问题 |
| 9 | [参与贡献](#sec-9) | 贡献流程与发布检查项 |

---

<a id="sec-1"></a>
## 1. 工程内容与分布 / What's in this repo

### 1.1 仓库级文件

| 文件 | 职责 |
|---|---|
| `README.md` | 工程说明：内容分布、规范、规划、用法（本文件） |
| [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) | **Claude Code 插件清单**。声明插件名、版本、作者、关键词；Skill 目录默认扫描 `skills/` |
| [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) | **插件市场清单**。本仓库同时是插件与市场，别人添加一次即可安装 |
| [`skills/`](skills) | **全部 Skill**，每个一个独立目录，完全自包含 |
| [`skills.json`](skills.json) | **机器可读 Skill 注册表**。每个 Skill 的 `name` / `category` / `keywords` / `path` / `scripts` / `runtime`，供脚本或 Agent 直接解析做意图匹配；另含 `categories` 分类体系与 `roadmap` 规划 |
| [`llms.txt`](llms.txt) | 面向 LLM 与抓取器的纯文本索引：Skill 清单、分类、编写约定 |
| [`tools/validate_skills.py`](tools/validate_skills.py) | 仓库级校验：清单合法性、frontmatter 合规、**Skill 自包含**、三处索引一致性 |
| `.github/workflows/` | CI：每次 push / PR 自动跑校验 |
| `LICENSE` | MIT 许可 |
| `robots.txt` / `sitemap.xml` | 站点抓取入口（配合 GitHub Pages） |

<a id="sec-1-2"></a>
### 1.2 Skill 清单

> 与 [`skills.json`](skills.json) 保持同步，新增 Skill 时同时更新两处。

| Skill | 分类 | 说明 | 脚本 |
|---|---|---|---|
| **[`resume-screening`](skills/resume-screening/SKILL.md)**<br>简历批量筛选与岗位匹配度评分<br><sub>Batch Resume Screening & Job-Fit Scoring</sub> | `talent-acquisition` 招聘与人才评估 | 解析 PDF / Word / TXT / MD 简历，依据岗位评分模型逐维度打分（5 个维度各 20 分，总分 100 分，硬性淘汰规则优先执行），输出候选人评分汇总表、初筛结论（≥80 分）与面试侧重点建议 | 3 个 Python 脚本 |

Skill 按业务域组织，计划覆盖四域：

| 业务域 | `category` | 典型任务 |
|---|---|---|
| 招聘与人才评估 | `talent-acquisition` | 简历批量筛选、岗位匹配度评分、JD 撰写、结构化面试题库、Offer 对比 |
| 会议与协同办公 | `meeting-collaboration` | 会议纪要、行动项提取与闭环、议程生成、决策记录、待办跟踪 |
| 文档与数据处理 | `document-processing` | 周报月报与复盘报告、表格与数据清洗分析、文档审校、模板批量生成 |
| 组织与团队效能 | `team-effectiveness` | SOP 与流程沉淀、新人入职引导、绩效评估材料、1-on-1 纪要、知识库整理 |

---

<a id="sec-2"></a>
## 2. 安装与使用 / Install & Use

### 2.1 作为 Claude Code 插件安装（推荐）

本仓库自带插件清单与市场清单，两条命令即可装上全部 Skill：

```bash
# 添加插件市场
claude plugin marketplace add malan-skills/malanskills_for_office_efficiency

# 安装插件
claude plugin install malanskills-for-office-efficiency@malanskills-office-efficiency
```

装好后每个 Skill 都带插件名前缀，可直接调用：

```
/malanskills-for-office-efficiency:resume-screening
```

**本地开发调试**（不发布，直接挂载当前仓库）：

```bash
claude --plugin-dir /path/to/malanskills_for_office_efficiency
```

### 2.2 单独安装某个 Skill

| 作用域 Scope | 路径 Path |
|---|---|
| 用户级 User | `~/.claude/skills/resume-screening/` |
| 项目级 Project | `<项目根>/.claude/skills/resume-screening/` |
| CodeBuddy | `~/.codebuddy/skills/resume-screening/` |

```bash
git clone https://github.com/malan-skills/malanskills_for_office_efficiency.git
cd malanskills_for_office_efficiency

# 复制单个 Skill 到用户级目录（它本身就是自包含的）
cp -r skills/resume-screening ~/.claude/skills/

# 或用 Agent Skills CLI 只取一个
npx skills add malan-skills/malanskills_for_office_efficiency --skill resume-screening
```

### 2.3 校验

```bash
# 清单合法性 + frontmatter 合规 + Skill 自包含 + 三处索引一致性
python3 tools/validate_skills.py

# Claude Code 官方校验（需本机已装 Claude Code）
claude plugin validate . --strict
```

### 2.4 使用示例

直接用自然语言提出需求，Agent 会依据 `description` 自动命中对应 Skill：

| 场景 | 中文提问 | English prompt |
|---|---|---|
| 简历筛选 | "帮我评估这 5 份简历对「高级后端开发工程师」岗位的匹配度" | "Screen these 5 resumes against the Senior Backend Engineer role and rank them" |
| 岗位匹配 | "这批简历里哪些能进面试？给出排序和理由" | "Which of these candidates should go to interview? Give me a ranked shortlist" |
| 新增岗位 | "给「数据分析师」岗位补一份评分模型" | "Add a scorecard for the Data Analyst role" |

每个 Skill 的详细用法见其目录下的 README：[`skills/resume-screening/README.md`](skills/resume-screening/README.md)。

> **一个 Skill 一次只做一件事**：请求里带上文件与目标对象（岗位、项目、周期），命中率最高。

---

<a id="sec-3"></a>
## 3. 工程结构 / Repository Layout

```text
malanskills_for_office_efficiency/
├── .claude-plugin/
│   ├── plugin.json                   # 插件清单：name / version / author / keywords
│   └── marketplace.json              # 市场清单：owner / plugins[]（source 指向本仓库）
├── skills/                           # ← 全部 Skill，插件默认扫描此目录
│   ├── resume-screening/             #   Skill 1：简历批量筛选（招聘与人才评估域）
│   │   ├── SKILL.md                  #   必需：frontmatter + 路径约定 + 指令正文
│   │   ├── README.md                 #   该 Skill 的独立说明与用法
│   │   ├── references/               #   领域知识，按需读取
│   │   │   ├── scoring-rubric.md     #   5 维度评分细则与硬性淘汰规则优先级
│   │   │   └── jobs/
│   │   │       ├── _index.md         #   岗位索引（岗位名 → 文件路径 → 硬性规则）
│   │   │       └── 高级后端开发工程师.md  #   岗位评分模型原文
│   │   └── scripts/                  #   确定性计算，零框架依赖
│   │       ├── extract_resume_text.py     # 简历文本提取（PDF / docx / txt / md）
│   │       ├── calculate_match_score.py   # 分项分数 → 总分 / 初筛 / 面试建议
│   │       └── summarize_batch.py         # 多份结果 JSON → Markdown 汇总表格
│   └── <future-skill-name>/          #   后续 Skill 遵循完全相同的形状
│       ├── SKILL.md
│       ├── README.md
│       └── scripts/  references/  assets/  examples/
│
├── README.md                         # 工程说明（本文件）
├── skills.json                       # 机器可读 Skill 注册表
├── llms.txt                          # LLM / 抓取器索引
├── robots.txt / sitemap.xml          # 抓取入口
├── tools/
│   └── validate_skills.py            # 仓库级校验脚本（纯标准库）
├── .github/workflows/
│   └── validate-skills.yml           # CI
├── LICENSE                           # MIT
└── .gitignore
```

### 组织约定

| 约定 | 说明 |
|---|---|
| **一个 Skill 一个目录，放在 `skills/` 下** | `skills/` 是 Claude Code 插件的默认发现目录，也是各类扫描器的通用递归入口；层级最浅，路径解析最稳 |
| **每个 Skill 完全自包含** | 只引用自身目录内的文件；路径相对 Skill 根目录；**禁止绝对路径**、禁止 `../` 越界、禁止依赖仓库根的文件。复制单个目录即可独立运行 |
| 目录名 == `name` | frontmatter 的 `name` 必须与所在目录名逐字一致（kebab-case），否则部分加载器无法定位资源 |
| `SKILL.md` 是唯一入口 | 正文只放流程、判断规则、资源调度；细节下沉到 `references/`、`examples/` |
| `scripts/` 承担确定性计算 | 能用脚本算的不让模型猜；脚本可直接执行而不进入上下文，且只接受显式入参、不猜路径 |
| 每个 Skill 配一个 README | 目录级 README 让该 Skill 被单独浏览、单独安装时仍是完整可读的页面 |
| 领域数据可扩展 | 领域知识（如岗位评分模型）放 `references/<domain>/`，新增条目不改 `SKILL.md` |
| 仓库根维护注册表 | `skills.json` / `llms.txt` / README 索引表三处同步，人读与机器读各取所需 |

---

<a id="sec-4"></a>
## 4. Skill 编写规范 / Skill Spec & Conventions

遵循 [Agent Skills Specification](https://agentskills.io/specification)。✅ 为硬性约束，⭐ 为推荐实践。

### 4.1 `SKILL.md` frontmatter

| 字段 | 必填 | 约束 | 用途 |
|---|:---:|---|---|
| `name` | ✅ | 1–64 字符；仅 `a-z` `0-9` `-`；不以 `-` 开头/结尾；无连续 `--`；**必须与所在目录名完全一致** | Skill 唯一标识 |
| `description` | ✅ | 1–1024 字符；须写清「做什么」+「何时使用」+ 触发关键词；**中英双语** | 决定 Agent 是否在会话中选中该 Skill |
| `license` | ➖ | SPDX 名称或指向随包许可证文件 | 合规 |
| `compatibility` | ➖ | ≤500 字符；运行环境、系统包、网络访问要求 | 避免在错误环境调用 |
| `metadata` | ➖ | `字符串: 字符串` 映射，承载 `category` / `version` / `keywords` | 分类归档与检索 |
| `allowed-tools` | ➖ | 空格分隔的预批准工具名（实验性） | 沙箱授权 |

```yaml
---
name: resume-screening               # 必须等于目录名
description: >-
  简历批量筛选与岗位匹配度评分技能。当用户提交一份或多份简历附件……输出候选人评分汇总表格。
  Batch resume screening and job-fit scoring: parse PDF/DOCX/TXT/MD resumes, score each
  candidate against a role scorecard, and output a ranked shortlist table.
  Trigger keywords: 简历筛选, 简历打分, resume screening, candidate evaluation, shortlist.
license: MIT
compatibility: Python >= 3.9；PDF 解析需 pypdf 之一；不访问网络。 / No network access.
metadata:
  category: talent-acquisition
  version: "1.0.0"
  keywords: "简历筛选,简历打分,resume screening,candidate evaluation"
allowed-tools: Read Write Bash Glob Grep
---
```

⭐ `description` 是**唯一**常驻上下文的内容，也是 Agent 选中 Skill 的唯一依据：中英双语各写一遍，触发词要覆盖「用户会怎么说」，而不只是「功能叫什么」。

### 4.2 自包含约定（硬性）

一个 Skill 目录被复制到任何位置都必须能独立运行，因此：

| 规则 | 做法 |
|---|---|
| 路径相对 Skill 根 | 文档与脚本中引用资源一律写 `references/...`、`scripts/...`，并声明「相对本 `SKILL.md` 所在目录」 |
| 禁止绝对路径 | 不出现 `/Users/...`、`/home/...`、`C:\...` |
| 禁止越界 | 不用 `../` 跳出本目录，不引用仓库根的 `skills.json`、`tools/` 等 |
| 脚本不猜路径 | 脚本只接受显式入参（文件/目录参数），不在内部拼接仓库结构路径 |
| 领域数据内置 | 所需领域资料放在自己的 `references/` 下，不共享仓库级文件 |

以上五条由 `tools/validate_skills.py` 自动检查。

### 4.3 文件预算（渐进式披露）

| 层级 | 加载时机 | 预算 | 说明 |
|---|---|---|---|
| ① 元数据（`name` + `description`） | 每次会话常驻 | ≈100 tokens | 所以描述要「密」而短 |
| ② `SKILL.md` 正文 | Skill 被命中时 | <5k tokens，**≤500 行** | 只放流程、判断规则、调度逻辑 |
| ③ `scripts/` `references/` `README.md` | 按需 | 无限 | 脚本可直接执行；参考资料按需读取 |

⭐ **一条内容只放一处**：字段表、长示例、领域数据细节一律下沉到 `references/` 或 `examples/`。

### 4.4 命名与分类

- **目录名 / `name`**：kebab-case，`<对象>-<动作>` 或 `<业务域>-<任务>`，如 `resume-screening`、`meeting-minutes`、`spreadsheet-analyst`；两者必须一致。
- **`metadata.category`**：取[四域分类](#sec-1-2)中四个 `category` 之一。
- **文件命名**：脚本 `snake_case.py`；参考文档语义化小写命名（如 `references/scoring-rubric.md`）。

---

<a id="sec-5"></a>
## 5. 能力地图与规划 / Capability Map & Roadmap

### 5.1 四域 × Skill 规划

| 业务域 | 现有 Skill | 规划中 Skill |
|---|---|---|
| 招聘与人才评估<br>`talent-acquisition` | [`resume-screening`](skills/resume-screening/SKILL.md) | `job-description-builder`、`interview-kit`、`offer-decision-matrix` |
| 会议与协同办公<br>`meeting-collaboration` | — | `meeting-minutes`、`action-item-tracker`、`decision-log` |
| 文档与数据处理<br>`document-processing` | — | `report-builder`、`spreadsheet-analyst`、`document-review` |
| 组织与团队效能<br>`team-effectiveness` | — | `sop-writer`、`onboarding-checklist`、`performance-review` |

每个 Skill 独立成目录、独立发布：只关心招聘筛选的使用者不需要读文档处理的脚本。规划中的条目同步登记在 [`skills.json`](skills.json) 的 `roadmap` 字段。

### 5.2 工程进度

**已完成**

- [x] `resume-screening` Skill（招聘域：3 个脚本 + 评分细则 + 岗位评分模型 + 域内索引）
- [x] 目录名与 frontmatter `name` 对齐
- [x] 改为插件形态：Skill 统一置于 `skills/`，新增 `.claude-plugin/plugin.json` 与 `marketplace.json`
- [x] 自包含改造：Skill 内全部路径相对自身根目录，无绝对路径、无跨目录依赖
- [x] frontmatter 补齐 `license` / `compatibility` / `metadata`（`category`、`version`、`keywords`）/ `allowed-tools`
- [x] 仓库骨架：`skills.json` 注册表、`llms.txt`、`robots.txt` / `sitemap.xml`、MIT License、`.gitignore`
- [x] `tools/validate_skills.py` 校验脚本（含插件清单与自包含检查）+ GitHub Actions CI
- [x] 双语 README，每个 Skill 目录自带 README

**发布前一次性配置**

- [ ] 仓库简介填为 `skills.json` 中的 `summary_zh` / `summary_en`
- [ ] 将 `skills.json` 的 `topics` 同步为仓库 Topics（GitHub 最多 20 个）
- [ ] 配置 Social preview 预览图
- [ ] 开启 GitHub Pages（`https://malan-skills.github.io/malanskills_for_office_efficiency/`），使 `sitemap.xml` / `robots.txt` 生效
- [ ] 本地跑通 `claude plugin validate . --strict`，打首个 tag / Release

**规划中**

- [ ] 会议与协同域：`meeting-minutes`、`action-item-tracker`、`decision-log`
- [ ] 文档与数据域：`report-builder`、`spreadsheet-analyst`、`document-review`
- [ ] 组织与效能域：`sop-writer`、`onboarding-checklist`、`performance-review`
- [ ] 招聘域：`job-description-builder`、`interview-kit`
- [ ] 仓库级：更多岗位评分模型、真实数据源接入、发布自动化

---

<a id="sec-6"></a>
## 6. 新增一个 Skill / Adding a New Skill

<a id="sec-6-1"></a>
### 6.1 流程（7 步）

1. **建目录**：`git checkout -b feat/<skill-name>`，在 `skills/` 下创建与 skill 同名的 kebab-case 目录。
2. **写 `SKILL.md`**：frontmatter 的 `name` 必须等于目录名；`description` 写清「做什么 + 何时使用 + 触发词」，中英双语，≤1024 字符；正文第一节写「路径约定」，声明所有路径相对本 Skill 根目录。
3. **搭资源目录**：`scripts/`（确定性计算）、`references/`（长文档与领域数据）、`assets/`（模板）、`examples/`（调用示例），按需创建。
4. **写指令正文**：目标 ≤500 行，只保留流程、判断规则、资源调度逻辑。
5. **写 `README.md` 与 `examples/`**：至少 3 个中英文提问示例，说明输入、输出与依赖。
6. **注册**：更新 [`skills.json`](skills.json) 的 `skills` 与 `llms.txt`，并在本文档的 [Skill 清单](#sec-1-2) 增行。
7. **自检 + PR**：跑 `python3 tools/validate_skills.py`（自包含检查会拦住绝对路径与越界引用），PR 描述中贴一段真实产出样例。

<a id="sec-6-2"></a>
### 6.2 校验清单

- [ ] 目录位于 `skills/` 下，目录名 == frontmatter `name`（kebab-case，无连续 `--`）
- [ ] `description` 含「做什么 + 何时使用 + 触发词」，中英双语，≤1024 字符
- [ ] `metadata` 含 `category`（四域之一）、`version`、`keywords`
- [ ] `SKILL.md` ≤500 行，且与 `references/` 无内容重复
- [ ] **自包含**：无绝对路径、无 `../` 越界、脚本不拼接仓库结构路径、引用的内部文件均存在
- [ ] 数值计算全部落在 `scripts/`，Skill 正文明确写「禁止手工编造数值」
- [ ] 目录内有 `README.md`（中英双语，含用法示例）
- [ ] `SKILL.md` 内写明能力边界与需人工决策项
- [ ] `python3 tools/validate_skills.py` 与 `claude plugin validate . --strict` 均通过

---

<a id="sec-7"></a>
## 7. 质量校验 / Quality Gates

```bash
# 规范校验：清单合法性、frontmatter、自包含、三处索引一致性
python3 tools/validate_skills.py

# Claude Code 官方校验（需本机已装 Claude Code）
claude plugin validate . --strict

# 注册表 JSON 合法性
python3 -c "import json;print(len(json.load(open('skills.json'))['skills']))"

# 脚本可编译
python3 -m compileall -q skills
```

**当前状态**：`tools/validate_skills.py` 全部通过（1 个 Skill，0 error / 0 warning）；CI 在每次 push / PR 自动执行结构校验与 JSON 校验。

**校验项**：插件 `name` 合规且非保留名、manifest 必填字段、marketplace 条目名与 manifest 名一致、目录名与 `name` 一致、`name` 为 kebab-case、`description` 长度与中英双语、`metadata.category` 属于已声明分类、`metadata.version` 与 `keywords` 齐备、`SKILL.md` ≤500 行、**每个 Skill 无绝对路径 / 无越界引用 / 内部引用均存在**、每个 Skill 配有 README、`skills.json` 与磁盘目录一一对应、`llms.txt` 与 `README.md` 均引用全部 Skill 路径。

---

<a id="sec-8"></a>
## 8. FAQ

**Q：Skill 放在 `skills/` 下会不会不被其他 Agent 发现？**
A：不会。`skills/` 是 Claude Code 插件的默认扫描目录，同时也是各类扫描器最通用的递归入口（`skills/*/SKILL.md`）。目录名仍需与 frontmatter 的 `name` 一致。

**Q：这些 Skill 会去爬真实数据吗？**
A：不会。以 `resume-screening` 为例，输入是你上传的简历附件，脚本在本地做解析与确定性计算，不发起网络请求。接入真实数据源时替换数据层即可。/ No live crawling — local parsing and deterministic computation only; swap the data layer to go live.

**Q：打分结果能替代人工决策吗？**
A：不能。评分是把评估标准显性化、让不同人按同一把尺子打分，输出是**可复现的辅助判断**，最终录用与淘汰仍需人工确认。

**Q：怎么判断该用哪个 Skill？**
A：读 [`skills.json`](skills.json)，用用户提问中的关键词匹配 `keywords` 与 `category`。命中 `resume-screening` 的典型信号：「筛简历 / 简历打分 / 匹配度 / 这批简历谁能进面试 / resume screening / shortlist」。

**Q：SKILL.md 会不会占满 Agent 上下文？**
A：不会。分层加载：常驻的只有 `name` + `description`（≈100 tokens）；命中才加载正文（<5k tokens）；脚本可直接执行而不进上下文。

**Q：能只拿走一个 Skill 吗？**
A：能。`skills/<name>/` 是自包含的，整目录复制到 `~/.claude/skills/` 即可运行，不依赖仓库其他文件。

**Q：只有做办公的人才需要吗？**
A：不是。业务域里的 JD 撰写、面试题库、绩效评估材料、SOP 沉淀同样适用于招聘、HR、管理岗。

**Q：能商用 / 二次分发吗？**
A：可以，MIT 许可，保留 `LICENSE` 与版权声明即可。

---

<a id="sec-9"></a>
## 9. 参与贡献 / Contributing

1. Fork 本仓库并新建分支：`feat/<skill-name>` 或 `fix/<topic>`。
2. 按 [6.1](#sec-6-1) 完成 7 步流程，确保 [6.2](#sec-6-2) 全绿。
3. PR 描述写清：解决什么办公场景问题、真实产出样例、校验命令输出。

## License

[MIT](LICENSE) © 2026 malanskills contributors
