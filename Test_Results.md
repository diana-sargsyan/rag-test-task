# Test Results — gpt-4o-mini

**Date:** 2026-02-27 17:46
**Execution Accuracy:** 100.0%

| # | Question | Status | Generated SQL |
|---|----------|--------|--------------|
| 1 | List all clients with their industries. | ✅ | `SELECT client_name, industry FROM clients;` |
| 2 | Which clients are based in the UK? | ✅ | `SELECT client_name FROM clients WHERE country = 'UK';` |
| 3 | List all invoices issued in March 2024 with their statuses. | ✅ | `SELECT invoice_id, invoice_date, due_date, status FROM invoices WHERE invoice_date BETWEEN '2024-03-01' AND '2024-03-31';` |
| 4 | Which invoices are currently marked as 'Overdue'? | ✅ | `SELECT invoice_id, client_id, invoice_date, due_date, status FROM invoices WHERE status = 'Overdue'` |
| 5 | For each service_name in InvoiceLineItems, how many line items are there? | ✅ | `SELECT service_name, COUNT(*) as line_item_count FROM invoice_line_items GROUP BY service_name;` |
| 6 | List all invoices for Acme Corp with their invoice IDs, invoice dates, due dates, and statuses. | ✅ | `SELECT i.invoice_id, i.invoice_date, i.due_date, i.status FROM invoices i JOIN clients c ON i.client_id = c.client_id WHERE c.client_name = 'Acme Corp'` |
| 7 | Show all invoices issued to Bright Legal in February 2024, including their status and currency. | ✅ | `SELECT i.invoice_id, i.invoice_date, i.due_date, i.status, i.currency FROM invoices i JOIN clients c ON i.client_id = c.client_id WHERE c.client_name = 'Bright Legal' AND i.invoice_date BETWEEN '2024-02-01' AND '2024-02-29';` |
| 8 | For invoice I1001, list all line items with service name, quantity, unit price, tax rate, and compute the line total (including tax) for each. | ✅ | `SELECT service_name, quantity, unit_price, tax_rate, (quantity * unit_price * (1 + tax_rate)) as line_total FROM invoice_line_items WHERE invoice_id = 'I1001';` |
| 9 | For each client, compute the total amount billed in 2024 (including tax) across all their invoices. | ✅ | `SELECT c.client_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_billed FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY c.client_name;` |
| 10 | Which client has the highest total billed amount in 2024, and what is that total? | ✅ | `SELECT c.client_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_billed FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY c.client_name ORDER BY total_billed DESC LIMIT 1;` |
| 11 | Across all clients, which three services generated the most revenue in 2024? Show the total revenue per service. | ✅ | `SELECT ili.service_name, SUM(ili.quantity * ili.unit_price) as total_revenue  FROM invoice_line_items ili  JOIN invoices i ON ili.invoice_id = i.invoice_id  WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31'  GROUP BY ili.service_name  ORDER BY total_revenue DESC  LIMIT 3;` |
| 12 | Which invoices are overdue as of 2024-12-31? List invoice ID, client name, invoice_date, due_date, and status. | ✅ | `SELECT i.invoice_id, c.client_name, i.invoice_date, i.due_date, i.status FROM invoices i JOIN clients c ON i.client_id = c.client_id WHERE i.due_date < '2024-12-31' AND i.status = 'Overdue'` |
| 13 | Group revenue by client country: for each country, compute the total billed amount in 2024 (including tax). | ✅ | `SELECT c.country, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_billed FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY c.country;` |
| 14 | For the service 'Contract Review', list all clients who purchased it and the total amount they paid for that service (including tax). | ✅ | `SELECT c.client_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_paid FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE ili.service_name = 'Contract Review' GROUP BY c.client_name` |
| 15 | Considering only European clients, what are the top 3 services by total revenue (including tax) in H2 2024 (2024-07-01 to 2024-12-31)? | ✅ | `SELECT ili.service_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_revenue FROM invoice_line_items ili JOIN invoices i ON ili.invoice_id = i.invoice_id JOIN clients c ON i.client_id = c.client_id WHERE i.invoice_date BETWEEN '2024-07-01' AND '2024-12-31' AND c.client_id IN ('C002', 'C004', 'C008', 'C010', 'C013', 'C015', 'C019') GROUP BY ili.service_name ORDER BY total_revenue DESC LIMIT 3;` |

## Detailed Results

### 1. List all clients with their industries.

**Status:** ✅ Correct (exact)

**Reference SQL:**
```sql
SELECT client_name, industry FROM clients;
```

**Generated SQL:**
```sql
SELECT client_name, industry FROM clients;
```

**Answer:** Here is the list of all clients along with their respective industries:

