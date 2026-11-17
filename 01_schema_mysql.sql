-- Core banking schema (MySQL 8). Run once:  mysql -u root -p < sql/01_schema_mysql.sql
CREATE DATABASE IF NOT EXISTS bank_db;
USE bank_db;

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id  VARCHAR(20)  PRIMARY KEY,
    first_name   VARCHAR(60),
    last_name    VARCHAR(60),
    email        VARCHAR(120),
    city         VARCHAR(80),
    credit_score INT,
    created_at   DATE
);

CREATE TABLE accounts (
    account_id   VARCHAR(20)  PRIMARY KEY,
    customer_id  VARCHAR(20)  NOT NULL,
    account_type VARCHAR(20),
    balance_usd  DECIMAL(14,2),
    open_date    DATE,
    CONSTRAINT fk_acc_cust FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE transactions (
    transaction_id   VARCHAR(20)  PRIMARY KEY,
    account_id       VARCHAR(20)  NOT NULL,
    merchant_id      VARCHAR(20),
    amount_usd       DECIMAL(12,2),
    transaction_date DATETIME,          -- original Kaggle timestamp (uniformly random, kept for reference)
    live_ts          DATETIME,          -- reshaped timestamp used for the live-load simulation
    CONSTRAINT fk_txn_acc FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    INDEX idx_live_ts (live_ts)
);

-- Pipeline output table (written by Python)
CREATE TABLE IF NOT EXISTS Clean_Infrastructure_Logs (
    log_ts        DATETIME,
    policy        VARCHAR(30),
    tx_per_min    INT,
    cpu_4core_eq  DOUBLE,
    forecast_cpu  DOUBLE,
    active_cores  INT,
    cpu_actual    DOUBLE,
    health_pct    DOUBLE,
    scale_action  VARCHAR(20),
    INDEX idx_log_ts (log_ts)
);
