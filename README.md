# The Polite Scraper

A small Python scraping pipeline that collects book data from the Books to Scrape practice sandbox, cleans and validates the data, and stores the results as JSON.

## Target Classification

### Target

Books to Scrape:

https://books.toscrape.com/

Books to Scrape is a public practice sandbox specifically designed for learning web scraping.

### Scope

This scraper will process only the first three catalogue pages.

Each catalogue page contains 20 books, giving:

- 3 catalogue pages
- 60 book pages
- 60 unique book records

The scraper will collect only the data required by the assignment.

### Data Collected

For each book, the scraper will collect:

- title
- product URL
- price text
- availability text
- rating text
- description
- source catalogue page
- fetched timestamp

The cleaned records will additionally contain:

- price_gbp

### Robots.txt

I checked:

`https://books.toscrape.com/robots.txt`

Result:

The request returned `404 Not Found`, so no robots.txt file was found.

A missing robots.txt file is not treated as permission to scrape. The target is appropriate because Books to Scrape is explicitly provided as a practice sandbox for learning web scraping.

A missing robots.txt file would not be treated as permission to scrape.

### Responsible Scraping

This project targets Books to Scrape because it is explicitly provided as a practice sandbox for scraping.

The scraper will:

- identify itself with a User-Agent
- use request timeouts
- wait at least 500 ms between real requests
- cache downloaded pages during development
- check HTTP status codes
- avoid unnecessary requests
- never bypass authentication, paywalls, blocks, or other access controls

I will not reuse this code on another site without checking its rules and terms first.