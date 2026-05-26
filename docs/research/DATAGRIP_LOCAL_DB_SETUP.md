# DataGrip Local Research DB Setup

DataGrip is the UI only. The actual scripts use `FOREX_BOT_RESEARCH_DATABASE_URL`.

## Expected Local Layout

- Data source: `local`
- Database: `forex_bot`
- Preferred schema: `market_data`

## Environment Variable

Use a normal PostgreSQL URL locally:

```bash
FOREX_BOT_RESEARCH_DATABASE_URL=postgresql://localhost:5432/forex_bot
```

If your local Postgres requires auth, use your local username/password in the URL, but never commit it and never commit `.env`.

## Create / Verify the Schema

```bash
python scripts/preflight_research_db.py --create-schema
```

After that, refresh DataGrip.

If DataGrip says "No schemas selected", right-click `forex_bot` and show/select `market_data` or `public`.

## Verify Tables in DataGrip

```sql
SELECT COUNT(*) FROM market_data.candles;

SELECT instrument, granularity, COUNT(*)
FROM market_data.candles
GROUP BY 1,2
ORDER BY 1,2;
```

## Safety Notes

- Never commit `.env`
- Never commit real credentials
- DataGrip config files are not part of the app contract
