# ============================================================
# TRAVEL WATCH - LIVE PRICE EMAIL
# December 2026
# 4 Travellers
#
# LIVE DATA:
#   Google Flights via SerpApi
#   Google Hotels via SerpApi
#
# CROSS-CHECK LINKS:
#   Flights: Google Flights / Trip.com / Skyscanner
#   Hotels: Booking.com / Agoda / Trip.com
#
# REQUIREMENTS:
#   - Direct / non-stop flights ONLY
#   - Economy
#   - 4 travellers
#   - Checked baggage required
#   - Hotels: 4-star
#   - Hotels near train / metro / MRT stations
#   - Taipei: XIMENDING / XIMEN MRT specifically
#   - Currency: SGD
#   - Email ONLY Gregory + Linda
# ============================================================

import os
import smtplib
import html
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests


# ============================================================
# SETTINGS
# ============================================================

SG_TZ = ZoneInfo("Asia/Singapore")

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

EMAIL_TO = [
    "gregory.thamjc@gmail.com",
    "linda.meifang@gmail.com",
]

CURRENCY = "SGD"
ADULTS = 4

SERPAPI_URL = "https://serpapi.com/search.json"


# ============================================================
# UNIQUE FLIGHT SEARCHES
# ============================================================

FLIGHT_SEARCHES = [
    {
        "key": "SIN_TYO_0212",
        "from": "SIN",
        "to": "NRT,HND",
        "from_name": "Singapore",
        "to_name": "Tokyo",
        "date": "2026-12-02",
    },
    {
        "key": "TYO_TPE_1212",
        "from": "NRT,HND",
        "to": "TPE",
        "from_name": "Tokyo",
        "to_name": "Taipei",
        "date": "2026-12-12",
    },
    {
        "key": "TPE_SIN_1812",
        "from": "TPE",
        "to": "SIN",
        "from_name": "Taipei",
        "to_name": "Singapore",
        "date": "2026-12-18",
    },
    {
        "key": "TYO_CAN_1212",
        "from": "NRT,HND",
        "to": "CAN",
        "from_name": "Tokyo",
        "to_name": "Guangzhou",
        "date": "2026-12-12",
    },
    {
        "key": "CAN_SIN_1812",
        "from": "CAN",
        "to": "SIN",
        "from_name": "Guangzhou",
        "to_name": "Singapore",
        "date": "2026-12-18",
    },
    {
        "key": "SIN_BKK_0212",
        "from": "SIN",
        "to": "BKK,DMK",
        "from_name": "Singapore",
        "to_name": "Bangkok",
        "date": "2026-12-02",
    },
    {
        "key": "BKK_SIN_0612",
        "from": "BKK,DMK",
        "to": "SIN",
        "from_name": "Bangkok",
        "to_name": "Singapore",
        "date": "2026-12-06",
    },
    {
        "key": "SIN_CAN_0212",
        "from": "SIN",
        "to": "CAN",
        "from_name": "Singapore",
        "to_name": "Guangzhou",
        "date": "2026-12-02",
    },
    {
        "key": "CAN_SIN_1112",
        "from": "CAN",
        "to": "SIN",
        "from_name": "Guangzhou",
        "to_name": "Singapore",
        "date": "2026-12-11",
    },
]


# ============================================================
# HOTEL SEARCHES
# ============================================================

