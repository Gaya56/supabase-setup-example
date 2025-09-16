# 📊 `crawl_results` Table Schema

## 🔑 Core Fields

- **`id`** (`bigint`) - Auto-incrementing primary key
- **`url`** (`text`) - Crawled webpage URL
- **`title`** (`text`) - Page title from `<title>` tag
- **`content`** (`text`) - Extracted text content (HTML removed)

## 📋 Metadata & Processing

- **`metadata`** (`jsonb`) - Structured page data (Open Graph, keywords, etc.)
- **`extraction_data`** (`jsonb`) - Processing parameters and extraction details
- **`content_length`** (`integer`) - Character count of extracted content
- **`content_hash`** (`bigint`) - Hash for duplicate detection and change tracking

## 🤖 AI/Vector Features

- **`embedding`** (`vector`) - pgvector embedding for semantic search and similarity matching

## ⏰ Timestamps

- **`crawled_at`** (`timestamptz`) - When page was accessed
- **`created_at`** (`timestamptz`) - Record creation time
- **`updated_at`** (`timestamptz`) - Last modification time

## 🎯 Purpose

Supports intelligent web crawling with:
- **Content extraction** and structured storage
- **Duplicate detection** via content hashing
- **Semantic search** using vector embeddings
- **Change tracking** with timestamps
- **Rich metadata** in JSON format

Designed for crawl4ai integration with automatic embedding generation.
