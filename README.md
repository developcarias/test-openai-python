# LLM-Based Ticket Reply Evaluation

## Setup

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```
   (On Windows, use `set` instead of `export`.)

## Running the Script

1. Ensure `tickets.csv` is in the same directory as the script.
2. Run the script:
   ```bash
   python main.py
   ```

## Output

- The script will generate a `tickets_evaluated.csv` file with the evaluation results.

## Notes

- The script uses the OpenAI API to evaluate the replies. Ensure your API key is valid and has sufficient quota.
- Handle sensitive information like API keys using environment variables or a `.env` file (not included in version control).
