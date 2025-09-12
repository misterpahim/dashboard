CREATE TABLE IF NOT EXISTS kpi_facts (
  report_date DATE NOT NULL,
  metric_code VARCHAR(64) NOT NULL,
  metric_value DOUBLE,
  PRIMARY KEY (report_date, metric_code)
);

CREATE OR REPLACE VIEW v_daily_oee AS
SELECT
  MAX(CASE WHEN metric_code='DIE_DOWN_MIN'  THEN metric_value END) AS die_down_min,
  MAX(CASE WHEN metric_code='MACH_DOWN_MIN' THEN metric_value END) AS mach_down_min,
  MAX(CASE WHEN metric_code='ENG_DOWN_MIN'  THEN metric_value END) AS eng_down_min,
  MAX(CASE WHEN metric_code='PROD_DOWN_MIN' THEN metric_value END) AS prod_down_min,
  MAX(CASE WHEN metric_code='OTH_DOWN_MIN'  THEN metric_value END) AS oth_down_min,
  MAX(CASE WHEN metric_code='OEE_PCT'       THEN metric_value END) AS oee_pct,
  report_date
FROM kpi_facts
GROUP BY report_date;
