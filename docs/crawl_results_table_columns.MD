# 📊 `crawl_results` Table Column Descriptions

## 🔑 Primary Key

- **`id`** (`bigint`) - Auto-incrementing unique identifier for each crawl record. This is the primary key that automatically generates sequential numbers for each new row.

## 🌐 Web Crawling Core Data

- **`url`** (`text`) - The web URL that was crawled. This stores the complete web address of the page that was processed (e.g., `https://docs.python.org/3/tutorial/index.html`).

- **`title`** (`text`, nullable) - The extracted title of the webpage. This would typically be the `<title>` tag content from the HTML page.

- **`content`** (`text`, nullable) - The main text content extracted from the webpage. This contains the cleaned and processed text from the page, removing HTML tags and formatting.

## 📋 Metadata & Processing Info

- **`metadata`** (`jsonb`, nullable) - Structured metadata about the webpage stored as JSON. This can include information like:
  - Page description
  - Author information
  - Open Graph tags (og:title, og:description, etc.)
  - Twitter card data
  - Keywords
  - Any other structured data found on the page

- **`extraction_data`** (`jsonb`, nullable) - Additional data extracted during the crawling process, stored as JSON. This might include:
  - Processing parameters
  - Extraction rules used
  - Additional structured data
  - Processing status information

## 📏 Content Analytics

- **`content_length`** (`integer`, nullable) - The character count of the extracted content. Useful for analytics and content sizing.

- **`content_hash`** (`bigint`, nullable) - A hash value of the content for duplicate detection and change tracking. This helps identify when content has been modified.

## 🤖 AI/ML Features

- **`embedding`** (`vector`, nullable) - Vector embedding representation of the content, likely for semantic search, similarity matching, or AI/ML applications. This is using the pgvector extension for storing high-dimensional vectors.

## ⏰ Timestamps

- **`crawled_at`** (`timestamptz`, nullable) - When the webpage was actually crawled/accessed. Defaults to current timestamp.

- **`created_at`** (`timestamptz`, nullable) - When this database record was first created. Defaults to current timestamp.

- **`updated_at`** (`timestamptz`, nullable) - When this database record was last modified. Defaults to current timestamp.

## 🎯 What This Table Records

This appears to be a **web crawling/scraping system** that:

1. **Crawls web pages** and extracts their content
2. **Stores structured data** about each page (title, content, metadata)
3. **Tracks content changes** via hashing
4. **Generates AI embeddings** for semantic search capabilities
5. **Maintains audit trails** with multiple timestamp fields
6. **Supports rich metadata** storage in JSON format

This type of table is commonly used in:

- **Content management systems**
- **Search engines**
- **Knowledge bases**
- **AI/ML training data collection**
- **Website monitoring systems**
- **SEO analysis tools**

The presence of the `embedding` vector field suggests this system is likely used for **semantic search** or **AI-powered content analysis**.
