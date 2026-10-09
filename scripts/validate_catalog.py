"""Validate expandable Skill/demo references, media, chapters, and local files."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

TYPES = {"video", "audio", "image", "interactive", "link"}
ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def validate(catalog, web):
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    def text(obj, key, label):
        require(isinstance(obj.get(key), str) and bool(obj[key].strip()), f"{label}.{key}: nonempty text required")
    def resource(value, label):
        require(isinstance(value, str) and bool(value), label + ": resource required")
        if not isinstance(value, str) or not value:
            return
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            require(parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password, label + ": use an HTTPS URL without credentials")
        else:
            target = (web / parsed.path).resolve()
            require(target.is_relative_to(web.resolve()) and target.is_file(), label + ": local resource missing or outside the site")
    require(catalog.get("schemaVersion") == 1, "schemaVersion must be 1")
    site = catalog.get("site", {})
    for field in ["title", "owner", "description", "github"]:
        text(site, field, "site")
    resource(site.get("github"), "site.github")
    skills, demos = catalog.get("skills", []), catalog.get("demos", [])
    require(isinstance(skills, list) and isinstance(demos, list), "skills and demos must be arrays")
    if not isinstance(skills, list) or not isinstance(demos, list):
        return errors
    def ids(items, label):
        found = set()
        for item in items:
            if not isinstance(item, dict):
                errors.append(label + ": entries must be objects")
                continue
            value = item.get("id", "")
            require(isinstance(value, str) and ID.fullmatch(value), label + ": id must use lowercase words and hyphens")
            if isinstance(value, str):
                require(value not in found, label + ": duplicate id " + value)
                found.add(value)
        return found
    skill_ids, demo_ids = ids(skills,"skills"), ids(demos,"demos")
    if site.get("featuredDemoId"):
        require(site["featuredDemoId"] in demo_ids, "site.featuredDemoId must refer to an existing demo")
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        label = "skill " + str(skill.get("id"))
        for field in ["name", "category", "summary", "repository"]:
            text(skill, field, label)
        resource(skill.get("repository"), label + ".repository")
        if skill.get("artwork"):
            resource(skill["artwork"], label + ".artwork")
        references = skill.get("demoIds", [])
        require(isinstance(references, list), label + ".demoIds must be an array")
        if isinstance(references, list):
            require(all(isinstance(id, str) and id in demo_ids for id in references), label + ": unknown demo reference")
        for field in ["tags", "capabilities"]:
            require(isinstance(skill.get(field, []), list) and all(isinstance(value, str) for value in skill.get(field, [])), label + "." + field + " must be a text array")
    for demo in demos:
        if not isinstance(demo, dict):
            continue
        label = "demo " + str(demo.get("id"))
        for field in ["title", "summary", "description"]:
            text(demo, field, label)
        require(demo.get("type") in TYPES, label + ": unsupported media type")
        resource(demo.get("src"), label + ".src")
        for field in ["poster", "audio", "source", "download", "rights"]:
            if demo.get(field):
                resource(demo[field], label + "." + field)
        require(isinstance(demo.get("facts", []), list) and all(isinstance(value, str) for value in demo.get("facts", [])), label + ".facts must be a text array")
        contributors = demo.get("contributors", [])
        require(isinstance(contributors, list), label + ".contributors must be an array")
        if isinstance(contributors, list):
            for contributor in contributors:
                if not isinstance(contributor, dict):
                    errors.append(label + ": contributor must be an object")
                    continue
                require(contributor.get("skillId") in skill_ids, label + ": unknown contributing skill")
                text(contributor, "role", label + ".contributor")
        chapters = demo.get("chapters", [])
        require(isinstance(chapters, list), label + ".chapters must be an array")
        previous = -1
        if isinstance(chapters, list):
            for chapter in chapters:
                if not isinstance(chapter, dict):
                    errors.append(label + ": chapter must be an object")
                    continue
                time = chapter.get("time")
                require(isinstance(time, (int,float)) and time >= 0 and time > previous, label + ": chapter times must increase and be nonnegative")
                if isinstance(time, (int,float)):
                    previous = time
                text(chapter, "title", label + ".chapter")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--catalog", type=Path, default=root / "docs/data/catalog.json")
    parser.add_argument("--web", type=Path, default=root / "docs")
    args = parser.parse_args()
    try:
        data = json.loads(args.catalog.read_text(encoding="utf-8"))
        errors = validate(data, args.web)
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(1, f"Invalid catalog: {error}\n")
    if errors:
        parser.exit(1, "Invalid catalog:\n- " + "\n- ".join(errors) + "\n")
    print(f"CATALOG_VALID: {len(data['skills'])} skills / {len(data['demos'])} demos")


if __name__ == "__main__":
    main()
