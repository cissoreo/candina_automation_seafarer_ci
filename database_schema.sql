-- =====================================================================
-- SEAFARER CV DATABASE SCHEMA v2
-- Matches the 3 Excel tables: Personal_Information, Certificate_Output, Experience_Output
-- Run this in your Supabase SQL Editor (Dashboard -> SQL Editor -> New query)
-- =====================================================================

-- Clean slate: drop old tables if they exist (safe to re-run)
DROP TABLE IF EXISTS experiences CASCADE;
DROP TABLE IF EXISTS certificates CASCADE;
DROP TABLE IF EXISTS personal_information CASCADE;

-- Drop the old v1 tables too (if anyone ran the previous schema)
DROP TABLE IF EXISTS sea_service CASCADE;
DROP TABLE IF EXISTS certifications CASCADE;
DROP TABLE IF EXISTS seafarers CASCADE;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================================
-- TABLE 1: personal_information  (main seafarer profile, 36 fields)
-- =====================================================================
CREATE TABLE personal_information (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Name fields
    name                 VARCHAR(100),    -- First name (e.g. "Anatolii")
    surname              VARCHAR(100),    -- Last name (e.g. "Babenko")
    middle_name          VARCHAR(100),
    calling_name         VARCHAR(100),    -- Nickname / preferred name
    national_full_name   VARCHAR(255),    -- Full name as it appears nationally

    -- Personal details
    date_of_birth        DATE,
    place_of_birth       VARCHAR(255),
    status               INTEGER,         -- Code from Status lookup (4=applicant, 0=seafarer, ...)
    nationality          VARCHAR(10),     -- 3-letter ISO code (UKR, MDA, PHL ...)
    citizen              INTEGER,         -- Code from citizenship_id (1=Citizen, 2=Alien, ...)
    marital_status       VARCHAR(50),
    gender               VARCHAR(20),
    number_of_children   INTEGER,

    -- Contact
    phone                VARCHAR(50),
    mobile               VARCHAR(50),
    email                VARCHAR(255),

    -- Availability
    available_from       DATE,
    available_to         DATE,
    fast_note            TEXT,
    client_date          DATE,
    check_in_note        TEXT,

    -- IDs
    personal_id          VARCHAR(100),    -- Passport-like (e.g. GL584750)
    accounting_number    VARCHAR(100),
    taxation_country     VARCHAR(10),
    taxation_id          VARCHAR(100),

    -- Philippines-specific govt IDs
    sss                  VARCHAR(50),
    philhealth           VARCHAR(50),
    pag_ibig             VARCHAR(50),

    -- Salary / contract
    minimum_salary       NUMERIC(12,2),
    salary_currency      INTEGER,         -- Code (1=USD, 2=EUR, 3=GBP, 4=BRL)
    salary_type          INTEGER,         -- Code (1=daily, 2=monthly, 3=annually)

    -- Location
    current_country      VARCHAR(10),     -- 3-letter ISO code
    current_city         VARCHAR(100),

    -- Notice
    notice_period        INTEGER,
    notice_type          INTEGER,         -- Code (1=months, 2=weeks, 3=days)

    -- Current rank
    rank                 INTEGER,         -- Code from rank_id lookup (569=DECK FITTER, ...)

    -- Metadata
    cv_source_filename   VARCHAR(500),
    created_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for fast duplicate checking
CREATE INDEX idx_pi_name_dob ON personal_information(name, surname, date_of_birth);
CREATE INDEX idx_pi_email ON personal_information(email) WHERE email IS NOT NULL;
CREATE INDEX idx_pi_personal_id ON personal_information(personal_id) WHERE personal_id IS NOT NULL;

-- =====================================================================
-- TABLE 2: certificates  (one-to-many with personal_information)
-- =====================================================================
CREATE TABLE certificates (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seafarer_id     UUID NOT NULL REFERENCES personal_information(id) ON DELETE CASCADE,

    cert_id         INTEGER,             -- Specific certificate code (within its Type category)
    type            VARCHAR(100),        -- Category name: "Travel Documents", "Training",
                                         -- "Certificate of Competency", "Endorsements",
                                         -- "Medical", "Seafarer Migration Record"
    issue_country   VARCHAR(10),         -- 3-letter ISO code
    issuer          VARCHAR(255),
    issued          DATE,
    expires         DATE,
    number          VARCHAR(100),
    notes           TEXT,
    cert_name       VARCHAR(255),        -- Optional descriptive name

    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_cert_seafarer ON certificates(seafarer_id);
CREATE INDEX idx_cert_expires ON certificates(expires);

-- =====================================================================
-- TABLE 3: experiences  (sea service history, one-to-many)
-- =====================================================================
CREATE TABLE experiences (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seafarer_id         UUID NOT NULL REFERENCES personal_information(id) ON DELETE CASCADE,

    -- Vessel info
    vessel_name         VARCHAR(255),
    flag                VARCHAR(10),     -- 3-letter ISO code
    year_built          INTEGER,
    type                INTEGER,         -- Vessel Type code (152=Bulk carrier, ...)
    imo_no              VARCHAR(20),
    ship_builder        VARCHAR(255),
    loa                 NUMERIC(10,2),   -- Length overall (meters)
    dwt                 NUMERIC(12,2),   -- Deadweight tonnage
    gt                  NUMERIC(12,2),   -- Gross tonnage

    -- Equipment codes
    pumping_system      INTEGER,         -- Vessel Pump code
    cargo_handling_gear INTEGER,         -- Vessel Gear code
    engine_type         INTEGER,         -- Engine Type code (3=MAN, 5=Wartsila, ...)
    engine_model        VARCHAR(100),
    engine_power        NUMERIC(12,2),   -- in HP or kW

    dp_type             INTEGER,         -- DP Type code
    dp_manufacturer     INTEGER,         -- DP Manufacturer code
    operation_type      INTEGER,         -- Operation Type code

    -- Service details
    location_port       VARCHAR(255),
    location_country    VARCHAR(10),
    rank                INTEGER,         -- Rank code held on this vessel
    sign_on             DATE,
    sign_off            DATE,
    off_reason          INTEGER,         -- Reason code

    -- Company info
    owner_employer      VARCHAR(255),
    crewing_company     VARCHAR(255),

    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_exp_seafarer ON experiences(seafarer_id);
CREATE INDEX idx_exp_dates ON experiences(sign_on, sign_off);

-- =====================================================================
-- TRIGGER: auto-update updated_at on personal_information
-- =====================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_pi_updated_at ON personal_information;
CREATE TRIGGER update_pi_updated_at
    BEFORE UPDATE ON personal_information
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================================
-- Done!  You should now see 3 tables:
--   - personal_information  (main profile)
--   - certificates          (multiple per seafarer)
--   - experiences           (multiple per seafarer)
-- =====================================================================
