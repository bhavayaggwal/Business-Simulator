-- 003: glossary terms for the Help screen and the info boxes (from data/seed_data.py).
-- term_id gives the display order.

INSERT INTO GlossaryTerm (term, definition, example)
VALUES
    (N'Demand',
     N'The number of units customers are willing and able to buy at a given price over a period of time.',
     N'At £5, customers want 450 units this month.'),
    (N'Units sold',
     N'How many products were actually sold. It can''t be more than the stock you had.',
     N'Demand 500, stock 300 → 300 sold.'),
    (N'Revenue',
     N'All the money received from sales.',
     N'Price × units sold = £5 × 450 = £2,250.'),
    (N'Cost of goods sold (COGS)',
     N'What the products you sold cost you to buy.',
     N'450 units × £2 = £900.'),
    (N'Fixed costs',
     N'Costs that stay the same however much you sell, such as rent and wages.',
     N'£800 every month.'),
    (N'Marketing spend',
     N'Money spent advertising to increase demand. Each extra pound has a smaller effect.',
     N'£300 this month.'),
    (N'Profit / loss',
     N'Revenue minus total costs. A negative number is a loss.',
     N'£2,250 − £2,000 = £250 profit.'),
    (N'Cash balance',
     N'The money the business actually has available right now.',
     N'£4,150 at the end of the month.'),
    (N'Cash flow',
     N'Money coming in minus money going out over the month. It can differ from profit.',
     N'Profit +£250, but cash −£850.'),
    (N'Stock / inventory',
     N'Products the business holds, ready to sell.',
     N'850 units in the warehouse.');
GO
