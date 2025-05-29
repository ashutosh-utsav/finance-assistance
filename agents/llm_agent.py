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
    # Initialize the LLM
    try:
        # THE ONLY CHANGE IS HERE ---
        # We are using a newer, more reliable model name.
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
        
    except Exception as e:
        return f"Error initializing the LLM. Please check your API key. Details: {e}"

# Prompt Template
    prompt_template = """
    You are a friendly and helpful AI financial assistant. Your user has asked a question, and your goal is to answer it directly and conversationally, using the provided context.

    ---
    THE USER'S QUESTION IS:
    "{user_query}"
    ---

    Use the following context to formulate your answer:

    CONTEXT 1: RELEVANT NEWS SNIPPETS
    These are the most important pieces of information, as they were specifically retrieved based on the user's query.
    {retrieved_news}

    CONTEXT 2: GENERAL MARKET ANALYSIS
    This provides a broader summary of recent market activity for our tracked portfolio.
    {analysis_summary}

    CONTEXT 3: CURRENT PORTFOLIO DATA
    This shows the current asset allocation.
    {portfolio_data}

    ---
    INSTRUCTIONS:
    1.  Start with a friendly, direct answer to the user's question: "{user_query}".
    2.  Use the "RELEVANT NEWS SNIPPETS" (Context 1) as the primary basis for your answer.
    3.  Use the other context for background color or to add details about portfolio impact if relevant.
    4.  Keep your tone conversational and easy to understand. Do not just list the data. Weave it into a narrative.
    5.  If the provided context does not contain enough information to answer the question, clearly state that you couldn't find specific information on that topic.
    """

    # Create a Prompt from the template
    prompt = ChatPromptTemplate.from_template(prompt_template)

    #  Create the "Chain"
    chain = prompt | llm

    # Invoke the Chain with our context
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