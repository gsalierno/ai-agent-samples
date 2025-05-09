import random
import asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent, Tool, ModelRetry

# 1️Travel Planner Tool
class TravelInput(BaseModel):
    destination: str = Field(..., description="City to visit")
    days: int = Field(..., description="Number of days")

class TravelOutput(BaseModel):
    itinerary: list[str] = Field(..., description="Day-by-day plan")

@Tool
def travel_planner(input: TravelInput) -> TravelOutput:
    itinerary = [f"Day {i+1}: Visit famous spots in {input.destination}" for i in range(input.days)]
    return TravelOutput(itinerary=itinerary)

#Translator Tool
class TranslateInput(BaseModel):
    text: str
    language: str

class TranslateOutput(BaseModel):
    translation: str

@Tool
def translator(input: TranslateInput) -> TranslateOutput:
    translations = {'thank you': {'French': 'merci'}}
    translation = translations.get(input.text.lower(), {}).get(input.language, "Translation not found")
    return TranslateOutput(translation=translation)

class WeatherInput(BaseModel):
    city: str
    day: int

class WeatherOutput(BaseModel):
    forecast: str

# 3️Weather Checker Tool (with retry logic)
@Tool
def weather_checker(input: WeatherInput) -> WeatherOutput:
    # Simulate a 50% chance of failure to test retry
    if random.random() < 0.5:
        print(f"Simulated API failure for {input.city} on day {input.day}")
        raise ModelRetry(f"Temporary API failure for {input.city} on day {input.day}")
    # Fake weather data
    forecast = f"Day {input.day}: Sunny in {input.city}"
    return WeatherOutput(forecast=forecast)

# Set up the Agent
agent = Agent(
    'google-gla:gemini-1.5-flash',
    tools=[travel_planner, translator, weather_checker],
    system_prompt=(
        "You are a travel assistant. You can plan trips, translate text, "
        "and check the weather forecast for a destination."
    ),
    retries=3,
    instrument=True
)

# Run the agent
if __name__ == "__main__":
    prompt = (
        "Plan a 3-day trip to Paris, tell me how to say 'thank you' in French, "
        "and give me the weather forecast for each day of the trip."
    )
    result = asyncio.run(agent.run(prompt))
    print(result)
