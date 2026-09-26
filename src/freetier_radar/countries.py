"""Every country and territory a vendor's territory words can name, under its
ISO 3166-1 alpha-2 code — the codes GitHub's Innovation Graph counts developers
under, Kosovo's XK included — with the name the pages print first and the
spellings vendors use for it.

A border is recorded as codes and read back off the vendor's page as names, so
the table has two jobs, and the second one is where lists break. On 2026-09-25 a
first mapping of Google's region list lost Côte d'Ivoire to its apostrophe,
"Congo (DRC)" to its brackets and Cyprus to the words "Republic of"; every
spelling a vendor has been read using is here, and a name the matcher cannot
place is reported rather than guessed.

`codes_named` reads a page the way a person reads a list: the longest name at a
place wins, so Guinea-Bissau, Papua New Guinea and Equatorial Guinea are not
also Guinea, South Sudan is not also Sudan, and "Taiwan, Province of China" is
not also mainland China; and a phrase that carries a country's name without
naming the country — New Mexico, Northern Ireland — names none.
"""
from __future__ import annotations

import re
from functools import lru_cache

__all__ = ["COUNTRIES", "NOT_COUNTRIES", "DNS_SUBNETS", "country_name", "codes_named"]

# code -> (the name a page prints, then every other spelling a vendor uses).
# Matched as written, capitals and all: "chad", "turkey" and "china" are words.
# "Korea" alone is the Republic of Korea, as every commercial list prints it
# (TRAE's); the North is "North Korea" or "DPRK" wherever a vendor names it.
COUNTRIES: dict[str, tuple[str, ...]] = {
    "AD": ('Andorra', 'Principality of Andorra'),
    "AE": ('the United Arab Emirates', 'United Arab Emirates'),
    "AF": ('Afghanistan', 'Islamic Republic of Afghanistan'),
    "AG": ('Antigua and Barbuda', 'Antigua & Barbuda'),
    "AI": ('Anguilla',),
    "AL": ('Albania', 'Republic of Albania'),
    "AM": ('Armenia', 'Republic of Armenia'),
    "AO": ('Angola', 'Republic of Angola'),
    "AQ": ('Antarctica',),
    "AR": ('Argentina', 'Argentine Republic'),
    "AS": ('American Samoa',),
    "AT": ('Austria', 'Republic of Austria'),
    "AU": ('Australia',),
    "AW": ('Aruba',),
    "AX": ('the Åland Islands', 'Åland Islands', 'Aland Islands'),
    "AZ": ('Azerbaijan', 'Republic of Azerbaijan'),
    "BA": ('Bosnia and Herzegovina', 'Republic of Bosnia and Herzegovina', 'Bosnia & Herzegovina'),
    "BB": ('Barbados',),
    "BD": ('Bangladesh', "People's Republic of Bangladesh"),
    "BE": ('Belgium', 'Kingdom of Belgium'),
    "BF": ('Burkina Faso',),
    "BG": ('Bulgaria', 'Republic of Bulgaria'),
    "BH": ('Bahrain', 'Kingdom of Bahrain'),
    "BI": ('Burundi', 'Republic of Burundi'),
    "BJ": ('Benin', 'Republic of Benin'),
    "BL": ('Saint Barthélemy', 'Saint Barthelemy', 'St. Barthélemy', 'St. Barthelemy', 'St Barthelemy'),
    "BM": ('Bermuda',),
    "BN": ('Brunei', 'Brunei Darussalam'),
    "BO": ('Bolivia', 'Bolivia, Plurinational State of', 'Plurinational State of Bolivia'),
    "BQ": ('the Caribbean Netherlands', 'Caribbean Netherlands', 'Bonaire, Sint Eustatius and Saba', 'Bonaire'),
    "BR": ('Brazil', 'Federative Republic of Brazil'),
    "BS": ('the Bahamas', 'Bahamas', 'Commonwealth of the Bahamas', 'The Bahamas'),
    "BT": ('Bhutan', 'Kingdom of Bhutan'),
    "BV": ('Bouvet Island',),
    "BW": ('Botswana', 'Republic of Botswana'),
    "BY": ('Belarus', 'Republic of Belarus'),
    "BZ": ('Belize',),
    "CA": ('Canada',),
    "CC": ('the Cocos (Keeling) Islands', 'Cocos (Keeling) Islands'),
    "CD": ('DR Congo', 'Congo, The Democratic Republic of the', 'Congo (DRC)', 'DRC', 'Democratic Republic of the Congo', 'Congo (Kinshasa)', 'Congo-Kinshasa', 'Congo, Democratic Republic of the'),
    "CF": ('the Central African Republic', 'Central African Republic'),
    "CG": ('the Republic of the Congo', 'Republic of the Congo', 'Congo', 'Congo (Brazzaville)', 'Congo-Brazzaville', 'Congo, Republic of the'),
    "CH": ('Switzerland', 'Swiss Confederation'),
    "CI": ("Côte d'Ivoire", "Republic of Côte d'Ivoire", 'Ivory Coast', "Cote d'Ivoire"),
    "CK": ('the Cook Islands', 'Cook Islands'),
    "CL": ('Chile', 'Republic of Chile'),
    "CM": ('Cameroon', 'Republic of Cameroon'),
    "CN": ('mainland China', 'China', "People's Republic of China", 'Chinese mainland', 'China (mainland)', 'Mainland China', '中国大陆', '中国内地'),
    "CO": ('Colombia', 'Republic of Colombia'),
    "CR": ('Costa Rica', 'Republic of Costa Rica'),
    "CU": ('Cuba', 'Republic of Cuba'),
    "CV": ('Cabo Verde', 'Republic of Cabo Verde', 'Cape Verde'),
    "CW": ('Curaçao', 'Curacao'),
    "CX": ('Christmas Island',),
    "CY": ('Cyprus', 'Republic of Cyprus'),
    "CZ": ('Czechia', 'Czech Republic'),
    "DE": ('Germany', 'Federal Republic of Germany'),
    "DJ": ('Djibouti', 'Republic of Djibouti'),
    "DK": ('Denmark', 'Kingdom of Denmark'),
    "DM": ('Dominica', 'Commonwealth of Dominica'),
    "DO": ('the Dominican Republic', 'Dominican Republic'),
    "DZ": ('Algeria', "People's Democratic Republic of Algeria"),
    "EC": ('Ecuador', 'Republic of Ecuador'),
    "EE": ('Estonia', 'Republic of Estonia'),
    "EG": ('Egypt', 'Arab Republic of Egypt'),
    "EH": ('Western Sahara',),
    "ER": ('Eritrea', 'the State of Eritrea'),
    "ES": ('Spain', 'Kingdom of Spain'),
    "ET": ('Ethiopia', 'Federal Democratic Republic of Ethiopia'),
    "FI": ('Finland', 'Republic of Finland'),
    "FJ": ('Fiji', 'Republic of Fiji'),
    "FK": ('the Falkland Islands', 'Falkland Islands', 'Falkland Islands (Malvinas)'),
    "FM": ('Micronesia', 'Micronesia, Federated States of', 'Federated States of Micronesia'),
    "FO": ('the Faroe Islands', 'Faroe Islands'),
    "FR": ('France', 'French Republic'),
    "GA": ('Gabon', 'Gabonese Republic'),
    "GB": ('the United Kingdom', 'United Kingdom', 'United Kingdom of Great Britain and Northern Ireland', 'Great Britain'),
    "GD": ('Grenada',),
    "GE": ('Georgia',),
    "GF": ('French Guiana',),
    "GG": ('Guernsey',),
    "GH": ('Ghana', 'Republic of Ghana'),
    "GI": ('Gibraltar',),
    "GL": ('Greenland',),
    "GM": ('the Gambia', 'Gambia', 'Republic of the Gambia', 'The Gambia'),
    "GN": ('Guinea', 'Republic of Guinea'),
    "GP": ('Guadeloupe',),
    "GQ": ('Equatorial Guinea', 'Republic of Equatorial Guinea'),
    "GR": ('Greece', 'Hellenic Republic'),
    "GS": ('South Georgia', 'South Georgia and the South Sandwich Islands'),
    "GT": ('Guatemala', 'Republic of Guatemala'),
    "GU": ('Guam',),
    "GW": ('Guinea-Bissau', 'Republic of Guinea-Bissau'),
    "GY": ('Guyana', 'Republic of Guyana'),
    "HK": ('Hong Kong', 'Hong Kong Special Administrative Region of China', 'Hong Kong SAR', 'Hong Kong, China', 'Hong Kong (China)', '中国香港', '香港'),
    "HM": ('the Heard and McDonald Islands', 'Heard and McDonald Islands', 'Heard Island and McDonald Islands'),
    "HN": ('Honduras', 'Republic of Honduras'),
    "HR": ('Croatia', 'Republic of Croatia'),
    "HT": ('Haiti', 'Republic of Haiti'),
    "HU": ('Hungary',),
    "ID": ('Indonesia', 'Republic of Indonesia'),
    "IE": ('Ireland',),
    "IL": ('Israel', 'State of Israel'),
    "IM": ('Isle of Man',),
    "IN": ('India', 'Republic of India'),
    "IO": ('the British Indian Ocean Territory', 'British Indian Ocean Territory'),
    "IQ": ('Iraq', 'Republic of Iraq'),
    "IR": ('Iran', 'Iran, Islamic Republic of', 'Islamic Republic of Iran'),
    "IS": ('Iceland', 'Republic of Iceland'),
    "IT": ('Italy', 'Italian Republic'),
    "JE": ('Jersey',),
    "JM": ('Jamaica',),
    "JO": ('Jordan', 'Hashemite Kingdom of Jordan'),
    "JP": ('Japan',),
    "KE": ('Kenya', 'Republic of Kenya'),
    "KG": ('Kyrgyzstan', 'Kyrgyz Republic'),
    "KH": ('Cambodia', 'Kingdom of Cambodia'),
    "KI": ('Kiribati', 'Republic of Kiribati'),
    "KM": ('the Comoros', 'Comoros', 'Union of the Comoros'),
    "KN": ('Saint Kitts and Nevis', 'St. Kitts and Nevis', 'St Kitts and Nevis', 'Saint Kitts & Nevis'),
    "KP": ('North Korea', "Korea, Democratic People's Republic of", "Democratic People's Republic of Korea", 'DPRK'),
    "KR": ('South Korea', 'Korea, Republic of', 'Republic of Korea', 'Korea'),
    "KW": ('Kuwait', 'State of Kuwait'),
    "KY": ('the Cayman Islands', 'Cayman Islands'),
    "KZ": ('Kazakhstan', 'Republic of Kazakhstan', 'Kazakstan'),
    "LA": ('Laos', "Lao People's Democratic Republic"),
    "LB": ('Lebanon', 'Lebanese Republic'),
    "LC": ('Saint Lucia', 'St. Lucia', 'St Lucia'),
    "LI": ('Liechtenstein', 'Principality of Liechtenstein'),
    "LK": ('Sri Lanka', 'Democratic Socialist Republic of Sri Lanka'),
    "LR": ('Liberia', 'Republic of Liberia'),
    "LS": ('Lesotho', 'Kingdom of Lesotho'),
    "LT": ('Lithuania', 'Republic of Lithuania'),
    "LU": ('Luxembourg', 'Grand Duchy of Luxembourg'),
    "LV": ('Latvia', 'Republic of Latvia'),
    "LY": ('Libya',),
    "MA": ('Morocco', 'Kingdom of Morocco'),
    "MC": ('Monaco', 'Principality of Monaco'),
    "MD": ('Moldova', 'Moldova, Republic of', 'Republic of Moldova'),
    "ME": ('Montenegro',),
    "MF": ('Saint Martin', 'Saint Martin (French part)', 'St. Martin'),
    "MG": ('Madagascar', 'Republic of Madagascar'),
    "MH": ('the Marshall Islands', 'Marshall Islands', 'Republic of the Marshall Islands'),
    "MK": ('North Macedonia', 'Republic of North Macedonia', 'Macedonia'),
    "ML": ('Mali', 'Republic of Mali'),
    "MM": ('Myanmar', 'Republic of Myanmar', 'Burma', 'Myanmar (Burma)'),
    "MN": ('Mongolia',),
    "MO": ('Macao', 'Macao Special Administrative Region of China', 'Macau', 'Macao SAR', 'Macau SAR', 'Macao, China', 'Macau, China', '中国澳门', '澳门'),
    "MP": ('the Northern Mariana Islands', 'Northern Mariana Islands', 'Commonwealth of the Northern Mariana Islands'),
    "MQ": ('Martinique',),
    "MR": ('Mauritania', 'Islamic Republic of Mauritania'),
    "MS": ('Montserrat',),
    "MT": ('Malta', 'Republic of Malta'),
    "MU": ('Mauritius', 'Republic of Mauritius'),
    "MV": ('the Maldives', 'Maldives', 'Republic of Maldives'),
    "MW": ('Malawi', 'Republic of Malawi'),
    "MX": ('Mexico', 'United Mexican States'),
    "MY": ('Malaysia',),
    "MZ": ('Mozambique', 'Republic of Mozambique'),
    "NA": ('Namibia', 'Republic of Namibia'),
    "NC": ('New Caledonia',),
    "NE": ('Niger', 'Republic of the Niger'),
    "NF": ('Norfolk Island',),
    "NG": ('Nigeria', 'Federal Republic of Nigeria'),
    "NI": ('Nicaragua', 'Republic of Nicaragua'),
    "NL": ('the Netherlands', 'Netherlands', 'Kingdom of the Netherlands'),
    "NO": ('Norway', 'Kingdom of Norway'),
    "NP": ('Nepal', 'Federal Democratic Republic of Nepal'),
    "NR": ('Nauru', 'Republic of Nauru'),
    "NU": ('Niue',),
    "NZ": ('New Zealand',),
    "OM": ('Oman', 'Sultanate of Oman'),
    "PA": ('Panama', 'Republic of Panama'),
    "PE": ('Peru', 'Republic of Peru'),
    "PF": ('French Polynesia',),
    "PG": ('Papua New Guinea', 'Independent State of Papua New Guinea'),
    "PH": ('the Philippines', 'Philippines', 'Republic of the Philippines'),
    "PK": ('Pakistan', 'Islamic Republic of Pakistan'),
    "PL": ('Poland', 'Republic of Poland'),
    "PM": ('Saint Pierre and Miquelon', 'St. Pierre and Miquelon', 'St Pierre and Miquelon'),
    "PN": ('the Pitcairn Islands', 'Pitcairn'),
    "PR": ('Puerto Rico', 'Puerto-Rico'),
    "PS": ('Palestine', 'Palestine, State of', 'the State of Palestine', 'Palestinian Territories', 'Palestinian Territory'),
    "PT": ('Portugal', 'Portuguese Republic'),
    "PW": ('Palau', 'Republic of Palau'),
    "PY": ('Paraguay', 'Republic of Paraguay'),
    "QA": ('Qatar', 'State of Qatar'),
    "RE": ('Réunion', 'Reunion'),
    "RO": ('Romania',),
    "RS": ('Serbia', 'Republic of Serbia'),
    "RU": ('Russia', 'Russian Federation'),
    "RW": ('Rwanda', 'Rwandese Republic'),
    "SA": ('Saudi Arabia', 'Kingdom of Saudi Arabia'),
    "SB": ('the Solomon Islands', 'Solomon Islands'),
    "SC": ('Seychelles', 'Republic of Seychelles'),
    "SD": ('Sudan', 'Republic of the Sudan'),
    "SE": ('Sweden', 'Kingdom of Sweden'),
    "SG": ('Singapore', 'Republic of Singapore'),
    "SH": ('Saint Helena', 'Saint Helena, Ascension and Tristan da Cunha', 'St. Helena', 'St Helena'),
    "SI": ('Slovenia', 'Republic of Slovenia'),
    "SJ": ('Svalbard and Jan Mayen', 'Svalbard'),
    "SK": ('Slovakia', 'Slovak Republic'),
    "SL": ('Sierra Leone', 'Republic of Sierra Leone'),
    "SM": ('San Marino', 'Republic of San Marino'),
    "SN": ('Senegal', 'Republic of Senegal'),
    "SO": ('Somalia', 'Federal Republic of Somalia'),
    "SR": ('Suriname', 'Republic of Suriname'),
    "SS": ('South Sudan', 'Republic of South Sudan'),
    "ST": ('São Tomé and Príncipe', 'Sao Tome and Principe', 'Democratic Republic of Sao Tome and Principe'),
    "SV": ('El Salvador', 'Republic of El Salvador'),
    "SX": ('Sint Maarten', 'Sint Maarten (Dutch part)'),
    "SY": ('Syria', 'Syrian Arab Republic'),
    "SZ": ('Eswatini', 'Kingdom of Eswatini', 'Swaziland'),
    "TC": ('the Turks and Caicos Islands', 'Turks and Caicos Islands'),
    "TD": ('Chad', 'Republic of Chad'),
    "TF": ('the French Southern Territories', 'French Southern Territories'),
    "TG": ('Togo', 'Togolese Republic'),
    "TH": ('Thailand', 'Kingdom of Thailand'),
    "TJ": ('Tajikistan', 'Republic of Tajikistan'),
    "TK": ('Tokelau',),
    "TL": ('Timor-Leste', 'Democratic Republic of Timor-Leste', 'East Timor'),
    "TM": ('Turkmenistan',),
    "TN": ('Tunisia', 'Republic of Tunisia'),
    "TO": ('Tonga', 'Kingdom of Tonga'),
    "TR": ('Türkiye', 'Republic of Türkiye', 'Turkey', 'Turkiye'),
    "TT": ('Trinidad and Tobago', 'Republic of Trinidad and Tobago', 'Trinidad & Tobago'),
    "TV": ('Tuvalu',),
    "TW": ('Taiwan', 'Taiwan, Province of China', '中国台湾', '台湾'),
    "TZ": ('Tanzania', 'Tanzania, United Republic of', 'United Republic of Tanzania'),
    "UA": ('Ukraine',),
    "UG": ('Uganda', 'Republic of Uganda'),
    "UM": ('the U.S. Minor Outlying Islands', 'U.S. Minor Outlying Islands', 'United States Minor Outlying Islands', 'US Minor Outlying Islands'),
    "US": ('the United States', 'United States', 'United States of America', 'USA'),
    "UY": ('Uruguay', 'Eastern Republic of Uruguay'),
    "UZ": ('Uzbekistan', 'Republic of Uzbekistan'),
    "VA": ('Vatican City', 'Holy See (Vatican City State)', 'Holy See', 'Vatican'),
    "VC": ('Saint Vincent and the Grenadines', 'St. Vincent and the Grenadines', 'St Vincent and the Grenadines', 'Saint Vincent & the Grenadines'),
    "VE": ('Venezuela', 'Venezuela, Bolivarian Republic of', 'Bolivarian Republic of Venezuela'),
    "VG": ('the British Virgin Islands', 'British Virgin Islands', 'Virgin Islands, British', 'Virgin Islands (British)'),
    "VI": ('the U.S. Virgin Islands', 'U.S. Virgin Islands', 'Virgin Islands, U.S.', 'Virgin Islands of the United States', 'US Virgin Islands', 'United States Virgin Islands', 'Virgin Islands (U.S.)'),
    "VN": ('Vietnam', 'Viet Nam', 'Socialist Republic of Viet Nam'),
    "VU": ('Vanuatu', 'Republic of Vanuatu'),
    "WF": ('Wallis and Futuna',),
    "WS": ('Samoa', 'Independent State of Samoa'),
    "XK": ('Kosovo',),
    "YE": ('Yemen', 'Republic of Yemen'),
    "YT": ('Mayotte',),
    "ZA": ('South Africa', 'Republic of South Africa'),
    "ZM": ('Zambia', 'Republic of Zambia'),
    "ZW": ('Zimbabwe', 'Republic of Zimbabwe'),
}

