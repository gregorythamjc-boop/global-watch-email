# global_watch_email.py

import os
import smtplib
import traceback
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import feedparser
import yfinance as yf
from dotenv import load_dotenv


load_dotenv()

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

TODAY = datetime.now().strftime("%d %b %Y")
GENERATED_TIME = datetime.now().strftime("%d %b %Y, %I:%M %p")


NEWS_FEEDS = {
    "CNBC World": "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    "CNBC Markets": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "CNA Singapore": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml",
}


GLOBAL_MARKETS = {
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Dow Jones": "^DJI",
    "Hang Seng": "^HSI",
    "Nikkei": "^N225",
    "STI": "^STI",
}

MAGNIFICENT_7 = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Alphabet": "GOOGL",
    "Amazon": "AMZN",
    "Nvidia": "NVDA",
    "Meta": "META",
    "Tesla": "TSLA",
}

INTEREST_RATE_WATCH = {
    "US 3M Treasury Yield": "^IRX",
    "US 5Y Treasury Yield": "^FVX",
    "US 10Y Treasury Yield": "^TNX",
    "US 30Y Treasury Yield": "^TYX",
    "USD/SGD": "SGD=X",
    "Singapore REIT Proxy": "C38U.SI",
    "STI Proxy": "^STI",
}

FX_AGAINST_SGD = {
    "USD/SGD": "SGD=X",
    "EUR/SGD": "EURSGD=X",
    "GBP/SGD": "GBPSGD=X",
    "AUD/SGD": "AUDSGD=X",
    "JPY/SGD": "JPYSGD=X",
    "CNH/SGD": "CNHSGD=X",
}

COMMODITIES_FX_CRYPTO = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Brent Oil": "BZ=F",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "USD/SGD": "SGD=X",
    "US 10Y Treasury": "^TNX",
}

STRUCTURED_NOTES_WATCHLIST = {
    "US Magnificent 7": MAGNIFICENT_7,
    "US Software": {
        "Microsoft": "MSFT",
        "Salesforce": "CRM",
        "Adobe": "ADBE",
        "ServiceNow": "NOW",
        "Oracle": "ORCL",
    },
    "US Semiconductors": {
        "Nvidia": "NVDA",
        "AMD": "AMD",
        "Broadcom": "AVGO",
        "Qualcomm": "QCOM",
        "Intel": "INTC",
    },
    "US Pharmaceuticals": {
        "Eli Lilly": "LLY",
        "Johnson & Johnson": "JNJ",
        "Merck": "MRK",
        "Pfizer": "PFE",
        "AbbVie": "ABBV",
    },
    "US Financials": {
        "JPMorgan": "JPM",
        "Bank of America": "BAC",
        "Goldman Sachs": "GS",
        "Morgan Stanley": "MS",
        "Citigroup": "C",
    },
    "Singapore Banks": {
        "DBS": "D05.SI",
        "OCBC": "O39.SI",
        "UOB": "U11.SI",
    },
    "Singapore REITs": {
        "CICT": "C38U.SI",
        "Ascendas REIT": "A17U.SI",
        "Mapletree Logistics Trust": "M44U.SI",
        "Mapletree Industrial Trust": "ME8U.SI",
    },
    "China Tech": {
        "Alibaba": "9988.HK",
        "Tencent": "0700.HK",
        "Meituan": "3690.HK",
        "JD.com": "9618.HK",
        "Baidu": "9888.HK",
    },
}


UNIT_TRUST_FOCUS = {
    "US Technology / AI": {
        "Fund Names": [
            "Franklin Technology Fund",
            "Allianz Global Artificial Intelligence",
            "BlackRock World Technology Fund",
        ],
        "Drivers": {
            "Nasdaq": "^IXIC",
            "Nvidia": "NVDA",
            "Microsoft": "MSFT",
            "Broadcom": "AVGO",
        },
    },
    "Income Funds": {
        "Fund Names": [
            "PIMCO GIS Income Fund",
            "Allianz Income and Growth",
            "JPMorgan Income Fund",
        ],
        "Drivers": {
            "US 10Y Treasury": "^TNX",
            "S&P 500": "^GSPC",
            "USD/SGD": "SGD=X",
        },
    },
    "Bond Funds": {
        "Fund Names": [
            "PIMCO GIS Global Bond Fund",
            "AB Global Bond Portfolio",
            "Fidelity Global Bond Fund",
        ],
        "Drivers": {
            "US 10Y Treasury": "^TNX",
            "USD/SGD": "SGD=X",
            "Gold": "GC=F",
        },
    },
}


