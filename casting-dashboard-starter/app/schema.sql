
CREATE DATABASE IF NOT EXISTS casting CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE casting;
CREATE TABLE IF NOT EXISTS metric_definitions (
  metric_code VARCHAR(64) PRIMARY KEY,
  description VARCHAR(255) NOT NULL,
  cell_ref VARCHAR(16) NOT NULL,
  sheet_selector VARCHAR(64) NOT NULL,
  unit VARCHAR(32) NOT NULL
);
CREATE TABLE IF NOT EXISTS fact_daily_kpi (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  report_date DATE NOT NULL,
  sheet_name VARCHAR(32) NOT NULL,
  department VARCHAR(64) NULL,
  metric_code VARCHAR(64) NOT NULL,
  metric_value DOUBLE NULL,
  source_file VARCHAR(255) NOT NULL,
  loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_kpi (report_date, sheet_name, metric_code),
  CONSTRAINT fk_metric_def FOREIGN KEY (metric_code) REFERENCES metric_definitions(metric_code)
);
INSERT IGNORE INTO metric_definitions (metric_code, description, cell_ref, sheet_selector, unit)
VALUES ('EFFICIENCY','Daily OEE/Efficiency','Z172','numeric','ratio');
