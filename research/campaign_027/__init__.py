"""CAMPAIGN_027 — filtered H4 z-score reversion train/validation evidence package.

Import-isolated research code: depends only on ``forex_bot`` (the frozen strategy
decision + financing) and ``research.edge_discovery`` (cost / matched-null /
filter-ablation lab). No broker / executor / loop / approval import. Produces the
campaign's own edge-discovery-compatible ledgers for the train/validation sprint.
Nothing here approves a strategy or opens the test lockbox.
"""
