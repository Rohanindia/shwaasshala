"""
Templates and multilingual text generators for ShwaasShala school advisories.
Strictly under 60 words for parent WhatsApp broadcasts.
"""

def get_whatsapp_message(
    risk_level: str,
    place: str,
    cpcb_band: str,
    cpcb_aqi: int,
    safe_window: str,
    lang: str = "en"
) -> str:
    lang = (lang or "en").lower()
    
    if lang == "hi":
        if risk_level == "GREEN":
            return (
                f"🌿 *श्वासशाला अपडेट: {place}*\n"
                f"आज हवा साफ और सुरक्षित है ({cpcb_band}, AQI {cpcb_aqi})। "
                f"सुबह की प्रार्थना और आउटडोर खेल पूरी तरह सुरक्षित हैं। "
                f"सर्वश्रेष्ठ बाहरी समय: {safe_window}। "
                f"शुभ दिन!"
            )
        elif risk_level == "AMBER":
            return (
                f"⚠️ *श्वासशाला सावधानी सूचना: {place}*\n"
                f"आज हवा मध्यम श्रेणी में है ({cpcb_band}, AQI {cpcb_aqi})। "
                f"थका देने वाले बाहरी खेल सीमित करें। "
                f"अस्थमा और एलर्जी से पीड़ित बच्चे इनडोर रहें। "
                f"सुरक्षित बाहरी समय: {safe_window}।"
            )
        else:  # RED
            return (
                f"🚨 *श्वासशाला वायु चेतावनी: {place}*\n"
                f"आज प्रदूषण अधिक है ({cpcb_band}, AQI {cpcb_aqi})! "
                f"आउटडोर असेंबली और खेल रद्द हैं। खिड़कियां बंद रखें। "
                f"स्कूल आवागमन पर मास्क अवश्य पहनें। "
                f"अस्थमा वाले बच्चे इनहेलर साथ रखें।"
            )
            
    elif lang == "kn":
        if risk_level == "GREEN":
            return (
                f"🌿 *ಶ್ವಾಸಶಾಲಾ ಮಾಹಿತಿ: {place}*\n"
                f"ಇಂದು ವಾಯು ಗುಣಮಟ್ಟ ಉತ್ತಮವಾಗಿದೆ ({cpcb_band}, AQI {cpcb_aqi}). "
                f"ಬೆಳಗಿನ ಪ್ರಾರ್ಥನೆ ಮತ್ತು ಹೊರಾಂಗಣ ಆಟಗಳು ಸಂಪೂರ್ಣ ಸುರಕ್ಷಿತ. "
                f"ಉತ್ತಮ ಹೊರಾಂಗಣ ಸಮಯ: {safe_window}. "
                f"ಶುಭ ದಿನ!"
            )
        elif risk_level == "AMBER":
            return (
                f"⚠️ *ಶ್ವಾಸಶಾಲಾ ಎಚ್ಚರಿಕೆ: {place}*\n"
                f"ವಾಯು ಗುಣಮಟ್ಟ ಸಾಧಾರಣವಾಗಿದೆ ({cpcb_band}, AQI {cpcb_aqi}). "
                f"ಕಠಿಣ ಹೊರಾಂಗಣ ಆಟಗಳನ್ನು ಮಿತಿಗೊಳಿಸಿ. "
                f"ಅಸ್ತಮಾ ಮತ್ತು ಸೂಕ್ಷ್ಮತೆಯುಳ್ಳ ಮಕ್ಕಳು ಒಳಾಂಗಣದಲ್ಲೇ ಇರಲಿ. "
                f"ಸುರಕ್ಷಿತ ಸಮಯ: {safe_window}."
            )
        else:  # RED
            return (
                f"🚨 *ಶ್ವಾಸಶಾಲಾ ತುರ್ತು ಎಚ್ಚರಿಕೆ: {place}*\n"
                f"ವಾಯು ಮಾಲಿನ್ಯ ಅಧಿಕವಾಗಿದೆ ({cpcb_band}, AQI {cpcb_aqi})! "
                f"ಹೊರಾಂಗಣ ಪ್ರಾರ್ಥನೆ ಮತ್ತು ಕ್ರೀಡೆಗಳನ್ನು ರದ್ದುಗೊಳಿಸಲಾಗಿದೆ. "
                f"ಶಾಲೆಗೆ ಪ್ರಯಾಣಿಸುವಾಗ ಮಾಸ್ಕ್ ಧರಿಸಿ. "
                f"ಅಸ್ತಮಾ ಇರುವ ಮಕ್ಕಳು ಇನ್‌ಹೇಲರ್ ಇಟ್ಟುಕೊಳ್ಳಿ."
            )
            
    else:  # Default: English
        if risk_level == "GREEN":
            return (
                f"🌿 *ShwaasShala Morning Update: {place}*\n"
                f"Air quality is healthy ({cpcb_band}, AQI {cpcb_aqi}). "
                f"Morning assembly & outdoor sports are fully safe today. "
                f"Best outdoor window: {safe_window}. "
                f"Have a great, active school day!"
            )
        elif risk_level == "AMBER":
            return (
                f"⚠️ *ShwaasShala Advisory: {place}*\n"
                f"Air quality is moderate ({cpcb_band}, AQI {cpcb_aqi}). "
                f"Limit strenuous outdoor exertion. "
                f"Children with asthma or respiratory sensitivities should stay indoors. "
                f"Optimal outdoor window: {safe_window}."
            )
        else:  # RED
            return (
                f"🚨 *ShwaasShala Air Alert: {place}*\n"
                f"Air quality is unsafe for children ({cpcb_band}, AQI {cpcb_aqi})! "
                f"Morning assembly & outdoor sports suspended. Keep classroom windows closed. "
                f"Masks advised during commute. Asthmatic students must carry inhalers."
            )
