Chuẩn, đây là bộ `CREATE VIEW` tối ưu để bạn paste trực tiếp vào **Supabase SQL Editor**.  
Mục tiêu: luôn thấy `coin_name/symbol` khi đọc dữ liệu, nhưng vẫn giữ schema chuẩn hoá.

```sql
-- Optional: gom vào schema analytics để dễ quản lý
create schema if not exists analytics;

-- 1) Market snapshots + coin metadata
create or replace view analytics.vw_market_snapshots_with_coin as
select
  ms.id,
  ms.coin_id,
  c.coingecko_id,
  c.symbol,
  c.name as coin_name,
  c.market_cap_rank,
  ms.price_usd,
  ms.market_cap,
  ms.volume_24h,
  ms.percent_change_1h,
  ms.percent_change_24h,
  ms.percent_change_7d,
  ms.timestamp
from market_snapshots ms
join coins c on c.id = ms.coin_id;

-- 2) OHLCV candles + coin metadata
create or replace view analytics.vw_ohlcv_candles_with_coin as
select
  o.id,
  o.coin_id,
  c.coingecko_id,
  c.symbol,
  c.name as coin_name,
  c.market_cap_rank,
  o.timeframe,
  o.open_price,
  o.high_price,
  o.low_price,
  o.close_price,
  o.volume,
  o.timestamp
from ohlcv_candles o
join coins c on c.id = o.coin_id;

-- 3) Feature metrics + coin metadata
create or replace view analytics.vw_feature_metrics_with_coin as
select
  f.id,
  f.coin_id,
  c.coingecko_id,
  c.symbol,
  c.name as coin_name,
  c.market_cap_rank,
  f.window,
  f.volatility,
  f.drawdown,
  f.avg_return,
  f.computed_at
from feature_metrics f
join coins c on c.id = f.coin_id;

-- 4) Risk metrics + coin metadata
create or replace view analytics.vw_risk_metrics_with_coin as
select
  r.id,
  r.coin_id,
  c.coingecko_id,
  c.symbol,
  c.name as coin_name,
  c.market_cap_rank,
  r.risk_score,
  r.risk_level,
  r.model_version,
  r.config_hash,
  r.computed_at
from risk_metrics r
join coins c on c.id = r.coin_id;

-- 5) Latest risk per coin (rất hữu ích cho dashboard)
create or replace view analytics.vw_latest_risk_per_coin as
with ranked as (
  select
    r.*,
    row_number() over (partition by r.coin_id order by r.computed_at desc) as rn
  from risk_metrics r
)
select
  ranked.id,
  ranked.coin_id,
  c.coingecko_id,
  c.symbol,
  c.name as coin_name,
  c.market_cap_rank,
  ranked.risk_score,
  ranked.risk_level,
  ranked.model_version,
  ranked.config_hash,
  ranked.computed_at
from ranked
join coins c on c.id = ranked.coin_id
where ranked.rn = 1;

-- 6) Latest market snapshot per coin
create or replace view analytics.vw_latest_market_snapshot_per_coin as
with ranked as (
  select
    ms.*,
    row_number() over (partition by ms.coin_id order by ms.timestamp desc) as rn
  from market_snapshots ms
)
select
  ranked.id,
  ranked.coin_id,
  c.coingecko_id,
  c.symbol,
  c.name as coin_name,
  c.market_cap_rank,
  ranked.price_usd,
  ranked.market_cap,
  ranked.volume_24h,
  ranked.percent_change_1h,
  ranked.percent_change_24h,
  ranked.percent_change_7d,
  ranked.timestamp
from ranked
join coins c on c.id = ranked.coin_id
where ranked.rn = 1;

-- 7) Coin monitor board (latest snapshot + latest risk trên cùng 1 dòng)
create or replace view analytics.vw_coin_monitor as
select
  m.coin_id,
  m.coingecko_id,
  m.symbol,
  m.coin_name,
  m.market_cap_rank,
  m.price_usd,
  m.market_cap,
  m.volume_24h,
  m.percent_change_24h,
  m.timestamp as market_timestamp,
  r.risk_score,
  r.risk_level,
  r.model_version,
  r.config_hash,
  r.computed_at as risk_computed_at
from analytics.vw_latest_market_snapshot_per_coin m
left join analytics.vw_latest_risk_per_coin r on r.coin_id = m.coin_id;
```

## Gợi ý quyền truy cập (nếu bật RLS)
Nếu bạn muốn client Supabase đọc trực tiếp các view này:

```sql
grant usage on schema analytics to anon, authenticated;
grant select on all tables in schema analytics to anon, authenticated;
alter default privileges in schema analytics grant select on tables to anon, authenticated;
```

## 3 query kiểm tra nhanh
```sql
select * from analytics.vw_coin_monitor order by market_cap_rank asc limit 20;
select * from analytics.vw_latest_risk_per_coin order by risk_score desc limit 20;
select * from analytics.vw_latest_market_snapshot_per_coin where symbol = 'btc';
```

Nếu muốn, mình sẽ đưa thêm phiên bản **materialized view** cho dashboard nặng (nhanh hơn khi dữ liệu lớn).