def get_market_data(ticker):
    try:
        data = yf.Ticker(ticker).history(period="5d", auto_adjust=False)

        if data.empty or len(data) < 2:
            return {
                "price": "N/A",
                "daily_change": "N/A",
                "five_day_change": "N/A",
                "status": "Insufficient data",
            }

        latest = float(data["Close"].iloc[-1])
        previous = float(data["Close"].iloc[-2])
        first = float(data["Close"].iloc[0])

        daily_change = ((latest - previous) / previous) * 100
        five_day_change = ((latest - first) / first) * 100

        return {
            "price": round(latest, 4),
            "daily_change": round(daily_change, 2),
            "five_day_change": round(five_day_change, 2),
            "status": "OK",
        }

    except Exception as e:
        return {
            "price": "N/A",
            "daily_change": "N/A",
            "five_day_change": "N/A",
            "status": str(e),
        }


def format_change(change):
    if isinstance(change, (int, float)):
        color = "green" if change >= 0 else "red"
        arrow = "▲" if change >= 0 else "▼"
        return f'<span style="color:{color}; font-weight:bold;">{arrow} {abs(change):.2f}%</span>'
    return '<span style="color:#999999;">Data unavailable</span>'


def average_daily_change(items):
    changes = []
    for name, ticker in items.items():
        data = get_market_data(ticker)
        if isinstance(data["daily_change"], (int, float)):
            changes.append(data["daily_change"])
    return round(sum(changes) / len(changes), 2) if changes else None


def build_table(title, items):
    rows = ""
    for name, ticker in items.items():
        data = get_market_data(ticker)
        rows += f"""
        <tr>
            <td>{name}</td>
            <td>{ticker}</td>
            <td>{data["price"]}</td>
            <td>{format_change(data["daily_change"])}</td>
            <td>{format_change(data["five_day_change"])}</td>
        </tr>
        """

    return f"""
    <h2>{title}</h2>
    <table>
        <tr>
            <th>Name</th>
            <th>Ticker</th>
            <th>Latest</th>
            <th>Daily Change</th>
            <th>5-Day Change</th>
        </tr>
        {rows}
    </table>
    """


def calculate_sector_performance():
    sector_scores = []

    for sector, names in STRUCTURED_NOTES_WATCHLIST.items():
        avg = average_daily_change(names)
        if avg is not None:
            sector_scores.append({
                "sector": sector,
                "average_change": avg,
            })

    sector_scores.sort(key=lambda x: x["average_change"], reverse=True)
    return sector_scores


def build_theme_table(title, themes):
    rows = ""
    for rank, item in enumerate(themes, start=1):
        rows += f"""
        <tr>
            <td>{rank}</td>
            <td>{item["sector"]}</td>
            <td>{format_change(item["average_change"])}</td>
        </tr>
        """

    return f"""
    <h2>{title}</h2>
    <table>
        <tr>
            <th>Rank</th>
            <th>Theme</th>
            <th>Average Daily Performance</th>
        </tr>
        {rows}
    </table>
    """


def get_market_regime():
    spx = get_market_data("^GSPC")
    nasdaq = get_market_data("^IXIC")
    btc = get_market_data("BTC-USD")
    gold = get_market_data("GC=F")

    risk_score = 0

    for item in [spx, nasdaq, btc]:
        if isinstance(item["daily_change"], (int, float)) and item["daily_change"] > 0:
            risk_score += 1

    if isinstance(gold["daily_change"], (int, float)) and gold["daily_change"] > 0:
        risk_score -= 1

    if risk_score >= 2:
        return "RISK ON"
    elif risk_score <= 0:
        return "RISK OFF"
    return "MIXED"


