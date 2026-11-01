# DATA GENERATION SPECIFICATION & REPRODUCIBILITY GUIDE

This document explains the deterministic generation engine, taxonomy design, language variation algorithms, anomaly injection protocols, and reproducibility benchmarks.

---

## 1. Engine Configuration & Determinism

- **Fixed Master Random Seed**: `20261022`
- **Pseudorandom Generator**: Python `random.Random(20261022)` isolated instance.
- **Reproducibility Guarantee**: Given identical seeds, the generator produces exact bitwise identical primary keys, foreign keys, text corpora, dates, and ratings.

---

## 2. Execution Modes

| Dimension | Starter Mode | Full Enterprise Mode |
|---|---|---|
| Target Customers | 1,000 | 10,000 |
| Products | 10 | 25 |
| Channels | 8 | 12 |
| Surveys | 50 | 500 |
| Survey Responses | 5,000 | 50,000 |
| Customer Reviews | 5,000 | 50,000 |
| Support Messages | 2,000 | 20,000 |
| Injected Anomalies | 10 | 100 |
| Total Feedback Records | 12,010 | 120,100 |

Both modes share the identical core generator logic, ensuring zero discrepancy between starter testing and enterprise deployments.

---

## 3. Taxonomy Definitions

### Product Taxonomy (8 Categories, 25 Products)
- **Electronics**: Aura UltraBook Pro 16, NovaPulse True Wireless Earbuds, Horizon 4K Smart OLED Monitor, Titanium Smartwatch Ultra.
- **Software**: CloudSync Enterprise Suite, DevForge AI Code Assistant, CyberShield Endpoint Antivirus, DesignCraft Vector Studio.
- **Home Appliances**: RoboClean Precision Vacuum X5, BrewMaster Smart Espresso Bar, AeroPure HEPA Air Purifier Pro.
- **Financial Services**: Apex Wealth Robo-Advisor, SecurePay Business Merchant Account, CashFlow Plus Credit Line.
- **Telecommunications**: FiberGig Ultra 1Gbps Fiber, 5G Freedom Unlimited Mobile Plan, CloudVoIP PBX Hosted System.
- **Retail**: EcoThread Organic Cotton Hoodie, Venture Ergonomic Travel Backpack, PeakGrip All-Weather Hiking Boots.
- **Healthcare Services**: WellConnect 24/7 Telehealth Access, VitalCheck Home Health Lab Kit, MindEase Digital Therapy Program.
- **Subscription Services**: OmniStream 4K Cinema Pass, GourmetBox Weekly Fresh Meal Kit.

### Channel Taxonomy (12 Channels)
- Website (DIGITAL)
- Mobile Application (DIGITAL)
- Email (DIRECT)
- Phone Support (VOICE)
- Live Chat (DIGITAL)
- Social Media (SOCIAL)
- Online Marketplace (THIRD_PARTY)
- Customer Survey (DIRECT)
- Third-party Review Platform (THIRD_PARTY)
- In-person Service (DIRECT)
- Developer Community Forum (COMMUNITY)
- Partner Reseller Portal (PARTNER)

---

## 4. Time-Dependent Shift Simulation

To test the platform's time-series anomaly detection engine, the generator introduces a localized surge in negative feedback:
- **Target Products**: `PROD-000001` (Aura UltraBook Pro 16) and `PROD-000005` (CloudSync Enterprise Suite).
- **Time Window**: Feedback records dated after September 1, 2026.
- **Behavior**: Shifts the negative sentiment probability from a normal baseline of $25\%$ to $65\%$, concentrated on `Application Performance` (THEME-000005) and `Technical Issues` (THEME-000017).
- **Analytical Result**: Accurately triggers `SentimentShiftAlert` alerts in the Trend Detection module.

---

## 5. Injected Negative Scenarios (Section 11)

1. **Sentiment Contradiction**: `REV-ANOM-000001` (5-star rating on *"Complete garbage! It broke on day 1..."*).
2. **Duplicate Survey Response**: `RESP-DUP-RESP-SUR-2026-000001-001` (Exact duplicate response submitted by same customer).
3. **PII Leakage**: `MSG-ANOM-PII-000001` (Unsanitized SSN and telephone number inside support message).
4. **Taxonomy Violation**: `REV-ANOM-THEME-000001` (Theme assigned as `THEME-999999` outside approved taxonomy).
5. **Test Label Leakage**: `RESP-ANOM-LEAK-000001` (Input text contains `[[TEST_LABEL: NEGATIVE]]`).
6. **Missing Foreign Key**: `REV-ANOM-FK-000001` (References orphan customer `CUST-999999`).
7. **Invalid Date Ordering**: `RESP-ANOM-DATE-000001` (Response date in 2023 precedes customer creation in 2025).
8. **Invalid Lifecycle Transition**: `TKT-ANOM-000001` (Ticket `resolved_at` precedes `created_at` by 6 hours).
9. **Missing Mandatory Field**: `REV-ANOM-EMPTY-000001` (Empty `review_text`).
10. **Invalid Sentiment Value**: `RESP-ANOM-SENT-000001` (Sentiment label set to invalid value `SUPER_ANGRY`).

---

## 6. Reproducibility Verification Command

```powershell
python scripts/verify_reproducibility.py
```
Outputs SHA-256 checksums matching the verified reference run in `docs/REPRODUCIBILITY_REPORT.md`.