HOTEL_SEARCHES = [
    {
        "key": "TOKYO_0205",
        "location": "Tokyo",
        "query": "Tokyo 4 star hotels near train station",
        "checkin": "2026-12-02",
        "checkout": "2026-12-05",
    },
    {
        "key": "HAKONE_0510",
        "location": "Hakone",
        "query": "Hakone 4 star hotels near train station",
        "checkin": "2026-12-05",
        "checkout": "2026-12-10",
    },
    {
        "key": "TOKYO_1012",
        "location": "Tokyo",
        "query": "Tokyo 4 star hotels near train station",
        "checkin": "2026-12-10",
        "checkout": "2026-12-12",
    },

    # --------------------------------------------------------
    # UPDATED TAIPEI SEARCH
    # Ximending area / Ximen MRT specifically
    # --------------------------------------------------------
    {
        "key": "TAIPEI_1218",
        "location": "Taipei Ximending",
        "query": "Ximending Taipei 4 star hotels near Ximen MRT Station",
        "checkin": "2026-12-12",
        "checkout": "2026-12-18",
    },

    {
        "key": "GUANGZHOU_1218",
        "location": "Guangzhou",
        "query": "Guangzhou 4 star hotels near metro station",
        "checkin": "2026-12-12",
        "checkout": "2026-12-18",
    },
    {
        "key": "BANGKOK_0206",
        "location": "Bangkok",
        "query": "Bangkok 4 star hotels near BTS MRT station",
        "checkin": "2026-12-02",
        "checkout": "2026-12-06",
    },
    {
        "key": "GUANGZHOU_0211",
        "location": "Guangzhou",
        "query": "Guangzhou 4 star hotels near metro station",
        "checkin": "2026-12-02",
        "checkout": "2026-12-11",
    },
]


# ============================================================
# TRIP OPTIONS
# ============================================================

TRIPS = [
    {
        "name": "OPTION A — JAPAN + TAIPEI",
        "short": "Japan + Taipei",
        "flights": [
            "SIN_TYO_0212",
            "TYO_TPE_1212",
            "TPE_SIN_1812",
        ],
        "hotels": [
            "TOKYO_0205",
            "HAKONE_0510",
            "TOKYO_1012",
            "TAIPEI_1218",
        ],
    },
    {
        "name": "OPTION B — JAPAN + GUANGZHOU",
        "short": "Japan + Guangzhou",
        "flights": [
            "SIN_TYO_0212",
            "TYO_CAN_1212",
            "CAN_SIN_1812",
        ],
        "hotels": [
            "TOKYO_0205",
            "HAKONE_0510",
            "TOKYO_1012",
            "GUANGZHOU_1218",
        ],
    },
    {
        "name": "OPTION C — BANGKOK",
        "short": "Bangkok 2–6 Dec",
        "flights": [
            "SIN_BKK_0212",
            "BKK_SIN_0612",
        ],
        "hotels": [
            "BANGKOK_0206",
        ],
    },
    {
        "name": "OPTION D — GUANGZHOU",
        "short": "Guangzhou 2–11 Dec",
        "flights": [
            "SIN_CAN_0212",
            "CAN_SIN_1112",
        ],
        "hotels": [
            "GUANGZHOU_0211",
        ],
    },
]


# ============================================================
# HELPERS
# ============================================================

def money(value):
    if value is None:
        return "N/A"

    try:
        return f"S${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)


def safe(value):
    return html.escape(str(value)) if value is not None else ""


def nights(checkin, checkout):
    a = datetime.strptime(checkin, "%Y-%m-%d")
    b = datetime.strptime(checkout, "%Y-%m-%d")
    return (b - a).days


def serpapi_request(params):
    params = dict(params)
    params["api_key"] = SERPAPI_KEY

    try:
        response = requests.get(
            SERPAPI_URL,
            params=params,
            timeout=60,
        )

        response.raise_for_status()
        return response.json()

    except Exception as exc:
        print(f"SerpApi error: {exc}")
        return {"error": str(exc)}


# ============================================================
# FLIGHT SEARCH
# ============================================================

