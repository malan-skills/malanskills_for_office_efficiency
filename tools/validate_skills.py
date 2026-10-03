#!/usr/bin/env python3
"""Repository-level validator for this Agent Skill collection / Claude Code plugin.

Pure standard library, no third-party dependencies. Run from anywhere:

    python3 tools/validate_skills.py

Checks performed
  1. Repository files exist (README / skills.json / llms.txt / LICENSE)
  2. Plugin + marketplace manifests are valid
  3. Every skill under skills/ has compliant frontmatter
  4. Every skill is SELF-CONTAINED: no absolute paths, no escaping the
     skill directory, and every referenced relative path really exists
  5. skills.json / llms.txt / README.md stay in sync with what is on disk

Exit code 0 = all hard checks passed, 1 = at least one hard check failed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
PLUGIN_DIR = ROOT / ".claude-plugin"
REGISTRY = ROOT / "skills.json"
INDEX = ROOT / "llms.txt"
README = ROOT / "README.md"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
RESERVED_PREFIXES = ("claude-", "anthropic-", "anthropics-", "cc-plugin-")
RESERVED_EXACT = {"claude", "anthropic", "anthropics", "claude-code", "claude-mods"}

# --- self-containment detectors -------------------------------------------
ABS_PATH_RES = [
    re.compile(r"/(?:Users|home|root)/[A-Za-z0-9._-]+/"),  # macOS / Linux 绝对路径
    re.compile(r"\b[A-Za-z]:\\{1,2}[A-Za-z0-9._-]+"),        # Windows 盘符路径
    re.compile(r"\]\(/[^)]*\)"),                            # Markdown 绝对链接
]
ESCAPE_RE = re.compile(r"(?<![\w.])\.\./(?=[A-Za-z0-9_一-鿿.-]+)")
REL_REF_RE = re.compile(
    r"(?<![\w/.-])((?:references|scripts|assets|examples)/[^\s`），。、；：\"'|]+)"
)

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def ok(msg: str) -> None:
    print(f"  \033[32mOK\033[0m    {msg}")


def section(title: str) -> None:
    print(f"\n\033[1m== {title} ==\033[0m")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the leading `---` YAML block with a deliberately small subset parser.

    Supports `key: value`, `key:` followed by an indented mapping (used by
    `metadata`), and folded scalars (`>-` / `>`).
    """
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip("\n")
    body = text[end + 4:]
    data: dict = {}
    current_key: str | None = None
    folding: str | None = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if folding is not None:
            if raw.startswith((" ", "\t")):
                data[folding] = (data[folding] + " " + raw.strip()).strip()
                continue
            folding = None
        if raw.startswith((" ", "\t")) and current_key:
            key, _, value = raw.strip().partition(":")
            bucket = data.get(current_key)
            if isinstance(bucket, dict):
                bucket[key.strip()] = value.strip().strip('"').strip("'")
            continue
        key, _, value = raw.partition(":")
        current_key = key.strip()
        value = value.strip()
        if value in (">-", ">", "|", "|-"):
            data[current_key] = ""
            folding = current_key
        elif value:
            data[current_key] = value.strip('"').strip("'")
        else:
            data[current_key] = {}
    return data, body


