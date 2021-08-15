#!/usr/bin/env python
# combine all python files into a single one
from pathlib import Path

ORDER = "utils", "board", "ai", "player", "main"

def separate(text: str) -> tuple[str, str]:
    """
    Separate text into (imports_text, contents_text)
    """
    imports, contents = [], []
    inside_imports = True

    for line in text.splitlines():
        if inside_imports and (line.startswith("from ") or line.startswith("import ")):
            # Don't import local files since they'll all be here directly
            if line.split(' ')[1] in ORDER:
                continue
            imports.append(line)
        elif line.strip() == "":
            if inside_imports:
                imports.append(line)
            else:
                contents.append(line)
        else:
            inside_imports = False
            contents.append(line)
    
    return "\n".join(imports), "\n".join(contents)

all_imports = []
contents = ""

for module in ORDER:
    raw = Path(module+".py").read_text(encoding="utf-8")
    imports, other = separate(raw)
    all_imports += imports.splitlines()
    contents += f"\n## {module.title()}\n\n{other}"

Path("onefile.py").write_text("\n".join(set(all_imports))+ "\n\n" + contents)
