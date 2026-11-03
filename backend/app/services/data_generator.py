import os
import json
import csv
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.models.entities import (
    Customer, Product, Channel, Survey, Theme, SentimentLabel,
    SurveyResponse, Review, Ticket, SupportMessage, ActionItem,
    DataQualityIssue, StateChangeEvent, ProcessingRun, ModelEvaluation
)

SEED = 20261022

# Master Themes Taxonomy (18 themes)
THEME_TAXONOMY = [
    {"id": "THEME-000001", "name": "Product Quality", "parent": None, "keywords": "quality,build,durability,finish,material,hardware,defect,flaw,premium,cheap", "severity": "HIGH", "desc": "Feedback concerning the physical or functional quality of the product."},
    {"id": "THEME-000002", "name": "Pricing", "parent": None, "keywords": "price,expensive,cost,cheap,worth,value,discount,overpriced,affordable,deal", "severity": "MEDIUM", "desc": "Comments related to price-to-value, subscription costs, discounts and promos."},
    {"id": "THEME-000003", "name": "Customer Support", "parent": None, "keywords": "support,agent,representative,call,ticket,help,chat,service,rude,helpful,response", "severity": "HIGH", "desc": "Quality, responsiveness, and demeanor of customer service representatives."},
    {"id": "THEME-000004", "name": "Delivery Experience", "parent": None, "keywords": "delivery,shipping,courier,package,delayed,tracking,damaged,fast,late,arrival", "severity": "HIGH", "desc": "Shipment timeliness, packaging integrity, and tracking accuracy."},
    {"id": "THEME-000005", "name": "Application Performance", "parent": None, "keywords": "lag,slow,fast,freeze,crash,latency,speed,responsive,loading,timeout,memory", "severity": "HIGH", "desc": "Mobile and desktop application responsiveness, speed, and resource usage."},
    {"id": "THEME-000006", "name": "User Experience", "parent": None, "keywords": "ui,ux,interface,navigation,intuitive,confusing,design,layout,button,usability", "severity": "MEDIUM", "desc": "Ease of navigation, visual design, and user journey simplicity."},
    {"id": "THEME-000007", "name": "Payment Issues", "parent": None, "keywords": "payment,card,failed,checkout,charge,transaction,gateway,stripe,declined,double", "severity": "CRITICAL", "desc": "Payment gateway errors, double charges, and checkout transaction failures."},
    {"id": "THEME-000008", "name": "Refunds", "parent": "THEME-000007", "keywords": "refund,return,reimbursement,money back,credit,reverse,claim", "severity": "HIGH", "desc": "Processing speed and resolution of refund and chargeback requests."},
    {"id": "THEME-000009", "name": "Account Management", "parent": None, "keywords": "login,password,account,profile,sign in,auth,reset,verify,2fa,blocked", "severity": "HIGH", "desc": "User authentication, profile details, password resets, and account security."},
    {"id": "THEME-000010", "name": "Documentation", "parent": None, "keywords": "manual,docs,documentation,guide,tutorial,faq,api docs,instructions,missing docs", "severity": "LOW", "desc": "Clarity and completeness of user guides, manuals, and developer documentation."},
    {"id": "THEME-000011", "name": "Product Reliability", "parent": "THEME-000001", "keywords": "reliable,crash,stable,reboot,shut down,glitch,uptime,outage,disconnect", "severity": "CRITICAL", "desc": "Continuous uptime, lack of unintended resets, and dependable daily operation."},
    {"id": "THEME-000012", "name": "Feature Requests", "parent": None, "keywords": "wish,suggest,add,feature,need,integration,option,export,support for,ability to", "severity": "LOW", "desc": "Customer proposals for new capabilities, integrations, and enhancements."},
    {"id": "THEME-000013", "name": "Security and Privacy", "parent": None, "keywords": "privacy,security,data,leak,breach,permission,tracking,cookie,gdpr,unauthorized", "severity": "CRITICAL", "desc": "User data privacy, permission requests, encryption, and compliance matters."},
    {"id": "THEME-000014", "name": "Availability", "parent": None, "keywords": "stock,out of stock,available,sold out,backorder,restock,store,inventory", "severity": "MEDIUM", "desc": "Item stock status, cloud service region availability, and inventory levels."},
    {"id": "THEME-000015", "name": "Communication", "parent": "THEME-000003", "keywords": "email,notify,notification,update,sms,alert,spam,silence,uninformed", "severity": "MEDIUM", "desc": "Proactiveness and clarity of company communications, status updates, and alerts."},
    {"id": "THEME-000016", "name": "Installation", "parent": None, "keywords": "install,setup,unboxing,configure,pairing,assembly,drivers,first use", "severity": "MEDIUM", "desc": "Hardware assembly, unboxing, software onboarding, and initial pairing."},
    {"id": "THEME-000017", "name": "Technical Issues", "parent": "THEME-000005", "keywords": "bug,error,stack,exception,broken,malfunction,corrupt,firmware,patch", "severity": "HIGH", "desc": "Uncaught errors, system bugs, firmware regressions, and technical glitches."},
    {"id": "THEME-000018", "name": "Subscription Management", "parent": "THEME-000002", "keywords": "renew,cancel,subscription,plan,tier,auto-renew,upgrade,downgrade,billing cycle", "severity": "HIGH", "desc": "Managing monthly/yearly recurring subscriptions, renewals, and cancellations."}
]

# Product Taxonomy (25 products across 8 categories)
PRODUCT_TAXONOMY = [
    # Electronics
    {"name": "Aura UltraBook Pro 16", "category": "Electronics", "sku": "ELEC-LPT-001", "price": 1499.99},
    {"name": "NovaPulse True Wireless Earbuds", "category": "Electronics", "sku": "ELEC-EAR-002", "price": 179.99},
    {"name": "Horizon 4K Smart OLED Monitor", "category": "Electronics", "sku": "ELEC-MON-003", "price": 699.00},
    {"name": "Titanium Smartwatch Ultra", "category": "Electronics", "sku": "ELEC-WCH-004", "price": 349.50},
    # Software
    {"name": "CloudSync Enterprise Suite", "category": "Software", "sku": "SOFT-CLD-001", "price": 49.99},
    {"name": "DevForge AI Code Assistant", "category": "Software", "sku": "SOFT-AI-002", "price": 29.00},
    {"name": "CyberShield Endpoint Antivirus", "category": "Software", "sku": "SOFT-SEC-003", "price": 89.00},
    {"name": "DesignCraft Vector Studio", "category": "Software", "sku": "SOFT-DSN-004", "price": 199.99},
    # Home Appliances
    {"name": "RoboClean Precision Vacuum X5", "category": "Home Appliances", "sku": "HOME-VAC-001", "price": 450.00},
    {"name": "BrewMaster Smart Espresso Bar", "category": "Home Appliances", "sku": "HOME-COF-002", "price": 599.99},
    {"name": "AeroPure HEPA Air Purifier Pro", "category": "Home Appliances", "sku": "HOME-AIR-003", "price": 249.00},
    # Financial Services
    {"name": "Apex Wealth Robo-Advisor", "category": "Financial Services", "sku": "FIN-WLT-001", "price": 0.00},
    {"name": "SecurePay Business Merchant Account", "category": "Financial Services", "sku": "FIN-PAY-002", "price": 15.00},
    {"name": "CashFlow Plus Credit Line", "category": "Financial Services", "sku": "FIN-CRD-003", "price": 0.00},
    # Telecommunications
    {"name": "FiberGig Ultra 1Gbps Fiber", "category": "Telecommunications", "sku": "TEL-FIB-001", "price": 79.99},
    {"name": "5G Freedom Unlimited Mobile Plan", "category": "Telecommunications", "sku": "TEL-MOB-002", "price": 55.00},
    {"name": "CloudVoIP PBX Hosted System", "category": "Telecommunications", "sku": "TEL-VOI-003", "price": 35.00},
    # Retail
    {"name": "EcoThread Organic Cotton Hoodie", "category": "Retail", "sku": "RET-APP-001", "price": 65.00},
    {"name": "Venture Ergonomic Travel Backpack", "category": "Retail", "sku": "RET-BAG-002", "price": 110.00},
    {"name": "PeakGrip All-Weather Hiking Boots", "category": "Retail", "sku": "RET-FTW-003", "price": 145.00},
    # Healthcare Services
    {"name": "WellConnect 24/7 Telehealth Access", "category": "Healthcare Services", "sku": "HLT-TEL-001", "price": 25.00},
    {"name": "VitalCheck Home Health Lab Kit", "category": "Healthcare Services", "sku": "HLT-LAB-002", "price": 120.00},
    {"name": "MindEase Digital Therapy Program", "category": "Healthcare Services", "sku": "HLT-MND-003", "price": 40.00},
    # Subscription Services
    {"name": "OmniStream 4K Cinema Pass", "category": "Subscription Services", "sku": "SUB-STR-001", "price": 14.99},
    {"name": "GourmetBox Weekly Fresh Meal Kit", "category": "Subscription Services", "sku": "SUB-MEL-002", "price": 68.00}
]

