import os
import pandas as pd
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)


# Read the CSV file
def read_tickets(file_path):
    return pd.read_csv(file_path)


# Evaluate using OpenAI LLM
def evaluate_reply(ticket, reply):
    prompt = (
        f"Evaluate the following reply to a customer ticket.\n\n"
        f"Ticket: {ticket}\n\n"
        f"Reply: {reply}\n\n"
        "Please provide the evaluation in the following format:\n"
        "Content Score: [1-5]\n"
        "Content Explanation: [Your explanation here]\n"
        "Format Score: [1-5]\n"
        "Format Explanation: [Your explanation here]"
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            store=True,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error: {e}")
        return None


# Process the response from LLM
def process_evaluation(evaluation):
    # Split the evaluation by lines and filter out empty lines
    lines = [line for line in evaluation.strip().split('\n') if line.strip()]

    # Extract content score
    content_score_line = next(
        (line for line in lines if line.startswith('Content Score:')), None
    )
    if content_score_line:
        content_score = int(content_score_line.split(':')[1].strip())
    else:
        content_score = None

    # Extract content explanation
    content_explanation_start = (
        lines.index(content_score_line) + 1 if content_score_line else 0
    )
    content_explanation_lines = []
    for line in lines[content_explanation_start:]:
        if line.startswith('Format Score:'):
            break
        content_explanation_lines.append(line)
    content_explanation = (
        ' '.join(content_explanation_lines)
        .strip().replace('Content Explanation:', '')
        .strip() if content_explanation_lines else ''
    )

    # Extract format score
    format_score_line = next(
        (line for line in lines if line.startswith('Format Score:')), None
    )
    if format_score_line:
        format_score = int(format_score_line.split(':')[1].strip())
    else:
        format_score = None

    # Extract format explanation
    format_explanation_start = (
        lines.index(format_score_line) + 1 if format_score_line else 0
    )
    format_explanation_lines = []
    for line in lines[format_explanation_start:]:
        format_explanation_lines.append(line)
    format_explanation = (
        ' '.join(format_explanation_lines)
        .strip()
        .replace('Format Explanation:', '')
        .strip() if format_explanation_lines else ''
    )

    return content_score, content_explanation, format_score, format_explanation


# Write the evaluated results to a new CSV
def write_evaluated_tickets(df, output_path):
    df.to_csv(output_path, index=False)


# Main processing function
def main():
    input_file = 'tickets.csv'
    output_file = 'tickets_evaluated.csv'

    # Read tickets
    try:
        tickets_df = read_tickets(input_file)
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
        return
    except pd.errors.EmptyDataError:
        print("Error: The input file is empty.")
        return
    except Exception as e:
        print(f"Unexpected error reading file: {e}")
        return

    # Initialize lists to store evaluation results
    content_scores = []
    content_explanations = []
    format_scores = []
    format_explanations = []

    # Evaluate each ticket
    for index, row in tickets_df.iterrows():
        if pd.isna(row['ticket']) or pd.isna(row['reply']):
            print(f"Warning: Missing data at row {index}. Skipping this row.")
            continue
        evaluation = evaluate_reply(row['ticket'], row['reply'])
        if evaluation is None:
            print(
                f"Warning: Evaluation failed for row {index}"
                f". Skipping this row."
            )
            continue
        try:
            content_score, content_explanation, format_score, format_explanation = process_evaluation(evaluation)  # noqa
            content_scores.append(content_score)
            content_explanations.append(content_explanation)
            format_scores.append(format_score)
            format_explanations.append(format_explanation)
        except Exception as e:
            print(
                f"Unexpected error processing "
                f"evaluation at row {index}: {e}"
            )
            continue

    # Check if lists are empty
    if not content_scores:
        print("Error: No valid evaluations were processed.")
        return

    # Add evaluation results to DataFrame
    tickets_df['content_score'] = content_scores
    tickets_df['content_explanation'] = content_explanations
    tickets_df['format_score'] = format_scores
    tickets_df['format_explanation'] = format_explanations

    # Write to output CSV
    write_evaluated_tickets(tickets_df, output_file)

# Run the main function
if __name__ == "__main__":
    main()
