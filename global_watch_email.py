# ============================================================
# GLOBAL WATCH DAILY EMAIL
# Designed for GitHub Actions
# Schedule: 07:00 Singapore Time Daily
# ============================================================

import os
import smtplib
import traceback
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import feedparser
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv


# ============================================================
# SETTINGS
# ============================================================

load_dotenv()

SG_TZ = ZoneInfo("Asia/Singapore")

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO") or EMAIL_FROM
FMP_API_KEY = os.getenv("FMP_API_KEY")
FMP_BASE = "https://financialmodelingprep.com/stable"

# Leave empty while testing.
# Add email addresses here later if you want the team to receive it.
EMAIL_BCC = []


def sg_now():
    return datetime.now(SG_TZ)


TODAY = sg_now().strftime("%d %b %Y")
GENERATED_TIME = sg_now().strftime("%d %b %Y, %I:%M %p SGT")


# ============================================================
# NEWS
# ============================================================

NEWS_FEEDS = {
    "CNBC World":
        "https://www.cnbc.com/id/100727362/device/rss/rss.html",

    "CNBC Markets":
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",

    "CNBC Investing":
        "https://www.cnbc.com/id/15839069/device/rss/rss.html",

    "CNBC Asia":
        "https://www.cnbc.com/id/19832390/device/rss/rss.html",

    "CNBC Economy":
        "https://www.cnbc.com/id/20910258/device/rss/rss.html",

    "CNA Singapore":
        "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml",
}


# ============================================================
# GLOBAL MARKETS
# ============================================================

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
    "Shanghai Composite": "000001.SS",
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


# ============================================================
# STRUCTURED NOTES
# ============================================================

STRUCTURED_NOTE_WATCHLIST = {

    "US Tech": [
        "AAPL",
        "MSFT",
        "NVDA",
        "META",
        "AMZN",
        "GOOGL",
        "TSLA",
    ],

    "US Banks": [
        "JPM",
        "BAC",
        "C",
        "GS",
        "MS",
    ],

    "US Semiconductors": [
        "NVDA",
        "AMD",
        "AVGO",
        "TSM",
    ],

    "China Tech": [
        "BABA",
        "9988.HK",
        "0700.HK",
        "JD",
        "PDD",
    ],

    "Singapore Banks": [
        "D05.SI",
        "O39.SI",
        "U11.SI",
    ],

    "Singapore REITs": [
        "C38U.SI",
        "A17U.SI",
        "M44U.SI",
    ],
}


# ============================================================
# BOND MARKET
# ============================================================

BOND_MARKET_WATCHLIST = {
    "US 10Y Treasury Yield": "^TNX",
    "US 13 Week Treasury Yield": "^IRX",
    "Investment Grade Bond ETF": "LQD",
    "High Yield Bond ETF": "HYG",
    "Long Treasury Bond ETF": "TLT",
    "Intermediate Treasury Bond ETF": "IEF",
}


# ============================================================
# UNIT TRUST WATCHLIST
#
# IMPORTANT:
# Do not invent Yahoo Finance tickers.
#
# Funds with no reliable Yahoo ticker are deliberately set to
# None. They remain visible in Global Watch, but performance
# will not be fabricated.
# ============================================================

UNIT_TRUST_WATCHLIST = {

    "Allianz Income and Growth":
        "0P0000S6YQ.SI",

    "Manulife GMADI":
        "0P0001IY1U.SI",

    "Fidelity Global Technology":
        "0P00000V2I.SI",

    "JPMorgan ASEAN Fund":
        "0P00000U7O.SI",

    # PIMCO
    "PIMCO GIS Income Fund":
        "0P0000Y077.SI",

    "PIMCO GIS Balanced Income & Growth Fund":
        None,

    # Amova
    "Amova Singapore Equity Fund":
        None,
}


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_float(value):

    try:

        if isinstance(value, pd.DataFrame):

            if value.empty:
                return None

            value = value.iloc[0, 0]

        elif isinstance(value, pd.Series):

            if value.empty:
                return None

            value = value.iloc[0]

        return float(value)

    except Exception:

        return None


