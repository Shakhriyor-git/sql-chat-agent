import os
from dotenv import load_dotenv

load_dotenv()

# Project root (parent of src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
DB_PATH = os.path.join(BASE_DIR, "data", "credit.db")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-3.5-turbo"