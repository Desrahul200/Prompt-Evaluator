# AutoGen Debugger & Prompt Evaluator

A streamlined tool for evaluating and improving LLM prompts with a chain of AutoGen agents.  
It analyzes a *prompt / response* pair, suggests clearer prompts, generates a fresh answer, and compares results.

---

## Features

| Agent | Purpose |
|-------|---------|
| **CriticAgent**      | Rates correctness, hallucination risk, tone, relevance |
| **PromptFixerAgent** | Rewrites the prompt in two clearer versions |
| **GeneratorAgent**   | Produces a new answer (B) from the first improved prompt |
| **ComparatorAgent**  | Decides whether answer A or answer B is better |

---

## Project Structure

```
├── agents/
│   ├── __init__.py
│   ├── critic.py
│   ├── fixer.py
│   └── comparator.py
├── app.py          # Streamlit UI
├── config.py       # LLM configuration helpers
├── main.py         # Agent orchestration
├── .env            # Environment variables
└── README.md
```

---

## Quick Start

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** (example below) *or* export variables in your shell.

   ```dotenv
   # Pick at least one provider
   GROQ_API_KEY=your_groq_key
   # OPENAI_API_KEY=your_openai_key
   # ANTHROPIC_API_KEY=your_anthropic_key

   # Optional overrides
   # OLLAMA_BASE_URL=http://localhost:11434/v1
   # DEFAULT_MODEL="Mixtral (Groq/Ollama - Default)"
   # TEMPERATURE=0.7
   # TIMEOUT=600
   ```

3. **Run the Streamlit app**

   ```bash
   streamlit run app.py
   ```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY`        | Key for Groq Mixtral / Llama-3 models |
| `OPENAI_API_KEY`      | Key for OpenAI models (e.g. GPT-4) |
| `ANTHROPIC_API_KEY`   | Key for Anthropic models (e.g. Claude-3) |
| `OLLAMA_BASE_URL`     | Ollama HTTP endpoint if running locally |
| `DEFAULT_MODEL`       | Initial model shown in the UI |
| `TEMPERATURE`         | Generation randomness (0 – 1) |
| `TIMEOUT`             | Per-request timeout in seconds |

If no cloud keys are present, the app falls back to an Ollama instance running on your machine.

---

## Usage

1. Enter a **prompt** and the LLM’s existing **Answer A**.  
2. Select an LLM backend in the sidebar.  
3. Click **Run Evaluation**.  
   * The app runs Critic and Prompt Fixer.  
   * The first improved prompt is fed to the Generator to create **Answer B**.  
   * Comparator judges A vs B.  
4. View results in three tabs:
   * Critic Analysis
   * Improved Prompts
   * Response Comparison  
5. Toggle “Export results as JSON” in the sidebar to download the run.

---

## Extending

* **agents/** – customise or add new agents.  
  Important methods:
  * `CriticAgent.evaluate(answer_a)`
  * `PromptFixerAgent.fix(prompt)`
  * `ComparatorAgent.compare(answer_a, answer_b)`
* **config.py** – add more providers or tweak defaults.  
* **main.py** – orchestration; insert extra agents or alternate selection logic.  
* **app.py** – Streamlit front-end; adjust layout, style, or controls.

---

## Contributing

Pull requests and issues are welcome.  
Feel free to open an issue for bugs, ideas, or feature requests.
