# GTA VI Twitch CCU Forecaster

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/irgore/gta6-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/irgore/gta6-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Comparable-calibrated trajectory model for forecasting GTA VI's launch-day Twitch viewer counts hour by hour. Built for [make.fun](https://make.fun/bounty/gta6-twitch-ccu-forecast-01)'s "Forecast GTA VI's launch-day Twitch viewers hour by hour" bounty ($250 in USDC).

**Strategy**: Uses 42 comparable game launches to build a weighted trajectory shape, calibrates quantile spreads from empirical log-MAD with outlier trimming, and fills sparse hours by interpolation. Beats the house persistence baseline by capturing the day's ramp-up → peak → decline pattern.

## Run

```bash
python3 main.py
```

Reads `/input/*.in` JSON cases, writes `/output/*.out` forecasts. Set `MAKEFUN_INPUT_DIR` and `MAKEFUN_OUTPUT_DIR` for local testing.