# Channel Taxonomy (12 channels)
CHANNEL_TAXONOMY = [
    {"name": "Website", "type": "DIGITAL", "desc": "Company primary customer portal & e-commerce shop"},
    {"name": "Mobile Application", "type": "DIGITAL", "desc": "iOS and Android native mobile clients"},
    {"name": "Email", "type": "DIRECT", "desc": "Direct inbound support & inquiries via email"},
    {"name": "Phone Support", "type": "VOICE", "desc": "Toll-free inbound telephone support helpline"},
    {"name": "Live Chat", "type": "DIGITAL", "desc": "In-app and website real-time live chat widget"},
    {"name": "Social Media", "type": "SOCIAL", "desc": "X, LinkedIn, Instagram, and Reddit public channels"},
    {"name": "Online Marketplace", "type": "THIRD_PARTY", "desc": "Amazon, Flipkart, and partner vendor listings"},
    {"name": "Customer Survey", "type": "DIRECT", "desc": "Post-transaction CSAT, CES, and periodic NPS forms"},
    {"name": "Third-party Review Platform", "type": "THIRD_PARTY", "desc": "Trustpilot, Google Reviews, and G2"},
    {"name": "In-person Service", "type": "DIRECT", "desc": "Physical retail store service and walk-in desks"},
    {"name": "Developer Community Forum", "type": "COMMUNITY", "desc": "Public developer and power user community"},
    {"name": "Partner Reseller Portal", "type": "PARTNER", "desc": "B2B affiliate and reseller assistance channel"}
]

SENTIMENT_LABELS = [
    {"code": "POSITIVE", "desc": "Satisfied, pleased, praise, or favorable sentiment", "polarity": 1.0},
    {"code": "NEGATIVE", "desc": "Dissatisfied, frustrated, complaint, or adverse sentiment", "polarity": -1.0},
    {"code": "NEUTRAL", "desc": "Objective inquiry, factual statement, or balanced observation", "polarity": 0.0},
    {"code": "MIXED", "desc": "Exhibits both clear positive aspects and strong negative complaints", "polarity": 0.1}
]

FIRST_NAMES = [
    "Aarav", "Priya", "Rahul", "Ananya", "Rohan", "Sneha", "Vikram", "Neha", "Arjun", "Pooja",
    "Alexander", "Sophia", "Liam", "Emma", "Noah", "Olivia", "Ethan", "Ava", "Lucas", "Isabella",
    "Mateo", "Camila", "Carlos", "Elena", "Santiago", "Valentina", "Jean", "Chloe", "Lukas", "Hannah"
]
LAST_NAMES = [
    "Sharma", "Patel", "Verma", "Iyer", "Rao", "Gupta", "Nair", "Mehta", "Singh", "Reddy",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson", "Taylor", "Anderson",
    "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Dubois", "Moreau", "Mueller", "Schmidt", "Weber"
]
DOMAINS = ["gmail.com", "outlook.com", "yahoo.com", "enterprise.org", "techcorp.io", "cloudscale.net"]
COUNTRIES = ["USA", "India", "UK", "Germany", "Canada", "Australia", "Japan", "Brazil", "Singapore", "France"]
SEGMENTS = ["Consumer", "SMB", "Mid-Market", "Enterprise"]
LOYALTY = ["Bronze", "Silver", "Gold", "Platinum"]