1. Acme Corp - Manufacturing
2. Bright Legal - Legal
3. Summit Finance - Financial Services
4. GreenField Retail - Retail
5. Northwind Logistics - Logistics
6. BlueSky Consulting - Consulting
7. Nova Health - Healthcare
8. Urban Tech - Technology
9. RedRock Energy - Energy
10. Silverline Media - Media
11. Zenith Education - Education
12. Alpine Hospitality - Hospitality
13. Orion Security - Security
14. Pacific Foods - Food

---

### 2. Which clients are based in the UK?

**Status:** ✅ Correct (exact)

**Reference SQL:**
```sql
SELECT client_name FROM clients WHERE country = 'UK';
```

**Generated SQL:**
```sql
SELECT client_name FROM clients WHERE country = 'UK';
```

**Answer:** The clients based in the UK are:

1. Bright Legal
2. Silverline Media

---

### 3. List all invoices issued in March 2024 with their statuses.

**Status:** ✅ Correct (superset_cols)

**Reference SQL:**
```sql
SELECT invoice_id, status FROM invoices WHERE invoice_date BETWEEN '2024-03-01' AND '2024-03-31';
```

**Generated SQL:**
```sql
SELECT invoice_id, invoice_date, due_date, status FROM invoices WHERE invoice_date BETWEEN '2024-03-01' AND '2024-03-31';
```

**Answer:** In March 2024, there were two invoices issued:

1. **Invoice ID:** I1003
   - **Invoice Date:** 2024-03-05
   - **Due Date:** 2024-04-05
   - **Status:** Paid

2. **Invoice ID:** I1004
   - **Invoice Date:** 2024-03-20
   - **Due Date:** 2024-04-20
   - **Status:** Paid

---

### 4. Which invoices are currently marked as 'Overdue'?

**Status:** ✅ Correct (superset_cols)

**Reference SQL:**
```sql
SELECT invoice_id FROM invoices WHERE status = 'Overdue';
```

**Generated SQL:**
```sql
SELECT invoice_id, client_id, invoice_date, due_date, status FROM invoices WHERE status = 'Overdue'
```

**Answer:** There are currently 9 invoices marked as 'Overdue'. Here are the details:

1. **Invoice ID:** I1002
   - **Client ID:** C002
   - **Invoice Date:** 2024-02-15
   - **Due Date:** 2024-03-15

2. **Invoice ID:** I1005
   - **Client ID:** C004
   - **Invoice Date:** 2024-04-01
   - **Due Date:** 2024-05-01

3. **Invoice ID:** I1009
   - **Client ID:** C008
   - **Invoice Date:** 2024-06-01
   - **Due Date:** 2024-07-01

4. **Invoice ID:** I1013
   - **Client ID:** C012
   - **Invoice Date:** 2024-07

---

### 5. For each service_name in InvoiceLineItems, how many line items are there?

**Status:** ✅ Correct (exact)

**Reference SQL:**
```sql
SELECT service_name, COUNT(*) as count FROM invoice_line_items GROUP BY service_name;
```

**Generated SQL:**
```sql
SELECT service_name, COUNT(*) as line_item_count FROM invoice_line_items GROUP BY service_name;
```

**Answer:** Here is the count of line items for each service in the Invoice Line Items:

- **Contract Review**: 11 line items
- **Court Appearance**: 13 line items
- **Custom Reporting**: 11 line items
- **IT Security Assessment**: 14 line items
- **M&A Advisory**: 16 line items
- **Regulatory Compliance Audit**: 10 line items
- **Tax Planning**: 14 line items
- **Training Session**: 7 line items

---

### 6. List all invoices for Acme Corp with their invoice IDs, invoice dates, due dates, and statuses.

**Status:** ✅ Correct (exact)

**Reference SQL:**
```sql
SELECT i.invoice_id, i.invoice_date, i.due_date, i.status FROM invoices i JOIN clients c ON i.client_id = c.client_id WHERE c.client_name = 'Acme Corp';
```

**Generated SQL:**
```sql
SELECT i.invoice_id, i.invoice_date, i.due_date, i.status FROM invoices i JOIN clients c ON i.client_id = c.client_id WHERE c.client_name = 'Acme Corp'
```

**Answer:** Here are all the invoices for Acme Corp:

1. **Invoice ID:** I1001
   - **Invoice Date:** 2024-01-10
   - **Due Date:** 2024-02-10
   - **Status:** Paid

2. **Invoice ID:** I1004
   - **Invoice Date:** 2024-03-20
   - **Due Date:** 2024-04-20
   - **Status:** Paid

3. **Invoice ID:** I1022
   - **Invoice Date:** 2024-10-15
   - **Due Date:** 2024-11-14
   - **Status:** Paid

---

### 7. Show all invoices issued to Bright Legal in February 2024, including their status and currency.

**Status:** ✅ Correct (superset_cols)

