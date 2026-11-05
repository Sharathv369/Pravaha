import React, { createContext, useContext, useState, ReactNode } from 'react';

export type Language = 'EN' | 'HI';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  EN: {
    // Brand & Header
    'brand.tagline': 'Predict the Surge. Protect the People.',
    'brand.version': 'CORE v4.2',
    'nav.dashboard': 'Dashboard',
    'nav.map': 'River Map',
    'nav.alerts': 'Flood Alerts',
    'nav.community': 'Community',
    'nav.relief': 'Relief Hub',
    'nav.search': 'Search all 38 USGS stations, basins, IDs...',
    'nav.emergency': 'EMERGENCY PROTOCOL',
    'nav.gauges': '33 EVALUATED LORSO GAUGES',
    'nav.safeSpotsCount': '8 Safe Shelters Active',
    
    // Common Actions
    'action.inspect': 'Inspect Telemetry',
    'action.selected': 'Currently Selected',
    'action.fullHydrograph': 'Full Hydrograph',
    'action.issueAlert': 'Issue Alert',
    'action.triggerDispatch': 'Trigger Municipal Dispatch',
    'action.transmitting': 'Transmitting Simulation...',
    'action.showAll': 'Show All (38 Datasets)',
    'action.showLess': 'Show Top 5',
    'action.top5': 'Top 5',
    'action.top10': 'Top 10',
    'action.all38': 'All 38 Stations',
    'action.allStations': 'All Stations',
    'action.searchStations': 'Search 38 stations by ID or river...',
    'action.filterAll': 'All Basins',
    'action.viewSafeSpots': 'Find Safe Spots & Shelters',
    'action.close': 'Close',
    'action.retry': 'Retry Connection',
    'action.submit': 'Submit Report',
    
    // Dashboard Page
    'dash.heroTitle': 'Predict the Surge. Protect the People.',
    'dash.heroDesc': 'Hydrological early warning system combining verified USGS telemetry, NASA MERRA-2 meteorology, and physically constrained LORSO machine learning.',
    'dash.lorsoBadge': 'LORSO Machine Learning Core',
    'dash.stationPool': 'VERIFIED USGS STREAMGAUGE STATIONS',
    'dash.stationPoolDesc': 'All 38 streamgauging stations with historical discharge records, coordinate metadata and drainage basin profiles.',
    'dash.showingStations': 'Displaying all 38 verified hydrological datasets',
    'dash.metrics.activeStations': 'Stations in Dataset',
    'dash.metrics.floodRiskWatch': 'Flood Risk Watch',
    'dash.metrics.historicalMax': 'Historical Max Recorded',
    'dash.metrics.precipInflow': '24h Precip Inflow',
    'dash.metrics.activeAlerts': 'Active Broadcast Alerts',
    'dash.metrics.pooledR2': 'Pooled R² (LORSO Benchmark)',
    'dash.tabs.overview': 'Overview',
    'dash.tabs.hydrograph': 'Hydrograph Telemetry',
    'dash.tabs.catchment': 'Catchment Physiography',
    'dash.tabs.lorso': 'LORSO Model Validation',
    'dash.tabs.scenarios': 'Scenario Projections',
    'dash.tabs.incidentStream': 'Citizen Incident Stream',
    'dash.timeRanges.7d': '7 Days',
    'dash.timeRanges.30d': '30 Days',
    'dash.timeRanges.90d': '90 Days',
    'dash.timeRanges.1y': '1 Year',
    'dash.timeRanges.all': 'Full Record',
    'dash.recordLimitation': 'Historical Record Limitation for Station',

    // River Map Page
    'map.title': 'River Intelligence GIS Engine',
    'map.viewport': 'Active Basin Viewport',
    'map.drainage': 'Verified Drainage Area',
    'map.floodMode': 'Flood Monitoring',
    'map.reliefMode': 'Relief Logistics',
    'map.layer.stations': 'River Stations (38)',
    'map.layer.shelters': 'Safe Spots & Shelters (8)',
    'map.layer.radar': 'High-Resolution QPE Radar • Simulated',
    'map.layer.vectors': 'USGS River Vectors',
    'map.layer.polygons': 'Catchment Polygons • Simulated',
    'map.layer.sos': 'Citizen SOS Signals (14) • Demo',
    'map.style.terrain': 'Terrain',
    'map.style.satellite': 'Satellite',
    'map.style.streets': 'Streets',
    'map.fitBounds': 'Fit All 38 Stations',
    'map.searchPlaceholder': 'Search 38 stations by name, ID or basin...',
    'map.nearestStation': 'Nearest USGS Station',
    'map.clickPrompt': 'Click anywhere on map to find nearest station',
    'map.tab.historic': 'Option 1 — Historic Station Telemetry',
    'map.tab.simulator': 'Option 2 — Rainfall Scenario Simulator',
    'map.scenario.title': 'Rainfall Scenario Simulator',
    'map.scenario.subtitle': 'Runoff scenario is an interactive computational demonstration • Demo',
    'map.scenario.disclaimer': 'DEMONSTRATION SCENARIO — NOT OPERATIONAL FORECAST',
    'map.scenario.inflow': 'Catchment Precipitation Depth',
    'map.scenario.duration': 'Storm Inflow Duration',
    'map.scenario.soil': 'Antecedent Soil Saturation',
    'map.scenario.soil.dry': 'Dry Basin (Low Runoff)',
    'map.scenario.soil.normal': 'Normal Moisture',
    'map.scenario.soil.saturated': 'Fully Saturated (Rapid Runoff)',
    'map.scenario.peak': 'Simulated Peak Crest',
    'map.scenario.status': 'Hydrological Surge Status',
    'map.scenario.minimize': 'Minimize',
    'map.scenario.expand': 'Open Rainfall Simulator',
    'map.safeSpot.title': 'Demonstration High-Ground Evacuation Scenario',
    'map.safeSpot.freeboard': 'Freeboard Above Surge',
    'map.safeSpot.capacity': 'Shelter Capacity',
    'map.safeSpot.supplies': 'Emergency Supplies',
    'map.safeSpot.contact': 'Emergency Frequency / Comms',
    'map.safeSpot.certified': 'Demonstration Scenario',
    'map.safeSpot.findRoute': 'Open Relief Logistics',
    
    // Alerts Page
    'alerts.title': 'Advanced Flood Alert System',
    'alerts.subtitle': 'Automated hydrological multi-channel early warning dispatcher. Coordinates cell broadcasts, WhatsApp community sentinels, and municipal sirens when discharge forecasts cross safety floors.',
    'alerts.table.title': 'Verified USGS Station Early Warning Matrix',
    'alerts.table.desc': 'Continuous automated early warning monitoring across all 38 verified USGS streamgauging stations in PRAVAHA.',
    'alerts.search': 'Filter broadcasts by station, ID or basin...',
    'alerts.geofence': 'Broadcast Geofence Radius',
    'alerts.channels': 'Active Transmission Channels',
    'alerts.kin': 'Kin Alert Network',
    'alerts.kinDesc': 'Verified emergency contacts automatically alerted when local surge thresholds trigger.',
    'alerts.ping': 'Send Verification Ping',
    'alerts.pingSent': 'Ping Transmitted',
    
    // Community Page
    'community.title': 'Community Sentinel & Ground-Truth Network',
    'community.subtitle': 'Decentralized peer-to-peer reporting of localized flash surges, bridge debris blockages, and high-ground shelter status.',
    'community.submitReport': 'Submit Ground Incident Report',
    'community.activeReports': 'Verified Community Hazard Reports',
    'community.hazardType': 'Hazard Category',
    'community.location': 'Location Description',
    'community.severity': 'Observed Severity',
    'community.description': 'Observations & Notes',
    'community.upvote': 'Verify / Upvote',
    'community.verifiedBy': 'Verified by residents',
    'community.reportSuccess': 'Report transmitted to Sentinel Feed',
    
    // Relief Hub Page
    'relief.title': 'NGO & First Responder Relief Coordination Hub',
    'relief.subtitle': 'Unified logistics staging, amphibious transport routing, and relief shelter supplies balancing during high-water emergencies.',
    'relief.sheltersTitle': 'Active High-Ground Safe Shelters',
    'relief.resourcesTitle': 'Relief Resource Stockpiles & Staging',
    'relief.partnerNGOs': 'Accredited Relief Partners',
    'relief.dispatchSupplies': 'Dispatch Supplies',
    'relief.requestTransport': 'Request Boat Transport',
    'relief.statusReady': 'Ready for Deployment',
    'relief.statusDispatched': 'En Route to Shelter',
    
    // Risk Levels
    'risk.critical': 'Critical Surge',
    'risk.warning': 'Flood Warning',
    'risk.advisory': 'Advisory Threshold',
    'risk.normal': 'Normal Baseflow',
  },
  HI: {
    // Brand & Header
    'brand.tagline': 'बाढ़ का पूर्वानुमान। नागरिकों की सुरक्षा।',
    'brand.version': 'संस्करण 4.2',
    'nav.dashboard': 'डैशबोर्ड',
    'nav.map': 'नदी मानचित्र',
    'nav.alerts': 'चेतावनी तंत्र',
    'nav.community': 'नागरिक रिपोर्ट',
    'nav.relief': 'राहत केंद्र',
    'nav.search': 'सभी 38 USGS स्टेशन, बेसिन, आईडी खोजें...',
    'nav.emergency': 'आपातकालीन प्रोटोकॉल',
    'nav.gauges': '33 मूल्यांकित LORSO गेज',
    'nav.safeSpotsCount': '8 सुरक्षित आश्रय सक्रिय',
    
    // Common Actions
    'action.inspect': 'टेलीमेट्री देखें',
    'action.selected': 'वर्तमान चयनित',
    'action.fullHydrograph': 'विस्तृत हाइड्रोग्राफ',
    'action.issueAlert': 'चेतावनी जारी करें',
    'action.triggerDispatch': 'नगर निगम प्रेषण शुरू करें',
    'action.transmitting': 'सिमुलेशन प्रेषित हो रहा है...',
    'action.showAll': 'सभी 38 डेटासेट देखें',
    'action.showLess': 'शीर्ष 5 स्टेशन देखें',
    'action.top5': 'शीर्ष 5',
    'action.top10': 'शीर्ष 10',
    'action.all38': 'सभी 38 स्टेशन',
    'action.allStations': 'सभी स्टेशन',
    'action.searchStations': 'स्टेशन आईडी या नदी नाम से खोजें...',
    'action.filterAll': 'सभी बेसिन',
    'action.viewSafeSpots': 'सुरक्षित स्थल एवं आश्रय खोजें',
    'action.close': 'बंद करें',
    'action.retry': 'पुनः प्रयास करें',
    'action.submit': 'रिपोर्ट दर्ज करें',
    
    // Dashboard Page
    'dash.heroTitle': 'बाढ़ का पूर्वानुमान। नागरिकों की सुरक्षा।',
    'dash.heroDesc': 'सत्यापित USGS टेलीमेट्री, NASA MERRA-2 मौसम विज्ञान और भौतिक सीमाओं पर आधारित LORSO मशीन लर्निंग का उपयोग करने वाली प्रारंभिक बाढ़ चेतावनी प्रणाली।',
    'dash.lorsoBadge': 'LORSO मशीन लर्निंग कोर',
    'dash.stationPool': 'सत्यापित USGS नदी गेज स्टेशन',
    'dash.stationPoolDesc': 'ऐतिहासिक जल प्रवाह रिकॉर्ड, निर्देशांक और जल निकासी बेसिन प्रोफाइल वाले सभी 38 स्टेशन।',
    'dash.showingStations': 'सभी 38 सत्यापित हाइड्रोलॉजिकल डेटासेट प्रदर्शित',
    'dash.metrics.activeStations': 'डेटासेट में स्टेशन',
    'dash.metrics.floodRiskWatch': 'बाढ़ जोखिम निगरानी',
    'dash.metrics.historicalMax': 'ऐतिहासिक अधिकतम दर्ज',
    'dash.metrics.precipInflow': '24 घंटे वर्षा प्रवाह',
    'dash.metrics.activeAlerts': 'सक्रिय चेतावनी प्रसारण',
    'dash.metrics.pooledR2': 'LORSO बेंचमार्क R²',
    'dash.tabs.overview': 'सिंहावलोकन',
    'dash.tabs.hydrograph': 'हाइड्रोग्राफ टेलीमेट्री',
    'dash.tabs.catchment': 'कैचमेंट विशेषताएं',
    'dash.tabs.lorso': 'LORSO मॉडल सत्यापन',
    'dash.tabs.scenarios': 'परिदृश्य अनुमान',
    'dash.tabs.incidentStream': 'नागरिक घटना रिपोर्ट',
    'dash.timeRanges.7d': '7 दिन',
    'dash.timeRanges.30d': '30 दिन',
    'dash.timeRanges.90d': '90 दिन',
    'dash.timeRanges.1y': '1 वर्ष',
    'dash.timeRanges.all': 'संपूर्ण रिकॉर्ड',
    'dash.recordLimitation': 'स्टेशन के लिए ऐतिहासिक रिकॉर्ड सीमा',

    // River Map Page
    'map.title': 'नदी मानचित्र खुफिया प्रणाली (GIS)',
    'map.viewport': 'सक्रिय बेसिन दृश्य',
    'map.drainage': 'सत्यापित जल निकासी क्षेत्र',
    'map.floodMode': 'बाढ़ निगरानी',
    'map.reliefMode': 'राहत रसद',
    'map.layer.stations': 'नदी स्टेशन (38)',
    'map.layer.shelters': 'सुरक्षित स्थल एवं आश्रय (8)',
    'map.layer.radar': 'उच्च-रिज़ॉल्यूशन रडार • सिम्युलेटेड',
    'map.layer.vectors': 'नदी बहाव मार्ग',
    'map.layer.polygons': 'कैचमेंट बहुभुज • सिम्युलेटेड',
    'map.layer.sos': 'नागरिक एसओएस संकेत (14) • डेमो',
    'map.style.terrain': 'स्थलाकृति',
    'map.style.satellite': 'उपग्रह दृश्य',
    'map.style.streets': 'सड़क दृश्य',
    'map.fitBounds': 'सभी 38 स्टेशन दिखाएं',
    'map.searchPlaceholder': 'नाम, आईडी या बेसिन द्वारा 38 स्टेशन खोजें...',
    'map.nearestStation': 'निकटतम USGS स्टेशन',
    'map.clickPrompt': 'निकटतम स्टेशन खोजने के लिए मानचित्र पर कहीं भी क्लिक करें',
    'map.tab.historic': 'विकल्प 1 — ऐतिहासिक स्टेशन टेलीमेट्री',
    'map.tab.simulator': 'विकल्प 2 — वर्षा परिदृश्य सिम्युलेटर',
    'map.scenario.title': 'वर्षा परिदृश्य सिम्युलेटर',
    'map.scenario.subtitle': 'अपवाह परिदृश्य एक इंटरैक्टिव कम्प्यूटेशनल सिमुलेशन है • डेमो',
    'map.scenario.disclaimer': 'प्रदर्शन परिदृश्य — परिचालन पूर्वानुमान नहीं',
    'map.scenario.inflow': 'कैचमेंट में वर्षा की गहराई',
    'map.scenario.duration': 'तूफान वर्षा अवधि',
    'map.scenario.soil': 'मिट्टी की प्रारंभिक संतृप्ति',
    'map.scenario.soil.dry': 'सूखा बेसिन (कम अपवाह)',
    'map.scenario.soil.normal': 'सामान्य नमी',
    'map.scenario.soil.saturated': 'पूर्णतः संतृप्त (तीव्र अपवाह)',
    'map.scenario.peak': 'अनुमानित चरम जल प्रवाह',
    'map.scenario.status': 'हाइड्रोलॉजिकल उछाल स्थिति',
    'map.scenario.minimize': 'छोटा करें',
    'map.scenario.expand': 'वर्षा सिम्युलेटर खोलें',
    'map.safeSpot.title': 'प्रदर्शन परिदृश्य — उच्च-भूमि आश्रय',
    'map.safeSpot.freeboard': 'बाढ़ जलस्तर से सुरक्षित ऊंचाई',
    'map.safeSpot.capacity': 'आश्रय क्षमता',
    'map.safeSpot.supplies': 'आपातकालीन राहत सामग्री',
    'map.safeSpot.contact': 'आपातकालीन संपर्क / संचार',
    'map.safeSpot.certified': 'प्रदर्शन परिदृश्य',
    'map.safeSpot.findRoute': 'राहत रसद खोलें',
    
    // Alerts Page
    'alerts.title': 'उन्नत बाढ़ चेतावनी प्रणाली',
    'alerts.subtitle': 'स्वचालित हाइड्रोलॉजिकल प्रारंभिक चेतावनी प्रेषक। जब पूर्वानुमान खतरे के स्तर को पार करता है तो सेल प्रसारण, व्हाट्सएप और सायरन का समन्वय करता है।',
    'alerts.table.title': 'सत्यापित USGS स्टेशन पूर्व चेतावनी मैट्रिक्स',
    'alerts.table.desc': 'PRAVAHA में सभी 38 सत्यापित USGS नदी स्टेशनों पर निरंतर स्वचालित निगरानी।',
    'alerts.search': 'स्टेशन, आईडी या बेसिन द्वारा अलर्ट खोजें...',
    'alerts.geofence': 'प्रसारण दायरा (रेडियस)',
    'alerts.channels': 'सक्रिय प्रसारण चैनल',
    'alerts.kin': 'पारिवारिक सुरक्षा नेटवर्क',
    'alerts.kinDesc': 'स्थानीय बाढ़ सीमा पार होने पर सत्यापित संपर्कों को स्वचालित रूप से सतर्क किया जाता है।',
    'alerts.ping': 'सत्यापन पिंग भेजें',
    'alerts.pingSent': 'पिंग प्रेषित किया गया',
    
    // Community Page
    'community.title': 'नागरिक संतरी एवं ज़मीनी सत्यापन नेटवर्क',
    'community.subtitle': 'स्थानीय बाढ़, पुल पर मलबे के अवरोध और सुरक्षित आश्रयों की स्थिति की विकेंद्रीकृत नागरिक रिपोर्टिंग।',
    'community.submitReport': 'ज़मीनी घटना रिपोर्ट दर्ज करें',
    'community.activeReports': 'सत्यापित नागरिक खतरा रिपोर्ट',
    'community.hazardType': 'खतरे की श्रेणी',
    'community.location': 'स्थान का विवरण',
    'community.severity': 'देखी गई गंभीरता',
    'community.description': 'अवलोकन एवं टिप्पणियां',
    'community.upvote': 'सत्यापित करें / समर्थन दें',
    'community.verifiedBy': 'नागरिकों द्वारा सत्यापित',
    'community.reportSuccess': 'रिपोर्ट संतरी फीड में सफलतापूर्वक दर्ज हुई',
    
    // Relief Hub Page
    'relief.title': 'एनजीओ एवं राहत कार्यकर्ता समन्वय केंद्र',
    'relief.subtitle': 'उच्च-जल आपात स्थिति के दौरान एकीकृत रसद, नाव परिवहन मार्ग और राहत आश्रय आपूर्ति का समन्वय।',
    'relief.sheltersTitle': 'सक्रिय उच्च-भूमि सुरक्षित आश्रय',
    'relief.resourcesTitle': 'राहत सामग्री भंडार एवं रसद केंद्र',
    'relief.partnerNGOs': 'मान्यता प्राप्त राहत साझेदार',
    'relief.dispatchSupplies': 'राहत सामग्री भेजें',
    'relief.requestTransport': 'नाव परिवहन का अनुरोध करें',
    'relief.statusReady': 'तैनाती के लिए तैयार',
    'relief.statusDispatched': 'आश्रय की ओर रवाना',
    
    // Risk Levels
    'risk.critical': 'गंभीर बाढ़ उछाल',
    'risk.warning': 'बाढ़ चेतावनी',
    'risk.advisory': 'सलाहकार स्तर',
    'risk.normal': 'सामान्य प्रवाह',
  },
};

const LanguageContext = createContext<LanguageContextType>({
  language: 'EN',
  setLanguage: () => {},
  t: (key: string) => key,
});

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    return (localStorage.getItem('pravaha_lang') as Language) || 'EN';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('pravaha_lang', lang);
  };

  const t = (key: string): string => {
    return translations[language]?.[key] || translations['EN'][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
