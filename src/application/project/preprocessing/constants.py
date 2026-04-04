IGNORED_DIRECTORIES = ["venv", "__pycache__"]
ALLOWED_EXTENSIONS = [
    # language
    ".py",
    ".jinja",
    ".tpl"  # ".ipynb",
    ".html",
    ".css",
    ".js",
    ".ts",
    # execs
    ".sh",
    ".bat",
    ".ps1"
    # envs
    ".env",
    # docs
    ".md",
    ".txt",
    # config
    ".toml",
    ".yaml",
    ".yml",  # ".json" -> структуру
    # data
    # ".csv" -> first 4 lines
]
TOKENIZER_MODEL = "cl100k_base"
