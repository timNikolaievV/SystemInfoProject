import json, os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

def ensure_reports_dir(path="reports"):
    os.makedirs(path, exist_ok=True)
    return path

def save_json(data, path_dir="reports"):
    ensure_reports_dir(path_dir)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = os.path.join(path_dir, f"sysdiag-{stamp}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return out

def render_html(data, templates_dir="templates", path_dir="reports"):
    ensure_reports_dir(path_dir)
    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html"])
    )
    tpl = env.get_template("report.html")
    html = tpl.render(d=data)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = os.path.join(path_dir, f"sysdiag-{stamp}.html")

    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    return out