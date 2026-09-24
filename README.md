
# ManchemTrade POC v0.1
## Quick Start
cd manchemtrade_poc
docker-compose up --build
API: http://localhost:8000/docs
Health: http://localhost:8000/health

Mock mode if no TRADIER keys - returns fake positions/fills.

## Test
curl -X POST http://localhost:8000/api/v1/webhook/test_user/wh_secret123 -H "Content-Type: application/json" -d '{"secret":"wh_secret123","action":"BUY_CALL","ticker":"SPX","occ_symbol":"SPX 260923C05850000","quantity":1,"alert_id":"test_123"}'
curl -X POST "http://localhost:8000/api/quicktrade/execute?underlying=SPX&leg1_strike=5850&leg2_strike=5860&qty=1"
curl http://localhost:8000/api/positions
