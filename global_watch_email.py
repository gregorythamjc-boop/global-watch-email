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
    "STI Singapore": "^STI",
    "Hang Seng": "^HSI",
    "Nikkei 225": "^N225",
    "Gold": "GC=F",
    "Crude Oil": "CL=F",
    "Bitcoin": "BTC-USD",
    "USD/SGD": "SGD=X",
}


ASIA_MARKETS = {
    "Singapore STI": "^STI",
    "Hong Kong HSI": "^HSI",
    "China Shanghai Composite": "000001.SS",
    "Japan Nikkei 225": "^N225",
    "South Korea KOSPI": "^KS11",
    "India Nifty 50": "^NSEI",
}


MAGNIFICENT_7 = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Alphabet": "GOOGL",
    "Amazon": "AMZN",
    "Meta": "META",
    "Nvidia": "NVDA",
    "Tesla": "TSLA",
}


STRUCTURED_NOTE_WATCHLIST = {
    "US Tech": ["AAPL", "MSFT", "NVDA", "META", "AMZN", "GOOGL", "TSLA"],
    "US Banks": ["JPM", "BAC", "C", "GS", "MS"],
    "US Semiconductors": ["NVDA", "AMD", "AVGO", "TSM"],
    "China Tech": ["BABA", "9988.HK", "0700.HK", "JD", "PDD"],
    "Singapore Banks": ["D05.SI", "O39.SI", "U11.SI"],
    "Singapore REITs": ["C38U.SI", "A17U.SI", "M44U.SI"],
}


BOND_MARKET_WATCHLIST = {
    "US 10Y Treasury Yield": "^TNX",
    "US 13 Week Treasury Yield": "^IRX",
    "Investment Grade Bond ETF": "LQD",
    "High Yield Bond ETF": "HYG",
    "Long Treasury Bond ETF": "TLT",
    "Intermediate Treasury Bond ETF": "IEF",
}


def get_price_change(ticker):
    try:
        print(f"Checking ticker: {ticker}")

        stock = yf.Ticker(ticker)

        data = stock.history(
            period="5d",
            auto_adjust=True
        )

        if data.empty or len(data) < 2:
            print(f"{ticker}: EMPTY DATA")
            return None

        latest = float(data["Close"].iloc[-1])
        previous = float(data["Close"].iloc[-2])

        change = ((latest - previous) / previous) * 100

        return latest, change

    except Exception as e:
        print(f"ERROR: {ticker}")
        print(e)
        return None


def direction_icon(change):
    if change > 0:
        return "▲"
    elif change < 0:
        return "▼"
    return "–"


def generate_executive_summary():
    return f"""
    <h1>Global Watch - {TODAY}</h1>

    <p><b>Generated:</b> {GENERATED_TIME}</p>

    <h2>🧭 Executive Summary</h2>

    <p>
    Today’s briefing covers global news, global markets, Asia outlook,
    Magnificent 7, USD/SGD, interest rates, structured note ideas,
    bond ideas, unit trust themes and FA client talking points.
    </p>

    <p>
    <b>Overall FA Message:</b><br>
    Markets remain opportunity-rich but selective. Clients should review
    portfolio allocation, liquidity needs, income requirements, risk tolerance,
    FX exposure and estate planning gaps.
    </p>
    """


def generate_news_section():
    html = "<h2>📰 Major News</h2>"

    for source, url in NEWS_FEEDS.items():
        html += f"<h3>{source}</h3><ul>"

        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:5]:
                title = entry.get("title", "No title")
                link = entry.get("link", "#")
                html += f'<li><a href="{link}">{title}</a></li>'

        except Exception:
            html += f"<li>Unable to pull news from {source}</li>"

        html += "</ul>"

    return html


def generate_market_summary():
    html = "<h2>🌍 Global Market Summary</h2><ul>"

    for name, ticker in GLOBAL_MARKETS.items():
        result = get_price_change(ticker)

        if result:
            latest, change = result
            icon = direction_icon(change)
            html += f"<li><b>{name}</b>: {latest:.2f} ({icon} {change:.2f}%)</li>"
        else:
            html += f"<li><b>{name}</b>: Data unavailable</li>"

    html += "</ul>"

    html += """
    <p>
    <b>Market View:</b><br>
    Global markets remain driven by interest-rate expectations, inflation data,
    corporate earnings, geopolitical risk and liquidity conditions.
    </p>
    """

    return html


