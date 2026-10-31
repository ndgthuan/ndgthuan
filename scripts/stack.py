"""Regenerate the TECH STACK block of README.md. Edit GROUPS, then run: python scripts/stack.py"""
import base64, re, urllib.parse, urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent  # repo root
OLD = {"microsoftsqlserver", "oracle", "dbt", "polars", "powerbi", "tableau", "amazonaws", "microsoftazure", "openai"}
MAX_URL = 3500  # GitHub's image proxy rejects much longer URLs


def num(m):
    v = f"{float(m.group()):.2f}".rstrip("0").rstrip(".")
    if v in ("-0", ""):
        v = "0"
    v = "-" + v[2:] if v.startswith("-0.") else (v[1:] if v.startswith("0.") else v)
    return " " + v  # keep numbers apart so "0" never merges with a following ".5"


def old_icon(slug):
    svg = urllib.request.urlopen(f"https://cdn.jsdelivr.net/npm/simple-icons@8.15.0/icons/{slug}.svg").read().decode()
    svg = re.sub(r"<title>.*?</title>", "", svg)
    return re.sub(r"-?\d*\.\d+", num, svg)


def local_badge(label, color, icon_svg, fg):
    path = re.search(r'<path d="([^"]+)"', icon_svg).group(1)
    width = 26 + int(len(label) * 6.6) + 8
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20">'
        f'<rect width="{width}" height="20" fill="#{color}"/>'
        f'<svg x="5" y="3" width="14" height="14" viewBox="0 0 24 24"><path d="{path}" fill="{fg}"/></svg>'
        f'<text x="24" y="14" fill="{fg}" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">{label}</text>'
        "</svg>\n"
    )
    name = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    (OUT / "assets" / "badges").mkdir(parents=True, exist_ok=True)
    (OUT / "assets" / "badges" / f"{name}.svg").write_text(svg, encoding="utf-8")
    return f"./assets/badges/{name}.svg"


def badge(label, color, slug, logo_color="white"):
    text = urllib.parse.quote(label.replace("-", "--").replace("_", "__").replace(" ", "_"), safe="_-")
    base = f"https://img.shields.io/badge/{text}-{color}?style=flat-square"
    if slug not in OLD:
        return f'  <img src="{base}&logo={slug}&logoColor={logo_color}" height="25" alt="{label}" />'
    icon = old_icon(slug)
    data = "data:image/svg+xml;base64," + base64.b64encode(icon.replace("<svg ", f'<svg fill="{logo_color}" ', 1).encode()).decode()
    url = f"{base}&logo={urllib.parse.quote(data, safe='')}"
    if len(url) > MAX_URL:
        url = local_badge(label, color, icon, logo_color)
    return f'  <img src="{url}" height="25" alt="{label}" />'


GROUPS = [
    ("Languages", [("Python", "3776AB", "python"), ("SQL", "CC2927", "microsoftsqlserver"), ("Go", "00ADD8", "go"), ("C++", "00599C", "cplusplus"), ("C", "A8B9CC", "c", "black"), ("C#", "512BD4", "dotnet"), ("Dart", "0175C2", "dart"), ("R", "276DC3", "r"), ("Bash", "4EAA25", "gnubash")]),
    ("Databases", [("SQL Server", "CC2927", "microsoftsqlserver"), ("PostgreSQL", "4169E1", "postgresql"), ("MySQL", "4479A1", "mysql"), ("Oracle", "F80000", "oracle"), ("SQLite", "003B57", "sqlite"), ("MongoDB", "47A248", "mongodb"), ("Redis", "DC382D", "redis"), ("Firestore", "FFCA28", "firebase", "black")]),
    ("Processing & Streaming", [("Pandas", "150458", "pandas"), ("NumPy", "013243", "numpy"), ("Polars", "CD792C", "polars"), ("Apache Spark", "E25A1C", "apachespark"), ("Apache Kafka", "231F20", "apachekafka"), ("Hadoop", "66CCFF", "apachehadoop", "black"), ("Hive", "FDEE21", "apachehive", "black")]),
    ("Orchestration & Transformation", [("Apache Airflow", "017CEE", "apacheairflow"), ("dbt", "FF694B", "dbt")]),
    ("Warehouse & Lakehouse", [("Snowflake", "29B5E8", "snowflake"), ("BigQuery", "669DF6", "googlebigquery"), ("Databricks", "FF3621", "databricks"), ("DuckDB", "FFF000", "duckdb", "black"), ("Delta Lake", "00ADD4", "delta")]),
    ("AI & Machine Learning", [("PyTorch", "EE4C2C", "pytorch"), ("TensorFlow", "FF6F00", "tensorflow"), ("Keras", "D00000", "keras"), ("scikit-learn", "F7931E", "scikitlearn"), ("Hugging Face", "FFD21E", "huggingface", "black"), ("LangChain", "1C3C3C", "langchain"), ("Ollama", "000000", "ollama"), ("ChatGPT", "10A37F", "openai"), ("Claude", "D97757", "claude"), ("Gemini", "4285F4", "googlegemini"), ("OpenCV", "5C3EE8", "opencv"), ("MLflow", "0194E2", "mlflow"), ("FastAPI", "009688", "fastapi"), ("Streamlit", "FF4B4B", "streamlit")]),
    ("BI & Analytics", [("Power BI", "F2C811", "powerbi", "black"), ("Tableau", "E97627", "tableau"), ("Metabase", "509EE3", "metabase"), ("Superset", "20A6C9", "apachesuperset"), ("Jupyter", "F37626", "jupyter")]),
    ("Cloud & DevOps", [("AWS", "232F3E", "amazonaws"), ("Google Cloud", "4285F4", "googlecloud"), ("Azure", "0078D4", "microsoftazure"), ("Docker", "2496ED", "docker"), ("Kubernetes", "326CE5", "kubernetes"), ("Terraform", "844FBA", "terraform"), ("GitHub Actions", "2088FF", "githubactions"), ("Linux", "FCC624", "linux", "black"), ("Git", "F05032", "git")]),
    ("Tools", [("Cursor", "000000", "cursor"), ("DBeaver", "382923", "dbeaver"), ("Postman", "FF6C37", "postman"), ("Anaconda", "44A833", "anaconda")]),
]

out = []
for title, items in GROUPS:
    out.append(f'### {title}\n<p align="left">')
    out += [badge(*it) for it in items]
    out.append("</p>\n")
block = "\n".join(out)

readme = OUT / "README.md"
text = readme.read_text(encoding="utf-8")
text = re.sub(r"## TECH STACK\n\n.*?\n---\n", lambda m: "## TECH STACK\n\n" + block + "\n---\n", text, flags=re.S)
readme.write_text(text, encoding="utf-8")