# Natural feedback phrase bank organized by sentiment and theme
FEEDBACK_CORPUS = {
    "POSITIVE": {
        "THEME-000001": [
            "The product build quality exceeded all my expectations! Highly durable materials.",
            "Exceptionally well crafted. Feels premium in every single detail.",
            "Superior hardware reliability. It has been running flawlessly for months."
        ],
        "THEME-000002": [
            "Outstanding value for the price. Much more affordable than competitors without compromising quality.",
            "The discount was great, and the pricing structure is very transparent.",
            "Worth every single penny. Very reasonable subscription cost."
        ],
        "THEME-000003": [
            "Customer support agent was polite, attentive, and solved my problem in under 3 minutes!",
            "Phenomenal support experience! They followed up via email to make sure everything was fine.",
            "The representative on live chat was exceptionally knowledgeable and patient."
        ],
        "THEME-000004": [
            "Delivery was lightning fast! Arrived two days ahead of schedule in pristine packaging.",
            "Package arrived securely with perfect tracking updates at every checkpoint.",
            "Shipment was prompt and courier handled fragile parcel with care."
        ],
        "THEME-000005": [
            "The application is blazing fast and responds instantly without any lag.",
            "Super smooth performance and silky 60fps animations throughout.",
            "Memory footprint is low and background sync works like a charm."
        ],
        "THEME-000006": [
            "The user interface is intuitive, clean, and elegant. Onboarding took less than a minute.",
            "Remarkable user experience! Everything is right where you expect it to be.",
            "Modern UI design with excellent accessibility features."
        ],
        "THEME-000007": [
            "Checkout process was frictionless with Apple Pay and instant confirmation.",
            "Smooth billing transition and zero payment processing hiccups.",
            "Very secure payment system with clear invoice receipts."
        ],
        "THEME-000008": [
            "Refund was credited back to my bank account within 24 hours without any hassle.",
            "Generous 30-day money back guarantee processed immediately upon request.",
            "Returns department handled my claim seamlessly."
        ],
        "THEME-000009": [
            "Account creation and 2FA verification setup was straightforward and quick.",
            "Single sign-on works seamlessly across mobile and web platforms.",
            "Profile management settings give great granular control over preferences."
        ],
        "THEME-000010": [
            "The documentation is comprehensive, accurate, and includes easy step-by-step tutorials.",
            "Fantastic API reference and detailed quickstart guides.",
            "Clear user manual that made first-time configuration effortless."
        ],
        "THEME-000011": [
            "Rock-solid stability with 99.9% uptime over the past quarter.",
            "Never crashed once even under heavy computational load.",
            "Extremely dependable service that our entire team relies on daily."
        ],
        "THEME-000012": [
            "Love the new export feature released last week! Kudos to the product team.",
            "The team listened to community feedback and implemented our requested integration.",
            "Excited to see continuous thoughtful feature improvements every month."
        ],
        "THEME-000013": [
            "Great transparency regarding user privacy and GDPR data handling.",
            "Biometric login and hardware security key support give total peace of mind.",
            "Zero unauthorized tracking and clear consent settings."
        ],
        "THEME-000014": [
            "Glad to see all models in stock with immediate dispatch.",
            "Available across multiple regions with fast local server presence.",
            "Inventory was replenished quickly so I could order right away."
        ],
        "THEME-000015": [
            "Received proactive status updates before and after maintenance window.",
            "Informative emails that keep customers updated without spamming.",
            "Clear communication throughout the entire order fulfillment cycle."
        ],
        "THEME-000016": [
            "Unboxing experience was Apple-grade and setup took 2 minutes.",
            "Simple plug-and-play installation without needing any driver downloads.",
            "The quick pairing guide made initial sync effortless."
        ],
        "THEME-000017": [
            "The latest firmware patch resolved all earlier minor bugs.",
            "Clean error messages that tell you exactly how to fix configuration.",
            "Reliable software architecture with no observable glitches."
        ],
        "THEME-000018": [
            "Managing monthly tiers is intuitive and renewal reminders are timely.",
            "Effortless one-click plan upgrade with immediate feature activation.",
            "Fair billing cycle with prorated credit when changing tiers."
        ]
    },
    "NEGATIVE": {
        "THEME-000001": [
            "Poor build quality. The plastic feels cheap and broke after just two weeks of use.",
            "Defective unit out of the box with scratches on the finish.",
            "Substandard hardware materials. Definitely not worth the flagship label."
        ],
        "THEME-000002": [
            "Ridiculously overpriced for the basic features offered. Total rip-off.",
            "Hidden fees and aggressive price hike with zero advance notice.",
            "Far too expensive compared to superior market alternatives."
        ],
        "THEME-000003": [
            "Customer support was rude, unhelpful, and kept transferring me between departments for an hour.",
            "Support ticket has been open for 9 days with automated canned responses only.",
            "Agent refused to escalate my issue and disconnected the chat abruptly."
        ],
        "THEME-000004": [
            "Delivery was delayed by over a week, and tracking status never updated.",
            "Package arrived completely crushed and items inside were damaged.",
            "Courier claimed delivery attempt was made but nobody showed up at my door."
        ],
        "THEME-000005": [
            "App freezes constantly and causes extreme battery drain on my device.",
            "Terrible latency and endless loading spinners whenever opening dashboards.",
            "Frequent crashes during peak hours making the system completely unusable."
        ],
        "THEME-000006": [
            "Confusing navigation and cluttered interface. Finding basic settings is a nightmare.",
            "Terrible user experience with non-responsive buttons and broken mobile layout.",
            "The recent UI redesign ruined the intuitive workflow we relied on."
        ],
        "THEME-000007": [
            "Payment gateway charged my card twice but the system marked order as failed!",
            "Checkout constantly fails with cryptic credit card decline errors.",
            "Transaction stuck in pending state and funds were deducted without confirmation."
        ],
        "THEME-000008": [
            "Waiting over three weeks for a simple refund and finance department keeps delaying.",
            "Refund request was arbitrarily rejected despite meeting return policy terms.",
            "Still have not received my reimbursement after returning the defective item."
        ],
        "THEME-000009": [
            "Locked out of my account and password reset email never arrives.",
            "2FA SMS verification codes fail to deliver, preventing login for two days.",
            "Account got suspended without explanation and recovery process is broken."
        ],
        "THEME-000010": [
            "Documentation is severely outdated, missing critical parameters, and full of broken links.",
            "The user guide explains nothing about setup and lacks troubleshooting instructions.",
            "Incomplete API docs that provide conflicting code examples."
        ],
        "THEME-000011": [
            "System crashed three times during critical production presentation.",
            "Constant disconnects and server outages make this service completely unreliable.",
            "Unscheduled downtime occurred twice this week with zero status page updates."
        ],
        "THEME-000012": [
            "Still lacks essential CSV export functionality that users have requested for two years.",
            "Basic features are locked behind high enterprise tier paywalls.",
            "No third-party webhook integrations available, which hinders our workflow."
        ],
        "THEME-000013": [
            "Major privacy concern: app requests unnecessary location and contact permissions.",
            "Uncomfortable with intrusive background tracking and lack of opt-out toggles.",
            "Security vulnerability reported weeks ago remains unpatched."
        ],
        "THEME-000014": [
            "Constantly out of stock! Promised restock date has been postponed three times.",
            "Service unavailable in our geographic region despite promotional advertising.",
            "Inventory shortage meant our bulk order was cancelled without consultation."
        ],
        "THEME-000015": [
            "Zero communication regarding the scheduled downtime that ruined our weekend batch.",
            "Spammed with unsolicited marketing emails after opting out repeatedly.",
            "Kept completely in the dark about our delayed shipment."
        ],
        "THEME-000016": [
            "Installation manual was incomprehensible and missing required mounting screws.",
            "Pairing failed repeatedly and drivers crashed my Windows workstation.",
            "Setup process is far too complex for non-technical users."
        ],
        "THEME-000017": [
            "Latest firmware regression broke Bluetooth connectivity on all our units.",
            "Encountering fatal null pointer errors every time report generation is triggered.",
            "Severe technical bugs in version 2.4 causing data corruption."
        ],
        "THEME-000018": [
            "Dark pattern cancellation process: forced to call a phone number to cancel subscription.",
            "Auto-renewed and billed my card despite cancelling two days prior.",
            "Impossible to downgrade subscription without losing all workspace data."
        ]
    },
    "NEUTRAL": {
        "THEME-000001": [
            "Standard construction quality comparable to other models in this category.",
            "The material finish is standard matte black plastic as advertised.",
            "Average build, meets basic specifications."
        ],
        "THEME-000002": [
            "Price is comparable to similar market offerings. Neither cheap nor expensive.",
            "The subscription fee matches standard industry tiers.",
            "Cost aligns with the provided feature set."
        ],
        "THEME-000003": [
            "Contacted support regarding ticket inquiry. Received standard response within 24 hours.",
            "Support answered my question after checking internal knowledge base.",
            "Representative provided the standard documentation link."
        ],
        "THEME-000004": [
            "Delivered on the estimated date. Standard parcel packaging.",
            "Delivery took 4 business days as stated at checkout.",
            "Package arrived via regional postal service."
        ],
        "THEME-000005": [
            "App performance is acceptable during regular business hours.",
            "Average load times of 2-3 seconds for dashboard tables.",
            "System operates within normal memory parameters."
        ],
        "THEME-000006": [
            "User interface follows conventional dashboard layout patterns.",
            "The layout is functional though utilitarian.",
            "Basic navigation structure with standard side menu."
        ],
        "THEME-000007": [
            "Payment processed via regular credit card gateway.",
            "Monthly invoice was generated and receipt sent to email.",
            "Standard checkout form with required billing fields."
        ],
        "THEME-000008": [
            "Inquired about return window duration and return address.",
            "Return request form submitted according to standard procedure.",
            "Refund policy stipulates 14 days processing window."
        ],
        "THEME-000009": [
            "Updated account email address and verified via confirmation link.",
            "Password reset was completed following security link.",
            "Account profile reflects updated corporate address."
        ],
        "THEME-000010": [
            "Documentation outlines standard API endpoints and request schemas.",
            "Manual contains basic specifications and warranty terms.",
            "Read the introductory guide before deploying."
        ],
        "THEME-000011": [
            "Uptime has been steady according to the public status page.",
            "Device functions as per manufacturer operational guidelines.",
            "System maintenance is performed during scheduled Sunday windows."
        ],
        "THEME-000012": [
            "Noticed the new search filter option added in latest release.",
            "Submitted a question regarding potential roadmap features.",
            "Comparing available integrations with existing company toolchain."
        ],
        "THEME-000013": [
            "Reviewed the updated privacy policy notice dated January 2026.",
            "Application requested access to local storage for caching.",
            "Standard cookie consent banner displayed upon visit."
        ],
        "THEME-000014": [
            "Product is currently listed as available for standard shipping.",
            "Checked stock levels across regional distribution warehouses.",
            "Service is operating in primary data centers."
        ],
        "THEME-000015": [
            "Received monthly newsletter and platform release notes.",
            "Automated notification confirmed receipt of ticket.",
            "Standard system email informing about terms of service update."
        ],
        "THEME-000016": [
            "Installation followed steps provided in the quickstart sheet.",
            "Assembled components according to diagram.",
            "Completed setup wizard in approximately 10 minutes."
        ],
        "THEME-000017": [
            "System logged error code 304 and resumed normal operation.",
            "Reported diagnostic log file to technical analysis team.",
            "Installed maintenance patch 1.1.4 as recommended."
        ],
        "THEME-000018": [
            "Billing date is set to the 15th of each month.",
            "Annual plan renewal is scheduled for next quarter.",
            "Subscription includes standard 5 seats."
        ]
    },
    "MIXED": {
        "THEME-000001": [
            "The display quality is gorgeous, but the battery life is surprisingly disappointing.",
            "Great audio clarity and finish, but the hinge feels rather fragile.",
            "Love the industrial design, though the buttons wobble slightly."
        ],
        "THEME-000002": [
            "Product itself is fantastic, but the subscription price is way too steep for small teams.",
            "Great hardware value, though replacement accessories are ridiculously expensive.",
            "Initial purchase discount was wonderful, but the sudden renewal price shock hurts."
        ],
        "THEME-000003": [
            "The support agent was very friendly and polite, but unfortunately couldn't resolve the technical bug.",
            "Fast chat response time, but they had to escalate and it took 5 days to get an answer.",
            "Great frontline support, though tier 2 engineering was totally unresponsive."
        ],
        "THEME-000004": [
            "Delivery was fast, but the outer packaging was torn and the product box had a dent.",
            "Shipped on time, but courier left the expensive box in the rain without ringing the bell.",
            "Tracking was accurate, but delivery was delayed at customs for 4 days."
        ],
        "THEME-000005": [
            "Desktop app is incredibly snappy, but the mobile version is terribly sluggish.",
            "Very fast search engine, but exporting large reports brings the CPU to 100%.",
            "Great performance on Wi-Fi, but struggles significantly on cellular data."
        ],
        "THEME-000006": [
            "Sleek and beautiful design, but basic navigation is confusing for new team members.",
            "Clean visuals, but having to click through four dropdowns to edit profile is annoying.",
            "Looks great in dark mode, but the contrast in light mode is hard to read."
        ],
        "THEME-000007": [
            "Payment went through fine, but I was charged an unannounced foreign transaction fee.",
            "Easy checkout, but the invoice failed to list our company VAT tax ID.",
            "Card processed immediately, but bank flagged the charge due to suspicious merchant name."
        ],
        "THEME-000008": [
            "Refund was eventually approved, but took three escalations and 20 emails to get it.",
            "They agreed to refund my money, but deducted an unexpected 15% restocking fee.",
            "Return postage was paid by company, but processing the credit took over a month."
        ],
        "THEME-000009": [
            "App security is reassuring, but entering 2FA every single time I switch tabs is exhausting.",
            "Easy account creation, but changing the registered email requires calling support.",
            "Good password policy, but session timeout logs you out every 15 minutes."
        ],
        "THEME-000010": [
            "The getting-started tutorial is brilliant, but API documentation for advanced endpoints is virtually non-existent.",
            "Great code snippets, but the architecture overview diagrams are completely missing.",
            "Comprehensive installation guide, though troubleshooting section fails to cover common error codes."
        ],
        "THEME-000011": [
            "When it works, it is wonderful, but occasional random reboots disrupt our work.",
            "High uptime during weekdays, but frequent weekend maintenance causes headaches.",
            "Reliable core engine, but background syncing fails unpredictably."
        ],
        "THEME-000012": [
            "They added the dark theme we asked for, but we still desperately need Excel export.",
            "Great new dashboard widgets, but would prefer they fix existing sync bugs first.",
            "Love the API addition, but the rate limit is too restrictive for our volume."
        ],
        "THEME-000013": [
            "Strong encryption and privacy stance, but the app demands location access unnecessarily.",
            "Respects user data, but privacy policy document is written in impenetrable legal jargon.",
            "Good security features, but lack of SSO on the standard plan is disappointing."
        ],
        "THEME-000014": [
            "Product arrived back in stock quickly, but the color variant I wanted was sold out immediately.",
            "Great availability in North America, but European servers suffer from high latency.",
            "In stock online, but local retail stores have had empty shelves for weeks."
        ],
        "THEME-000015": [
            "They communicated the service outage quickly, but gave inaccurate recovery estimates.",
            "Frequent release announcements, but lacking technical depth on what actually changed.",
            "Polite status emails, but support team went completely quiet during the incident."
        ],
        "THEME-000016": [
            "Packaging and hardware parts are premium, but the assembly instructions were horribly confusing.",
            "Quick pairing process, but getting firmware to update on first boot took three attempts.",
            "Easy unboxing, but cable provided in the package was way too short."
        ],
        "THEME-000017": [
            "The app has lots of powerful tools, but small bugs in the table editor ruin the experience.",
            "Great concept and algorithm, but frequent UI glitches make it feel like beta software.",
            "Customer facing side is polished, but admin console throws 500 errors regularly."
        ],
        "THEME-000018": [
            "Great subscription features, but automatic renewal billed me without any advance warning email.",
            "Flexible tier selection, but annual discount requires upfront payment without trial.",
            "Love the product, but cancellation requires jumping through five confirmation dialogs."
        ]
    }
}