def format_change_html(change):

    if change is None:
        return "N/A"

    if change > 0:

        return (
            '<span style="color:#0a8f3c;'
            'font-weight:bold;">'
            f'▲ {change:.2f}%'
            '</span>'
        )

    elif change < 0:

        return (
            '<span style="color:#c62828;'
            'font-weight:bold;">'
            f'▼ {change:.2f}%'
            '</span>'
        )

    else:

        return (
            '<span style="color:#666666;'
            'font-weight:bold;">'
            f'– {change:.2f}%'
            '</span>'
        )


# ============================================================
# MARKET PRICE ENGINE
# ============================================================

def get_price_change_yfinance(ticker):

    try:

        data = yf.download(
            ticker,
            period="5d",
            interval="1d",
            progress=False,
            auto_adjust=True,
            threads=False,
        )

        if data.empty or "Close" not in data:
            return None

        close = data["Close"].dropna()

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        if len(close) < 2:
            return None

        latest = safe_float(close.iloc[-1])
        previous = safe_float(close.iloc[-2])

        if latest is None:
            return None

        if previous in (None, 0):
            return None

        change = ((latest - previous) / previous) * 100

        return latest, change

    except Exception as e:

        print(
            f"yfinance failed for {ticker}: {e}"
        )

        return None


def get_price_change_yahoo_api(ticker):

    try:

        url = (
            "https://query1.finance.yahoo.com/"
            f"v8/finance/chart/{ticker}"
        )

        params = {
            "range": "5d",
            "interval": "1d",
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        result = data["chart"]["result"][0]

        prices = (
            result["indicators"]
            ["quote"][0]
            ["close"]
        )

        prices = [
            p for p in prices
            if p is not None
        ]

        if len(prices) < 2:
            return None

        latest = float(prices[-1])
        previous = float(prices[-2])

        if previous == 0:
            return None

        change = (
            (latest - previous)
            / previous
        ) * 100

        return latest, change

    except Exception as e:

        print(
            f"Yahoo API failed for "
            f"{ticker}: {e}"
        )

        return None


def get_price_change(ticker):

    print(
        f"Checking ticker: {ticker}"
    )

    result = (
        get_price_change_yfinance(ticker)
    )

    if result:

        latest, change = result

        print(
            f"{ticker}: "
            f"{latest:.2f}, "
            f"{change:.2f}%"
        )

        return result

    result = (
        get_price_change_yahoo_api(ticker)
    )

    if result:

        latest, change = result

        print(
            f"{ticker}: "
            f"{latest:.2f}, "
            f"{change:.2f}%"
        )

        return result

    print(
        f"{ticker}: Data unavailable"
    )

    return None


# ============================================================
# FUND PERFORMANCE ENGINE
#
# Primary: Financial Modeling Prep (FMP)
# Fallback: Yahoo Finance
#
# Calculates:
# - 7 calendar day return
# - 1 month return
# - YTD return
# ============================================================

def _performance_from_series(close):
    if close is None or len(close) < 2:
        return None

    close = close.dropna().sort_index()
    if len(close) < 2:
        return None

    latest = safe_float(close.iloc[-1])
    if latest is None:
        return None

    latest_date = close.index[-1]

    def price_on_or_before(target):
        hist = close[close.index <= target]
        return safe_float(hist.iloc[-1]) if not hist.empty else None

    one_week = price_on_or_before(latest_date - pd.Timedelta(days=7))
    one_month = price_on_or_before(latest_date - pd.DateOffset(months=1))

    year_data = close[close.index.year == latest_date.year]
    ytd_start = safe_float(year_data.iloc[0]) if not year_data.empty else None

    def ret(old):
        return ((latest - old) / old) * 100 if old not in (None, 0) else None

    return {
        "latest": latest,
        "week": ret(one_week),
        "month": ret(one_month),
        "ytd": ret(ytd_start),
        "date": latest_date.strftime("%d %b %Y"),
    }


def get_fmp_fund_performance(symbol):
    """Return historical performance from FMP when a verified FMP symbol exists."""
    if not FMP_API_KEY or not symbol:
        return None

    try:
        response = requests.get(
            f"{FMP_BASE}/historical-price-eod/light",
            params={"symbol": symbol, "apikey": FMP_API_KEY},
            timeout=20,
        )
        response.raise_for_status()
        rows = response.json()

        if not isinstance(rows, list) or len(rows) < 2:
            return None

        points = {}
        for row in rows:
            date = row.get("date")
            price = row.get("price")
            if date and price is not None:
                try:
                    points[pd.Timestamp(date)] = float(price)
                except Exception:
                    pass

        if len(points) < 2:
            return None

        close = pd.Series(points).sort_index()
        result = _performance_from_series(close)
        if result:
            result["source"] = "FMP"
        return result

    except Exception as e:
        print(f"FMP fund history failed for {symbol}: {e}")
        return None


def get_yahoo_fund_performance(ticker):
    if not ticker:
        return None

    try:
        data = yf.download(
            ticker,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True,
            threads=False,
        )

        if data.empty or "Close" not in data:
            print(f"No Yahoo fund data for {ticker}")
            return None

        close = data["Close"].dropna()
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        result = _performance_from_series(close)
        if result:
            result["source"] = "Yahoo Finance"
        return result

    except Exception as e:
        print(f"Yahoo fund performance failed for {ticker}: {e}")
        return None


def get_fund_performance(ticker, fmp_symbol=None):
    # Use FMP first only when an exact/verified FMP symbol has been configured.
    result = get_fmp_fund_performance(fmp_symbol)
    if result:
        return result

    # Preserve your current Yahoo identifiers as fallback.
    return get_yahoo_fund_performance(ticker)


# ============================================================
# GENERIC MARKET LIST
# ============================================================

def generate_price_list(
    title,
    watchlist,
):

    html = (
        f"<h2>{title}</h2><ul>"
    )

    for name, ticker in (
        watchlist.items()
    ):

        result = (
            get_price_change(ticker)
        )

        if result:

            latest, change = result

            html += (
                f"<li><b>{name}</b>: "
                f"{latest:.2f} "
                f"({format_change_html(change)})"
                "</li>"
            )

        else:

            html += (
                f"<li><b>{name}</b>: "
                "Data unavailable"
                "</li>"
            )

    html += "</ul>"

    return html


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

def generate_executive_summary():

    return f"""
    <h1>Global Watch - {TODAY}</h1>

    <p>
        <b>Generated:</b>
        {GENERATED_TIME}
    </p>

    <h2>🧭 Executive Summary</h2>

    <p>
    Today’s briefing covers CNBC and CNA news,
    global markets, Asia markets, Magnificent 7,
    USD/SGD, interest rates, structured-note
    underlyings, bonds and unit trusts.
    </p>

    <p>
    <b>Overall FA Message:</b><br>
    Markets remain opportunity-rich but selective.
    Review portfolio allocation, liquidity,
    income requirements, risk tolerance,
    currency exposure and diversification.
    </p>
    """


# ============================================================
# NEWS
# ============================================================

def generate_news_section():

    html = (
        "<h2>📰 Major News</h2>"
    )

    for source, url in (
        NEWS_FEEDS.items()
    ):

        html += (
            f"<h3>{source}</h3><ul>"
        )

        try:

            feed = feedparser.parse(url)

            if not feed.entries:

                html += (
                    "<li>No headlines "
                    "available.</li>"
                )

            for entry in (
                feed.entries[:5]
            ):

                title = entry.get(
                    "title",
                    "No title",
                )

                link = entry.get(
                    "link",
                    "#",
                )

                html += (
                    f'<li>'
                    f'<a href="{link}">'
                    f'{title}'
                    f'</a>'
                    f'</li>'
                )

        except Exception as e:

            html += (
                "<li>Unable to pull "
                f"news: {e}</li>"
            )

        html += "</ul>"

    return html


# ============================================================
# GLOBAL MARKET SUMMARY
# ============================================================

def generate_market_summary():

    html = generate_price_list(
        "🌍 Global Market Summary",
        GLOBAL_MARKETS,
    )

    html += """
    <p>
    <b>Market Watch:</b><br>
    Key drivers include interest-rate expectations,
    inflation, economic growth, corporate earnings,
    geopolitical risk and liquidity conditions.
    </p>
    """

    return html


# ============================================================
# ASIA
# ============================================================

def generate_asia_outlook():

    html = generate_price_list(
        "🌏 Asia Market Watch",
        ASIA_MARKETS,
    )

    html += """
    <h3>📌 Asia Watchpoints</h3>

    <table border="1"
           cellpadding="6"
           cellspacing="0"
           style="border-collapse:collapse;width:100%;">

        <tr>
            <th>Market</th>
            <th>Key Drivers</th>
        </tr>

        <tr>
            <td>Singapore</td>
            <td>
            Bank earnings, dividends,
            REITs and SGD conditions
            </td>
        </tr>

        <tr>
            <td>Hong Kong / China</td>
            <td>
            Policy support, technology,
            property and investor sentiment
            </td>
        </tr>

        <tr>
            <td>Japan</td>
            <td>
            Corporate reforms,
            shareholder returns and Yen
            </td>
        </tr>

        <tr>
            <td>India</td>
            <td>
            Growth, demographics,
            infrastructure and valuations
            </td>
        </tr>

        <tr>
            <td>South Korea</td>
            <td>
            Semiconductors,
            AI demand and exports
            </td>
        </tr>

    </table>
    """

    return html


# ============================================================
# MAGNIFICENT 7
# ============================================================

def generate_magnificent_7():

    html = generate_price_list(
        "🇺🇸 Magnificent 7 Watch",
        MAGNIFICENT_7,
    )

    html += """
    <p>
    <b>Portfolio Watch:</b><br>
    The Magnificent 7 remains important for US
    equity performance. Monitor concentration,
    valuation and diversification risks.
    </p>
    """

    return html


# ============================================================
# FX AND RATES
# ============================================================

def generate_fx_and_rates():

    usd_sgd = get_price_change(
        "SGD=X"
    )

    html = (
        "<h2>💵 FX & Interest Rates</h2>"
    )

    if usd_sgd:

        latest, change = usd_sgd

        html += (
            "<p><b>USD/SGD:</b> "
            f"{latest:.4f} "
            f"({format_change_html(change)})"
            "</p>"
        )

    else:

        html += (
            "<p><b>USD/SGD:</b> "
            "Data unavailable</p>"
        )

    html += """
    <p>
    <b>USD Rates:</b><br>
    Monitor inflation, employment,
    economic growth and Federal Reserve
    expectations.
    </p>

    <p>
    <b>SGD Rates:</b><br>
    Singapore rates are influenced by
    global USD rates, domestic liquidity
    and MAS exchange-rate policy.
    </p>
    """

    return html


# ============================================================
# STRUCTURED NOTE UNDERLYINGS
# ============================================================

def generate_structured_notes_watchlist():

    html = (
        "<h2>📊 Structured Note "
        "Underlying Watchlist</h2>"
    )

    for sector, tickers in (
        STRUCTURED_NOTE_WATCHLIST.items()
    ):

        html += (
            f"<h3>{sector}</h3><ul>"
        )

        for ticker in tickers:

            result = (
                get_price_change(ticker)
            )

            if result:

                latest, change = result

                html += (
                    f"<li><b>{ticker}</b>: "
                    f"{latest:.2f} "
                    f"({format_change_html(change)})"
                    "</li>"
                )

            else:

                html += (
                    f"<li><b>{ticker}</b>: "
                    "Data unavailable</li>"
                )

        html += "</ul>"

    return html


# ============================================================
# STRUCTURED NOTE DISCUSSION THEMES
# ============================================================

def generate_sn_ideas():

    return """
    <h2>💡 Structured Note Discussion Themes</h2>

    <table border="1"
           cellpadding="6"
           cellspacing="0"
           style="border-collapse:collapse;width:100%;">

        <tr>
            <th>Theme</th>
            <th>Potential Underlyings</th>
            <th>Key Risk to Monitor</th>
        </tr>

        <tr>
            <td>Singapore Banks</td>
            <td>DBS / OCBC / UOB</td>
            <td>
            Rates, earnings and
            financial-sector concentration
            </td>
        </tr>

        <tr>
            <td>US Banks</td>
            <td>JPM / BAC / GS / MS</td>
            <td>
            Credit cycle and US rates
            </td>
        </tr>

        <tr>
            <td>US Technology</td>
            <td>
            Apple / Microsoft /
            Meta / Amazon
            </td>
            <td>
            Valuation and concentration
            </td>
        </tr>

        <tr>
            <td>Semiconductors / AI</td>
            <td>
            Nvidia / AMD /
            Broadcom / TSMC
            </td>
            <td>
            Volatility and AI expectations
            </td>
        </tr>

        <tr>
            <td>China Technology</td>
            <td>
            Alibaba / Tencent /
            JD / PDD
            </td>
            <td>
            Policy, geopolitics and sentiment
            </td>
        </tr>

    </table>

    <p style="font-size:12px;color:gray;">
    Structured-product pricing varies by issuer,
    volatility, tenor, barrier, autocall structure
    and prevailing market conditions.
    </p>
    """


# ============================================================
# BONDS
# ============================================================

def generate_bond_market_watch():

    html = generate_price_list(
        "🏦 Bond Market Watch",
        BOND_MARKET_WATCHLIST,
    )

    html += """
    <p>
    <b>Bond Watch:</b><br>
    Monitor the direction of yields,
    duration sensitivity, credit spreads
    and default risk.
    </p>
    """

    return html


def generate_bond_ideas():

    return """
    <h2>💡 Bond Discussion Themes</h2>

    <ul>
        <li>
        <b>SGD Investment Grade:</b>
        SGD income and credit-quality discussion.
        </li>

        <li>
        <b>USD Investment Grade:</b>
        Yield opportunities with USD FX exposure.
        </li>

        <li>
        <b>Short Duration:</b>
        Lower duration sensitivity.
        </li>

        <li>
        <b>Asia Investment Grade:</b>
        Regional income diversification.
        </li>

        <li>
        <b>High Yield:</b>
        Higher income potential with
        materially higher credit risk.
        </li>

        <li>
        <b>Long Duration:</b>
        Greater sensitivity to changes
        in interest rates.
        </li>
    </ul>
    """


# ============================================================
# UNIT TRUST SECTION
# ============================================================

def generate_unit_trust_section():

    html = """
    <h2>🏆 Unit Trust Watchlist</h2>

    <p>
    Returns below are calculated from available
    market data. The 7-day return compares the
    latest observation against the nearest
    available observation on or before seven
    calendar days earlier.
    </p>

    <table border="1"
           cellpadding="7"
           cellspacing="0"
           style="border-collapse:collapse;width:100%;">

        <tr style="background-color:#f2f2f2;">
            <th>Fund</th>
            <th>Latest</th>
            <th>As Of</th>
            <th>7 Days</th>
            <th>1 Month</th>
            <th>YTD</th>
        </tr>
    """

    fund_results = []

    for fund_name, ticker in (
        UNIT_TRUST_WATCHLIST.items()
    ):

        result = None

        if ticker:

            result = (
                get_fund_performance(ticker)
            )

        if result:

            fund_results.append({
                "name": fund_name,
                "ticker": ticker,
                "latest": result["latest"],
                "week": result["week"],
                "month": result["month"],
                "ytd": result["ytd"],
                "date": result["date"],
                "source": result.get("source", "Unknown"),
            })

            html += f"""
            <tr>
                <td>
                    <b>{fund_name}</b><br>
                    <span style="
                        font-size:11px;
                        color:gray;
                    ">
                    {ticker}
                    </span>
                </td>

                <td>
                    {result["latest"]:.4f}
                </td>

                <td>
                    {result["date"]}
                </td>

                <td>
                    {format_change_html(result["week"])}
                </td>

                <td>
                    {format_change_html(result["month"])}
                </td>

                <td>
                    {format_change_html(result["ytd"])}
                </td>
            </tr>
            """

        else:

            html += f"""
            <tr>
                <td>
                    <b>{fund_name}</b>
                </td>

                <td colspan="5">
                    Reliable automated NAV data
                    unavailable from the current
                    Yahoo Finance feed.
                </td>
            </tr>
            """

    html += "</table>"


    # ========================================================
    # RANK AVAILABLE FUNDS
    # ========================================================

    ranked_funds = [
        fund
        for fund in fund_results
        if fund["week"] is not None
    ]

    ranked_funds.sort(
        key=lambda x: x["week"],
        reverse=True,
    )


    # ========================================================
    # TOP 10
    # ========================================================

    top_funds = ranked_funds[:10]

    html += """
    <h3>🚀 Top Performing Funds — Last 7 Days</h3>

    <table border="1"
           cellpadding="7"
           cellspacing="0"
           style="border-collapse:collapse;width:100%;">

        <tr style="background-color:#e8f5e9;">
            <th>Rank</th>
            <th>Fund</th>
            <th>7-Day Return</th>
        </tr>
    """

    if top_funds:

        for rank, fund in enumerate(
            top_funds,
            1,
        ):

            html += f"""
            <tr>
                <td>{rank}</td>
                <td>
                    <b>{fund["name"]}</b>
                </td>
                <td>
                    {format_change_html(fund["week"])}
                </td>
            </tr>
            """

    else:

        html += """
        <tr>
            <td colspan="3">
                No 7-day fund data available.
            </td>
        </tr>
        """

    html += "</table>"


    # ========================================================
    # BOTTOM 10
    # ========================================================

    bottom_funds = sorted(
        ranked_funds,
        key=lambda x: x["week"],
    )[:10]

    html += """
    <h3>🔻 Worst Performing Funds — Last 7 Days</h3>

    <table border="1"
           cellpadding="7"
           cellspacing="0"
           style="border-collapse:collapse;width:100%;">

        <tr style="background-color:#ffebee;">
            <th>Rank</th>
            <th>Fund</th>
            <th>7-Day Return</th>
        </tr>
    """

    if bottom_funds:

        for rank, fund in enumerate(
            bottom_funds,
            1,
        ):

            html += f"""
            <tr>
                <td>{rank}</td>
                <td>
                    <b>{fund["name"]}</b>
                </td>
                <td>
                    {format_change_html(fund["week"])}
                </td>
            </tr>
            """

    else:

        html += """
        <tr>
            <td colspan="3">
                No 7-day fund data available.
            </td>
        </tr>
        """

    html += """
    </table>

    <p style="font-size:12px;color:gray;">
    Rankings cover funds in this Global Watch
    watchlist for which comparable automated
    performance data is available. They are not
    rankings of the entire Singapore unit-trust
    market. Verify NAV and performance with the
    relevant fund manager, iFAST/FSMOne or official
    fund factsheet before use.
    </p>

    <h3>🌍 Unit Trust Themes to Watch</h3>

    <table border="1"
           cellpadding="6"
           cellspacing="0"
           style="border-collapse:collapse;width:100%;">

        <tr>
            <th>Theme</th>
            <th>Watchpoints</th>
        </tr>

        <tr>
            <td>Technology / AI</td>
            <td>
            Earnings, valuations,
            capex and concentration
            </td>
        </tr>

        <tr>
            <td>Healthcare</td>
            <td>
            Earnings, innovation and
            defensive characteristics
            </td>
        </tr>

        <tr>
            <td>Financials</td>
            <td>
            Rates, margins, credit
            and dividends
            </td>
        </tr>

        <tr>
            <td>REITs / Property</td>
            <td>
            Rates, refinancing and
            occupancy
            </td>
        </tr>

        <tr>
            <td>China / Greater China</td>
            <td>
            Policy, property,
            earnings and sentiment
            </td>
        </tr>

        <tr>
            <td>India</td>
            <td>
            Growth, earnings
            and valuations
            </td>
        </tr>

        <tr>
            <td>Japan</td>
            <td>
            Corporate reform,
            earnings and Yen
            </td>
        </tr>

        <tr>
            <td>Investment Grade Bonds</td>
            <td>
            Yields, duration and
            credit spreads
            </td>
        </tr>

        <tr>
            <td>High Yield Bonds</td>
            <td>
            Credit quality,
            spreads and defaults
            </td>
        </tr>

    </table>
    """

    return html


# ============================================================
# FA TALKING POINTS
# ============================================================

def generate_fa_talking_points():

    return """
    <h2>🗣 FA Discussion Checklist</h2>

    <ul>

        <li>
        <b>Liquidity:</b>
        Review emergency cash and upcoming
        financial commitments.
        </li>

        <li>
        <b>Income:</b>
        Review required income, sustainability,
        credit risk and distribution sources.
        </li>

        <li>
        <b>Growth:</b>
        Review time horizon, diversification
        and concentration.
        </li>

        <li>
        <b>Cash-heavy portfolios:</b>
        Discuss inflation, reinvestment risk
        and staged deployment where suitable.
        </li>

        <li>
        <b>Volatile markets:</b>
        Revisit risk tolerance, time horizon
        and diversification.
        </li>

        <li>
        <b>HNW planning:</b>
        Review liquidity, protection,
        estate planning and legacy objectives.
        </li>

    </ul>
    """


# ============================================================
# BUILD EMAIL
# ============================================================

def build_email_body():

    html = """
    <html>

    <body style="
        font-family:Arial,sans-serif;
        line-height:1.6;
        max-width:1000px;
        margin:auto;
    ">
    """

    html += (
        generate_executive_summary()
    )

    html += (
        generate_news_section()
    )

    html += (
        generate_market_summary()
    )

    html += (
        generate_asia_outlook()
    )

    html += (
        generate_magnificent_7()
    )

    html += (
        generate_fx_and_rates()
    )

    html += (
        generate_structured_notes_watchlist()
    )

    html += (
        generate_sn_ideas()
    )

    html += (
        generate_bond_market_watch()
    )

    html += (
        generate_bond_ideas()
    )

    html += (
        generate_unit_trust_section()
    )

    html += (
        generate_fa_talking_points()
    )

    html += """
    <hr>

    <p style="
        font-size:12px;
        color:gray;
    ">

    <b>Important:</b>
    Market prices, fund NAVs and news feeds may
    be delayed or unavailable. Verify important
    figures against official sources before use.

    <br><br>

    Disclaimer: This briefing is for information
    and discussion purposes only. It is not
    financial advice or a product recommendation
    and does not take into account any client's
    objectives, financial situation or needs.
    Conduct the required fact-find, risk profiling,
    product due diligence and suitability assessment
    before making any recommendation.

    </p>

    </body>
    </html>
    """

    return html


# ============================================================
# SEND EMAIL
# ============================================================

def send_email():

    if not EMAIL_FROM:

        raise ValueError(
            "EMAIL_FROM is missing from "
            "GitHub Secrets."
        )

    if not EMAIL_PASSWORD:

        raise ValueError(
            "EMAIL_PASSWORD is missing from "
            "GitHub Secrets."
        )

    if not EMAIL_TO:

        raise ValueError(
            "EMAIL_TO is missing."
        )

    subject = (
        f"Global Watch - {TODAY}"
    )

    msg = MIMEMultipart(
        "alternative"
    )

    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    html_body = (
        build_email_body()
    )

    msg.attach(
        MIMEText(
            html_body,
            "html",
            "utf-8",
        )
    )

    recipients = [EMAIL_TO]

    recipients.extend(
        EMAIL_BCC
    )

    # Remove accidental duplicate recipients
    recipients = list(
        dict.fromkeys(recipients)
    )

    print(
        "Sending Global Watch to:",
        EMAIL_TO,
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
    ) as server:

        server.login(
            EMAIL_FROM,
            EMAIL_PASSWORD,
        )

        server.sendmail(
            EMAIL_FROM,
            recipients,
            msg.as_string(),
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        print(
            "=================================="
        )

        print(
            "STARTING GLOBAL WATCH"
        )

        print(
            f"Singapore time: {GENERATED_TIME}"
        )

        print(
            "=================================="
        )

        # Quick market-data test
        test_result = (
            get_price_change("AAPL")
        )

        print(
            f"AAPL test result: "
            f"{test_result}"
        )

        # Generate and send one report
        send_email()

        print(
            "Global Watch email "
            "sent successfully."
        )

        print(
            "=================================="
        )

        print(
            "GLOBAL WATCH COMPLETE"
        )

        print(
            "=================================="
        )

    except Exception as e:

        print(
            "ERROR RUNNING GLOBAL WATCH:"
        )

        print(e)

        traceback.print_exc()

        # Important for GitHub Actions:
        # fail the workflow if the report fails.
        raise
