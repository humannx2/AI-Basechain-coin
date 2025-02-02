import asyncio
import os
import google.generativeai as genai
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from dotenv import load_dotenv
import json

load_dotenv()

async def crawl_gmgn(url):
    browser_config = BrowserConfig(headless=True, verbose=True)
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    async with AsyncWebCrawler(browser_config=browser_config) as crawler:
        result = await crawler.arun(
            url=url,
            config=crawl_config
        )
        # print(result.markdown)

        if result.success:
            # Configure Gemini
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

            generation_config = {
                "temperature": 0.1, # Lower temperature for more focused output
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }

            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro", 
                generation_config=generation_config,
            )

            chat_session = model.start_chat(history=[])
            
            prompt = """
            Analyze this token data and provide detailed insights in the following areas:

            1. Top Holders Analysis:
               - Top 10 holder percentages
               - Dev wallet status and transactions
               - Sniper activity and counts
               - Blue chip holder percentage

            2. Security Analysis:
               - Contract verification status
               - Honeypot check results
               - Buy/Sell taxes
               - Risk assessment score
               - Renounced status


            Raw Data:
            {data}

            Format the response as a clean JSON object without any markdown formatting or additional headers or ```json```. Include all available metrics and insights from the provided data and return the response in json format.
            """

            # print(prompt.format(data=str(result.markdown)))

            response = chat_session.send_message(prompt.format(data=str(result)))



            with open("analyzed_token_data_1.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("Analyzed Token Data saved to analyzed_token_data.json")
            print(response.text)
            return response.text
        else:
            print("Attempt failed")

# asyncio.run(main())