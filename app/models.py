from pydantic import BaseModel
from typing import List


# --- Pydantic Models ---
class LiquidityPool(BaseModel):

    platform: str
    pair: str
    liquidity: float
    change: float

class WhaleTransaction(BaseModel):
    address: str
    amount: float
    asset: str
    time_ago: str

class DexAnalyticsResponse(BaseModel):
    total_dex_volume: float
    dex_volume_change: float
    total_liquidity: float
    liquidity_change: float
    unique_traders: int
    traders_change: float
    liquidity_pool: List[LiquidityPool]
    whale_transactions: List[WhaleTransaction]

class FeatureEngineering(BaseModel):
    name: str
    weight: int
    color: str
    value: int

class BlockchainRecognition(BaseModel):
    name: str
    timeFrame: str
    riskColor: str
    riskLevel: str
    riskPercentage: int

class AlertThreshold(BaseModel):
    name: str
    status: str
    color: str
    bgColor: str

class AISignalsResponse(BaseModel):
    strength: str
    confidence: int
    pattern: str
    patternPhase: str
    prediction: str
    forecast: str
    featureEngineering: List[FeatureEngineering]
    blockchainRecognition: List[BlockchainRecognition]
    alertThresholds: List[AlertThreshold]

class RiskAssessmentResponse(BaseModel):
    sectionId: str
    overallRiskScore: str
    riskLevel: str
    smartContractSafetyPercentage: int
    smartContractStatus: str
    liquidityLockStatus: str
    liquidityLockRemainingDays: int
    ownershipStatus: str
    ownershipStatusDescription: str
    mintFunctionStatus: str
    mintFunctionDescription: str
    transferRestrictions: str
    transferRestrictionsDescription: str
    liquidityRisk: str
    liquidityRiskPercentage: int
    concentrationRisk: str
    concentrationRiskPercentage: int
    smartContractRisk: str
    smartContractRiskPercentage: int

class HistoricalResponse(BaseModel):
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

class CombinedTokenData(BaseModel):
    token_price_data: dict
    gmgn_info: dict
    dex_analytics: DexAnalyticsResponse
    ai_signals: AISignalsResponse
    risk_assessment: RiskAssessmentResponse
    historical_data: HistoricalResponse
