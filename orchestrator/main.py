import sys
import os
import json
from fastapi import FastAPI
from pydantic import BaseModel

# --- IMPORTANT: Add project root to the Python path ---
# This allows us to import from the 'agents' directory.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Import all your agents ---
from agents import api_agent, scraper_agent, retriever_agent, analysis_agent, llm_agent

# Initialize the FastAPI app
app = FastAPI(
    title="Financial Assistant API",
    description="An API to orchestrate financial agents for market analysis.",
    version="1.0.0"
)

# Define the request model for the /query endpoint
class QueryRequest(BaseModel):
    query: str
    
# --- Define the main API Endpoint ---
@app.post("/query", summary="Get a full market brief for a query")
async def get_market_brief(request: QueryRequest):
    """
    This endpoint takes a user's text query and orchestrates the full agent
    workflow to generate a comprehensive market brief.
    """
    user_query = request.query
    print(f"Received query: {user_query}")

    # --- AGENT WORKFLOW ---

    # 1. API Agent: Get portfolio data
    print("Step 1: Calling API Agent for portfolio data...")
    portfolio_data = api_agent.get_portfolio_allocation()

    # 2. Scraper Agent: Get latest news
    print("Step 2: Calling Scraper Agent for news...")
    scraped_headlines = scraper_agent.get_earnings_surprises()
    if not scraped_headlines:
        return {"error": "Could not scrape any news. The workflow cannot continue."}

    # 3. Retriever Agent: Create a knowledge base and retrieve relevant news
    print("Step 3: Calling Retriever Agent...")
    # Create embeddings for the scraped news (in-memory for this request)
    retriever_agent.create_and_store_embeddings(scraped_headlines)
    # Retrieve the most relevant news snippets for the user's query
    retrieved_news = retriever_agent.retrieve_top_k(user_query, k=3)

    # 4. Analysis Agent: Get structured insights
    print("Step 4: Calling Analysis Agent...")
    analysis_summary = analysis_agent.analyze_portfolio_risk(portfolio_data, scraped_headlines)
    
    # 5. LLM Agent: Generate the final narrative
    print("Step 5: Calling LLM Agent to generate final summary...")
    # Bundle all context for the LLM
    full_context = {
        "portfolio_data": portfolio_data,
        "analysis_summary": analysis_summary,
        "retrieved_news": retrieved_news
    }
    final_summary = llm_agent.generate_summary(full_context)

    print("--- Workflow Complete ---")
    
    # Return the final response
    return {"response": final_summary, "context_used": full_context}

@app.get("/", summary="Root endpoint for health check")
def read_root():
    return {"status": "API is running."}