def check_manifests() -> None:
    section("插件清单 / Plugin manifests")
    plugin_json = PLUGIN_DIR / "plugin.json"
    market_json = PLUGIN_DIR / "marketplace.json"

    plugin: dict = {}
    if plugin_json.is_file():
        try:
            plugin = json.loads(plugin_json.read_text(encoding="utf-8"))
            ok(".claude-plugin/plugin.json 是合法 JSON")
        except json.JSONDecodeError as exc:
            fail(f"plugin.json JSON 解析失败: {exc}")
    else:
        fail(".claude-plugin/plugin.json 缺失")

    if plugin:
        name = plugin.get("name", "")
        if not name:
            fail("plugin.json 缺少必填字段 name")
        else:
            if not NAME_RE.match(name) or len(name) > 64:
                fail(f"plugin.json name ({name}) 必须是 kebab-case 且 <=64 字符")
            else:
                ok(f"plugin name = {name}")
            low = name.lower()
            if low.startswith(RESERVED_PREFIXES):
                fail(f"plugin.json name ({name}) 使用了保留前缀 {RESERVED_PREFIXES}")
            if low in RESERVED_EXACT:
                fail(f"plugin.json name ({name}) 是保留名")
        for field in ("description", "version", "license", "author", "keywords"):
            if field not in plugin:
                warn(f"plugin.json 建议补充 {field}")
        for path_field in ("skills", "commands", "agents", "hooks", "mcpServers"):
            value = plugin.get(path_field)
            items = value if isinstance(value, list) else ([value] if value else [])
            for item in items:
                if not isinstance(item, str):
                    continue
                if not item.startswith(("./", ".")):
                    fail(f"plugin.json 的 {path_field} 路径必须以 ./ 开头: {item}")
                if ".." in item:
                    fail(f"plugin.json 的 {path_field} 路径不得含 ..: {item}")
                if not (ROOT / item).resolve().exists():
                    fail(f"plugin.json 的 {path_field} 指向不存在的路径: {item}")
        ok("plugin.json 组件路径合法")

    if market_json.is_file():
        try:
            market = json.loads(market_json.read_text(encoding="utf-8"))
            ok(".claude-plugin/marketplace.json 是合法 JSON")
        except json.JSONDecodeError as exc:
            fail(f"marketplace.json JSON 解析失败: {exc}")
            market = {}
        for field in ("name", "owner", "plugins"):
            if field not in market:
                fail(f"marketplace.json 缺少必填字段 {field}")
        for entry in market.get("plugins", []) or []:
            if not entry.get("name"):
                fail("marketplace.json 的插件条目缺少 name")
            if not entry.get("source"):
                fail("marketplace.json 的插件条目缺少 source")
            if plugin and entry.get("name") != plugin.get("name"):
                fail(
                    "marketplace 条目名须与 plugin.json 的 name 一致，否则安装失败: "
                    f"{entry.get('name')} != {plugin.get('name')}"
                )
        if market.get("plugins"):
            ok(f"marketplace 声明 {len(market['plugins'])} 个插件")
    else:
        warn(".claude-plugin/marketplace.json 缺失（自用可省略，分发给他人时需要）")