def generate_asia_outlook():
    html = "<h2>🌏 Asia Market Outlook</h2><ul>"

    for name, ticker in ASIA_MARKETS.items():
        result = get_price_change(ticker)

        if result:
            latest, change = result
            icon = direction_icon(change)
            html += f"<li><b>{name}</b>: {latest:.2f} ({icon} {change:.2f}%)</li>"
        else:
            html += f"<li><b>{name}</b>: Data unavailable</li>"

    html += "</ul>"

    html += """
    <h3>📌 Asia Outlook Summary</h3>

    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse; width:100%;">
        <tr>
            <th>Market</th>
            <th>Current View</th>
            <th>Key Drivers</th>
        </tr>

        <tr>
            <td>Singapore</td>
            <td>Neutral to Positive</td>
            <td>Bank earnings, dividend support, REIT recovery, SGD stability</td>
        </tr>

        <tr>
            <td>Hong Kong / China</td>
            <td>Neutral to Recovery Watch</td>
            <td>Policy support, tech sentiment, property stabilisation, investor confidence</td>
        </tr>

        <tr>
            <td>Japan</td>
            <td>Positive</td>
            <td>Corporate reforms, shareholder returns, inflation normalisation, weaker Yen</td>
        </tr>

        <tr>
            <td>India</td>
            <td>Positive Long Term</td>
            <td>Economic growth, demographics, infrastructure spending, domestic consumption</td>
        </tr>

        <tr>
            <td>South Korea</td>
            <td>Positive</td>
            <td>Semiconductor cycle, AI demand, exports, technology recovery</td>
        </tr>
    </table>

    <h3>💡 Asia Investment Ideas</h3>

    <ul>
        <li><b>Singapore Banks:</b> DBS, OCBC, UOB for income and dividend-focused clients.</li>
        <li><b>Singapore REITs:</b> Recovery theme if rates stabilise or fall.</li>
        <li><b>Japan Equities:</b> Supported by corporate governance reform and shareholder returns.</li>
        <li><b>India Equities:</b> Long-term structural growth and consumption theme.</li>
        <li><b>Asia Investment Grade Bonds:</b> Suitable for income and diversification clients.</li>
        <li><b>China / Hong Kong Tech:</b> Recovery opportunity, but higher volatility.</li>
        <li><b>Asia Dividend Funds:</b> Useful for income with regional diversification.</li>
    </ul>

    <h3>🌏 Asia Structured Note Ideas</h3>

    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse; width:100%;">
        <tr>
            <th>Theme</th>
            <th>Potential Underlyings</th>
            <th>Client Type</th>
            <th>Key Risk</th>
        </tr>

        <tr>
            <td>Singapore Banks</td>
            <td>DBS / OCBC / UOB</td>
            <td>Conservative income clients</td>
            <td>Bank earnings, rate cycle, market volatility</td>
        </tr>

        <tr>
            <td>Singapore REITs</td>
            <td>CapitaLand Integrated / Ascendas / Mapletree Logistics</td>
            <td>Income clients</td>
            <td>Interest rates, refinancing cost, property cycle</td>
        </tr>

        <tr>
            <td>China Tech</td>
            <td>Alibaba / Tencent / JD / Meituan</td>
            <td>Aggressive clients</td>
            <td>Policy risk, earnings risk, volatility</td>
        </tr>

        <tr>
            <td>Asia Semiconductors</td>
            <td>TSMC / Samsung / SK Hynix</td>
            <td>Growth and income clients</td>
            <td>AI cycle, chip demand, geopolitical risk</td>
        </tr>

        <tr>
            <td>Japan Index</td>
            <td>Nikkei 225 linked structures</td>
            <td>Moderate to growth clients</td>
            <td>Yen movement, valuation, export cycle</td>
        </tr>

        <tr>
            <td>India Index</td>
            <td>Nifty 50 linked structures</td>
            <td>Long-term growth clients</td>
            <td>Valuation, liquidity, currency risk</td>
        </tr>
    </table>

    <h3>🗣 FA Asia Talking Point</h3>

    <p>
    Asia remains one of the most important long-term allocation regions.
    Singapore offers income and dividend stability, Japan benefits from
    corporate reforms, India remains a structural growth story, while China
    and Hong Kong provide recovery potential for investors who can accept
    higher volatility.
    </p>
    """

    return html


def generate_magnificent_7():
    html = "<h2>🇺🇸 Magnificent 7 Watch</h2><ul>"

    for name, ticker in MAGNIFICENT_7.items():
        result = get_price_change(ticker)

        if result:
            latest, change = result
            icon = direction_icon(change)
            html += f"<li><b>{name}</b>: US${latest:.2f} ({icon} {change:.2f}%)</li>"
        else:
            html += f"<li><b>{name}</b>: Data unavailable</li>"

    html += "</ul>"

    html += """
    <p>
    <b>FA View:</b><br>
    The Magnificent 7 remains important for US equity sentiment, but concentration
    risk is high. Clients with heavy US technology exposure should review diversification.
    </p>
    """

    return html


