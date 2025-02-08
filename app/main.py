from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import operator

# from models.forecasting import Prediction
from services.moralisapi import fetch_token_price
import uvicorn
from services.gmgn_api import get_gmgn_info, GMGNResponse
from services.crewat import crew,gngm_crew,twitter_crew,predict_crew
from services.twitter_api import (
    search_twitter,
    SearchType,
    TwitterSearchResponse,
)
from dotenv import load_dotenv
from services.gemini import analyze_gmgn_data
from models import LiquidityPool, WhaleTransaction, DexAnalyticsResponse, FeatureEngineering, BlockchainRecognition, AISignalsResponse, AlertThreshold, RiskAssessmentResponse, HistoricalResponse, CombinedTokenData, TokenData
from services.gmgncrawler import crawl_gmgn
import os
import json
from typing import Optional, List, Dict

app = FastAPI()
load_dotenv()


@app.get("/token-price", response_model=DexAnalyticsResponse)
def get_token_price(pairAddress: str):
    price_data = fetch_token_price(pairAddress)
    if "error" in price_data:
        raise HTTPException(status_code=400, detail=price_data["error"])
    token_data = TokenData(**price_data)
    return calculate_dex_analytics(token_data)


def calculate_dex_analytics(token_data: TokenData) -> DexAnalyticsResponse:
    total_dex_volume = sum(token_data.totalVolume.values())
    dex_volume_change = token_data.pricePercentChange.get("24h", 0.0)
    total_liquidity = token_data.totalLiquidityUsd
    liquidity_change = token_data.liquidityPercentChange.get("24h", 0.0)
    unique_traders = len(set(token_data.buyers.keys()).union(set(token_data.sellers.keys())))
    traders_change = ((len(token_data.buyers) + len(token_data.sellers)) / unique_traders) if unique_traders else 0.0
    liquidity_pool = [LiquidityPool(pairAddress=token_data.pairAddress, totalLiquidityUsd=token_data.totalLiquidityUsd)]
    whale_transactions = [
        WhaleTransaction(transactionType="buy", amountUsd=amount) for amount in token_data.buyVolume.values() if amount > 10000
    ] + [
        WhaleTransaction(transactionType="sell", amountUsd=amount) for amount in token_data.sellVolume.values() if amount > 10000
    ]
    return DexAnalyticsResponse(
        total_dex_volume=total_dex_volume,
        dex_volume_change=dex_volume_change,
        total_liquidity=total_liquidity,
        liquidity_change=liquidity_change,
        unique_traders=unique_traders,
        traders_change=traders_change,
        liquidity_pool=liquidity_pool,
        whale_transactions=whale_transactions
    )


@app.post("/analyze-token-price")
async def analyze_token_price(token_pair_address: str):
    # Fetch the token price
    price_data =get_token_price(token_pair_address)
    if "error" in price_data:
        raise HTTPException(status_code=400, detail=price_data["error"])
    price_analysis=crew.kickoff(inputs={"data":price_data})
    return price_analysis

# class DevWalletStatus(BaseModel):
#     balance: str
#     status: str


# class SniperActivity(BaseModel):
#     sniper_count: int
#     total_transactions: int


# class RiskAssessmentScore(BaseModel):
#     honeypot_is: str
#     gopluslabs: str


# class SecurityAnalysis(BaseModel):
#     contract_verification_status: str
#     honeypot_check_results: str
#     buy_tax: float
#     sell_tax: float
#     risk_assessment_score: RiskAssessmentScore
#     renounced_status: str
#     liquidity_locked: str


# class TopHoldersAnalysis(BaseModel):
#     top_10_holder_percentage: float
#     dev_wallet_status: DevWalletStatus
#     dev_wallet_transactions: str
#     sniper_activity: SniperActivity
#     blue_chip_holder_percentage: float


# class AdditionalInformation(BaseModel):
#     name: str
#     symbol: str
#     price: float
#     market_cap: int
#     _24h_volume: int
#     total_supply: int
#     circulating_supply: int
#     holders: int
#     pair_address: str
#     pool_created: str


