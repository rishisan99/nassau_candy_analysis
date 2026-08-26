POSITIVE = "#27AE60"
NEGATIVE = "#E74C3C"
NEUTRAL  = "#2980B9"

COLORS = {
    'primary'  : '#2C3E50',
    'profit'   : '#27AE60',
    'revenue'  : '#2980B9',
    'cost'     : '#E74C3C',
    'warning'  : '#F39C12',
    'highlight': '#8E44AD'
}

DIVISION_COLORS = {
    'Chocolate': '#27AE60',
    'Sugar'    : '#2980B9',
    'Other'    : '#F39C12'
}

REGION_COLORS = {
    'Pacific' : '#2980B9',
    'Atlantic': '#27AE60',
    'Interior': '#F39C12',
    'Gulf'    : '#8E44AD'
}

FACTORY_COLORS = {
    "Lot's O' Nuts"    : '#27AE60',
    "Wicked Choccy's"  : '#2980B9',
    "Sugar Shack"      : '#F39C12',
    "Secret Factory"   : '#8E44AD',
    "The Other Factory": '#E74C3C'
}

# matplotlib's default font can't render emoji glyphs (shows as tofu boxes
# in legends), so quadrant labels here are plain text
QUADRANT_COLORS = {
    'STAR'        : '#27AE60',
    'HIDDEN GEM'  : '#2980B9',
    'VOLUME TRAP' : '#F39C12',
    'DEAD WEIGHT' : '#E74C3C'
}

QUADRANT_EMOJI = {
    'STAR'       : '⭐',
    'HIDDEN GEM' : '💎',
    'VOLUME TRAP': '⚠️',
    'DEAD WEIGHT': '❌'
}

# products with avg margin below this are flagged as at-risk — well below
# the ~66% company average, roughly the point where a product is barely
# more profitable than it is costly to make
AT_RISK_MARGIN_THRESHOLD = 40

# a month is flagged as an anomaly when revenue drops this much or more
# vs the prior month — catches real drops (e.g. Oct after a Sep spike)
# without flagging every normal seasonal swing
REVENUE_DROP_THRESHOLD = 20