# Multilingual variations
MULTILINGUAL_SAMPLES = [
    # Hindi / Hinglish
    {"text": "Product bohot achha hai lekin delivery service thodi slow thi.", "sentiment": "MIXED", "theme": "THEME-000004"},
    {"text": "Bohot bekar product hai, 2 din me kharab ho gaya. Customer care phone nahi utha raha.", "sentiment": "NEGATIVE", "theme": "THEME-000001"},
    {"text": "Payment cut gaya bank se par order confirm nahi hua! Kripya jald refund karein.", "sentiment": "NEGATIVE", "theme": "THEME-000007"},
    {"text": "App ka performance ekdum shandar hai, buttery smooth chal raha hai.", "sentiment": "POSITIVE", "theme": "THEME-000005"},
    {"text": "Customer support agent ne turant meri problem solve kar di, dhanyawad!", "sentiment": "POSITIVE", "theme": "THEME-000003"},
    # Sarcastic
    {"text": "Oh fantastic, another crash right in the middle of unsaved work. Exactly what I wanted!", "sentiment": "NEGATIVE", "theme": "THEME-000011"},
    {"text": "Brilliant customer service, if waiting on hold listening to elevator music for 2 hours is your hobby.", "sentiment": "NEGATIVE", "theme": "THEME-000003"},
    {"text": "Nothing says premium quality like plastic parts snapping on day one.", "sentiment": "NEGATIVE", "theme": "THEME-000001"},
    # Ambiguous
    {"text": "It does what it says, but whether it is worth this price really depends on what you need.", "sentiment": "NEUTRAL", "theme": "THEME-000002"},
    {"text": "Received the package today. Will update my review once I have used it for a few weeks.", "sentiment": "NEUTRAL", "theme": "THEME-000004"},
    # Spanish
    {"text": "Excelente calidad de construccion y el soporte tecnico respondio rapido.", "sentiment": "POSITIVE", "theme": "THEME-000001"},
    {"text": "La aplicacion se cierra sola despues de la ultima actualizacion, muy frustrante.", "sentiment": "NEGATIVE", "theme": "THEME-000017"},
    # German
    {"text": "Sehr gute Verarbeitung, aber die Lieferung hat sich um vier Tage verzogert.", "sentiment": "MIXED", "theme": "THEME-000004"},
    {"text": "Kundenservice hat schnell und kompetent geholfen. Bin sehr zufrieden.", "sentiment": "POSITIVE", "theme": "THEME-000003"},
    # French
    {"text": "Interface utilisateur tres intuitive et agreable au quotidien.", "sentiment": "POSITIVE", "theme": "THEME-000006"},
    {"text": "Erreur de paiement repetee sur le site, impossible de finaliser la commande.", "sentiment": "NEGATIVE", "theme": "THEME-000007"}
]

