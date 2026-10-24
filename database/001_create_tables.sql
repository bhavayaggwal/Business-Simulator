-- 001: create the tables (PRD §5, docs/DATABASE.md).
-- Run by setup_db.py, which records it in SchemaVersion so it never runs twice.
-- Never edit this file once it has run: make a new numbered script instead.

CREATE TABLE UserProfile (
    user_id     INT IDENTITY(1,1) NOT NULL,
    username    NVARCHAR(30)      NOT NULL,
    created_at  DATETIME2         NOT NULL CONSTRAINT DF_UserProfile_created DEFAULT SYSDATETIME(),
    CONSTRAINT PK_UserProfile PRIMARY KEY (user_id),
    CONSTRAINT UQ_UserProfile_username UNIQUE (username)
);
GO

CREATE TABLE Industry (
    industry_id          INT IDENTITY(1,1) NOT NULL,
    name                 NVARCHAR(50)      NOT NULL,
    base_demand          INT               NOT NULL,
    reference_price      DECIMAL(10,2)     NOT NULL,
    unit_cost            DECIMAL(10,2)     NOT NULL,
    fixed_cost           DECIMAL(10,2)     NOT NULL,
    price_sensitivity    DECIMAL(4,2)      NOT NULL,
    max_marketing_boost  DECIMAL(4,2)      NOT NULL,
    marketing_k          DECIMAL(10,2)     NOT NULL,
    CONSTRAINT PK_Industry PRIMARY KEY (industry_id),
    CONSTRAINT UQ_Industry_name UNIQUE (name),
    CONSTRAINT CK_Industry_values CHECK (base_demand > 0 AND reference_price > 0
        AND unit_cost > 0 AND fixed_cost >= 0 AND price_sensitivity > 0
        AND max_marketing_boost >= 0 AND marketing_k > 0)
);
GO

CREATE TABLE Business (
    business_id        INT IDENTITY(1,1) NOT NULL,
    user_id            INT               NOT NULL,
    industry_id        INT               NOT NULL,
    name               NVARCHAR(60)      NOT NULL,
    starting_capital   DECIMAL(12,2)     NOT NULL,
    -- Copied from the industry when the business is created; the user may edit them.
    base_demand        INT               NOT NULL,
    reference_price    DECIMAL(10,2)     NOT NULL,
    unit_cost          DECIMAL(10,2)     NOT NULL,
    fixed_cost         DECIMAL(10,2)     NOT NULL,
    price_sensitivity  DECIMAL(4,2)      NOT NULL,
    -- Current position, updated after every simulated month.
    price              DECIMAL(10,2)     NOT NULL,
    marketing_budget   DECIMAL(10,2)     NOT NULL,
    current_month      INT               NOT NULL CONSTRAINT DF_Business_month DEFAULT 0,
    cash               DECIMAL(12,2)     NOT NULL,
    stock              INT               NOT NULL,
    created_at         DATETIME2         NOT NULL CONSTRAINT DF_Business_created DEFAULT SYSDATETIME(),
    CONSTRAINT PK_Business PRIMARY KEY (business_id),
    CONSTRAINT FK_Business_User FOREIGN KEY (user_id) REFERENCES UserProfile (user_id),
    CONSTRAINT FK_Business_Industry FOREIGN KEY (industry_id) REFERENCES Industry (industry_id),
    -- Business names only need to be unique within one profile.
    CONSTRAINT UQ_Business_user_name UNIQUE (user_id, name),
    CONSTRAINT CK_Business_values CHECK (starting_capital > 0 AND base_demand > 0
        AND reference_price > 0 AND unit_cost > 0 AND fixed_cost >= 0
        AND price_sensitivity > 0 AND price > 0 AND marketing_budget >= 0
        AND current_month >= 0 AND stock >= 0)
);
GO

CREATE TABLE MonthlyResult (
    result_id            INT IDENTITY(1,1) NOT NULL,
    business_id          INT               NOT NULL,
    month_no             INT               NOT NULL,
    price                DECIMAL(10,2)     NOT NULL,
    marketing_spend      DECIMAL(10,2)     NOT NULL,
    units_purchased      INT               NOT NULL,
    stock_purchase_cost  DECIMAL(10,2)     NOT NULL,
    market_factor        DECIMAL(4,3)      NOT NULL,
    demand               INT               NOT NULL,
    units_sold           INT               NOT NULL,
    opening_stock        INT               NOT NULL,
    closing_stock        INT               NOT NULL,
    revenue              DECIMAL(12,2)     NOT NULL,
    cogs                 DECIMAL(12,2)     NOT NULL,
    fixed_cost           DECIMAL(12,2)     NOT NULL,
    total_costs          DECIMAL(12,2)     NOT NULL,
    profit               DECIMAL(12,2)     NOT NULL,
    opening_cash         DECIMAL(12,2)     NOT NULL,
    closing_cash         DECIMAL(12,2)     NOT NULL,
    CONSTRAINT PK_MonthlyResult PRIMARY KEY (result_id),
    CONSTRAINT FK_MonthlyResult_Business FOREIGN KEY (business_id)
        REFERENCES Business (business_id),
    -- One row per month per business.
    CONSTRAINT UQ_MonthlyResult_month UNIQUE (business_id, month_no),
    CONSTRAINT CK_MonthlyResult_values CHECK (month_no >= 1 AND units_purchased >= 0
        AND market_factor BETWEEN 0.900 AND 1.100 AND demand >= 0
        AND units_sold >= 0 AND units_sold <= opening_stock + units_purchased
        AND opening_stock >= 0 AND closing_stock >= 0)
);
GO

CREATE TABLE GlossaryTerm (
    term_id     INT IDENTITY(1,1) NOT NULL,
    term        NVARCHAR(50)      NOT NULL,
    definition  NVARCHAR(200)     NOT NULL,
    example     NVARCHAR(200)     NULL,
    CONSTRAINT PK_GlossaryTerm PRIMARY KEY (term_id),
    CONSTRAINT UQ_GlossaryTerm_term UNIQUE (term)
);
GO
