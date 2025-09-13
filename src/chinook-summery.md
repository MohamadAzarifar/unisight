# Chinook Database

### **Introduction to the Chinook Schema (For Context)**

The NLQ engine must understand these key tables and relationships:

* **Music:** `Artist` -> `Album` -> `Track` -> `Genre` / `MediaType`
* **Customers & Sales:** `Customer` -> `Invoice` -> `InvoiceLine` -> `Track`
* **Employees:** `Employee` (ReportsTo for hierarchy)

---

### **Category 1: Business & Sales Questions**

#### **Easy Business & Sales Questions (Direct facts, single table or simple joins)**

1. How many customers do we have?
2. List all employees.
3. Show me the top 5 countries by number of customers.
4. What is the total revenue from all invoices?
5. How many invoices were issued in 2013?

**Intermediate (Aggregations, multiple joins, basic filtering)**
6. Who is the top-selling artist by revenue?
7. Who are our top 10 customers by total spending?
8. What is the average invoice total?
9. Show me the monthly sales revenue for 2012.
10. Which sales agent has the highest total sales?
11. How many customers does each employee support?
12. What is the distribution of sales across different countries?
13. Find all invoices from customers in Canada.
14. Show me a list of customers who have never placed an invoice. (Tests understanding of `LEFT JOIN` + `NULL`).
15. What is the most common billing city?

**Advanced (Complex joins, sub-queries, date functions, ratios)**
16. What was the single biggest invoice ever and which customer placed it?
17. Calculate the year-over-year growth rate of sales.
18. Find customers whose average invoice value is above the overall average.
19. Show the sales revenue for each music genre. (Requires joining Invoice -> InvoiceLine -> Track -> Genre).
20. Who is the highest-performing sales agent of all time? (Consider both total sales and number of customers managed).
21. Identify customers who have bought music from more than 3 different genres.
22. For each customer, find their first invoice date and their most recent invoice date.
23. What percentage of our total revenue comes from the USA?
24. Find all invoices where the customer bought a track from their own country.
25. Analyze the sales trend: show quarterly sales totals for the last two full years.

---

### **Category 2: Music & Media Questions**

#### **Easy Music & Media Questions (Direct facts, single table or simple joins)**

1. How many tracks are in the database?
2. List all available music genres.
3. How many albums does the artist "U2" have?
4. What is the longest song in the database?
5. Show me all tracks on the album "Jagged Little Pill".

**Intermediate (Aggregations, genre/artist analysis, playlists)**
6. Which genre has the most tracks?
7. List the top 10 artists by number of albums.
8. What is the average length (in milliseconds) of a track in the "Rock" genre?
9. Show me all playlists and how many tracks are in each.
10. Which media type (e.g., MPEG, AAC) is most common?
11. Find all tracks that are longer than 5 minutes.
12. How many composers are listed in the database? (Tests handling of `NULL` values, as many are NULL).
13. Show me all tracks that feature the word "Love" in the title.
14. Which album has the most tracks?
15. List all tracks from the "Classical" genre.

**Advanced (Complex analysis, correlations, text parsing)**
16. Who are the top 5 most prolific composers? (Assuming non-NULL composer field).
17. For the artist "Iron Maiden", what is the average track length per album?
18. Find artists who have released albums in at least 3 different genres.
19. **Classic Chinook Question:** List all tracks that are not in any playlist. (Tests `LEFT JOIN` + `NULL`).
20. Is there a correlation between track length and unit price? (e.g., are longer tracks more expensive?).
21. Identify the most "diverse" playlist - the one with tracks from the most genres.
22. Find the artist with the longest average track length.
23. Show a list of albums where all tracks are from the same genre.
24. For a given track (e.g., "Princess of the Dawn"), on which playlists does it appear?
25. Analyze the "Rock" genre: break it down into sub-genres by looking for common keywords in track names (e.g., "Metal", "Hard", "Punk"). (This is very advanced and tests NLP/pattern matching within the NLQ engine).

---

### **How to Use This List for Testing**

1. **Start Easy:** Begin with the "Easy" questions to test if the NLQ engine can connect to the database and perform basic queries.
2. **Test Joins:** Move to "Intermediate" questions to assess its ability to understand and navigate the schema relationships (e.g., `Customer` to `Invoice` to `InvoiceLine`).
3. **Challenge Understanding:** Use the "Advanced" questions to push the limits. These test complex logic, aggregation, and the engine's ability to parse nuanced user intent.
4. **Check for Errors:** Pay attention not just to correct answers, but also to how the engine handles ambiguity or questions it can't answer. Does it provide a helpful error message or clarification prompt?
5. **Synonyms and Phrasing:** Try rephrasing the same question. For example, "total sales" vs. "total revenue" vs. "sum of all invoices". A robust NLQ engine should handle these synonyms.

