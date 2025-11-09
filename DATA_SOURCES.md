# DATA_SOURCES - SS91-V3
Cada entrada: Factor | Descripción | Fuente/API | Tipo de dato | Función (fetch_...)

1. close — Close price EUR/USD — yfinance / ALPHA_VANTAGE — numeric — fetch_price
2. volume — Volume EUR/USD — yfinance — numeric — fetch_price
3. atr_14 — ATR(14) — pandas_ta — numeric — fetch_technical
4. atr_ma_20 — ATR MA(20) — pandas_ta — numeric — fetch_technical
5. sentimiento_twitter — Sentimiento en Twitter para EURUSD — snscrape + NLPCLOUD — sentiment (-1..1 mapped 0..1) — fetch_twitter_sentiment
6. sentimiento_reddit — Sentimiento en Reddit sobre EURUSD — Reddit API + NLPCLOUD — sentiment — fetch_reddit_sentiment
7. flujo_capital_minorista — Ratio long/short retail (proxy) — SERPAPI / Broker API (if available) — numeric — fetch_retail_flow
8. pico_google_trends_crisis — Google Trends spike (crisis keywords) — pytrends — numeric (0..100 -> 0..1) — fetch_google_trends
9. vistas_wikipedia_euro — Pageviews article "Euro" — Wikimedia REST — numeric — fetch_wikipedia_views
10. volumen_comentarios_noticias — Count comments on top related news — NEWSAPI + scraping — count normalized — fetch_news_comments
11. correlacion_crypto_btc — Rolling corr(EURUSD,BTC) — yfinance — numeric (-1..1 -> 0..1) — fetch_corr_btc
12. ranking_apps_trading — App ranking proxy (search via SERPAPI) — SERPAPI — numeric — fetch_app_ranking
13. spread_bid_ask — Spread proxy (OANDA or AlphaVantage intraday) — ALPHA_VANTAGE or OANDA — numeric — fetch_spread
14. volumen_pares_exoticos — Aggregated adv volume exotic pairs — CCXT / AlphaVantage — numeric — fetch_exotics_volume
15. deuda_tarjeta_consumidor — Consumer credit index — FRED API — numeric — fetch_fred('consumer_credit_series')
16. costo_publicidad_financiera — Proxy Google Ads interest or SERP CPI — SERPAPI / pytrends — numeric — fetch_ad_cost_proxy
17. noticia_ciberataque_bolsa — Count of news about cyberattacks — NEWSAPI — binary/count — fetch_news_flag("cyberattack")
18. noticia_escandalo_politico — News count political scandal — NEWSAPI — binary/count — fetch_news_flag("political scandal")
19. resultado_eleccion_regional — Binary / event flag (news) — NEWSAPI — binary — fetch_event_flag("election result")
20. anuncio_huelga_publica — News flag for strikes — NEWSAPI — binary — fetch_event_flag("strike")
21. actividad_red_social_bancos — Activity about banks on social media — snscrape/Reddit — numeric — fetch_banks_activity
22. volumen_pasajeros_aerolineas — Public traffic index or proxy — SERPAPI / Open Data — numeric — fetch_air_traffic_proxy
23. ventas_bienes_lujo — Auction house summaries or SERPAPI — SERPAPI — numeric — fetch_luxury_sales_proxy
24. indice_congestion_puertos — Freight proxy / BDI (if available) — SERPAPI or public index — numeric — fetch_freight_index
25. confianza_ceo_no_financiero — Survey proxy / news sentiment — SERPAPI/NEWSAPI — numeric — fetch_ceo_confidence
26. tasa_registro_patentes — CrossRef/WIPO counts — CrossRef API (via SERPAPI) — numeric — fetch_patent_rate
27. consumo_electricidad_ind — Open data (ENTSO-E / FRED) — numeric — fetch_electricity_consumption
28. uso_transporte_publico — Google mobility or city open data — SERPAPI / mobility — numeric — fetch_mobility_proxy
29. cambio_politica_visado — News flag — NEWSAPI — binary — fetch_event_flag("visa policy")
30. aprobacion_ministro_economia — Polls scraped via SERPAPI — SERPAPI — numeric — fetch_poll_approval
31. precio_flete_maritimo — Baltic Dry Index proxy — SERPAPI or public BDI feed — numeric — fetch_bdi
32. donaciones_caridad_nacional — NGO public data / SERPAPI — numeric — fetch_charity_donations_proxy
33. informes_moral_empleados_bancos — Glassdoor proxy via SERPAPI — SERPAPI — numeric — fetch_glassdoor_proxy
34. imagenes_satelitales_parking — Proxy via SERPAPI or paid API — SERPAPI (if not available -> 0) — numeric — fetch_parking_sat_proxy
35. cambio_tasas_universidad — Education fees feed (scrape) — SERPAPI — numeric — fetch_university_fee_change
36. trafico_web_inmobiliarias — SERPAPI / SimilarWeb proxy — SERPAPI — numeric — fetch_realestate_traffic
37. resultado_subastas_arte — Auction result counts — SERPAPI — numeric — fetch_auction_results
38. tasa_apertura_pymes — Business registers (open data) — SERPAPI / national stats — numeric — fetch_new_business_rate
39. volumen_papers_academicos — CrossRef counts by topic — CrossRef API — numeric — fetch_papers_count
40. klinger_oscillator — pandas_ta — numeric — fetch_technical
41. aroon_oscillator — pandas_ta — numeric — fetch_technical
42. vortex_indicator — pandas_ta — numeric — fetch_technical
43. coppock_curve — pandas_ta — numeric — fetch_technical
44. dpo_oscillator — pandas_ta — numeric — fetch_technical
45. kst_oscillator — pandas_ta — numeric — fetch_technical

--- 

Cada `fetch_...()` corresponde a una función en `ss91_v3/data_pipeline.py`. Los factores de noticias/eventos usan `NEWSAPI` + `SERPAPI` y se normalizan a 0..1. Los técnicos se calculan localmente con `pandas_ta`.
