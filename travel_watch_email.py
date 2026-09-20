# ============================================================
# TRAVEL WATCH DAILY EMAIL
# December 2026
# 4 Travellers
# ============================================================

import os
import smtplib
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SG_TZ = ZoneInfo("Asia/Singapore")

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO") or EMAIL_FROM

# For now Travel Watch goes only to you.
# We can add your team later if wanted.
EMAIL_BCC = []

ADULTS = 4
YEAR = 2026


# ============================================================
# DATE / TIME
# ============================================================

def sg_now():
    return datetime.now(SG_TZ)


TODAY = sg_now().strftime("%d %b %Y")
GENERATED = sg_now().strftime("%d %b %Y, %I:%M %p SGT")


# ============================================================
# TRIP OPTIONS
# ============================================================

TRIPS = [
    {
        "name": "OPTION A — JAPAN + TAIPEI",
        "flights": [
            {
                "from": "SIN",
                "to": "TYO",
                "date": "2026-12-02",
                "label": "Singapore → Tokyo",
            },
            {
                "from": "TYO",
                "to": "TPE",
                "date": "2026-12-12",
                "label": "Tokyo → Taipei",
            },
            {
                "from": "TPE",
                "to": "SIN",
                "date": "2026-12-18",
                "label": "Taipei → Singapore",
            },
        ],
        "stays": [
            {
                "city": "Tokyo",
                "checkin": "2026-12-02",
                "checkout": "2026-12-05",
                "type": "Apartment / Hotel",
            },
            {
                "city": "Hakone",
                "checkin": "2026-12-05",
                "checkout": "2026-12-10",
                "type": "Ryokan / Hotel / Apartment",
            },
            {
                "city": "Tokyo",
                "checkin": "2026-12-10",
                "checkout": "2026-12-12",
                "type": "Apartment / Hotel",
            },
            {
                "city": "Taipei",
                "checkin": "2026-12-12",
                "checkout": "2026-12-18",
                "type": "Apartment",
            },
        ],
    },

    {
        "name": "OPTION B — JAPAN + GUANGZHOU",
        "flights": [
            {
                "from": "SIN",
                "to": "TYO",
                "date": "2026-12-02",
                "label": "Singapore → Tokyo",
            },
            {
                "from": "TYO",
                "to": "CAN",
                "date": "2026-12-12",
                "label": "Tokyo → Guangzhou",
            },
            {
                "from": "CAN",
                "to": "SIN",
                "date": "2026-12-18",
                "label": "Guangzhou → Singapore",
            },
        ],
        "stays": [
            {
                "city": "Tokyo",
                "checkin": "2026-12-02",
                "checkout": "2026-12-05",
                "type": "Apartment / Hotel",
            },
            {
                "city": "Hakone",
                "checkin": "2026-12-05",
                "checkout": "2026-12-10",
                "type": "Ryokan / Hotel / Apartment",
            },
            {
                "city": "Tokyo",
                "checkin": "2026-12-10",
                "checkout": "2026-12-12",
                "type": "Apartment / Hotel",
            },
            {
                "city": "Guangzhou",
                "checkin": "2026-12-12",
                "checkout": "2026-12-18",
                "type": "Apartment / Serviced Apartment",
            },
        ],
    },

    {
        "name": "OPTION C — BANGKOK STANDALONE",
        "flights": [
            {
                "from": "SIN",
                "to": "BKK",
                "date": "2026-12-02",
                "label": "Singapore → Bangkok",
            },
            {
                "from": "BKK",
                "to": "SIN",
                "date": "2026-12-06",
                "label": "Bangkok → Singapore",
            },
        ],
        "stays": [
            {
                "city": "Bangkok",
                "checkin": "2026-12-02",
                "checkout": "2026-12-06",
                "type": "Apartment / Hotel",
            },
        ],
    },

    {
        "name": "OPTION D — GUANGZHOU STANDALONE",
        "flights": [
            {
                "from": "SIN",
                "to": "CAN",
                "date": "2026-12-02",
                "label": "Singapore → Guangzhou",
            },
            {
                "from": "CAN",
                "to": "SIN",
                "date": "2026-12-11",
                "label": "Guangzhou → Singapore",
            },
        ],
        "stays": [
            {
                "city": "Guangzhou",
                "checkin": "2026-12-02",
                "checkout": "2026-12-11",
                "type": "Apartment / Serviced Apartment / Hotel",
            },
        ],
    },
]


# ============================================================
# SEARCH LINKS
# ============================================================

def google_flight_link(origin, destination, date):

    query = (
        f"Google Flights {origin} to {destination} "
        f"{date} direct flights 4 adults checked baggage"
    )

    return (
        "https://www.google.com/search?q="
        + urllib.parse.quote_plus(query)
    )


def booking_link(city, checkin, checkout):

    params = {
        "ss": city,
        "checkin": checkin,
        "checkout": checkout,
        "group_adults": ADULTS,
        "no_rooms": 1,
        "group_children": 0,
    }

    return (
        "https://www.booking.com/searchresults.html?"
        + urllib.parse.urlencode(params)
    )


def airbnb_link(city, checkin, checkout):

    params = {
        "query": city,
        "checkin": checkin,
        "checkout": checkout,
        "adults": ADULTS,
    }

    return (
        "https://www.airbnb.com/s/homes?"
        + urllib.parse.urlencode(params)
    )


# ============================================================
# BUILD TRIP
# ============================================================