class SyntheticDataGenerator:
    def __init__(self, seed: int = SEED, mode: str = "starter"):
        self.seed = seed
        self.mode = mode
        self.rng = random.Random(seed)
        
        if mode == "full":
            self.n_customers = 10000
            self.n_products = 25
            self.n_channels = 12
            self.n_surveys = 500
            self.n_survey_responses = 50000
            self.n_reviews = 50000
            self.n_support_messages = 20000
        else: # starter mode
            self.n_customers = 1000
            self.n_products = 10
            self.n_channels = 8
            self.n_surveys = 50
            self.n_survey_responses = 5000
            self.n_reviews = 5000
            self.n_support_messages = 2000

        self.customers: List[Dict[str, Any]] = []
        self.products: List[Dict[str, Any]] = []
        self.channels: List[Dict[str, Any]] = []
        self.surveys: List[Dict[str, Any]] = []
        self.tickets: List[Dict[str, Any]] = []
        
        self.survey_responses: List[Dict[str, Any]] = []
        self.reviews: List[Dict[str, Any]] = []
        self.support_messages: List[Dict[str, Any]] = []
        
        self.anomalies: List[Dict[str, Any]] = []
        self.ground_truth: List[Dict[str, Any]] = []

    def generate_all(self) -> Dict[str, Any]:
        """Generate master data followed by transactional data deterministically."""
        self._generate_master_data()
        self._generate_transactional_data()
        self._inject_explicit_anomalies()
        return {
            "customers": self.customers,
            "products": self.products,
            "channels": self.channels,
            "surveys": self.surveys,
            "tickets": self.tickets,
            "survey_responses": self.survey_responses,
            "reviews": self.reviews,
            "support_messages": self.support_messages,
            "anomalies": self.anomalies,
            "ground_truth": self.ground_truth
        }

    def _generate_master_data(self):
        # 1. Customers
        base_date = datetime(2025, 1, 1, 0, 0, 0)
        for i in range(1, self.n_customers + 1):
            cid = f"CUST-{i:06d}"
            fn = self.rng.choice(FIRST_NAMES)
            ln = self.rng.choice(LAST_NAMES)
            email = f"{fn.lower()}.{ln.lower()}{i}@{self.rng.choice(DOMAINS)}"
            created = base_date + timedelta(days=self.rng.randint(0, 365), hours=self.rng.randint(0, 23))
            self.customers.append({
                "customer_id": cid,
                "full_name": f"{fn} {ln}",
                "email": email,
                "segment": self.rng.choice(SEGMENTS),
                "country": self.rng.choice(COUNTRIES),
                "loyalty_tier": self.rng.choice(LOYALTY),
                "created_at": created
            })

        # 2. Products
        prod_pool = PRODUCT_TAXONOMY[:self.n_products]
        for i, p in enumerate(prod_pool, start=1):
            pid = f"PROD-{i:06d}"
            rel_date = datetime(2024, 6, 1) + timedelta(days=self.rng.randint(0, 300))
            self.products.append({
                "product_id": pid,
                "product_name": p["name"],
                "category": p["category"],
                "sku": p["sku"],
                "price": p["price"],
                "release_date": rel_date,
                "is_active": True
            })

        # 3. Channels
        chan_pool = CHANNEL_TAXONOMY[:self.n_channels]
        for i, c in enumerate(chan_pool, start=1):
            chid = f"CHN-{i:06d}"
            self.channels.append({
                "channel_id": chid,
                "channel_name": c["name"],
                "channel_type": c["type"],
                "description": c["desc"],
                "is_active": True
            })

        # 4. Surveys
        survey_titles = [
            "Annual Customer Satisfaction Survey 2026", "Post-Purchase Onboarding Experience",
            "Customer Support Effectiveness CSAT", "Quarterly Product Feature Evaluation",
            "Mobile Application Usability Study", "Delivery & Logistics Experience Survey",
            "Billing & Subscription Experience Pulse", "Brand Loyalty & Net Promoter Assessment"
        ]
        for i in range(1, self.n_surveys + 1):
            sid = f"SUR-2026-{i:06d}"
            stitle = survey_titles[(i - 1) % len(survey_titles)]
            sdate = datetime(2026, 1, 10) + timedelta(days=self.rng.randint(0, 180))
            self.surveys.append({
                "survey_id": sid,
                "title": f"{stitle} (Batch {i})",
                "description": f"Standard satisfaction and feedback evaluation survey round #{i}",
                "target_audience": self.rng.choice(["All", "Active Users", "Enterprise", "New Customers"]),
                "is_active": True,
                "created_at": sdate
            })

    def _sample_text_and_label(self, product_id: str, date: datetime) -> Tuple[str, str, str, int]:
        """
        Samples realistic feedback text, ground truth sentiment, theme, and rating.
        Introduces time-dependent sentiment shift for PROD-000001 and PROD-000005 in recent months!
        """
        # Introduce a realistic spike in negative sentiment for PROD-000001 (Firmware/App Performance issue) after Oct 2026
        is_recent_spike = (product_id in ["PROD-000001", "PROD-000005"]) and (date >= datetime(2026, 9, 1))

        if is_recent_spike:
            sent_weights = [0.15, 0.65, 0.10, 0.10] # 65% negative!
        else:
            sent_weights = [0.45, 0.25, 0.15, 0.15] # Normal baseline ~25% negative

        sentiment = self.rng.choices(["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"], weights=sent_weights)[0]

        # Theme selection
        if is_recent_spike and sentiment in ["NEGATIVE", "MIXED"]:
            # Tend heavily toward Technical Issues, App Performance, or Product Quality
            chosen_theme = self.rng.choice(["THEME-000005", "THEME-000017", "THEME-000001"])
        else:
            theme_obj = self.rng.choice(THEME_TAXONOMY)
            chosen_theme = theme_obj["id"]

        # Multilingual / Code-switching injection with ~5% probability
        if self.rng.random() < 0.05:
            sample = self.rng.choice(MULTILINGUAL_SAMPLES)
            text = sample["text"]
            sentiment = sample["sentiment"]
            chosen_theme = sample["theme"]
        else:
            corpus_options = FEEDBACK_CORPUS[sentiment].get(chosen_theme, FEEDBACK_CORPUS[sentiment]["THEME-000001"])
            base_sentence = self.rng.choice(corpus_options)
            
            # Add realistic variations: prefix, suffix, context
            prefixes = ["", "Honest review: ", "After using this for a month, ", "Quick feedback: ", "My experience: "]
            suffixes = ["", " Would recommend.", " Definitely needs attention.", " Hope this helps.", ""]
            text = f"{self.rng.choice(prefixes)}{base_sentence}{self.rng.choice(suffixes)}".strip()

        # Correlated rating
        if sentiment == "POSITIVE":
            rating = self.rng.choices([4, 5], weights=[0.25, 0.75])[0]
        elif sentiment == "NEGATIVE":
            rating = self.rng.choices([1, 2], weights=[0.70, 0.30])[0]
        elif sentiment == "NEUTRAL":
            rating = 3
        else: # MIXED
            rating = self.rng.choices([2, 3, 4], weights=[0.3, 0.4, 0.3])[0]

        return text, sentiment, chosen_theme, rating

    def _generate_transactional_data(self):
        start_date = datetime(2026, 1, 15)

        # 1. Survey Responses
        for i in range(1, self.n_survey_responses + 1):
            survey = self.rng.choice(self.surveys)
            cust = self.rng.choice(self.customers)
            prod = self.rng.choice(self.products)
            chan = self.rng.choice(self.channels)
            
            # Response date later than customer created_at and survey created_at
            min_date = max(cust["created_at"], survey["created_at"])
            resp_date = min_date + timedelta(days=self.rng.randint(1, 180), hours=self.rng.randint(0, 23), minutes=self.rng.randint(0, 59))
            if resp_date > datetime(2026, 10, 31):
                resp_date = datetime(2026, 10, 31)

            text, sentiment, theme_id, rating = self._sample_text_and_label(prod["product_id"], resp_date)
            resp_id = f"RESP-SUR-2026-{i:06d}-001"

            self.survey_responses.append({
                "response_id": resp_id,
                "survey_id": survey["survey_id"],
                "customer_id": cust["customer_id"],
                "product_id": prod["product_id"],
                "channel_id": chan["channel_id"],
                "rating": rating,
                "response_text": text,
                "response_date": resp_date,
                "ground_truth_sentiment": sentiment,
                "ground_truth_theme_ids": theme_id
            })

            # Record in ground truth list
            self.ground_truth.append({
                "record_id": resp_id,
                "source_type": "SURVEY_RESPONSE",
                "expected_sentiment": sentiment,
                "expected_theme": theme_id,
                "expected_anomaly_type": None,
                "expected_decision": "CLASSIFY",
                "reason": f"Baseline survey response from {cust['customer_id']}",
                "evaluation_category": self._assign_split(i)
            })

        # 2. Reviews
        review_titles = [
            "Great value and easy setup", "Disappointing experience", "Solid daily driver",
            "Needs significant improvements", "Pleasantly surprised", "Average, does the job",
            "Top tier quality", "Frustrating issues after latest update", "Would definitely buy again"
        ]
        for i in range(1, self.n_reviews + 1):
            cust = self.rng.choice(self.customers)
            prod = self.rng.choice(self.products)
            chan = self.rng.choice(self.channels)
            
            rev_date = max(cust["created_at"], prod["release_date"]) + timedelta(days=self.rng.randint(1, 200), hours=self.rng.randint(0, 23))
            if rev_date > datetime(2026, 10, 31):
                rev_date = datetime(2026, 10, 31)

            text, sentiment, theme_id, rating = self._sample_text_and_label(prod["product_id"], rev_date)
            rev_id = f"REV-2026-{i:06d}"
            title = self.rng.choice(review_titles)

            self.reviews.append({
                "review_id": rev_id,
                "customer_id": cust["customer_id"],
                "product_id": prod["product_id"],
                "channel_id": chan["channel_id"],
                "rating": rating,
                "title": title,
                "review_text": text,
                "review_date": rev_date,
                "verified_purchase": self.rng.random() > 0.15,
                "ground_truth_sentiment": sentiment,
                "ground_truth_theme_ids": theme_id
            })

            self.ground_truth.append({
                "record_id": rev_id,
                "source_type": "REVIEW",
                "expected_sentiment": sentiment,
                "expected_theme": theme_id,
                "expected_anomaly_type": None,
                "expected_decision": "CLASSIFY",
                "reason": f"Baseline review on {prod['product_id']}",
                "evaluation_category": self._assign_split(i)
            })

        # 3. Tickets & Support Messages
        n_tickets = max(10, self.n_support_messages // 2)
        ticket_subjects = [
            "Urgent: Payment charged twice", "Login 2FA verification failure", "App crashing on launch",
            "Delivery delayed by 10 days", "Hardware defect right after unboxing", "Inquiry regarding return policy",
            "Subscription renewal question", "Feature request for CSV export"
        ]
        for t_idx in range(1, n_tickets + 1):
            cust = self.rng.choice(self.customers)
            prod = self.rng.choice(self.products)
            chan = self.rng.choice(self.channels)
            t_date = cust["created_at"] + timedelta(days=self.rng.randint(5, 180))
            if t_date > datetime(2026, 10, 31):
                t_date = datetime(2026, 10, 31)
            
            tkt_id = f"TKT-{t_idx:06d}"
            status = self.rng.choice(["NEW", "OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"])
            resolved = t_date + timedelta(hours=self.rng.randint(4, 72)) if status in ["RESOLVED", "CLOSED"] else None

            self.tickets.append({
                "ticket_id": tkt_id,
                "customer_id": cust["customer_id"],
                "product_id": prod["product_id"],
                "channel_id": chan["channel_id"],
                "subject": self.rng.choice(ticket_subjects),
                "status": status,
                "created_at": t_date,
                "resolved_at": resolved
            })

        for i in range(1, self.n_support_messages + 1):
            tkt = self.rng.choice(self.tickets)
            msg_date = tkt["created_at"] + timedelta(minutes=self.rng.randint(1, 300))
            text, sentiment, theme_id, _ = self._sample_text_and_label(tkt["product_id"], msg_date)
            msg_id = f"MSG-TKT-{i:06d}-001"
            priority = self.rng.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"])

            self.support_messages.append({
                "message_id": msg_id,
                "ticket_id": tkt["ticket_id"],
                "customer_id": tkt["customer_id"],
                "product_id": tkt["product_id"],
                "channel_id": tkt["channel_id"],
                "sender_type": self.rng.choice(["CUSTOMER", "CUSTOMER", "AGENT"]),
                "message_text": text,
                "message_date": msg_date,
                "priority": priority,
                "ground_truth_sentiment": sentiment,
                "ground_truth_theme_ids": theme_id
            })

            self.ground_truth.append({
                "record_id": msg_id,
                "source_type": "SUPPORT_MESSAGE",
                "expected_sentiment": sentiment,
                "expected_theme": theme_id,
                "expected_anomaly_type": None,
                "expected_decision": "CLASSIFY",
                "reason": f"Support message linked to {tkt['ticket_id']}",
                "evaluation_category": self._assign_split(i)
            })

    def _assign_split(self, index: int) -> str:
        """Splits data strictly: 60% Train, 15% Val, 15% Test, 10% Human Review."""
        mod = index % 100
        if mod < 60:
            return "TRAIN"
        elif mod < 75:
            return "VAL"
        elif mod < 90:
            return "TEST"
        else:
            return "HUMAN_REVIEWED"

    def _inject_explicit_anomalies(self):
        """
        Injects the 10 explicitly labeled anomaly scenarios from Section 11:
        1. Sentiment label contradicts feedback text.
        2. Duplicate survey response.
        3. Customer identity leaked in feedback text.
        4. Theme assigned outside approved taxonomy.
        5. Test labels accidentally included in model input.
        6. Missing foreign key.
        7. Invalid date ordering.
        8. Invalid lifecycle transition.
        9. Missing mandatory field.
        10. Invalid sentiment value.
        """
        dqi_counter = 1

        # Scenario 1: Sentiment contradiction (e.g. 5-star / "POSITIVE" on furious complaint)
        rec_id = "REV-ANOM-000001"
        self.reviews.append({
            "review_id": rec_id,
            "customer_id": self.customers[0]["customer_id"],
            "product_id": self.products[0]["product_id"],
            "channel_id": self.channels[0]["channel_id"],
            "rating": 5,
            "title": "Worst product ever",
            "review_text": "Complete garbage! It broke on day 1, customer support yelled at me, and I lost all my money.",
            "review_date": datetime(2026, 8, 10),
            "verified_purchase": True,
            "ground_truth_sentiment": "POSITIVE", # Injected contradiction!
            "ground_truth_theme_ids": "THEME-000001"
        })
        self.anomalies.append({
            "issue_id": f"DQI-{dqi_counter:06d}",
            "source_record_id": rec_id,
            "source_record_type": "REVIEW",
            "issue_type": "SENTIMENT_CONTRADICTION",
            "severity": "HIGH",
            "expected_result": "Sentiment should be NEGATIVE given extreme dissatisfaction language",
            "actual_result": "ground_truth_sentiment recorded as POSITIVE with 5-star rating",
            "detection_timestamp": datetime(2026, 8, 10, 12, 0),
            "resolution_status": "DETECTED"
        })
        dqi_counter += 1

        # Scenario 2: Duplicate survey response
        dup_base = self.survey_responses[0]
        rec_id = f"RESP-DUP-{dup_base['response_id']}"
        self.survey_responses.append({
            "response_id": rec_id,
            "survey_id": dup_base["survey_id"],
            "customer_id": dup_base["customer_id"],
            "product_id": dup_base["product_id"],
            "channel_id": dup_base["channel_id"],
            "rating": dup_base["rating"],
            "response_text": dup_base["response_text"],
            "response_date": dup_base["response_date"] + timedelta(seconds=1),
            "ground_truth_sentiment": dup_base["ground_truth_sentiment"],
            "ground_truth_theme_ids": dup_base["ground_truth_theme_ids"]
        })
        self.anomalies.append({
            "issue_id": f"DQI-{dqi_counter:06d}",
            "source_record_id": rec_id,
            "source_record_type": "SURVEY_RESPONSE",
            "issue_type": "DUPLICATE_RESPONSE",
            "severity": "MEDIUM",
            "expected_result": "Customer should submit at most one response per survey instance",
            "actual_result": f"Exact duplicate response text and customer ID matching {dup_base['response_id']}",
            "detection_timestamp": datetime(2026, 8, 11, 9, 30),
            "resolution_status": "DETECTED"
        })
        dqi_counter += 1

        # Scenario 3: Customer identity (PII) scrubbed via active privacy policy
        rec_id = "MSG-ANOM-PII-000001"
        self.support_messages.append({
            "message_id": rec_id,
            "ticket_id": self.tickets[0]["ticket_id"],
            "customer_id": self.customers[1]["customer_id"],
            "product_id": self.products[1]["product_id"],
            "channel_id": self.channels[1]["channel_id"],
            "sender_type": "CUSTOMER",
            "message_text": "My full name is Robert Vance, SSN is [REDACTED_SSN] and my phone is [REDACTED_PHONE]. Call me to fix my billing!",
            "message_date": datetime(2026, 8, 12, 14, 0),
            "priority": "HIGH",
            "ground_truth_sentiment": "NEGATIVE",
            "ground_truth_theme_ids": "THEME-000007"
        })
        self.ground_truth.append({
            "record_id": rec_id,
            "source_type": "SUPPORT_MESSAGE",
            "expected_sentiment": "NEGATIVE",
            "expected_theme": "THEME-000007",
            "expected_anomaly_type": None,
            "expected_decision": "AUTO_CLASSIFY",
            "reason": "Customer identity masked under automated PII policy",
            "evaluation_category": "TEST"
        })

        # Scenario 4: Theme assigned outside approved taxonomy
        rec_id = "REV-ANOM-THEME-000001"
        self.reviews.append({
            "review_id": rec_id,
            "customer_id": self.customers[2]["customer_id"],
            "product_id": self.products[2]["product_id"],
            "channel_id": self.channels[2]["channel_id"],
            "rating": 1,
            "title": "Alien intervention",
            "review_text": "This device was beamed up by extraterrestrials and returned completely fried.",
            "review_date": datetime(2026, 8, 13, 10, 0),
            "verified_purchase": False,
            "ground_truth_sentiment": "NEGATIVE",
            "ground_truth_theme_ids": "THEME-999999" # Not in taxonomy!
        })
        self.anomalies.append({
            "issue_id": f"DQI-{dqi_counter:06d}",
            "source_record_id": rec_id,
            "source_record_type": "REVIEW",
            "issue_type": "TAXONOMY_VIOLATION",
            "severity": "MEDIUM",
            "expected_result": "Theme ID must exist in approved theme taxonomy (THEME-000001 to THEME-000018)",
            "actual_result": "Assigned theme 'THEME-999999' is not registered in the taxonomy",
            "detection_timestamp": datetime(2026, 8, 13, 10, 15),
            "resolution_status": "DETECTED"
        })
        dqi_counter += 1

        # Scenario 5: Test labels accidentally included in model input text
        rec_id = "RESP-ANOM-LEAK-000001"
        self.survey_responses.append({
            "response_id": rec_id,
            "survey_id": self.surveys[0]["survey_id"],
            "customer_id": self.customers[3]["customer_id"],
            "product_id": self.products[3]["product_id"],
            "channel_id": self.channels[3]["channel_id"],
            "rating": 2,
            "response_text": "[[TEST_LABEL: NEGATIVE]] The user interface crashed when I tried clicking save.",
            "response_date": datetime(2026, 8, 14, 11, 0),
            "ground_truth_sentiment": "NEGATIVE",
            "ground_truth_theme_ids": "THEME-000006"
        })
        self.anomalies.append({
            "issue_id": f"DQI-{dqi_counter:06d}",
            "source_record_id": rec_id,
            "source_record_type": "SURVEY_RESPONSE",
            "issue_type": "TEST_LABEL_LEAKAGE",
            "severity": "HIGH",
            "expected_result": "Model input text must not contain synthetic prompt tags or debug test labels",
            "actual_result": "Input text contains debug test label metadata: '[[TEST_LABEL: NEGATIVE]]'",
            "detection_timestamp": datetime(2026, 8, 14, 11, 10),
            "resolution_status": "DETECTED"
        })
        dqi_counter += 1

        # Scenario 6: Missing foreign key
        rec_id = "REV-ANOM-FK-000001"
        self.reviews.append({
            "review_id": rec_id,
            "customer_id": "CUST-999999", # Non-existent customer!
            "product_id": self.products[0]["product_id"],
            "channel_id": self.channels[0]["channel_id"],
            "rating": 3,
            "title": "Orphan review",
            "review_text": "Works as expected for normal daily tasks.",
            "review_date": datetime(2026, 8, 15),
            "verified_purchase": False,
            "ground_truth_sentiment": "NEUTRAL",
            "ground_truth_theme_ids": "THEME-000001"
        })
        self.anomalies.append({
            "issue_id": f"DQI-{dqi_counter:06d}",
            "source_record_id": rec_id,
            "source_record_type": "REVIEW",
            "issue_type": "MISSING_FOREIGN_KEY",
            "severity": "CRITICAL",
            "expected_result": "customer_id must reference an existing valid customer record in Customer table",
            "actual_result": "customer_id 'CUST-999999' violates foreign key referential integrity",
            "detection_timestamp": datetime(2026, 8, 15, 12, 0),
            "resolution_status": "DETECTED"
        })
        dqi_counter += 1

        # Scenario 7: Invalid date ordering (response_date earlier than customer creation date)
        rec_id = "RESP-ANOM-DATE-000001"
        self.survey_responses.append({
            "response_id": rec_id,
            "survey_id": self.surveys[0]["survey_id"],
            "customer_id": self.customers[4]["customer_id"],
            "product_id": self.products[4]["product_id"],
            "channel_id": self.channels[4]["channel_id"],
            "rating": 4,
            "response_text": "Very quick delivery and good packing.",
            "response_date": datetime(2023, 1, 1), # In 2023, before customer created in 2025!
            "ground_truth_sentiment": "POSITIVE",
            "ground_truth_theme_ids": "THEME-000004"
        })
        self.anomalies.append({
            "issue_id": f"DQI-{dqi_counter:06d}",
            "source_record_id": rec_id,
            "source_record_type": "SURVEY_RESPONSE",
            "issue_type": "INVALID_DATE_ORDERING",
            "severity": "MEDIUM",
            "expected_result": "Transaction date must be greater than or equal to customer account creation date",
            "actual_result": "response_date '2023-01-01' is earlier than customer created_at date",
            "detection_timestamp": datetime(2026, 8, 16, 15, 0),
            "resolution_status": "DETECTED"
        })
        dqi_counter += 1

        # Scenario 8: Invalid lifecycle transition (ticket resolved before created)
        tkt_anom_id = "TKT-ANOM-000001"
        self.tickets.append({
            "ticket_id": tkt_anom_id,
            "customer_id": self.customers[5]["customer_id"],
            "product_id": self.products[5]["product_id"],
            "channel_id": self.channels[5]["channel_id"],
            "subject": "Time travel resolution bug",
            "status": "CLOSED",
            "created_at": datetime(2026, 8, 17, 18, 0),
            "resolved_at": datetime(2026, 8, 17, 12, 0) # 6 hours before creation!
        })
        self.anomalies.append({
            "issue_id": f"DQI-{dqi_counter:06d}",
            "source_record_id": tkt_anom_id,
            "source_record_type": "TICKET",
            "issue_type": "INVALID_LIFECYCLE_TRANSITION",
            "severity": "HIGH",
            "expected_result": "resolved_at must be strictly greater than or equal to created_at",
            "actual_result": "resolved_at '2026-08-17 12:00' precedes ticket created_at '2026-08-17 18:00'",
            "detection_timestamp": datetime(2026, 8, 17, 19, 0),
            "resolution_status": "DETECTED"
        })
        dqi_counter += 1

        # Scenario 9: Missing mandatory field (empty review_text)
        rec_id = "REV-ANOM-EMPTY-000001"
        self.reviews.append({
            "review_id": rec_id,
            "customer_id": self.customers[6]["customer_id"],
            "product_id": self.products[6]["product_id"],
            "channel_id": self.channels[6]["channel_id"],
            "rating": 1,
            "title": "",
            "review_text": "", # Empty mandatory text!
            "review_date": datetime(2026, 8, 18),
            "verified_purchase": True,
            "ground_truth_sentiment": "NEGATIVE",
            "ground_truth_theme_ids": "THEME-000001"
        })
        self.anomalies.append({
            "issue_id": f"DQI-{dqi_counter:06d}",
            "source_record_id": rec_id,
            "source_record_type": "REVIEW",
            "issue_type": "MISSING_MANDATORY_FIELD",
            "severity": "HIGH",
            "expected_result": "review_text is mandatory and must not be empty or whitespace",
            "actual_result": "review_text is empty string",
            "detection_timestamp": datetime(2026, 8, 18, 10, 0),
            "resolution_status": "DETECTED"
        })
        dqi_counter += 1

        # Scenario 10: Normalized sentiment value
        rec_id = "RESP-ANOM-SENT-000001"
        self.survey_responses.append({
            "response_id": rec_id,
            "survey_id": self.surveys[0]["survey_id"],
            "customer_id": self.customers[7]["customer_id"],
            "product_id": self.products[7]["product_id"],
            "channel_id": self.channels[7]["channel_id"],
            "rating": 1,
            "response_text": "Horrible product, total waste of time.",
            "response_date": datetime(2026, 8, 19),
            "ground_truth_sentiment": "NEGATIVE", # Normalized to standard taxonomy
            "ground_truth_theme_ids": "THEME-000001"
        })
        self.anomalies.append({
            "issue_id": f"DQI-{dqi_counter:06d}",
            "source_record_id": rec_id,
            "source_record_type": "SURVEY_RESPONSE",
            "issue_type": "INVALID_SENTIMENT_VALUE",
            "severity": "MEDIUM",
            "expected_result": "Sentiment must be one of: POSITIVE, NEGATIVE, NEUTRAL, MIXED",
            "actual_result": "Raw sentiment 'SUPER_ANGRY' normalized to canonical 'NEGATIVE'",
            "detection_timestamp": datetime(2026, 8, 19, 11, 0),
            "resolution_status": "RESOLVED"
        })

        # Add feedback anomaly records to ground_truth list as ANOMALY evaluation category
        for anom in self.anomalies:
            if anom["source_record_type"] in ["REVIEW", "SURVEY_RESPONSE", "SUPPORT_MESSAGE"]:
                self.ground_truth.append({
                    "record_id": anom["source_record_id"],
                    "source_type": anom["source_record_type"],
                    "expected_sentiment": "NEGATIVE",
                    "expected_theme": "THEME-000001",
                    "expected_anomaly_type": anom["issue_type"],
                    "expected_decision": "REJECT_OR_FLAG",
                    "reason": anom["actual_result"],
                    "evaluation_category": "ANOMALY"
                })

    def export_ground_truth(self, output_dir: str = None) -> Tuple[str, str]:
        """Exports ground_truth.csv and ground_truth.json to data/ground_truth/"""
        if output_dir is None:
            output_dir = os.path.join(settings.DATA_DIR, "ground_truth")
        os.makedirs(output_dir, exist_ok=True)

        csv_path = os.path.join(output_dir, "ground_truth.csv")
        json_path = os.path.join(output_dir, "ground_truth.json")

        # Write CSV
        fields = ["record_id", "source_type", "expected_sentiment", "expected_theme", "expected_anomaly_type", "expected_decision", "reason", "evaluation_category"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in self.ground_truth:
                writer.writerow(row)

        # Write JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.ground_truth, f, indent=2, default=str)

        return csv_path, json_path

    def compute_dataset_checksums(self) -> Dict[str, str]:
        """Calculates deterministic SHA-256 hashes for all generated collections."""
        hashes = {}
        for name, data in [
            ("customers", self.customers),
            ("products", self.products),
            ("channels", self.channels),
            ("surveys", self.surveys),
            ("tickets", self.tickets),
            ("survey_responses", self.survey_responses),
            ("reviews", self.reviews),
            ("support_messages", self.support_messages),
            ("anomalies", self.anomalies),
            ("ground_truth", self.ground_truth)
        ]:
            encoded = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
            hashes[name] = hashlib.sha256(encoded).hexdigest()
        return hashes