def generate_fx_and_rates():
    usd_sgd = get_price_change("SGD=X")

    html = "<h2>💵 FX & Interest Rate Outlook</h2>"

    if usd_sgd:
        latest, change = usd_sgd
        icon = direction_icon(change)
        html += f"<p><b>USD/SGD:</b> {latest:.4f} ({icon} {change:.2f}%)</p>"
    else:
        html += "<p><b>USD/SGD:</b> Data unavailable</p>"

    html += """
    <p>
    <b>USD Interest Rate View:</b><br>
    US rate expectations remain a key market driver. If inflation remains sticky,
    rates may stay higher for longer. If growth slows, markets may price more rate cuts.
    </p>

    <p>
    <b>SGD Interest Rate View:</b><br>
    Singapore rates are influenced by USD rates, liquidity and MAS exchange-rate policy.
    SGD money market and short-duration income products remain useful for liquidity clients.
    </p>

    <p>
    <b>FX View Against SGD:</b><br>
    A strong USD benefits USD asset holders but introduces currency risk for SGD-based clients.
    SGD-based clients should review whether their portfolio income and liabilities are in the same currency.
    </p>
    """

    return html


def generate_structured_notes_watchlist():
    html = "<h2>📊 Structured Notes Underlying Watchlist</h2>"

    for sector, tickers in STRUCTURED_NOTE_WATCHLIST.items():
        html += f"<h3>{sector}</h3><ul>"

        for ticker in tickers:
            result = get_price_change(ticker)

            if result:
                latest, change = result
                icon = direction_icon(change)
                html += f"<li><b>{ticker}</b>: {latest:.2f} ({icon} {change:.2f}%)</li>"
            else:
                html += f"<li><b>{ticker}</b>: Data unavailable</li>"

        html += "</ul>"

    return html


def generate_sn_ideas():
    return """
    <h2>💡 Structured Note Ideas</h2>

    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse; width:100%;">
        <tr>
            <th>Theme</th>
            <th>Potential Underlyings</th>
            <th>Indicative Tenor</th>
            <th>Indicative Coupon Range*</th>
            <th>Client Type</th>
        </tr>

        <tr>
            <td>Singapore Banks</td>
            <td>DBS / OCBC / UOB</td>
            <td>6-12 months</td>
            <td>5% - 8%</td>
            <td>Conservative income clients</td>
        </tr>

        <tr>
            <td>US Banks</td>
            <td>JPM / BAC / GS / MS</td>
            <td>6-12 months</td>
            <td>7% - 10%</td>
            <td>Income clients</td>
        </tr>

        <tr>
            <td>US Technology</td>
            <td>Apple / Microsoft / Meta / Amazon</td>
            <td>6-12 months</td>
            <td>7% - 12%</td>
            <td>Growth and income clients</td>
        </tr>

        <tr>
            <td>Semiconductors / AI</td>
            <td>Nvidia / AMD / Broadcom / TSMC</td>
            <td>6-12 months</td>
            <td>8% - 15%</td>
            <td>Aggressive clients</td>
        </tr>

        <tr>
            <td>China Technology</td>
            <td>Alibaba / Tencent / JD / PDD</td>
            <td>6-12 months</td>
            <td>10% - 18%</td>
            <td>Aggressive clients</td>
        </tr>

        <tr>
            <td>Singapore REITs</td>
            <td>CapitaLand / Ascendas / Mapletree</td>
            <td>6-12 months</td>
            <td>6% - 9%</td>
            <td>Income-focused clients</td>
        </tr>
    </table>

    <p style="font-size:12px;">
    *Coupon ranges are indicative only and change daily based on volatility,
    issuer pricing, tenor, barrier level, autocall frequency and market conditions.
    </p>

    <p>
    <b>SN Suitability Checklist:</b><br>
    • Explain worst-performing underlying risk.<br>
    • Explain knock-in, autocall, issuer and liquidity risk.<br>
    • Confirm whether the client can hold to maturity.<br>
    • Confirm whether the client can accept receiving shares if knock-in occurs.<br>
    • Notes are not fixed deposits and capital is not guaranteed unless stated.
    </p>
    """


def generate_bond_market_watch():
    html = "<h2>🏦 Bond Market Watch</h2><ul>"

    for name, ticker in BOND_MARKET_WATCHLIST.items():
        result = get_price_change(ticker)

        if result:
            latest, change = result
            icon = direction_icon(change)
            html += f"<li><b>{name}</b>: {latest:.2f} ({icon} {change:.2f}%)</li>"
        else:
            html += f"<li><b>{name}</b>: Data unavailable</li>"

    html += "</ul>"

    html += """
    <p>
    <b>Bond Market View:</b><br>
    Bond opportunities remain linked to the rate cycle. If rates peak or fall,
    longer-duration bonds may benefit. If rates stay higher for longer,
    short-duration and investment grade bonds may be more suitable.
    </p>
    """

    return html


