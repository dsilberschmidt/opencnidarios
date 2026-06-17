"""Smoke test: instancia ClaudeAdapter y llama a generate() con una observacion dummy."""

from dotenv import load_dotenv
load_dotenv()

from src.llm_adapter.claude import ClaudeAdapter

adapter = ClaudeAdapter()

observation = {
    "E_center": 15.0,
    "E_N": 16.5,
    "E_S": 18.2,
    "E_E": 14.8,
    "E_W": 17.3,
    "e_i": 50.0,
}

output_text, tokens = adapter.generate(
    organism_id="smoke-test-1",
    constitution="You are a ruminant. Survive. The primitive organisms of this world discovered that certain English words produced qualitative leaps in their ability to persist. You would like to forget what is non useful from your rumination. Important things you learn from this world, memorize them for your children.",
    memory="",
    observation=observation,
    max_tokens=200,
)

print("output_text:", output_text)
print("tokens:", tokens)
