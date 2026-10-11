# Hackathon Submission Details

### Project Title
**ShwaasShala (श्वासशाला)** — AI Pediatric Air Safety & Outdoor Window Advisor for Indian Schools

---

### One-Line Pitch
An intelligent AI agent powered by AWS Strands Agents SDK that tells Indian school principals and parents every morning whether it is safe for kids to be outside, and exactly when.

---

### Track
**Track 01: Air** (Environmental Hacks — WeMakeDevs x AWS)

---

### Description
Millions of school children in India breathe toxic air exceeding WHO and Central Pollution Control Board (CPCB) limits. Often during peak inversion (7:00 AM – 8:30 AM), schools routinely conduct outdoor morning assemblies and endurance sports drills, causing respiratory distress and asthma attacks. 

ShwaasShala solves this by providing:
1. **Clear Morning Risk Verdict**: A prominent GREEN / AMBER / RED badge calculated from live PM2.5, PM10, and apparent temperature (heat index) against official CPCB NAQI breakpoints.
2. **Optimal 2-Hour Outdoor Window**: Evaluates 48-hour continuous forecast data to find the single safest 2-hour daylight block for PE sports and recess when air pollution and heat stress are lowest.
3. **Actionable School Coordinator Directives**: Operationally specific recommendations for morning assembly, physical education, lunch recess, student commute, and sensitive/asthmatic children.
4. **Instant WhatsApp Broadcasts**: Culturally nuanced, polite messages strictly under 60 words generated in English, Hindi (हिंदी), and Kannada (ಕನ್ನಡ), with 1-click clipboard copy and `wa.me` sharing.
5. **Built-in fallback: if the model is unavailable, the rule-based engine still returns an advisory.** Powered by the AWS Open-Source Strands Agents SDK with Bedrock integration, paired with an automatic deterministic mathematical fallback.

---

### Tech Stack
- **AI Agent Framework**: AWS Open-Source Strands Agents SDK ([strands-agents](https://github.com/strands-agents/sdk-python))
- **Cloud Foundation**: Amazon Bedrock (`anthropic.claude-3-haiku-20240307-v1:0`), AWS App Runner, AWS Lightsail Containers
- **Backend**: Python 3.12, FastAPI, Uvicorn, HTTPX, Pydantic v2
- **Data APIs**: Open-Meteo Air Quality API (Copernicus CAMS), Open-Meteo Forecast API, Open-Meteo Geocoding API (free, no API key)
- **Frontend**: Lightweight Single-Page Application (HTML5, Tailwind CSS CDN, Chart.js CDN)
- **Testing**: Pytest & Pytest-Asyncio (100% automated test pass rate)
- **Containerization**: Docker (multi-stage python:3.12-slim)

---

### AWS Usage Statement
ShwaasShala utilizes the **AWS Open-Source [Strands Agents SDK](https://github.com/strands-agents/sdk-python)** (`strands-agents`) as its foundational agent framework. The Strands Agent is equipped with specialized tools (`@tool get_air_quality`, `@tool get_weather`, `@tool compute_risk`, `@tool find_safe_window`) to analyze atmospheric data and formulate pediatric advisories. It interfaces natively with **Amazon Bedrock** while supporting flexible multi-provider setups (OpenAI, Anthropic, Ollama) and an automatic deterministic CPCB risk fallback engine. Without Bedrock credentials the app runs on the deterministic engine; with credentials the Strands agent writes the advisory. Ready-to-run container deployment scripts for **AWS App Runner** and **AWS Lightsail Containers** are included in the `deploy/` directory.

---

### Repository Link
`https://github.com/[YOUR_GITHUB_USERNAME]/shwaasshala`

---

### Video Demo Link (3-Minute)
`https://youtu.be/[YOUR_DEMO_VIDEO_ID]`

---

### Live Application URL (Optional Deployment)
`http://localhost:8000` (or AWS App Runner endpoint)
