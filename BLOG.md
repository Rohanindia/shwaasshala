# Building ShwaasShala: Protecting Millions of Young Lungs with AWS Strands Agents

*Published on AWS Builder Center | By Senior Full-Stack & AI Engineer*  
*Track: Environmental Hacks (WeMakeDevs x AWS) — Track 01: Air*

---

### The Problem: When Schools Breathe Blind
In urban and tier-2 India, millions of school children begin their day outdoors. At 7:30 AM during winter, ground-level temperature inversions trap toxic fine particulate matter (PM2.5) right above the asphalt. Ironically, that is the exact hour Indian schools conduct morning assembly and outdoor physical education (PE), often during peak inversion, triggering pediatric respiratory distress and asthma attacks.

School principals do not intentionally harm children; they lack localized, actionable decision support. Government air bulletins post city-wide averages hours after school starts, and weather apps display raw numbers (e.g., "165 µg/m³") that mean little to a busy school coordinator. Schools either shut down completely in panic or line children up in hazardous smog.

We built **ShwaasShala (श्वासशाला)** to give every school coordinator a definitive answer before 7:00 AM: Is it safe for children to be outside today? And if morning air is hazardous, what is the best 2-hour outdoor window for sports?

---

### The Stack: Lightweight, Deterministic, and Cloud-Native
To make ShwaasShala instantly deployable without heavy build tooling, we chose a fast Python backend with a zero-compilation frontend:

1. **Agent Orchestration**: **AWS Open-Source [Strands Agents SDK](https://github.com/strands-agents/sdk-python) (`strands-agents`)**. Strands provides declarative `@tool` decorators, structured Pydantic schema validation, and native connectors to **Amazon Bedrock** (`Claude 3 Haiku`).
2. **Data Ingestion**: Free, no API key atmospheric endpoints from Open-Meteo (Copernicus CAMS PM2.5, PM10, US AQI, temperature, and apparent heat index).
3. **Deterministic Math Engine**: Official Central Pollution Control Board (CPCB) NAQI piecewise linear interpolation combined with a conservative heat-stress threshold heuristic.
4. **FastAPI & In-Memory TTL Cache**: Sub-50ms endpoint responses with thread-safe 10-minute caching.
5. **Mobile-First Single Page UI**: Tailwind CSS CDN and Chart.js rendering 48-hour hourly pollution distributions with direct WhatsApp `wa.me` sharing.

---

### What Fought Back: Lessons from the Trenches
Building production-grade environmental agents brings real-world curveballs:

* **The Hallucination vs. Children's Health Dilemma**: Large Language Models are prone to inventing pollutant numbers or softening air hazards. We solved this by enforcing a hard separation of concerns: our deterministic Python engine computes the official CPCB breakpoints and optimal windows mathematically. The Strands Agent inspects these tools and synthesizes the human advisory.
* **Resilience in Production**: When building for hackathons or rural schools, cloud model endpoints can experience transient credential hiccups or throttling. Built-in fallback: if the model is unavailable, the rule-based engine still returns an advisory. Without Bedrock credentials the app runs on the deterministic engine; with credentials the Strands agent writes the advisory.
* **Culturally Attuned Communication**: Parents ignore technical PDFs. They read WhatsApp. We constrained parent messages to strictly under 60 words, translated with natural nuances in Hindi (हिंदी) and Kannada (ಕನ್ನಡ) for southern tech hubs like Hubballi and Bengaluru.

---

### What's Next: Rooftops and Real-Time IoT
ShwaasShala currently predicts air quality via regional numerical weather prediction and ground monitoring stations. Next steps include:
* **IoT Micro-Sensor Ingestion**: Connecting school rooftop air monitors via AWS IoT Core.
* **AWS End User Messaging**: Automated scheduled WhatsApp broadcast triggers directly to verified school coordinator accounts every morning at 6:30 AM.
* **State Education Board Dashboards**: Aggregating school compliance across whole districts to assist education ministries during seasonal emergency pollution episodes.

By pairing the AWS Strands Agents SDK with uncompromising pediatric health benchmarks, ShwaasShala proves that one focused, working feature beats five prototypes that almost work.

---
*Built with ❤️ for Indian school children at the WeMakeDevs x AWS Environmental Hackathon.*