def generate_bond_ideas():
    return """
    <h2>💡 Bond Ideas</h2>

    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse; width:100%;">
        <tr>
            <th>Bond Theme</th>
            <th>Potential Area</th>
            <th>Risk Level</th>
            <th>Suitable For</th>
        </tr>

        <tr>
            <td>SGD Investment Grade Bonds</td>
            <td>Local banks, quality corporates, statutory-board linked issuers</td>
            <td>Low to Medium</td>
            <td>Conservative SGD income clients</td>
        </tr>

        <tr>
            <td>USD Investment Grade Bonds</td>
            <td>Global banks, quality corporates, sovereign-linked issuers</td>
            <td>Medium</td>
            <td>Clients comfortable with USD exposure</td>
        </tr>

        <tr>
            <td>Short Duration Bonds</td>
            <td>1-3 year bond funds or short maturity bonds</td>
            <td>Low to Medium</td>
            <td>Cash-heavy clients</td>
        </tr>

        <tr>
            <td>Asia Investment Grade Bonds</td>
            <td>Asia IG bond funds</td>
            <td>Medium</td>
            <td>Income and diversification clients</td>
        </tr>

        <tr>
            <td>High Yield Bonds</td>
            <td>Global or Asia high yield bond funds</td>
            <td>High</td>
            <td>Aggressive income clients</td>
        </tr>

        <tr>
            <td>Long Duration Bonds</td>
            <td>Long maturity government or IG bonds</td>
            <td>Medium to High</td>
            <td>Clients expecting rate cuts</td>
        </tr>
    </table>
    """


def generate_unit_trust_section():
    return """
    <h2>📈 Unit Trust Ideas</h2>

    <ul>
        <li>Global equity funds for long-term growth</li>
        <li>Asia income funds for regional diversification</li>
        <li>Investment grade bond funds for income and stability</li>
        <li>Money market funds for liquidity parking</li>
        <li>Technology funds for higher-risk growth allocation</li>
        <li>Healthcare funds for defensive growth exposure</li>
        <li>Multi-asset income funds for balanced clients</li>
        <li>India and Japan funds for Asia growth exposure</li>
        <li>Asia dividend funds for income clients</li>
    </ul>

    <p>
    <b>FA Note:</b><br>
    Please verify actual fund performance, risk rating, platform availability,
    expense ratio and client suitability before recommendation.
    </p>
    """


def generate_fa_talking_points():
    return """
    <h2>🗣 FA Talking Points</h2>

    <ul>
        <li><b>Conservative clients:</b> Money market funds, short-duration bonds, investment grade bonds and SGD income solutions.</li>
        <li><b>Income clients:</b> Dividend equities, REITs, multi-asset income funds, bond funds and structured income solutions.</li>
        <li><b>Growth clients:</b> US equities, Magnificent 7, Asia growth, India, Japan, technology and healthcare themes.</li>
        <li><b>Cash-heavy clients:</b> Explain reinvestment risk, inflation erosion and staged deployment.</li>
        <li><b>Volatility-worried clients:</b> Use diversification, phased entry, income buckets and time horizon planning.</li>
        <li><b>HNW clients:</b> Estate planning, universal life, premium financing, trust planning, corporate cash and legacy equalisation.</li>
    </ul>
    """


def build_email_body():
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    """

    html += generate_executive_summary()
    html += generate_news_section()
    html += generate_market_summary()
    html += generate_asia_outlook()
    html += generate_magnificent_7()
    html += generate_fx_and_rates()
    html += generate_structured_notes_watchlist()
    html += generate_sn_ideas()
    html += generate_bond_market_watch()
    html += generate_bond_ideas()
    html += generate_unit_trust_section()
    html += generate_fa_talking_points()

    html += """
    <hr>

    <p style="font-size: 12px; color: gray;">
    Disclaimer: This briefing is for information and discussion purposes only.
    It is not financial advice, not a product recommendation and does not take
    into account any client’s personal objectives, financial situation or needs.
    Please conduct proper fact-find, risk profiling, product due diligence and
    suitability assessment before making any recommendation.
    </p>

    </body>
    </html>
    """

    return html


def send_email():
    if not EMAIL_FROM or not EMAIL_PASSWORD or not EMAIL_TO:
        raise ValueError(
            "Missing email settings. Please check EMAIL_FROM, EMAIL_PASSWORD and EMAIL_TO in GitHub Secrets."
        )

    subject = f"Global Watch - {TODAY}"

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    html_body = build_email_body()
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())


if __name__ == "__main__":
    try:
        print("========== YFINANCE TEST ==========")
        test_stock = yf.Ticker("AAPL")
        print(test_stock.history(period="5d"))
        print("========== TEST COMPLETE ==========")

        send_email()
        print("Email sent successfully.")

    except Exception as e:
        print("Error sending email:")
        print(e)
        traceback.print_exc()
