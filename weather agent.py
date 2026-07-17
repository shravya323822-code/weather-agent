#weather agent
!pip install -q gradio google-genai requests
import gradio as gr
import requests
from google import genai
client=genai.Client(api_key=" ")
def get_coordinates(city):
  url=f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
  response=requests.get(url,timeout=10)
  data=response.json()
  if "results" not in data:
    return None
  lat=data["results"][0]["latitude"]
  lon=data["results"][0]["longitude"]
  return lat,lon
def get_weather(lat,lon):
  url=(
      f"https://api.open-meteo.com/v1/forecast?"
      f"latitude={lat}&longitude={lon}"
      f"&current=temperature_2m,relative_humidity_2m,"
      f"wind_speed_10m,weather_code"
  )
  response=requests.get(url,timeout=10)
  data=response.json()
  return data["current"]
def weather_agent(query):
  prompt=f"""
extract only the city name from sentence below.
Sentence:
{query}
Return only the city name.
"""
  city=client.models.generate_content(
      model="gemini-2.5-pro",
      contents=prompt
  ).text.strip()
  location=get_coordinates(city)
  if location is None:
    return "City not found."
  lat,lon=location
  weather=get_weather(lat,lon)
  final_prompt=f"""
The user asked:
{query}
Weather Data
temperature:{weather['temperature_2m']}c
humidity:{weather['relative_humidity_2m']}%
wind_speed:{weather['wind_speed_10m']}km/h
weather_code:{weather['weather_code']}
Explain the weather in a friendly way
"""
  answer=client.models.generate_content(
      model="gemini-2.5-pro",
      contents=final_prompt
  )
  return answer.text

demo = gr.Interface(
    fn=weather_agent,
    inputs=gr.Textbox(
        label="Ask About Weather",
        placeholder="Example: What's the weather in Hyderabad?"
    ),
    outputs=gr.Textbox(label="Weather Report"),
    title="🌦️ AI Weather Agent",
    description="Ask about the weather in any city."
)

demo.launch(debug=True)
