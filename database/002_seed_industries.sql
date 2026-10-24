-- 002: the industries a student can choose from (copied from data/seed_data.py).
-- The figures are placeholders until the business teacher confirms them;
-- changing them later means a new numbered script, never editing this one.

INSERT INTO Industry (name, base_demand, reference_price, unit_cost, fixed_cost,
                      price_sensitivity, max_marketing_boost, marketing_k)
VALUES
    (N'Coffee Shop', 2000, 3.20, 0.90, 2500.00, 1.40, 0.50, 400),
    (N'Bakery', 1500, 2.50, 0.80, 2000.00, 1.30, 0.40, 300),
    (N'Clothing Shop', 300, 25.00, 10.00, 3000.00, 1.60, 0.70, 800),
    (N'Gym', 150, 35.00, 10.00, 4000.00, 1.20, 0.60, 600);
GO