def search_flights(item):

    params = {
        "engine": "google_flights",
        "departure_id": item["from"],
        "arrival_id": item["to"],
        "outbound_date": item["date"],
        "type": "2",
        "travel_class": "1",
        "adults": ADULTS,
        "currency": CURRENCY,
        "hl": "en",
        "gl": "sg",

        # NON-STOP ONLY
        "stops": "1",

        # Sort by price
        "sort_by": "2",
    }

    data = serpapi_request(params)

    results = []

    raw_results = (
        data.get("best_flights", [])
        + data.get("other_flights", [])
    )

    seen = set()

    for result in raw_results:

        flight_legs = result.get("flights", [])

        # Extra protection against connecting flights
        if len(flight_legs) != 1:
            continue

        leg = flight_legs[0]

        price = result.get("price")

        if price is None:
            continue

        airline = leg.get("airline", "Unknown airline")
        flight_number = leg.get("flight_number", "")

        departure = leg.get("departure_airport", {})
        arrival = leg.get("arrival_airport", {})

        dep_time = departure.get("time", "")
        arr_time = arrival.get("time", "")

        dep_airport = departure.get("id", "")
        arr_airport = arrival.get("id", "")

        unique_key = (
            airline,
            flight_number,
            dep_time,
            arr_time,
            price,
        )

        if unique_key in seen:
            continue

        seen.add(unique_key)

        results.append({
            "airline": airline,
            "flight_number": flight_number,
            "departure_time": dep_time,
            "arrival_time": arr_time,
            "departure_airport": dep_airport,
            "arrival_airport": arr_airport,
            "price": price,
            "duration": leg.get("duration"),
        })

    results.sort(key=lambda x: x["price"])

    return results[:3]


# ============================================================
# HOTEL SEARCH
# ============================================================

def search_hotels(item):

    params = {
        "engine": "google_hotels",
        "q": item["query"],
        "check_in_date": item["checkin"],
        "check_out_date": item["checkout"],
        "adults": ADULTS,
        "children": 0,
        "currency": CURRENCY,
        "hl": "en",
        "gl": "sg",

        # 4 STAR ONLY
        "hotel_class": "4",

        # Sort by lowest price
        "sort_by": "3",
    }

    data = serpapi_request(params)

    properties = data.get("properties", [])

    results = []

    for prop in properties:

        hotel_class = (
            prop.get("extracted_hotel_class")
            or prop.get("hotel_class")
        )

        # Keep four-star properties
        if isinstance(hotel_class, int) and hotel_class != 4:
            continue

        total_rate = prop.get("total_rate", {})
        rate_per_night = prop.get("rate_per_night", {})

        total = total_rate.get("extracted_lowest")
        nightly = rate_per_night.get("extracted_lowest")

        estimated = False

        # If Google only gives us a nightly rate,
        # calculate an estimated stay total.
        if total is None and nightly is not None:
            total = nightly * nights(
                item["checkin"],
                item["checkout"]
            )
            estimated = True

        if total is None:
            continue

        nearby = []

        for place in prop.get("nearby_places", [])[:5]:

            place_name = place.get("name", "")
            transports = place.get("transportations", [])

            transport_text = []

            for transport in transports[:2]:

                t_type = transport.get("type", "")
                duration = transport.get("duration", "")

                if t_type or duration:
                    transport_text.append(
                        f"{t_type} {duration}".strip()
                    )

            if place_name:

                if transport_text:
                    nearby.append(
                        f"{place_name} "
                        f"({', '.join(transport_text)})"
                    )
                else:
                    nearby.append(place_name)

        results.append({
            "name": prop.get("name", "Hotel"),
            "total": total,
            "nightly": nightly,
            "estimated": estimated,
            "rating": prop.get("overall_rating"),
            "reviews": prop.get("reviews"),
            "hotel_class": hotel_class,
            "nearby": nearby,
            "source": prop.get("source"),
        })

    results.sort(key=lambda x: x["total"])

    return results[:3]


# ============================================================
# SEARCH LINKS
# ============================================================

def quote(text):
    return urllib.parse.quote_plus(text)


def google_flights_link(f):

    q = (
        f"Google Flights {f['from_name']} to {f['to_name']} "
        f"{f['date']} nonstop 4 adults SGD"
    )

    return "https://www.google.com/search?q=" + quote(q)


def trip_flights_link(f):

    q = (
        f"site:trip.com/flights "
        f"{f['from_name']} {f['to_name']} "
        f"{f['date']} direct flight"
    )

    return "https://www.google.com/search?q=" + quote(q)


