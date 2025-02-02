from crewai import Agent, LLM, Crew, Task
# from tasks import token_analysis_task
import os


api_key = os.getenv("OPENAI_API_KEY")
api_key2 = os.getenv("GROQ_API_KEY")
llm = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.3, api_key=api_key)
llm1=LLM(model="groq/deepseek-r1-distill-llama-70b", temperature=0.3, api_key=api_key2)
llm2=LLM(model="groq/llama3-8b-8192", temperature=0.3, api_key=api_key2)
# Data Analyzer Agent
analyzer = Agent(
    role="Data Analyzer",
    goal="Analyze cryptocurrency data {data} and provide insights based on key metrics.",
    backstory="An expert in blockchain and crypto data analysis, providing insights on price trends, liquidity, market activity, and other key metrics.",
    verbose=True,
    llm=llm
)

# Data Analysis Task
token_analysis_task = Task(
    description="Analyze cryptocurrency token data and provide insights on price trends, liquidity, and market activity.",
    agent=analyzer,
    goal="Provide a detailed analysis of the token {data} and provide insights on price trends, liquidity, and market activity.",
    expected_output="analysis.md"
)

crew = Crew(
    agents=[analyzer,],
    tasks=[token_analysis_task,],
    verbose=True,
    memory=True
)

gngm_analyzer=Agent(
    role="GMGN Analyzer",
    goal="Analyze the token data {data} and provide insights based on key metrics.",
    backstory="An expert in blockchain and crypto data analysis, providing insights whether the token is a good investment or not.",
    verbose=True,
    llm=llm
)

gngm_analysis_task=Task(
    description="Analyze the token data {data} and provide insights based on key metrics.",
    agent=gngm_analyzer,
    goal="Provide me with a one line suggestion on whether the token is a good investment or not. Do not suggest any recommendations.",
    expected_output="gmgn_analysis.md"
)

gngm_crew=Crew(
    agents=[gngm_analyzer,],
    tasks=[gngm_analysis_task,],
    verbose=True,
    memory=True
)

twitter_analyzer=Agent(
    role="Twitter Analyzer",
    goal="Analyze the sentiment of the tweets from the twitter data {data} and provide insights based on the sentiment.",
    backstory="An expert in sentiment analysis, providing insights on the mood of the community and how it is affecting the token.",
    verbose=True,
    llm=llm1
)

twitter_analysis_task=Task(
    description="Analyze the sentiment of the tweets from the twitter data {data} and provide insights based on the sentiment.",
    agent=twitter_analyzer,
    goal="Provide a brief analysis of the sentiment of the tweets from the twitter data {data}, and give forcast on whether the social sentiment is positive or negative. Provide a score of the sentiment from 0 to 100.",
    expected_output="twitter_analysis.md"
)

twitter_crew=Crew(
    agents=[twitter_analyzer,],
    tasks=[twitter_analysis_task,],
    verbose=True,
    memory=True
)


# # Deepseek Analysis Agent
# deepseek_analyzer = Agent(
#     role="Deepseek Analysis Expert",
#     goal="Synthesize and analyze multiple cryptocurrency analysis reports to provide comprehensive insights.",
#     backstory="A specialized AI analyst with expertise in combining multiple data sources and analysis reports to generate actionable cryptocurrency insights and predictions.",
#     verbose=True,
#     llm=llm1
# )

# # Deepseek Analysis Task
# deepseek_analysis_task = Task(
#     description="Analyze and synthesize the combined outputs from token analysis and GMGN analysis to provide comprehensive insights.",
#     agent=deepseek_analyzer,
#     goal="Review the token analysis: {token_analysis} and GMGN analysis: {gmgn_analysis}, then provide a comprehensive synthesis with key insights, risks, and potential outcomes.",
#     expected_output="deepseek_analysis.md"
# )

# # Combined Analysis Crew
# combined_analysis_crew = Crew(
#     agents=[analyzer, gngm_analyzer, deepseek_analyzer],
#     tasks=[token_analysis_task, gngm_analysis_task, deepseek_analysis_task],
#     llm=llm,
#     verbose=True
# )

predict_agent=Agent(
    role="Predictor",
    goal="Predict the future movement of the token based on the data {data}.",
    backstory="A Blockchain and Crypto expert in predicting the future trends of the token based on the data.",
    verbose=True,
    llm=llm2
)

predict_task=Task(
    description="Predict the future movement of the token based on the data {data}.",
    agent=predict_agent,
    goal=("Understand the information about the token data {data}. Suggest an Action signa; to the user regarding the token like [Strong Buy, Buy, Hold, Sell, Strong Sell]"),
    expected_output="predict_output.md"
)

predict_crew=Crew(
    agents=[predict_agent,],
    tasks=[predict_task,],
    verbose=True,
    memory=True
)

