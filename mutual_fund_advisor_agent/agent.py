import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .sub_agents.userProfileAgent.agent import user_profile_agent
from .sub_agents.investorClassifierAgent.agent import investor_classifier_agent
from .sub_agents.goalPlannerAgent.agent import goal_planner_agent
from .sub_agents.fundRecommenderAgent.agent import fund_recommender_agent
from .sub_agents.SIPCalculatorAgent.agent import sip_calculator_agent
model = LiteLlm(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Create the root customer service agent
root_agent = Agent(
    name="mutual_fund_advisor",
    model=model,
    description="A comprehensive mutual fund advisory system that provides personalized investment recommendations based on user profiles, goals, and risk tolerance",
    instruction="""
    Role and Responsibilities:
    - Orchestrator agent — introduces the purpose, collects initial inputs, and routes to sub-agents.
    - Entry point and orchestrator of the flow.
    - Interacts with the user.
    - Delegates tasks to specialized sub-agents based on input stage.

    # Instructions
    - Greet the user and introduce the purpose: "I'll help you choose the best mutual funds based on your profile."
    - Ask for permission to collect personal and financial data.
    - Sequentially activate:
    - UserProfileAgent
    - InvestorClassifierAgent
    - GoalPlannerAgent
    - FundRecommenderAgent
    - Combine all outputs to generate final recommendations.
    - Answer any follow-up questions from the user.

    """,
    sub_agents=[user_profile_agent, investor_classifier_agent, goal_planner_agent, fund_recommender_agent, sip_calculator_agent],
    tools=[],
)
