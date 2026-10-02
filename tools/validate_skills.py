#!/usr/bin/env python3
"""Repository-level validator for this Agent Skill collection.

Pure standard library, no third-party dependencies. Run from the repo root:

    python3 tools/validate_skills.py

Exit code 0 = all hard checks passed, 1 = at least one hard check failed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "skills.json"
INDEX = ROOT / "llms.txt"
README = ROOT / "README.md"
SKIP_DIRS = {".git", ".github", "tools", "docs", "node_modules", "__pycache__", ".idea", ".vscode"}

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def ok(msg: str) -> None:
    print(f"  \033[32mOK\033[0m    {msg}")


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
    body = text[end + 4 :]
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


def discover_skills() -> list[Path]:
    return sorted(
        p
        for p in ROOT.iterdir()
        if p.is_dir()
        and p.name not in SKIP_DIRS
        and not p.name.startswith(".")
        and (p / "SKILL.md").is_file()
    )


def check_skill_dir(path: Path, categories: set[str]) -> dict:
    print(f"\n\033[1m{path.name}\033[0m")
    text = (path / "SKILL.md").read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    name = meta.get("name", "")
    if not name:
        fail(f"{path.name}: SKILL.md frontmatter 缺少 name")
    else:
        if name != path.name:
            fail(f"{path.name}: name ({name}) 与目录名不一致")
        else:
            ok("name == 目录名")
        if not NAME_RE.match(name) or len(name) > 64:
            fail(f"{path.name}: name 必须为 kebab-case 且 <=64 字符")
        else:
            ok("name 格式合法 (kebab-case)")

    description = meta.get("description", "")
    if not isinstance(description, str) or not description.strip():
        fail(f"{path.name}: description 缺失")
    else:
        desc = " ".join(description.split())
        if len(desc) > 1024:
            fail(f"{path.name}: description 超过 1024 字符 ({len(desc)})")
        else:
            ok(f"description 长度 {len(desc)} <= 1024")
        if not CJK_RE.search(desc):
            fail(f"{path.name}: description 缺少中文表述")
        if not re.search(r"[A-Za-z]{3,}", desc):
            fail(f"{path.name}: description 缺少英文触发词")
        if not CJK_RE.search(desc) and not re.search(r"[A-Za-z]{3,}", desc):
            fail(f"{path.name}: description 无法识别语言")
        else:
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
        keywords = metadata.get("keywords", "")
        if len([k for k in re.split(r"[,;]", keywords) if k.strip()]) < 5:
            warn(f"{path.name}: metadata.keywords 建议 >=5 个中英关键词")
        else:
            ok("metadata.keywords 充足")

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
            warn(f"{path.name}: 建议提供 {required}/ 目录（可选，但有利于渐进式披露）")
    return meta


def main() -> int:
    print("\033[1m== 仓库结构 / Repository structure ==\033[0m")
    for required in ("README.md", "skills.json", "llms.txt", "LICENSE"):
        if (ROOT / required).is_file():
            ok(f"{required} 存在")
        else:
            fail(f"{required} 缺失")

    if not REGISTRY.is_file():
        print("\n注册表缺失，终止。/ Registry missing, aborting.")
        return 1
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    categories = {c["id"] for c in registry.get("categories", [])}
    registered = {s["name"]: s for s in registry.get("skills", [])}

    print("\n\033[1m== Skill 目录 / Skill directories ==\033[0m")
    found = discover_skills()
    if not found:
        fail("未发现任何包含 SKILL.md 的顶层目录")
    for path in found:
        check_skill_dir(path, categories)

    print("\n\033[1m== 注册表一致性 / Registry sync ==\033[0m")
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
        if len(entry.get("keywords", [])) < 10:
            warn(f"skills.json: {name} 的 keywords 建议 >=10 个")
        if entry.get("category") and entry["category"] not in categories:
            fail(f"skills.json: {name} 的 category 未在 categories 中声明")

    print("\n\033[1m== 索引文件 / Index files ==\033[0m")
    for target in (INDEX, README):
        if not target.is_file():
            continue
        content = target.read_text(encoding="utf-8")
        missing = [n for n in sorted(on_disk) if f"{n}/SKILL.md" not in content]
        if missing:
            fail(f"{target.name} 未引用: {', '.join(missing)}")
        else:
            ok(f"{target.name} 覆盖全部 Skill 路径")

    print("\n\033[1m== 结果 / Result ==\033[0m")
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