# class CryptoAnalysisResponse(BaseModel):
    top_holders_analysis: TopHoldersAnalysis
    security_analysis: SecurityAnalysis
    additional_information: AdditionalInformation



@app.get("/gmgn-info")
async def get_gmgn_token_info(tokenAddress: str):
    base_url = "https://gmgn.ai/base/token/VIVOWmEQ_"
    url = operator.concat(base_url, tokenAddress)
    response = await crawl_gmgn(url)
    if response is None:
        raise HTTPException(status_code=400, detail="Error fetching GMGN data") 
    # return response
    gmgn_analysis = gngm_crew.kickoff(inputs={"data": response})
    return gmgn_analysis.raw


@app.get("/twitter-search")
async def search_tweets_endpoint(
    query: str, search_type: SearchType = SearchType.TOP, max_tweets: int = 10
):
    # Get Twitter credentials from environment variables
    twitter_username = os.getenv("TWITTER_USERNAME")
    twitter_password = os.getenv("TWITTER_PASSWORD")

    if not twitter_username or not twitter_password:
        raise HTTPException(
            status_code=500, detail="Twitter credentials not configured"
        )

    response = await search_twitter(
        query=query,
        search_type=search_type,
        max_tweets=max_tweets,
        username=twitter_username,
        password=twitter_password,
    )

    if response.status == "error":
        raise HTTPException(status_code=400, detail=response.error)
    response_dict=response.dict()
    # Extract only the tweet texts
    tweets_text_only = {"tweets": [tweet["text"] for tweet in response_dict["tweets"]]}
    # Convert to JSON format
    tweets_json = json.dumps(tweets_text_only, indent=4)
    analysis_result=twitter_crew.kickoff(inputs={"data":tweets_json})
    return analysis_result

    roi: int
    pumpPatterns: int
    averagePumpReturn: int
    recoveryTime: int
    activeAlerts: int
    highPriority: int
    triggeredToday: int
    triggeredChange: int
    successRate: int
    responseTime: float

# --- FastAPI Endpoints ---


@app.get("/dex-analytics", response_model=DexAnalyticsResponse)
async def get_dex_analytics(tokenAddress: str, pairAddress: str):
    # Logic to fetch data based on coinAddress and pairAddress
    price_data = fetch_token_price(pairAddress)
    gmgn_data=get_gmgn_token_info(tokenAddress)
    if "error" in price_data:
        raise HTTPException(status_code=400, detail=price_data["error"])
    return price_data
    # return {
    #     "total_dex_volume": 1234567890,
    #     "dex_volume_change": 15.2,
    #     "total_liquidity": 234567890,
    #     "liquidity_change": -3.5,
    #     "unique_traders": 890123,
    #     "traders_change": 5.4,
    #     "liquidity_pool": [
    #         {
    #             "platform": "Uniswap",
    #             "pair": "ETH/USDT",
    #             "liquidity": 50,
    #             "change": 12.5,
    #         },
    #         {
    #             "platform": "SushiSwap",
    #             "pair": "BTC/USDT",
    #             "liquidity": 30,
    #             "change": -5.2,
    #         },
    #     ],
    #     "whale_transactions": [
    #         {
    #             "address": "0x12345...",
    #             "amount": 500,
    #             "asset": "ETH",
    #             "time_ago": "5 minutes ago",
    #         },
    #         {
    #             "address": "0x67890...",
    #             "amount": -250,
    #             "asset": "BTC",
    #             "time_ago": "1 hour ago",
    #         },
    #     ],
    # }


