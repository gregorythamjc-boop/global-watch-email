# ============================================================
# TRAVEL WATCH DAILY EMAIL
# December 2026
# 4 Travellers
#
# REQUIREMENTS
# - Direct / non-stop flights ONLY
# - Checked luggage required
# - Accommodation for 4
# - ALL PRICES displayed in SGD (S$)
# - Email ONLY Gregory + Linda
# ============================================================

import os
import smtplib
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# ============================================================
# GENERAL SETTINGS
# ============================================================

SG_TZ = ZoneInfo("Asia/Singapore")

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Travel Watch recipients ONLY
EMAIL_TO = [
    "gregory.thamjc@gmail.com",
    "linda.meifang@gmail.com",
]

ADULTS = 4

DISPLAY_CURRENCY = "SGD"
CURRENCY_SYMBOL = "S$"


# ============================================================
# CURRENCY FORMAT
# ============================================================

def format_sgd(amount):
    """
    Format Travel Watch prices in Singapore dollars.
    """

    if amount is None:
        return "Price unavailable"

    return f"S${amount:,.2f}"


# ============================================================
# DATE / TIME
# ============================================================

def sg_now():
    return datetime.now(SG_TZ)


TODAY = sg_now().strftime("%d %b %Y")

GENERATED = sg_now().strftime(
    "%d %b %Y, %I:%M %p SGT"
)


# ============================================================
# TRIP OPTIONS
# ============================================================

TRIPS = [

    # ========================================================
    # OPTION A — JAPAN + TAIPEI
    # ========================================================

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


    # ========================================================
    # OPTION B — JAPAN + GUANGZHOU
    # ========================================================

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


    # ========================================================
    # OPTION C — BANGKOK STANDALONE
    # ========================================================

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


    # ========================================================
    # OPTION D — GUANGZHOU STANDALONE
    # ========================================================

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
                "type": (
                    "Apartment / Serviced Apartment / Hotel"
                ),
            },
        ],
    },
]


# ============================================================
# GOOGLE FLIGHT SEARCH
# ============================================================

def google_flight_link(
    origin,
    destination,
    date,
):

    query = (
        f"Google Flights "
        f"{origin} to {destination} "
        f"{date} "
        f"nonstop direct flights only "
        f"{ADULTS} adults "
        f"checked baggage "
        f"prices SGD"
    )

    return (
        "https://www.google.com/search?q="
        + urllib.parse.quote_plus(query)
    )


# ============================================================
# BOOKING.COM SEARCH
# ============================================================

def booking_link(
    city,
    checkin,
    checkout,
):

    params = {

        "ss": city,

        "checkin": checkin,

        "checkout": checkout,

        "group_adults": ADULTS,

        "no_rooms": 1,

        "group_children": 0,

        "selected_currency": DISPLAY_CURRENCY,
    }

    return (
        "https://www.booking.com/"
        "searchresults.html?"
        + urllib.parse.urlencode(params)
    )


# ============================================================
# AIRBNB SEARCH
# ============================================================

def airbnb_link(
    city,
    checkin,
    checkout,
):

    params = {

        "query": city,

        "checkin": checkin,

        "checkout": checkout,

        "adults": ADULTS,

        "currency": DISPLAY_CURRENCY,
    }

    return (
        "https://www.airbnb.com/s/homes?"
        + urllib.parse.urlencode(params)
    )


# ============================================================
# CALCULATE NUMBER OF NIGHTS
# ============================================================

def calculate_nights(
    checkin,
    checkout,
):

    checkin_date = datetime.strptime(
        checkin,
        "%Y-%m-%d",
    )

    checkout_date = datetime.strptime(
        checkout,
        "%Y-%m-%d",
    )

    return (
        checkout_date - checkin_date
    ).days


# ============================================================
# GENERATE EACH TRIP OPTION
# ============================================================

def generate_trip(trip):

    html = f"""

    <div style="
        border:1px solid #dddddd;
        border-radius:10px;
        padding:18px;
        margin-bottom:25px;
    ">

    <h2>
        {trip["name"]}
    </h2>


    <h3>
        ✈️ Direct / Non-Stop Flights Only
    </h3>


    <table
        border="1"
        cellpadding="7"
        cellspacing="0"
        style="
            border-collapse:collapse;
            width:100%;
        "
    >

        <tr style="background:#f2f2f2;">

            <th>Date</th>

            <th>Route</th>

            <th>Requirements</th>

            <th>Currency</th>

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
                <b>
                    {flight["label"]}
                </b>
            </td>

            <td>

                <b>NON-STOP ONLY</b>

                <br>

                {ADULTS} adults

                <br>

                Checked luggage required

            </td>

            <td>

                <b>
                    SGD (S$)
                </b>

            </td>

            <td>

                <a href="{link}">
                    Search Direct Flights
                </a>

            </td>

        </tr>

        """

    html += """

    </table>


    <h3>
        🏠 Accommodation
    </h3>


    <table
        border="1"
        cellpadding="7"
        cellspacing="0"
        style="
            border-collapse:collapse;
            width:100%;
        "
    >

        <tr style="background:#f2f2f2;">

            <th>Location</th>

            <th>Dates</th>

            <th>Nights</th>

            <th>Type</th>

            <th>Guests</th>

            <th>Currency</th>

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

        nights = calculate_nights(
            stay["checkin"],
            stay["checkout"],
        )

        html += f"""

        <tr>

            <td>

                <b>
                    {stay["city"]}
                </b>

            </td>


            <td>

                {stay["checkin"]}

                <br>

                to

                <br>

                {stay["checkout"]}

            </td>


            <td>
                {nights}
            </td>


            <td>
                {stay["type"]}
            </td>


            <td>
                {ADULTS}
            </td>


            <td>

                <b>
                    SGD (S$)
                </b>

            </td>


            <td>

                <a href="{booking}">
                    Booking.com
                </a>

                <br><br>

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
# COST COMPARISON
# ============================================================

