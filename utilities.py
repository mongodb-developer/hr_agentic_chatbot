import openai
import re
import config


# OPEN_AI_EMBEDDING_MODEL="text-embedding-3-small"
# OPEN_AI_EMBEDDING_MODEL_DIMENSION=256

# Generate an embedding using OpenAI's API
def get_embedding(text):
    """Generate an embedding for the given text using OpenAI's API."""

    # Check for valid input
    if not text or not isinstance(text, str):
        return None

    try:
        # Call OpenAI API to get the embedding
        embedding = openai.embeddings.create(
            input=text,
            model=config.OPEN_AI_EMBEDDING_MODEL, dimensions=config.OPEN_AI_EMBEDDING_MODEL_DIMENSION).data[0].embedding
        return embedding
    except Exception as e:
        print(f"Error in get_embedding: {e}")
        return None
    

def sanitize_name(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name) if name else None