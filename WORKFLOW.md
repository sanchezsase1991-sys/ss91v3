# WORKFLOW SS91-V3

Daily Routine:
- 10:00 Collector: collect 45 factors -> insert into `ss91_factors` (snapshot_time="10:00")
- 12:00 Decitor: read snapshot for today -> fetch latest prices/ATR -> core.decide() -> insert `ss91_decisions` -> ntfy
- Logging: both scripts log into Supabase `ss91_logs` and local files.

Manual run:
- python collector.py
- python decitor.py