def generate_trip(trip):

    html = f"""
    <div style="
        border:1px solid #dddddd;
        border-radius:10px;
        padding:18px;
        margin-bottom:25px;
    ">

    <h2>{trip["name"]}</h2>

    <h3>✈️ Flights</h3>

    <table border="1"
           cellpadding="7"
           cellspacing="0"
           style="
             border-collapse:collapse;
             width:100%;
           ">

    <tr style="background:#f2f2f2;">
        <th>Date</th>
        <th>Route</th>
        <th>Requirement</th>
        <th>Search</th>
    </tr>
    """

    for flight in trip["flights"]:

        link = google_flight_link(
            flight["from"],
            flight["to"],
            flight["date"],
        )

        html += f"""
        <tr>

            <td>
                {flight["date"]}
            </td>

            <td>
                <b>{flight["label"]}</b>
            </td>

            <td>
                Direct only<br>
                4 adults<br>
                Checked luggage
            </td>

            <td>
                <a href="{link}">
                Search Flights
                </a>
            </td>

        </tr>
        """

    html += """
    </table>

    <h3>🏠 Accommodation</h3>

    <table border="1"
           cellpadding="7"
           cellspacing="0"
           style="
             border-collapse:collapse;
             width:100%;
           ">

    <tr style="background:#f2f2f2;">
        <th>Location</th>
        <th>Dates</th>
        <th>Type</th>
        <th>Guests</th>
        <th>Search</th>
    </tr>
    """

    for stay in trip["stays"]:

        booking = booking_link(
            stay["city"],
            stay["checkin"],
            stay["checkout"],
        )

        airbnb = airbnb_link(
            stay["city"],
            stay["checkin"],
            stay["checkout"],
        )

        checkin = datetime.strptime(
            stay["checkin"],
            "%Y-%m-%d",
        )

        checkout = datetime.strptime(
            stay["checkout"],
            "%Y-%m-%d",
        )

        nights = (
            checkout - checkin
        ).days

        html += f"""
        <tr>

            <td>
                <b>{stay["city"]}</b>
            </td>

            <td>
                {stay["checkin"]}
                to
                {stay["checkout"]}
                <br>
                ({nights} nights)
            </td>

            <td>
                {stay["type"]}
            </td>

            <td>
                4
            </td>

            <td>

                <a href="{booking}">
                Booking.com
                </a>

                <br>

                <a href="{airbnb}">
                Airbnb
                </a>

            </td>

        </tr>
        """

    html += """
    </table>

    </div>
    """

    return html


# ============================================================
# BUILD EMAIL
# ============================================================

def build_email():

    html = f"""
    <html>

    <body style="
        font-family:Arial,sans-serif;
        line-height:1.5;
        max-width:1000px;
        margin:auto;
    ">

    <h1>
    ✈️ Travel Watch — December 2026
    </h1>

    <p>
    <b>Generated:</b> {GENERATED}
    </p>

    <p>
    <b>Travellers:</b> 4
    </p>

    <div style="
        background:#f5f5f5;
        padding:15px;
        border-radius:8px;
    ">

    <b>Search priorities</b>

    <br><br>

    ✈️ Direct / non-stop flights only<br>
    🧳 Checked baggage required<br>
    👨‍👩‍👦‍👦 Prices assessed for 4 travellers<br>
    🏠 Apartments prioritised where requested<br>
    💰 Compare total trip cost rather than
    headline airfare alone

    </div>

    <br>
    """

    for trip in TRIPS:

        html += generate_trip(trip)

    html += """
    <h2>💰 Cost Comparison</h2>

    <p>
    The next version of Travel Watch will
    populate this section with live airfare
    and accommodation prices once the pricing
    API is connected.
    </p>

    <table border="1"
           cellpadding="8"
           cellspacing="0"
           style="
             border-collapse:collapse;
             width:100%;
           ">

        <tr style="background:#f2f2f2;">
            <th>Option</th>
            <th>Airfare for 4</th>
            <th>Accommodation</th>
            <th>Total</th>
            <th>Per Person</th>
        </tr>

        <tr>
            <td>Japan + Taipei</td>
            <td>Pending live API</td>
            <td>Pending live API</td>
            <td>Pending</td>
            <td>Pending</td>
        </tr>

        <tr>
            <td>Japan + Guangzhou</td>
            <td>Pending live API</td>
            <td>Pending live API</td>
            <td>Pending</td>
            <td>Pending</td>
        </tr>

        <tr>
            <td>Bangkok 2–6 Dec</td>
            <td>Pending live API</td>
            <td>Pending live API</td>
            <td>Pending</td>
            <td>Pending</td>
        </tr>

        <tr>
            <td>Guangzhou 2–11 Dec</td>
            <td>Pending live API</td>
            <td>Pending live API</td>
            <td>Pending</td>
            <td>Pending</td>
        </tr>

    </table>

    <br>

    <p style="
        font-size:12px;
        color:#666666;
    ">

    Travel prices and availability change frequently.
    Always confirm the final fare, baggage allowance,
    taxes, cancellation conditions and accommodation
    charges on the booking provider's website before
    purchasing.

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
        raise ValueError("EMAIL_FROM missing.")

    if not EMAIL_PASSWORD:
        raise ValueError("EMAIL_PASSWORD missing.")

    if not EMAIL_TO:
        raise ValueError("EMAIL_TO missing.")

    msg = MIMEMultipart("alternative")

    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    msg["Subject"] = (
        f"Travel Watch — Dec 2026 — {TODAY}"
    )

    msg.attach(
        MIMEText(
            build_email(),
            "html",
            "utf-8",
        )
    )

    recipients = [
        EMAIL_TO,
        *EMAIL_BCC,
    ]

    recipients = list(
        dict.fromkeys(recipients)
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

    print(
        "Travel Watch email sent successfully."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "Starting Travel Watch..."
    )

    print(
        f"Generated: {GENERATED}"
    )

    send_email()

    print(
        "Travel Watch complete."
    )