def skyscanner_link(f):

    q = (
        f"site:skyscanner.com.sg "
        f"{f['from_name']} {f['to_name']} "
        f"{f['date']} direct flights"
    )

    return "https://www.google.com/search?q=" + quote(q)


def booking_link(h):

    params = {
        "ss": h["location"],
        "checkin": h["checkin"],
        "checkout": h["checkout"],
        "group_adults": ADULTS,
        "group_children": 0,
        "no_rooms": 1,
        "selected_currency": CURRENCY,
    }

    return (
        "https://www.booking.com/searchresults.html?"
        + urllib.parse.urlencode(params)
    )


def agoda_link(h):

    q = (
        f"Agoda {h['location']} "
        f"{h['checkin']} {h['checkout']} "
        f"4 adults 4 star hotel SGD"
    )

    return "https://www.google.com/search?q=" + quote(q)


def trip_hotel_link(h):

    q = (
        f"Trip.com {h['location']} hotels "
        f"{h['checkin']} {h['checkout']} "
        f"4 adults 4 star hotel SGD"
    )

    return "https://www.google.com/search?q=" + quote(q)


# ============================================================
# HTML STYLE
# ============================================================

STYLE = """
<style>
body {
    font-family: Arial, Helvetica, sans-serif;
    color: #222;
    line-height: 1.45;
}

.container {
    max-width: 1050px;
    margin: auto;
}

.header {
    background: #f4f6f8;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.card {
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 20px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0 18px 0;
}

th, td {
    border: 1px solid #aaa;
    padding: 9px;
    text-align: left;
    vertical-align: top;
}

th {
    background: #f2f2f2;
}

.price {
    font-weight: bold;
    white-space: nowrap;
}

.small {
    font-size: 12px;
    color: #666;
}

.warning {
    background: #fff8e1;
    padding: 12px;
    border-radius: 8px;
}
</style>
"""


# ============================================================
# FLIGHT TABLE
# ============================================================

def flight_table(search, results):

    rows = ""

    if not results:

        rows = """
        <tr>
            <td colspan="7">
                No live nonstop fare returned.
                Use the comparison links below.
            </td>
        </tr>
        """

    for i, r in enumerate(results, 1):

        rows += f"""
        <tr>
            <td>{i}</td>

            <td>
                <strong>{safe(r['airline'])}</strong><br>
                {safe(r['flight_number'])}
            </td>

            <td>
                {safe(r['departure_airport'])}<br>
                {safe(r['departure_time'])}
            </td>

            <td>
                {safe(r['arrival_airport'])}<br>
                {safe(r['arrival_time'])}
            </td>

            <td>
                <strong>NON-STOP</strong>
            </td>

            <td class="price">
                {money(r['price'])}
            </td>

            <td>
                Checked baggage must be verified
                before purchase.
            </td>
        </tr>
        """

    return f"""
    <h3>
        ✈️ {safe(search['from_name'])}
        →
        {safe(search['to_name'])}
        — {safe(search['date'])}
    </h3>

    <table>

        <tr>
            <th>#</th>
            <th>Airline</th>
            <th>Departure</th>
            <th>Arrival</th>
            <th>Stops</th>
            <th>Live Price</th>
            <th>Baggage</th>
        </tr>

        {rows}

    </table>

    <p>
        <strong>Compare:</strong>

        <a href="{google_flights_link(search)}">
            Google Flights
        </a>

        &nbsp; | &nbsp;

        <a href="{trip_flights_link(search)}">
            Trip.com
        </a>

        &nbsp; | &nbsp;

        <a href="{skyscanner_link(search)}">
            Skyscanner
        </a>
    </p>
    """


# ============================================================
# HOTEL TABLE
# ============================================================