@app.get("/ai-signals", response_model=AISignalsResponse)
async def get_ai_signals(coinAddress: str, pairAddress: str):
    # Logic to fetch AI signals data based on coinAddress and pairAddress
    return {
        "strength": "Strong Buy",
        "confidence": 85,
        "pattern": "Accumulation",
        "patternPhase": "Phase 2/4",
        "prediction": "+42% Expected",
        "forecast": "24h Forecast",
        "featureEngineering": [
            {
                "name": "Social Volume Velocity",
                "weight": 30,
                "color": "green",
                "value": 85,
            },
            {
                "name": "Influencer Impact",
                "weight": 20,
                "color": "blue",
                "value": 65,
            },
            {
                "name": "Historical Pump Pattern",
                "weight": 25,
                "color": "purple",
                "value": 75,
            },
        ],
        "blockchainRecognition": [
            {
                "name": "Wash Trading Detection",
                "timeFrame": "Last 24 Hours",
                "riskColor": "green",
                "riskLevel": "Low Risk",
                "riskPercentage": 5,
            },
            {
                "name": "Smart Money Movement",
                "timeFrame": "Accumulation Phase",
                "riskColor": "green",
                "riskLevel": "Strong Signal",
                "riskPercentage": 95,
            },
        ],
        "alertThresholds": [
            {
                "name": "Social Mention Spike (+400% in 4h)",
                "status": "Triggered",
                "color": "green",
                "bgColor": "green",
            },
            {
                "name": "Liquidity Change (±15% in 24h)",
                "status": "Warning",
                "color": "yellow",
                "bgColor": "yellow",
            },
            {
                "name": "Transaction Volume (2x 7-day avg)",
                "status": "Normal",
                "color": "gray",
                "bgColor": "gray",
            },
        ],
    }


