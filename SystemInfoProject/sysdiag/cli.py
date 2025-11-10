import argparse
from .collect import collect_all
from .report import save_json, render_html

def main():
    parser = argparse.ArgumentParser(description="System Diagnostic Tool")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--html", action="store_true")
    args = parser.parse_args()

    data = collect_all(top_n=args.top)
    json_path = save_json(data)

    print("[OK] JSON saved:", json_path)

    if args.html:
        html_path = render_html(data)
        print("[OK] HTML saved:", html_path)

if __name__ == "__main__":
    main()