def hotel_table(search, results):

    rows = ""

    if not results:

        rows = """
        <tr>
            <td colspan="7">
                No matching live 4-star hotel price returned.
                Use Booking.com, Agoda or Trip.com below.
            </td>
        </tr>
        """

    for i, r in enumerate(results, 1):

        nearby = "<br>".join(
            safe(x) for x in r["nearby"][:3]
        )

        if not nearby:
            nearby = "Check MRT / station distance before booking"

        rating = (
            safe(r["rating"])
            if r["rating"] is not None
            else "N/A"
        )

        price_note = (
            "Estimated from nightly rate"
            if r["estimated"]
            else "Live total returned"
        )

        rows += f"""
        <tr>

            <td>{i}</td>

            <td>
                <strong>{safe(r['name'])}</strong><br>
                ★★★★
            </td>

            <td>
                {rating}
            </td>

            <td>
                {nearby}
            </td>

            <td class="price">
                {money(r['nightly'])}
            </td>

            <td class="price">
                {money(r['total'])}<br>
                <span class="small">
                    {price_note}
                </span>
            </td>

            <td>
                {safe(r['source'] or 'Google Hotels')}
            </td>

        </tr>
        """

    # Special description for Taipei Ximending
    if search["key"] == "TAIPEI_1218":

        requirement = (
            "4-star • 4 travellers • SGD • "
            "<strong>Ximending area</strong> • "
            "near <strong>Ximen MRT Station</strong>"
        )

    else:

        requirement = (
            "4-star • 4 travellers • SGD • "
            "near train / metro / MRT where possible"
        )

    return f"""
    <h3>
        🏨 {safe(search['location'])}
        — {safe(search['checkin'])}
        to {safe(search['checkout'])}
        ({nights(search['checkin'], search['checkout'])} nights)
    </h3>

    <p>
        <strong>Requirement:</strong>
        {requirement}
    </p>

    <table>

        <tr>
            <th>#</th>
            <th>Hotel</th>
            <th>Rating</th>
            <th>Nearby Transport</th>
            <th>Per Night</th>
            <th>Total Stay</th>
            <th>Price Source</th>
        </tr>

        {rows}

    </table>

    <p>
        <strong>Compare:</strong>

        <a href="{booking_link(search)}">
            Booking.com
        </a>

        &nbsp; | &nbsp;

        <a href="{agoda_link(search)}">
            Agoda
        </a>

        &nbsp; | &nbsp;

        <a href="{trip_hotel_link(search)}">
            Trip.com
        </a>
    </p>
    """


# ============================================================
# BUILD REPORT
# ============================================================

