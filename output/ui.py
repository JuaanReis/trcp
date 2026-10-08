def load_banner():
    with open("output/banner.txt", "r", encoding="utf-8") as f:
        return f.read()

def banner():
    content = load_banner()
    lines = content.splitlines()

    width = 70

    print(f"╭{'─' * width}╮")

    for line in lines:
        print(f"│{line.center(width)}│")

    print(f"│{' ' * width}│")
    print(f"│{'TRINITY CLIENT PROSPECTOR 1.0.0'.center(width)}│")

    print(f"╰{'─' * width}╯")