**Reference SQL:**
```sql
SELECT i.invoice_id, i.status, i.currency FROM invoices i JOIN clients c ON i.client_id = c.client_id WHERE c.client_name = 'Bright Legal' AND i.invoice_date BETWEEN '2024-02-01' AND '2024-02-29';
```

**Generated SQL:**
```sql
SELECT i.invoice_id, i.invoice_date, i.due_date, i.status, i.currency FROM invoices i JOIN clients c ON i.client_id = c.client_id WHERE c.client_name = 'Bright Legal' AND i.invoice_date BETWEEN '2024-02-01' AND '2024-02-29';
```

**Answer:** In February 2024, there was one invoice issued to Bright Legal:

- **Invoice ID**: I1002
- **Invoice Date**: 2024-02-15
- **Due Date**: 2024-03-15
- **Status**: Overdue
- **Currency**: EUR

---

### 8. For invoice I1001, list all line items with service name, quantity, unit price, tax rate, and compute the line total (including tax) for each.

**Status:** ✅ Correct (exact)

**Reference SQL:**
```sql
SELECT service_name, quantity, unit_price, tax_rate, (quantity * unit_price * (1 + tax_rate)) as line_total FROM invoice_line_items WHERE invoice_id = 'I1001';
```

**Generated SQL:**
```sql
SELECT service_name, quantity, unit_price, tax_rate, (quantity * unit_price * (1 + tax_rate)) as line_total FROM invoice_line_items WHERE invoice_id = 'I1001';
```

**Answer:** For invoice I1001, here are the line items along with their details:

| Service Name        | Quantity | Unit Price | Tax Rate | Line Total (including tax) |
|---------------------|----------|------------|----------|-----------------------------|
| Court Appearance     | 1        | 500        | 0.2      | 600.0                       |
| M&A Advisory         | 2        | 200        | 0.0      | 400.0                       |
| Court Appearance     | 5        | 300        | 0.0      | 1500.0       

---

### 9. For each client, compute the total amount billed in 2024 (including tax) across all their invoices.

**Status:** ✅ Correct (exact)

**Reference SQL:**
```sql
SELECT c.client_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_billed FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY c.client_name;
```

**Generated SQL:**
```sql
SELECT c.client_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_billed FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY c.client_name;
```

**Answer:** In 2024, the total amount billed (including tax) for each client across all their invoices is as follows:

- **Acme Corp**: $6,830.00
- **Alpine Hospitality**: $3,398.50
- **Aurora Textiles**: $5,104.00
- **BlueSky Consulting**: $5,757.50
- **Bright Legal**: $3,590.00
- **Crescent Pharma**: $2,401.50
- **GreenField Retail**: $3,287.50
- **Harbor Insurance**: $3,487.50
- **Metro Transport**: $3,310.00
- **Northwind Logistics**: $2,426.50
- **Nova Health**: $3,696.00
- **Orion Security**: $4,062.5

---

### 10. Which client has the highest total billed amount in 2024, and what is that total?

**Status:** ✅ Correct (exact)

**Reference SQL:**
```sql
SELECT c.client_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_billed FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY c.client_name ORDER BY total_billed DESC LIMIT 1;
```

**Generated SQL:**
```sql
SELECT c.client_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_billed FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY c.client_name ORDER BY total_billed DESC LIMIT 1;
```

**Answer:** The client with the highest total billed amount in 2024 is **Acme Corp**, with a total of **$6,830.00**.

---

### 11. Across all clients, which three services generated the most revenue in 2024? Show the total revenue per service.

**Status:** ✅ Correct (exact)

**Reference SQL:**
```sql
SELECT ili.service_name, SUM(ili.quantity * ili.unit_price) as total_revenue FROM invoice_line_items ili JOIN invoices i ON ili.invoice_id = i.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY ili.service_name ORDER BY total_revenue DESC LIMIT 3;
```

**Generated SQL:**
```sql
SELECT ili.service_name, SUM(ili.quantity * ili.unit_price) as total_revenue 
FROM invoice_line_items ili 
JOIN invoices i ON ili.invoice_id = i.invoice_id 
WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' 
GROUP BY ili.service_name 
ORDER BY total_revenue DESC 
LIMIT 3;
```

**Answer:** The three services that generated the most revenue in 2024 are as follows:

1. **Court Appearance**: $11,100
2. **M&A Advisory**: $10,600
3. **Tax Planning**: $10,550

These figures represent the total revenue generated from each service, excluding tax.

---

### 12. Which invoices are overdue as of 2024-12-31? List invoice ID, client name, invoice_date, due_date, and status.

**Status:** ✅ Correct (exact)