def generate_cost_comparison():

    return """

    <h2>
        💰 Total Trip Cost Comparison — SGD
    </h2>


    <p>

        All prices in Travel Watch are to be
        compared and displayed in
        <b>Singapore Dollars (S$)</b>.

    </p>


    <table
        border="1"
        cellpadding="8"
        cellspacing="0"
        style="
            border-collapse:collapse;
            width:100%;
        "
    >

        <tr style="background:#f2f2f2;">

            <th>
                Option
            </th>

            <th>
                Direct Flights
                <br>
                Total for 4
            </th>

            <th>
                Accommodation
                <br>
                Total
            </th>

            <th>
                Total Trip
                <br>
                for 4
            </th>

            <th>
                Cost
                <br>
                Per Person
            </th>

        </tr>


        <tr>

            <td>
                🇯🇵 Japan + 🇹🇼 Taipei
            </td>

            <td>
                Pending live pricing
            </td>

            <td>
                Pending live pricing
            </td>

            <td>
                Pending
            </td>

            <td>
                Pending
            </td>

        </tr>


        <tr>

            <td>
                🇯🇵 Japan + 🇨🇳 Guangzhou
            </td>

            <td>
                Pending live pricing
            </td>

            <td>
                Pending live pricing
            </td>

            <td>
                Pending
            </td>

            <td>
                Pending
            </td>

        </tr>


        <tr>

            <td>
                🇹🇭 Bangkok
                <br>
                2–6 Dec
            </td>

            <td>
                Pending live pricing
            </td>

            <td>
                Pending live pricing
            </td>

            <td>
                Pending
            </td>

            <td>
                Pending
            </td>

        </tr>


        <tr>

            <td>
                🇨🇳 Guangzhou
                <br>
                2–11 Dec
            </td>

            <td>
                Pending live pricing
            </td>

            <td>
                Pending live pricing
            </td>

            <td>
                Pending
            </td>

            <td>
                Pending
            </td>

        </tr>

    </table>

    """


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

        <b>
            Generated:
        </b>

        {GENERATED}

    </p>


    <p>

        <b>
            Travellers:
        </b>

        {ADULTS}

    </p>


    <p>

        <b>
            Display Currency:
        </b>

        SGD — Singapore Dollars (S$)

    </p>


    <div style="
        background:#f5f5f5;
        padding:15px;
        border-radius:8px;
    ">

        <b>
            Search Requirements
        </b>

        <br><br>

        ✈️ <b>DIRECT / NON-STOP FLIGHTS ONLY</b>

        <br>

        🚫 Connecting flights excluded

        <br>

        🧳 Checked baggage required

        <br>

        👨‍👩‍👦‍👦 4 travellers

        <br>

        🏠 Accommodation suitable for 4

        <br>

        💵 <b>ALL PRICES IN SGD (S$)</b>

        <br>

        💰 Compare total trip cost,
        not just headline airfare

    </div>


    <br>

    """

    for trip in TRIPS:

        html += generate_trip(
            trip
        )


    html += generate_cost_comparison()


    html += """

    <br>

    <hr>


    <p style="
        font-size:12px;
        color:#666666;
    ">

        <b>
            Important:
        </b>

        Travel prices and availability
        change frequently.

        <br><br>

        Only direct / non-stop flights
        should be considered.

        Connecting flights should be excluded.

        <br><br>

        Flight comparisons should include
        the required checked baggage rather
        than comparing base fares alone.

        <br><br>

        All airfare and accommodation
        comparisons should be converted
        to Singapore Dollars (SGD / S$).

        <br><br>

        Accommodation totals should include
        applicable taxes, service fees and
        other mandatory charges where the
        pricing provider makes them available.

        <br><br>

        Always verify the final airfare,
        baggage allowance, taxes,
        cancellation terms and accommodation
        charges before booking.

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
            "EMAIL_FROM missing from GitHub Secrets."
        )


    if not EMAIL_PASSWORD:

        raise ValueError(
            "EMAIL_PASSWORD missing from GitHub Secrets."
        )


    # Only Gregory + Linda
    recipients = list(
        dict.fromkeys(
            EMAIL_TO
        )
    )


    msg = MIMEMultipart(
        "alternative"
    )


    msg["From"] = EMAIL_FROM


    msg["To"] = ", ".join(
        EMAIL_TO
    )


    msg["Subject"] = (
        f"Travel Watch — "
        f"Dec 2026 — "
        f"{TODAY}"
    )


    html_body = build_email()


    msg.attach(

        MIMEText(
            html_body,
            "html",
            "utf-8",
        )

    )


    print(
        "Travel Watch recipients:"
    )


    for recipient in recipients:

        print(
            f" - {recipient}"
        )


    print(
        "Display currency: SGD"
    )


    print(
        "Flight requirement: "
        "DIRECT / NON-STOP ONLY"
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
        "=================================="
    )

    print(
        "STARTING TRAVEL WATCH"
    )

    print(
        f"Generated: {GENERATED}"
    )

    print(
        f"Travellers: {ADULTS}"
    )

    print(
        "Currency: SGD (S$)"
    )

    print(
        "Flights: DIRECT / NON-STOP ONLY"
    )

    print(
        "Checked luggage: REQUIRED"
    )

    print(
        "=================================="
    )


    send_email()


    print(
        "=================================="
    )

    print(
        "TRAVEL WATCH COMPLETE"
    )

    print(
        "=================================="
    )