def check_self_contained(path: Path) -> None:
    """一个 Skill 只能依赖自己目录内的文件。"""
    problems = 0
    for md in sorted(path.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        rel = md.relative_to(path)
        for rx in ABS_PATH_RES:
            m = rx.search(text)
            if m:
                fail(
                    f"{path.name}/{rel}: 出现绝对路径或绝对链接 “{m.group(0)}”，"
                    f"Skill 必须只引用自身目录内的相对路径"
                )
                problems += 1
        for m in ESCAPE_RE.finditer(text):
            token = m.group(0)
            if not str((md.parent / token).resolve()).startswith(str(path.resolve())):
                fail(f"{path.name}/{rel}: 路径 {token} 跳出了 Skill 目录")
                problems += 1
        for m in REL_REF_RE.finditer(text):
            ref = m.group(1).rstrip(".,;:")
            if not (path / ref).exists():
                fail(f"{path.name}/{rel}: 引用了不存在的文件 {ref}")
                problems += 1
    for py in sorted(path.rglob("*.py")):
        text = py.read_text(encoding="utf-8", errors="ignore")
        rel = py.relative_to(path)
        for rx in ABS_PATH_RES[:2]:
            m = rx.search(text)
            if m:
                warn(f"{path.name}/{rel}: 出现疑似硬编码绝对路径 “{m.group(0)}”")
        for m in re.finditer(r"""__file__\s*,\s*["']([^"']+)["']""", text):
            if ".." in m.group(1):
                fail(f"{path.name}/{rel}: 通过 __file__ 引用了 Skill 目录之外的路径")
                problems += 1
    if problems == 0:
        ok("自包含检查通过（无绝对路径、无越界引用、内部引用均存在）")


def check_skill(path: Path, categories: set[str]) -> None:
    print(f"\n\033[1m{path.relative_to(ROOT)}\033[0m")
    text = (path / "SKILL.md").read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    name = meta.get("name", "")
    if not name:
        fail(f"{path.name}: frontmatter 缺少 name")
    else:
        if name != path.name:
            fail(f"{path.name}: name ({name}) 与目录名不一致")
        else:
            ok("name == 目录名")
        if not NAME_RE.match(name) or len(name) > 64:
            fail(f"{path.name}: name 必须为 kebab-case 且 <=64 字符")

    description = meta.get("description", "")
    if not isinstance(description, str) or not description.strip():
        fail(f"{path.name}: description 缺失")
    else:
        desc = " ".join(description.split())
        if len(desc) > 1024:
            fail(f"{path.name}: description 超过 1024 字符 ({len(desc)})")
        else:
            ok(f"description 长度 {len(desc)} <= 1024")
        has_zh = bool(CJK_RE.search(desc))
        has_en = bool(re.search(r"[A-Za-z]{3,}", desc))
        if not has_zh:
            fail(f"{path.name}: description 缺少中文表述")
        if not has_en:
            fail(f"{path.name}: description 缺少英文触发词")
        if has_zh and has_en:
            ok("description 中英双语")

    for field in ("license", "compatibility"):
        if not meta.get(field):
            warn(f"{path.name}: frontmatter 建议补充 {field}")

    metadata = meta.get("metadata") or {}
    if not isinstance(metadata, dict) or not metadata:
        fail(f"{path.name}: metadata 缺失（至少需要 category 与 version）")
    else:
        category = metadata.get("category", "")
        if category not in categories:
            fail(f"{path.name}: metadata.category ({category}) 不在 skills.json 的 categories 中")
        else:
            ok(f"metadata.category = {category}")
        if not metadata.get("version"):
            fail(f"{path.name}: metadata.version 缺失")
        else:
            ok(f"metadata.version = {metadata['version']}")
        keywords = [k for k in re.split(r"[,;]", metadata.get("keywords", "")) if k.strip()]
        if len(keywords) < 5:
            warn(f"{path.name}: metadata.keywords 建议 >=5 个中英关键词")
        else:
            ok(f"metadata.keywords {len(keywords)} 个")

    lines = len(body.strip().splitlines())
    if lines > 500:
        fail(f"{path.name}: SKILL.md 正文 {lines} 行，超过 500 行预算")
    else:
        ok(f"SKILL.md 正文 {lines} 行 (<=500)")

    if not (path / "README.md").is_file():
        warn(f"{path.name}: 缺少 README.md（该目录将无法作为独立页面被浏览）")
    else:
        ok("存在 README.md")

    for required in ("references", "scripts"):
        if not (path / required).is_dir():
            warn(f"{path.name}: 建议提供 {required}/ 目录")

    check_self_contained(path)


def main() -> int:
    section("仓库文件 / Repository files")
    for required in ("README.md", "skills.json", "llms.txt", "LICENSE"):
        if (ROOT / required).is_file():
            ok(f"{required} 存在")
        else:
            fail(f"{required} 缺失")

    if not REGISTRY.is_file():
        print("\n注册表缺失，终止。/ Registry missing, aborting.")
        return 1
    try:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"skills.json JSON 解析失败: {exc}")
        return 1
    categories = {c["id"] for c in registry.get("categories", [])}
    registered = {s["name"]: s for s in registry.get("skills", [])}

    check_manifests()

    section("Skill 目录 / Skill directories")
    found = (
        sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
        if SKILLS_DIR.is_dir()
        else []
    )
    if not found:
        fail("skills/ 下未发现任何包含 SKILL.md 的目录")
    for path in found:
        check_skill(path, categories)

    section("注册表一致性 / Registry sync")
    on_disk = {p.name for p in found}
    if on_disk == set(registered):
        ok(f"skills.json 与磁盘目录一致（{len(on_disk)} 个）")
    else:
        for missing in sorted(on_disk - set(registered)):
            fail(f"{missing} 存在于磁盘但未登记到 skills.json")
        for ghost in sorted(set(registered) - on_disk):
            fail(f"{ghost} 登记在 skills.json 但磁盘上不存在")
    for name, entry in registered.items():
        for field in ("path", "entry", "category", "description_zh", "description_en"):
            if not entry.get(field):
                fail(f"skills.json: {name} 缺少字段 {field}")
        if entry.get("path") and not (ROOT / entry["path"]).is_dir():
            fail(f"skills.json: {name} 的 path 指向不存在的目录: {entry['path']}")
        for rel in entry.get("scripts", []) + entry.get("tests", []) + entry.get("examples", []):
            if not (ROOT / rel).exists():
                fail(f"skills.json: {name} 登记的文件不存在: {rel}")
        if len(entry.get("keywords", [])) < 10:
            warn(f"skills.json: {name} 的 keywords 建议 >=10 个")

    section("索引文件 / Index files")
    for target in (INDEX, README):
        if not target.is_file():
            continue
        content = target.read_text(encoding="utf-8")
        missing = [f"skills/{n}" for n in sorted(on_disk) if f"skills/{n}" not in content]
        if missing:
            fail(f"{target.name} 未引用: {', '.join(missing)}")
        else:
            ok(f"{target.name} 覆盖全部 Skill 路径")

    section("结果 / Result")
    for w in warnings:
        print(f"  \033[33mWARN\033[0m  {w}")
    for e in errors:
        print(f"  \033[31mFAIL\033[0m  {e}")
    if errors:
        print(f"\n\033[31m{len(errors)} error(s), {len(warnings)} warning(s)\033[0m")
        return 1
    print(f"\n\033[32mAll checks passed. {len(on_disk)} skill(s), {len(warnings)} warning(s).\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
