# ShwaasShala (श्वासशाला) — 3-Minute Video Demo Script

**Hackathon Track**: Environmental Hacks (WeMakeDevs x AWS) — Track 01 Air  
**Target Duration**: Exactly 3 Minutes (180 Seconds)  
**Presenter**: Senior Full-Stack + AI Engineer

---

## [0:00 – 0:30] The Problem: Children's Lungs vs. School Routine

**[Visual: Split screen — Opening title slide transitions to camera with high-contrast photo of children doing morning physical training in heavy winter smog]**

> **Speaker (Passionate, authoritative):**  
> *"Every morning across India, 150 million school children wake up to hazardous air. But here is the tragedy: at 7:45 AM, during peak temperature inversions when particulate matter PM2.5 concentrates at ground level, schools across Delhi, Lucknow, and Kolkata still line students up for a 45-minute outdoor morning assembly and vigorous PE drills.*
> 
> *Why? Because principals don't have actionable, localized data. They either panic and shut down entire schools, or they ignore the air entirely.
> 
> *Meet **ShwaasShala** — an intelligent pediatric air safety agent built on the AWS Strands Agents SDK that tells Indian school coordinators every morning whether it is safe for kids to be outside, and exactly when."*

---

## [0:30 – 2:10] Live Interactive Product Demo (Delhi & Kolkata)

**[Visual: Screen recording of `http://localhost:8000` with desktop browser open]**

> **Speaker:**  
> *"Let's open the ShwaasShala dashboard. We have zero setup friction — no API keys required for atmospheric data.*
> 
> *Notice our quick preset chips: Delhi, Mumbai, Bengaluru, Hubballi-Dharwad, Kolkata, Lucknow, Pune, and Hyderabad. Or search any neighborhood in India."*

**[Visual: Click on 'Delhi' preset chip]**

> **Speaker:**  
> *"Look at this immediate result for Delhi Public School, Mathura Road. 
> Instantly, the coordinator sees an unambiguous, high-contrast verdict banner: **AMBER CAUTION**, with live PM2.5 at 69.4 µg/m³ and CPCB AQI 130.*
> 
> *Notice this small badge: `🛡️ Rule-based Fallback` or `⚡ AI-generated (Strands Agent)`. If cloud model credentials are unconfigured or throttled, our deterministic engine ensures the demo and school operations **never break**."*

**[Visual: Scroll down to the 'Safest 2-Hour Window' card and the 48-Hour Chart]**

> **Speaker:**  
> *"Instead of telling teachers 'don't go outside all day,' ShwaasShala calculates the **Safest 2-Hour Continuous Window**: today from 10:00 AM to 12:00 PM, when solar convection mixes the boundary layer and PM2.5 drops to its daily low.
> 
> *On the Chart.js visualizer below, you see the next 48 hours of hourly PM2.5 color-coded according to the official Indian Central Pollution Control Board (CPCB) NAQI scale: Emerald for Good, Amber for Moderate, Red for Unsafe. The gold border highlights the safest window.*
> 
> *Now scroll down to the **School Coordinator Action Plan**. We don't speak in abstract ppm numbers; we give operational directives:
> - **Morning Assembly**: Keep under 15 minutes or move indoors.
> - **PE Classes**: Replace endurance running with indoor yoga.
> - **Commute**: Masks advised for students on open auto-rickshaws.
> - **Asthmatic Students**: High alert — keep rescue inhalers immediately accessible."*

---

## [2:10 – 2:30] Culturally Translated WhatsApp Broadcast (Hindi & Kannada)

**[Visual: Focus on the Parent WhatsApp Broadcast card. Click the language buttons 'हिंदी' and 'ಕನ್ನಡ']**

> **Speaker:**  
> *"The biggest bottleneck in school administration is communicating with parents. 
> Principals don't write essays; they broadcast on WhatsApp.*
> 
> *Watch this: I click **हिंदी (Hindi)**. Instantly, ShwaasShala drafts a culturally adapted, polite broadcast under 60 words:
> '🌿 श्वासशाला सूचना... आज हवा मध्यम है... आउटडोर खेल सीमित करें... सुरक्षित समय: 10 AM - 12 PM।'*
> 
> *Click **ಕನ್ನಡ (Kannada)** for our southern hubs like Bengaluru and Hubballi-Dharwad.
> With one click on 'Copy WhatsApp Message' or 'Direct Share via wa.me', the school sends the broadcast to thousands of parent groups in seconds."*

---

## [2:30 – 2:50] AWS Architecture & The Strands Agents SDK

**[Visual: Slide showing the Mermaid architecture diagram and code snippet of `@tool` in `app/services/strands_agent.py`]**

> **Speaker:**  
> *"Under the hood, ShwaasShala is powered by the **AWS Open-Source Strands Agents SDK (`strands-agents`)**.
> 
> *We equipped the Strands Agent with four modular tools:
> 1. `get_air_quality`
> 2. `get_weather`
> 3. `compute_risk`
> 4. `find_safe_window`
> 
> *Strands handles tool discovery and parameter serialization, routing to **Amazon Bedrock** (`Claude 3 Haiku`). And our dual-layer failover guarantees zero downtime. For deployment, we've provided ready-to-run scripts for **AWS App Runner** and **AWS Lightsail**."*

---

## [2:50 – 3:00] Impact Close

**[Visual: Camera on presenter, showing live app on mobile phone screen side-by-side]**

> **Speaker (Inspiring, concluding):**  
> *"One feature that works beats five that almost do. 
> ShwaasShala is built, fully tested, and ready today to protect millions of developing lungs across Indian classrooms every single morning. 
> 
> *Thank you, AWS and WeMakeDevs."*

---
*(End of Video — Total Time: 3:00)*