@app.get("/risk-assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment(coinAddress: str, pairAddress: str):
    # Logic to fetch risk assessment data based on coinAddress and pairAddress
    return {
        "sectionId": "5a8714c4-1dbf-42ca-8baf-61526238d342",
        "overallRiskScore": "Medium Risk",
        "riskLevel": "6.5/10",
        "smartContractSafetyPercentage": 85,
        "smartContractStatus": "Audited & Verified",
        "liquidityLockStatus": "Locked",
        "liquidityLockRemainingDays": 180,
        "ownershipStatus": "Renounced",
        "ownershipStatusDescription": "Contract ownership has been renounced, reducing rugpull risk",
        "mintFunctionStatus": "Present",
        "mintFunctionDescription": "Contract contains mint function - potential supply inflation risk",
        "transferRestrictions": "Limited",
        "transferRestrictionsDescription": "Max transaction limit: 1% of total supply",
        "liquidityRisk": "Medium",
        "liquidityRiskPercentage": 45,
        "concentrationRisk": "High",
        "concentrationRiskPercentage": 75,
        "smartContractRisk": "Low",
        "smartContractRiskPercentage": 15,
    }


@app.get("/historical", response_model=HistoricalResponse)
async def get_historical_data(coinAddress: str, pairAddress: str):
    # Logic to fetch historical data based on coinAddress and pairAddress
    return {
        "roi": 1245,
        "pumpPatterns": 4,
        "averagePumpReturn": 85,
        "recoveryTime": 48,
        "activeAlerts": 24,
        "highPriority": 12,
        "triggeredToday": 8,
        "triggeredChange": 3,
        "successRate": 92,
        "responseTime": 1.2,
    }


@app.post("/aggregate-analysis")
async def aggregate_analysis(token_pair_address: str, token_address: str, query: str, search_type: SearchType = SearchType.TOP, max_tweets: int = 10):
    # Call analyze_token_price
    price_data = await analyze_token_price(token_pair_address)
    
    # Call get_gmgn_token_info
    gmgn_data = await get_gmgn_token_info(token_address)
    
    # Call search_tweets_endpoint
    tweets_data = await search_tweets_endpoint(query=query, search_type=search_type, max_tweets=max_tweets)
    
    # Combine all outputs into a single JSON response
    combined_output = {
        "price_analysis": price_data,
        "gmgn_info": gmgn_data,
        "tweets_analysis": tweets_data,
    }
    predict_output=predict_crew.kickoff(inputs={"data":combined_output})
    return predict_output

# --- FastAPI Endpoint ---
@app.get("/combined-token-data", response_model=CombinedTokenData)
async def get_combined_token_data(pairAddress: str, tokenAddress: str):
    # Fetch token price data
    price_data = get_token_price(pairAddress=pairAddress)
    if not price_data:
        raise HTTPException(status_code=400, detail="Error fetching token price data")

    # Fetch GMGN data
    base_url = "https://gmgn.ai/base/token/VIVOWmEQ_"
    url = operator.concat(base_url, tokenAddress)
    gmgn_data = await crawl_gmgn(url)
    if not gmgn_data:
        raise HTTPException(status_code=400, detail="Error fetching GMGN data")

    # gmgn_analysis = gngm_crew.kickoff(inputs={"data": gmgn_data})
    # gmgn_data = gmgn_analysis.raw  # Extract structured data

    # Extract values dynamically (ensuring missing values are handled)
    dex_analytics = DexAnalyticsResponse(
        total_dex_volume=gmgn_data.get("total_dex_volume", 0.0),
        dex_volume_change=gmgn_data.get("dex_volume_change", 0.0),
        total_liquidity=price_data.get("totalLiquidityUsd", 0.0),
        liquidity_change=price_data["liquidityPercentChange"]["24h"],
        unique_traders=gmgn_data.get("unique_traders", 0),
        traders_change=gmgn_data.get("traders_change", 0.0),
        liquidity_pool=[
            LiquidityPool(
                platform=price_data.get("exchange", "Unknown"),
                pair=price_data.get("pairLabel", ""),
                liquidity=price_data.get("totalLiquidityUsd", 0.0),
                change=price_data["liquidityPercentChange"]["24h"]
            )
        ],
        whale_transactions=[
            WhaleTransaction(
                address=tx["address"],
                amount=tx["amount"],
                asset=tx["asset"],
                time_ago=tx["time_ago"]
            ) for tx in gmgn_data.get("whale_transactions", [])
        ]
    )

    ai_signals = AISignalsResponse(
        strength=gmgn_data.get("ai_signals", {}).get("strength", "Unknown"),
        confidence=gmgn_data.get("ai_signals", {}).get("confidence", 0),
        pattern=gmgn_data.get("ai_signals", {}).get("pattern", ""),
        patternPhase=gmgn_data.get("ai_signals", {}).get("patternPhase", ""),
        prediction=gmgn_data.get("ai_signals", {}).get("prediction", ""),
        forecast=gmgn_data.get("ai_signals", {}).get("forecast", ""),
        featureEngineering=[
            FeatureEngineering(**feat) for feat in gmgn_data.get("ai_signals", {}).get("featureEngineering", [])
        ],
        blockchainRecognition=[
            BlockchainRecognition(**bc) for bc in gmgn_data.get("ai_signals", {}).get("blockchainRecognition", [])
        ],
        alertThresholds=[
            AlertThreshold(**alert) for alert in gmgn_data.get("ai_signals", {}).get("alertThresholds", [])
        ]
    )

    risk_assessment = RiskAssessmentResponse(**gmgn_data.get("risk_assessment", {}))

    historical_data = HistoricalResponse(
        roi=gmgn_data.get("historical_data", {}).get("roi", 0),
        pumpPatterns=gmgn_data.get("historical_data", {}).get("pumpPatterns", 0),
        averagePumpReturn=gmgn_data.get("historical_data", {}).get("averagePumpReturn", 0),
        recoveryTime=gmgn_data.get("historical_data", {}).get("recoveryTime", 0),
        activeAlerts=gmgn_data.get("historical_data", {}).get("activeAlerts", 0),
        highPriority=gmgn_data.get("historical_data", {}).get("highPriority", 0),
        triggeredToday=gmgn_data.get("historical_data", {}).get("triggeredToday", 0),
        triggeredChange=gmgn_data.get("historical_data", {}).get("triggeredChange", 0),
        successRate=gmgn_data.get("historical_data", {}).get("successRate", 0),
        responseTime=gmgn_data.get("historical_data", {}).get("responseTime", 0.0)
    )

    combined_data = CombinedTokenData(
        token_price_data=price_data,
        gmgn_info=gmgn_data,
        dex_analytics=dex_analytics,
        ai_signals=ai_signals,
        risk_assessment=risk_assessment,
        historical_data=historical_data
    )

    return combined_data



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