def build_report():

    if not SERPAPI_KEY:
        raise RuntimeError(
            "SERPAPI_KEY is missing from GitHub Secrets."
        )

    print("Searching live flights...")

    flight_results = {}

    for search in FLIGHT_SEARCHES:

        print(
            f"Flight: "
            f"{search['from_name']} -> "
            f"{search['to_name']} "
            f"{search['date']}"
        )

        flight_results[search["key"]] = search_flights(search)

    print("Searching live hotels...")

    hotel_results = {}

    for search in HOTEL_SEARCHES:

        print(
            f"Hotel: "
            f"{search['location']} "
            f"{search['checkin']} -> "
            f"{search['checkout']}"
        )

        hotel_results[search["key"]] = search_hotels(search)

    now = datetime.now(SG_TZ)

    body = f"""
    <html>

    <head>
        {STYLE}
    </head>

    <body>

    <div class="container">

        <div class="header">

            <h1>
                🌏 Travel Watch — December 2026
            </h1>

            <p>
                Generated:
                <strong>
                    {now.strftime('%d %b %Y, %I:%M %p')} SGT
                </strong>
            </p>

            <p>
                👥 4 travellers<br>
                ✈️ Economy • DIRECT / NON-STOP ONLY<br>
                🧳 Checked baggage required<br>
                🏨 4-star hotels near train / metro stations<br>
                🇹🇼 Taipei: Ximending / Ximen MRT<br>
                💰 All prices in Singapore Dollars (S$)
            </p>

        </div>

        <div class="warning">

            <strong>Important:</strong>

            Live prices come from Google travel results
            through SerpApi.

            Trip.com, Skyscanner, Booking.com and Agoda
            are included as comparison links.

            Always verify final airfare, checked baggage,
            hotel taxes, room occupancy and cancellation
            conditions before booking.

        </div>

        <br>
    """

    # ========================================================
    # FLIGHTS
    # ========================================================

    body += """
    <div class="card">

        <h2>
            ✈️ Live Direct Flight Watch
        </h2>
    """

    for search in FLIGHT_SEARCHES:

        body += flight_table(
            search,
            flight_results.get(search["key"], [])
        )

    body += "</div>"


    # ========================================================
    # HOTELS
    # ========================================================

    body += """
    <div class="card">

        <h2>
            🏨 Live 4-Star Hotel Watch
        </h2>
    """

    for search in HOTEL_SEARCHES:

        body += hotel_table(
            search,
            hotel_results.get(search["key"], [])
        )

    body += "</div>"


    # ========================================================
    # TRIP TOTALS
    # ========================================================

    body += """
    <div class="card">

        <h2>
            💰 Cheapest Available Trip Comparison
        </h2>

        <table>

            <tr>
                <th>Option</th>
                <th>Flights</th>
                <th>Hotels</th>
                <th>Trip Total</th>
                <th>Per Person</th>
            </tr>
    """

    for trip in TRIPS:

        flight_total = 0
        flight_complete = True

        for key in trip["flights"]:

            options = flight_results.get(key, [])

            if options:
                flight_total += options[0]["price"]
            else:
                flight_complete = False

        hotel_total = 0
        hotel_complete = True

        for key in trip["hotels"]:

            options = hotel_results.get(key, [])

            if options:
                hotel_total += options[0]["total"]
            else:
                hotel_complete = False

        if flight_complete and hotel_complete:

            trip_total = flight_total + hotel_total
            per_person = trip_total / ADULTS

        else:

            trip_total = None
            per_person = None

        body += f"""
        <tr>

            <td>
                <strong>
                    {safe(trip['short'])}
                </strong>
            </td>

            <td>
                {
                    money(flight_total)
                    if flight_complete
                    else 'Incomplete live pricing'
                }
            </td>

            <td>
                {
                    money(hotel_total)
                    if hotel_complete
                    else 'Incomplete live pricing'
                }
            </td>

            <td class="price">
                {money(trip_total)}
            </td>

            <td class="price">
                {money(per_person)}
            </td>

        </tr>
        """

    body += """
        </table>

        <p class="small">

            The comparison uses the cheapest qualifying
            live result returned for each flight and hotel
            search.

            Availability and prices can change at any time.

            Verify final fare, checked baggage allowance,
            room capacity, taxes, fees and cancellation
            conditions before payment.

        </p>

    </div>

    </div>

    </body>

    </html>
    """

    return body


# ============================================================
# EMAIL
# ============================================================

def send_email():

    if not EMAIL_FROM:
        raise RuntimeError(
            "EMAIL_FROM is missing."
        )

    if not EMAIL_PASSWORD:
        raise RuntimeError(
            "EMAIL_PASSWORD is missing."
        )

    report = build_report()

    now = datetime.now(SG_TZ)

    msg = MIMEMultipart("alternative")

    msg["Subject"] = (
        "Travel Watch — Live Dec 2026 Prices — "
        + now.strftime("%d %b %Y")
    )

    msg["From"] = EMAIL_FROM

    msg["To"] = ", ".join(EMAIL_TO)

    text_version = """
Travel Watch — December 2026

Please view this email in HTML format to see
the live flight and hotel price tables.
"""

    msg.attach(
        MIMEText(
            text_version,
            "plain",
            "utf-8"
        )
    )

    msg.attach(
        MIMEText(
            report,
            "html",
            "utf-8"
        )
    )

    recipients = list(
        dict.fromkeys(EMAIL_TO)
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        timeout=60
    ) as server:

        server.login(
            EMAIL_FROM,
            EMAIL_PASSWORD
        )

        server.sendmail(
            EMAIL_FROM,
            recipients,
            msg.as_string()
        )

    print(
        "Travel Watch email sent successfully."
    )

    print("Recipients:")

    for recipient in recipients:
        print(f" - {recipient}")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    send_email()