# Places whose names carry a country's name and are not that country.
NOT_COUNTRIES = ("New Jersey", "New Mexico", "Northern Ireland", "New Guinea", "Georgia Tech",
                 "Jersey City", "Turkey Point")

# A client subnet inside the country, for asking a resolver what a host answers
# there (EDNS Client Subnet): how CodeBuddy's border was measured on 2026-09-25,
# when www.codebuddy.ai answered 0.0.0.1 to the first three and an address to
# the fourth. A border measured this way can only name countries listed here.
DNS_SUBNETS = {
    "US": "73.0.0.0/24",    # Comcast
    "IN": "49.36.0.0/24",   # Reliance Jio
    "RU": "95.24.0.0/24",   # Beeline
    "DE": "85.214.0.0/24",  # Strato
}

_APOSTROPHES = str.maketrans({"\u2019": "'", "\u2018": "'", "\u02bc": "'", "\u00a0": " "})
_LATIN = "A-Za-z\u00c0-\u024f"


def country_name(code: str) -> str:
    """The name a page prints for a code: "mainland China", "Russia"."""
    return COUNTRIES[code][0]


def _pattern(name: str) -> str:
    """A name as a regex that will not match inside a longer word: a Latin
    edge must meet a non-letter, a CJK edge meets anything — "中国大陆居民"
    is one run of letters with no space to find."""
    body = re.escape(name)
    if re.match(f"[{_LATIN}]", name):
        body = f"(?<![{_LATIN}])" + body
    if re.search(f"[{_LATIN}0-9.)]$", name):
        body += f"(?![{_LATIN}])"
    return body


@lru_cache(maxsize=1)
def _matcher() -> tuple[re.Pattern[str], dict[str, str | None]]:
    owner: dict[str, str | None] = {n: None for n in NOT_COUNTRIES}
    for code, names in COUNTRIES.items():
        for n in names:
            owner.setdefault(n, code)
    ordered = sorted(owner, key=len, reverse=True)
    return re.compile("|".join(_pattern(n) for n in ordered)), owner


def codes_named(text: str) -> set[str]:
    """Every code a text names, the longest name at each place winning."""
    pattern, owner = _matcher()
    flat = " ".join(text.translate(_APOSTROPHES).split())
    found = {owner[m.group(0)] for m in pattern.finditer(flat)}
    return {c for c in found if c is not None}