**Reference SQL:**
```sql
SELECT i.invoice_id, c.client_name, i.invoice_date, i.due_date, i.status FROM invoices i JOIN clients c ON i.client_id = c.client_id WHERE i.status = 'Overdue' AND i.due_date < '2024-12-31';
```

**Generated SQL:**
```sql
SELECT i.invoice_id, c.client_name, i.invoice_date, i.due_date, i.status FROM invoices i JOIN clients c ON i.client_id = c.client_id WHERE i.due_date < '2024-12-31' AND i.status = 'Overdue'
```

**Answer:** As of 2024-12-31, the following invoices are overdue:

| Invoice ID | Client Name          | Invoice Date | Due Date    | Status  |
|------------|----------------------|--------------|-------------|---------|
| I1002      | Bright Legal         | 2024-02-15   | 2024-03-15  | Overdue |
| I1005      | GreenField Retail    | 2024-04-01   | 2024-05-01  | Overdue |
| I1009      | Urban Tech           | 2024-06-01   | 2024-07-01  | Overdue |
| I1013      | Alpine Hospitality    | 2024-07-20   | 2024-0

---

### 13. Group revenue by client country: for each country, compute the total billed amount in 2024 (including tax).

**Status:** ✅ Correct (exact)

**Reference SQL:**
```sql
SELECT c.country, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_billed FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY c.country;
```

**Generated SQL:**
```sql
SELECT c.country, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_billed FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE i.invoice_date BETWEEN '2024-01-01' AND '2024-12-31' GROUP BY c.country;
```

**Answer:** Here is the total billed amount (including tax) grouped by client country for the year 2024:

- **Australia**: $5,757.50
- **Brazil**: $2,051.50
- **Canada**: $2,426.50
- **France**: $4,062.50
- **Germany**: $3,287.50
- **India**: $2,401.50
- **Ireland**: $6,106.00
- **Netherlands**: $2,632.00
- **New Zealand**: $2,037.50
- **Norway**: $5,506.00
- **Portugal**: $5,104.00
- **Spain**: $3,310.00
- **Switzerland**: $3,398.50
- **UK**: $7,420.00
- **USA**: $22,003.00

This data reflects the total am

---

### 14. For the service 'Contract Review', list all clients who purchased it and the total amount they paid for that service (including tax).

**Status:** ✅ Correct (exact)

**Reference SQL:**
```sql
SELECT c.client_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_paid FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE ili.service_name = 'Contract Review' GROUP BY c.client_name;
```

**Generated SQL:**
```sql
SELECT c.client_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_paid FROM clients c JOIN invoices i ON c.client_id = i.client_id JOIN invoice_line_items ili ON i.invoice_id = ili.invoice_id WHERE ili.service_name = 'Contract Review' GROUP BY c.client_name
```

**Answer:** The following clients purchased the service 'Contract Review' along with the total amount they paid for that service (including tax):

1. **Aurora Textiles**: $2,200.00
2. **BlueSky Consulting**: $907.50
3. **Bright Legal**: $220.00
4. **Nova Health**: $360.00
5. **Orion Security**: $1,812.50
6. **Pacific Foods**: $800.00
7. **Prairie Agriculture**: $181.50
8. **Silverline Media**: $220.00
9. **Summit Finance**: $600.00
10. **Zenith Education**: $600.00

These amounts reflect the total paid for 

---

### 15. Considering only European clients, what are the top 3 services by total revenue (including tax) in H2 2024 (2024-07-01 to 2024-12-31)?

**Status:** ✅ Correct (exact)

**Reference SQL:**
```sql
SELECT ili.service_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_revenue FROM invoice_line_items ili JOIN invoices i ON ili.invoice_id = i.invoice_id JOIN clients c ON i.client_id = c.client_id WHERE c.country IN ('UK', 'France', 'Germany', 'Spain', 'Italy', 'Netherlands', 'Portugal') AND i.invoice_date BETWEEN '2024-07-01' AND '2024-12-31' GROUP BY ili.service_name ORDER BY total_revenue DESC LIMIT 3;
```

**Generated SQL:**
```sql
SELECT ili.service_name, SUM(ili.quantity * ili.unit_price * (1 + ili.tax_rate)) as total_revenue FROM invoice_line_items ili JOIN invoices i ON ili.invoice_id = i.invoice_id JOIN clients c ON i.client_id = c.client_id WHERE i.invoice_date BETWEEN '2024-07-01' AND '2024-12-31' AND c.client_id IN ('C002', 'C004', 'C008', 'C010', 'C013', 'C015', 'C019') GROUP BY ili.service_name ORDER BY total_revenue DESC LIMIT 3;
```

**Answer:** In the second half of 2024 (from July 1 to December 31), the top 3 services by total revenue (including tax) for European clients are:

1. **Contract Review**: $4,232.50
2. **Custom Reporting**: $2,990.00
3. **Training Session**: $2,406.00

---
