import sys, json, csv
sys.path.insert(0,"src")
from forex_bot.project_env import bootstrap_environ
from forex_bot.data.research_db import get_research_database_config
from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.domain.cross_instruments import NONUSD_CROSS_PAIRS
MAJORS=("EUR_USD","GBP_USD","USD_JPY","AUD_USD","USD_CAD","USD_CHF","NZD_USD")
def pip(inst): return 0.01 if "JPY" in inst.split("_") else 0.0001
store=PostgresCandleStore(get_research_database_config(environ=bootstrap_environ(),require=True))
rows=[]
SESS="CASE WHEN h>=22 OR h<6 THEN 'asian' WHEN h<12 THEN 'london' WHEN h<16 THEN 'overlap' ELSE 'ny' END"
with store.connection() as conn, conn.cursor() as cur:
    for inst in list(NONUSD_CROSS_PAIRS)+list(MAJORS):
        p=pip(inst)
        cur.execute(f"""SELECT COUNT(*),
            AVG((ask_c-bid_c)/{p}), percentile_cont(0.5) WITHIN GROUP (ORDER BY (ask_c-bid_c)/{p}),
            percentile_cont(0.9) WITHIN GROUP (ORDER BY (ask_c-bid_c)/{p}),
            percentile_cont(0.99) WITHIN GROUP (ORDER BY (ask_c-bid_c)/{p}),
            stddev_samp((ask_c-bid_c)/{p})
            FROM market_data.candles WHERE instrument=%s AND granularity='M1' AND bid_c IS NOT NULL AND ask_c IS NOT NULL""",(inst,))
        n,mean,med,p90,p99,sd=cur.fetchone()
        # session medians
        cur.execute(f"""SELECT s, percentile_cont(0.5) WITHIN GROUP (ORDER BY sp) FROM
            (SELECT (ask_c-bid_c)/{p} sp, {SESS.replace('h','EXTRACT(hour FROM time_utc)')} s
             FROM market_data.candles WHERE instrument=%s AND granularity='M1' AND bid_c IS NOT NULL) t
            GROUP BY s""",(inst,))
        sess={r[0]:round(float(r[1]),3) for r in cur.fetchall()}
        rows.append({"instrument":inst,"kind":"cross" if inst in NONUSD_CROSS_PAIRS else "major",
            "n":int(n),"mean_pips":round(float(mean),3),"median_pips":round(float(med),3),
            "p90_pips":round(float(p90),3),"p99_pips":round(float(p99),3),"std_pips":round(float(sd),3),
            "asian":sess.get("asian"),"london":sess.get("london"),"overlap":sess.get("overlap"),"ny":sess.get("ny")})
        print(f"{inst:9} {rows[-1]['kind']:5} med={rows[-1]['median_pips']:>6} mean={rows[-1]['mean_pips']:>6} p90={rows[-1]['p90_pips']:>6} p99={rows[-1]['p99_pips']:>7} std={rows[-1]['std_pips']:>6}")
json.dump({"diagnostic_only":True,"strategy_evidence":False,"rows":rows}, open("research/nonusd_cross_population/cost_baseline.json","w"), indent=2)
with open("research/nonusd_cross_population/cost_baseline.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("written cost_baseline.json/.csv")
