import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables from .env file (for GOOGLE_API_KEY)
load_dotenv()

def generate_summary(full_context: dict) -> str:
    """
    Generates a natural language summary using an LLM based on all available context.

    Args:
        full_context (dict): A dictionary containing all data from previous agents:
                             - portfolio_data
                             - retrieved_news
                             - analysis_summary

    Returns:
        str: A coherent, narrative market brief.
    """
    # 1. Initialize the LLM
    try:
        # --- THE ONLY CHANGE IS HERE ---
        # We are using a newer, more reliable model name.
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
        
    except Exception as e:
        return f"Error initializing the LLM. Please check your API key. Details: {e}"

    # 2. Engineer the Prompt Template
    prompt_template = """
    You are a sharp financial analyst reporting to a portfolio manager.
    Your task is to provide a concise, easy-to-read daily market brief based on the data below.
    Focus on the most significant changes and their potential impact.

    Here is the data for today:

    ---
    1. CURRENT PORTFOLIO ALLOCATION:
    {portfolio_data}

    2. KEY ANALYSIS SUMMARY:
    {analysis_summary}

    3. RELEVANT NEWS SNIPPETS (Retrieved from Vector Database):
    {retrieved_news}
    ---

    INSTRUCTIONS:
    - Synthesize all the information into a single, coherent paragraph.
    - Start with the most important takeaway.
    - Do not list the data; weave it into a narrative.
    - Keep it brief and to the point.
    """

    # 3. Create a Prompt from the template
    prompt = ChatPromptTemplate.from_template(prompt_template)

    # 4. Create the "Chain"
    chain = prompt | llm

    # 5. Invoke the Chain with our context
    try:
        response = chain.invoke(full_context)
        return response.content
    except Exception as e:
        return f"An error occurred while generating the summary: {e}"


# This part allows you to test the file directly
if __name__ == '__main__':
    print("--- LLM Agent Test ---")

    mock_full_context = {
        "portfolio_data": {
            "TSM": "40%", "005930.KS": "30%", "BABA": "15%", "BIDU": "15%"
        },
        "analysis_summary": {
            "portfolio_change_analysis": ["TSM allocation changed by +2.0% points", "005930.KS allocation changed by -2.0% points"],
            "earnings_analysis_summary": ["BABA: Beat/Positive outlook reported.", "005930.KS: Miss/Negative outlook reported.", "TSM: Beat/Positive outlook reported."]
        },
        "retrieved_news": [
            "[TSM] TSMC forecasts strong Q3 revenue between $19.6 billion and $20.4 billion, citing massive AI chip demand.",
            "[005930.KS] Samsung Electronics flags a likely 96% plunge in Q2 profit due to a chip glut.",
            "[BABA] Alibaba Beats Revenue Estimates On E-Commerce Strength, but profit margins fell."
        ]
    }
    
    print("\n--- Sending the following context to the LLM ---")
    print(json.dumps(mock_full_context, indent=2))

    final_summary = generate_summary(mock_full_context)

    print("\n--- AI-Generated Market Brief ---")
    print(final_summary)