This list provides a comprehensive foundation for evaluating the accuracy, depth, and user-friendliness of your NLQ application against the Chinook database.

## Here are questions you could ask, categorized by difficulty and the concepts they test

### Beginner (Basic SELECT, WHERE, JOIN, ORDER BY, LIMIT)

These questions focus on retrieving and filtering data from single or two tables.

1. **Listing Data:** What are the names of all our playlists?
2. **Filtering:** Which customers are from Canada or Germany?
3. **Sorting:** List all artists in alphabetical order (A-Z).
4. **Simple JOIN:** Show all tracks and their corresponding album titles.
5. **Aggregation (COUNT):** How many tracks are there in the database?
6. **LIMIT:** Who are our top 5 customers based on their total spent (need to join to Invoice and sum)? *(A bit of a sneak peek to intermediate)*
7. **Search (LIKE):** Find all artists whose name starts with "A".
8. **Null Check:** Find all employees who don't have a reported-to manager (where ReportsTo is NULL).

### Intermediate (Aggregate Functions, GROUP BY, HAVING, Multiple JOINs)

These require grouping data and applying conditions to those groups.

1. **Grouping & Aggregation:** What is the total number of tracks in each playlist? Show the playlist name and the count.
2. **Revenue Analysis:** What is the total sales amount for each country? Display the country and the total sum, ordered from highest to lowest.
3. **Filtering Groups (HAVING):** Which artists have more than 1 album in the database?
4. **Multi-table JOIN:** List all tracks from the genre "Rock", including the track name, album title, and artist name.
5. **Customer Spending:** Show the top 10 customers by their total invoice amount. Include their full name and total spent.
6. **Employee Performance:** Which sales support agent has brought in the most total revenue? (Join Customers to Employees to Invoices).
7. **Popularity:** What are the top 5 most purchased tracks? How many times was each one purchased? (This requires joining Track -> InvoiceLine -> Invoice and counting).
8. **Album vs. Compilation:** Show the average track length for each album and compare it to the overall average track length.

### Advanced (Subqueries, CTEs, Window Functions, Complex Logic)

These questions require breaking problems down into multiple steps or using advanced SQL features.

1. **Correlated Subquery:** For each customer, find their single most expensive invoice. (Show customer name, invoice date, and total).
2. **Common Table Expression (CTE):** Using a CTE, calculate the total revenue generated by each media type.
3. **Window Functions (RANK):** Rank employees based on the total sales revenue of their assigned customers.
4. **Date Analysis:** Show the monthly sales trend for the year 2013. Group invoices by month and show the total for each month.
5. **Percentage of Total:** What percentage of total sales does each genre represent? (Requires a subquery or window function to get the overall total).
6. **Customer Loyalty:** Identify customers who have purchased music from at least 3 different genres.
7. **Gaps in Collection:** Find artists in the database for which we have tracks but no associated album. (This tests understanding of data integrity and joins).
8. **Recursive Query (if supported):** Build a full organizational chart for all employees, showing who reports to whom at all levels.

### Business Intelligence & "What-If" Scenarios

These questions mimic real-world business decisions and require creative SQL.

1. **Customer Segmentation:** Classify customers into tiers like "Gold", "Silver", and "Bronze" based on their total spending.
2. **Value of a Customer:** Calculate the average customer lifetime value (total revenue per customer).
3. **Hit-Maker Analysis:** Is there a correlation between an artist's number of albums and their total track sales?
4. **Playlist Analysis:** What is the most common genre in the "Music" playlist? The "Movies" playlist?
5. **Sales Commission:** If sales support agents get a 2% commission on sales from their customers, how much commission would each employee earn?
6. **Inventory Value:** If we were to sell every track in our database at its unit price, what would the total potential revenue be?

---

### Example Query for a Common Question

Let's answer one: **"Which artists have more than 1 album in the database?"**

```sql
SELECT 
    ar.Name AS ArtistName, 
    COUNT(al.AlbumId) AS NumberOfAlbums
FROM 
    Artist ar
JOIN 
    Album al ON ar.ArtistId = al.ArtistId
GROUP BY 
    ar.ArtistId, ar.Name
HAVING 
    COUNT(al.AlbumId) > 1
ORDER BY 
    NumberOfAlbums DESC;
```

**This query:**

1. **JOINs** the `Artist` table to the `Album` table.
2. **GROUPs BY** the artist, so we can count albums per artist.
3. **COUNTs** the albums for each group.
4. **Filters** the groups using **HAVING** to only show artists where the count is greater than 1.
5. **ORDERS** the results to see the most prolific artists first.

The Chinook database is excellent because it allows you to practice nearly every fundamental and advanced SQL concept in a clear and relatable context.