def build_interest_rate_outlook():
    us10y = get_market_data("^TNX")
    us5y = get_market_data("^FVX")
    usdsgd = get_market_data("SGD=X")
    sg_reit = get_market_data("C38U.SI")

    if isinstance(us10y["five_day_change"], (int, float)) and us10y["five_day_change"] > 0:
        usd_rate_view = "USD rates are showing upward pressure. This may support USD strength but can pressure bonds, REITs and long-duration assets."
    elif isinstance(us10y["five_day_change"], (int, float)) and us10y["five_day_change"] < 0:
        usd_rate_view = "USD rates are easing. This may support bond prices, REITs and income funds."
    else:
        usd_rate_view = "USD rate direction is mixed or data is limited."

    if isinstance(usdsgd["five_day_change"], (int, float)) and usdsgd["five_day_change"] > 0:
        sgd_view = "USD/SGD is rising, which means SGD is weaker against USD over the short term."
    elif isinstance(usdsgd["five_day_change"], (int, float)) and usdsgd["five_day_change"] < 0:
        sgd_view = "USD/SGD is falling, which means SGD is stronger against USD over the short term."
    else:
        sgd_view = "SGD direction is mixed or data is limited."

    return f"""
    <h2>Interest Rate Outlook: USD and SGD</h2>
    <p><strong>USD Rates:</strong> {usd_rate_view}</p>
    <p><strong>SGD View:</strong> {sgd_view}</p>
    <p>
        For Singapore clients, higher USD yields may support income conversations but can create mark-to-market pressure on bond funds and REITs.
        Lower yields may improve sentiment for fixed income, REITs and multi-asset income strategies.
    </p>
    {build_table("Interest Rate Watchlist", INTEREST_RATE_WATCH)}
    """


def build_fx_view():
    usdsgd = get_market_data("SGD=X")

    if isinstance(usdsgd["five_day_change"], (int, float)) and usdsgd["five_day_change"] > 0:
        view = "SGD has weakened against USD. Clients with USD assets may benefit from translation gains, while SGD-based investors buying USD assets may face higher entry cost."
    elif isinstance(usdsgd["five_day_change"], (int, float)) and usdsgd["five_day_change"] < 0:
        view = "SGD has strengthened against USD. This may reduce SGD cost for USD investments, but may reduce translated gains from existing USD holdings."
    else:
        view = "FX direction is mixed or data is limited."

    return f"""
    <h2>FX Views Against SGD</h2>
    <p>{view}</p>
    {build_table("Major FX Against SGD", FX_AGAINST_SGD)}
    """


def build_overall_summary(top_5, bottom_5):
    regime = get_market_regime()
    strongest = top_5[0]["sector"] if top_5 else "N/A"
    weakest = bottom_5[0]["sector"] if bottom_5 else "N/A"
    mag7_avg = average_daily_change(MAGNIFICENT_7)
    usdsgd = get_market_data("SGD=X")
    us10y = get_market_data("^TNX")

    return f"""
    <h2>Overall Summary</h2>
    <ul>
        <li><strong>Market Regime:</strong> {regime}</li>
        <li><strong>Strongest Theme:</strong> {strongest}</li>
        <li><strong>Weakest Theme:</strong> {weakest}</li>
        <li><strong>Magnificent 7 Average Daily Move:</strong> {format_change(mag7_avg)}</li>
        <li><strong>US 10Y Yield Short-Term Move:</strong> {format_change(us10y["five_day_change"])}</li>
        <li><strong>USD/SGD Short-Term Move:</strong> {format_change(usdsgd["five_day_change"])}</li>
    </ul>
    <p>
        FA discussion angle: use this briefing to frame client conversations around portfolio resilience, income sustainability,
        FX exposure, rate sensitivity, and structured note underlying quality. This is for market preparation only and not a product recommendation.
    </p>
    """


