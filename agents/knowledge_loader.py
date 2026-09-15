from pathlib import Path


def load_knowledge():
    """
    Load all knowledge files from the knowledge folder.
    """

    knowledge_folder = Path(__file__).resolve().parent.parent / "knowledge"

    knowledge = {}

    for file_path in knowledge_folder.glob("*.txt"):
        knowledge[file_path.name] = file_path.read_text(
            encoding="utf-8"
        )

    return knowledge


if __name__ == "__main__":
    data = load_knowledge()

    print("Files loaded:", len(data))

    for filename in data:
        print("-", filename)