def get_news():
    news_html = ""

    for source, url in NEWS_FEEDS.items():
        news_html += f"<h3>{source}</h3><ul>"

        try:
            feed = feedparser.parse(url)
            entries = feed.entries[:5]

            if not entries:
                news_html += "<li>No headlines available.</li>"

            for entry in entries:
                title = entry.get("title", "No title")
                link = entry.get("link", "#")
                news_html += f'<li><a href="{link}">{title}</a></li>'

        except Exception as e:
            news_html += f"<li>Unable to load headlines: {e}</li>"

        news_html += "</ul>"

    return news_html


def build_structured_notes_watchlist():
    html = "<h2>Structured Notes Watchlist</h2>"
    for sector, names in STRUCTURED_NOTES_WATCHLIST.items():
        html += build_table(sector, names)
    return html


def build_unit_trust_focus():
    html = "<h2>Dynamic Unit Trust Focus</h2>"

    for category, details in UNIT_TRUST_FOCUS.items():
        funds = details["Fund Names"]
        drivers = details["Drivers"]
        avg_driver = average_daily_change(drivers)
        fund_list = "".join([f"<li>{fund}</li>" for fund in funds])

        html += f"""
        <h3>{category}</h3>
        <p><strong>Fund Names:</strong></p>
        <ul>{fund_list}</ul>
        <p><strong>Average Driver Performance Today:</strong> {format_change(avg_driver)}</p>
        {build_table("Live Market Drivers", drivers)}
        """

    return html


def build_compliance_note():
    return """
    <h2>Compliance Note</h2>
    <p>
        This briefing is for general market information and FA discussion preparation only.
        It is not a recommendation, offer, solicitation, or personal financial advice.
        Any product recommendation must be based on the client’s needs, risk profile,
        investment objectives, financial situation, knowledge, experience and suitability assessment.
    </p>
    """


def build_email_html():
    sector_scores = calculate_sector_performance()
    top_5 = sector_scores[:5]
    bottom_5 = sorted(sector_scores, key=lambda x: x["average_change"])[:5]

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: #222222;
                line-height: 1.5;
            }}
            h1 {{
                color: #0B3D2E;
            }}
            h2 {{
                color: #0B3D2E;
                border-bottom: 2px solid #0B3D2E;
                padding-bottom: 4px;
                margin-top: 28px;
            }}
            h3 {{
                color: #155E45;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 22px;
            }}
            th {{
                background-color: #0B3D2E;
                color: white;
                padding: 8px;
                border: 1px solid #dddddd;
                text-align: left;
            }}
            td {{
                padding: 8px;
                border: 1px solid #dddddd;
            }}
            tr:nth-child(even) {{
                background-color: #f7f7f7;
            }}
            a {{
                color: #0B5CAD;
                text-decoration: none;
            }}
            .small {{
                font-size: 12px;
                color: #666666;
            }}
        </style>
    </head>

    <body>
        <h1>Global Watch FA CIO Market Briefing - {TODAY}</h1>
        <p class="small">Generated: {GENERATED_TIME}</p>

        {build_overall_summary(top_5, bottom_5)}

        {build_table("Global Markets", GLOBAL_MARKETS)}

        {build_table("US Magnificent 7", MAGNIFICENT_7)}

        {build_interest_rate_outlook()}

        {build_fx_view()}

        {build_table("Commodities / FX / Crypto", COMMODITIES_FX_CRYPTO)}

        {build_theme_table("Top Performing Themes Today", top_5)}

        {build_theme_table("Weakest Themes Today", bottom_5)}

        {build_structured_notes_watchlist()}

        {build_unit_trust_focus()}

        <h2>News Headlines</h2>
        {get_news()}

        {build_compliance_note()}
    </body>
    </html>
    """


def send_email():
    if not EMAIL_FROM or not EMAIL_PASSWORD or not EMAIL_TO:
        raise ValueError("Missing email settings. Check EMAIL_FROM, EMAIL_PASSWORD and EMAIL_TO in .env file.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Global Watch FA CIO Market Briefing - {TODAY}"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    html_body = build_email_html()
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())


if __name__ == "__main__":
    try:
        send_email()
        print("Email sent successfully.")
    except Exception:
        print("Email failed.")
        print(traceback.format_exc())