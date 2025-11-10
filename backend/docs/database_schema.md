# Database Schema Documentation

**Project**: 大学向けコミュニケーションツール
**Version**: v3
**Last Updated**: 2025-11-10

---

## Overview

This document describes the database schema for the university communication tool backend. The system uses PostgreSQL as the primary database with SQLAlchemy ORM.

### Database Structure

The database consists of the following main entities:
- **Users**: System users (students, professors, staff)
- **Wiki Pages**: Collaborative knowledge base
- **Wiki Page Permissions**: Dynamic permission system
- **Tags**: User categorization system
- **User Tags**: Many-to-many relationship for tag assignments

---

## Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ WIKI_PAGES : creates
    USERS ||--o{ TAGS : creates
    USERS ||--o{ WIKI_PAGE_PERMISSIONS : has
    WIKI_PAGES ||--o{ WIKI_PAGE_PERMISSIONS : defines
    USERS ||--o{ USER_TAGS : has
    TAGS ||--o{ USER_TAGS : assigned_to

    USERS {
        uuid id PK
        string username UK
        string email UK
        string hashed_password
        enum kategori
        string gakuseki_bango UK
        string faculty
        string icon_path
        datetime created_at
    }

    WIKI_PAGES {
        int id PK
        string title
        text content
        uuid creator_id FK
        datetime created_at
        datetime updated_at
    }

    WIKI_PAGE_PERMISSIONS {
        int id PK
        int page_id FK
        uuid user_id FK
        enum permission_level
    }

    TAGS {
        int id PK
        string name UK
        uuid creator_id FK
    }

    USER_TAGS {
        int id PK
        uuid user_id FK
        int tag_id FK
    }
```

---

## Table Definitions

### Users Table

**Table Name**: `users`

Stores all system users with their authentication and profile information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| username | VARCHAR(100) | UNIQUE, NOT NULL | Login username |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt-hashed password |
| kategori | ENUM | NOT NULL | User category (see below) |
| gakuseki_bango | VARCHAR(20) | UNIQUE, NOT NULL | Student/Staff ID |
| faculty | VARCHAR(255) | NULLABLE | Faculty/Department name |
| icon_path | VARCHAR(255) | NULLABLE | Profile icon path |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation timestamp |

**User Categories (kategori)**:
- `学生` (STUDENT)
- `教授` (PROFESSOR)
- `准教授` (ASSOCIATE_PROFESSOR)
- `講師` (LECTURER)
- `事務` (STAFF)

**v3 Business Logic**:
- Students: `gakuseki_bango` must be provided during signup
- Staff/Professors: `gakuseki_bango` is auto-generated as `staff_{8-char-hex}`

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `username`
- UNIQUE INDEX on `email`
- UNIQUE INDEX on `gakuseki_bango`

**Relationships**:
- One-to-Many with `wiki_pages` (as creator)
- One-to-Many with `tags` (as creator)
- One-to-Many with `wiki_page_permissions`
- One-to-Many with `user_tags`

---

### Wiki Pages Table

**Table Name**: `wiki_pages`

Stores collaborative Wiki pages with versioning information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Wiki page ID |
| title | VARCHAR(200) | NOT NULL | Page title |
| content | TEXT | NOT NULL | Page content (markdown) |
| creator_id | UUID | FOREIGN KEY, NOT NULL | Creator user ID |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW(), ON UPDATE NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `creator_id`
- INDEX on `created_at`

**Relationships**:
- Many-to-One with `users` (creator)
- One-to-Many with `wiki_page_permissions`

**Cascade Rules**:
- ON DELETE CASCADE: When creator is deleted, pages are deleted
- ON UPDATE CASCADE: When creator_id changes, pages are updated

---

### Wiki Page Permissions Table

**Table Name**: `wiki_page_permissions`

Dynamic permission system for Wiki pages (similar to Google Docs).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Permission record ID |
| page_id | INTEGER | FOREIGN KEY, NOT NULL | Wiki page ID |
| user_id | UUID | FOREIGN KEY, NOT NULL | User ID |
| permission_level | ENUM | NOT NULL | Permission level (see below) |

**Permission Levels**:
- `VIEW_ONLY`: Read-only access
- `EDIT`: Full read/write access

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `(page_id, user_id)`
- INDEX on `page_id`
- INDEX on `user_id`

**Relationships**:
- Many-to-One with `wiki_pages`
- Many-to-One with `users`

**Cascade Rules**:
- ON DELETE CASCADE: When page is deleted, permissions are deleted
- ON DELETE CASCADE: When user is deleted, permissions are deleted

**Business Logic**:
- Creator automatically receives EDIT permission upon page creation
- Users can have at most one permission level per page (enforced by unique constraint)
- Sharing a page creates/updates a permission record

---

### Tags Table

**Table Name**: `tags`

User categorization system with creator tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Tag ID |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Tag name |
| creator_id | UUID | FOREIGN KEY, NOT NULL | Creator user ID |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `name`
- INDEX on `creator_id`

**Relationships**:
- Many-to-One with `users` (creator)
- One-to-Many with `user_tags`

**Cascade Rules**:
- ON DELETE CASCADE: When creator is deleted, tags are deleted

**v3 Business Logic**:
- Only creator can delete a tag
- Students can assign any tag to any user
- Professors/Staff can only assign tags they created

---

### User Tags Table

**Table Name**: `user_tags`

Many-to-many relationship between users and tags.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Assignment record ID |
| user_id | UUID | FOREIGN KEY, NOT NULL | User ID |
| tag_id | INTEGER | FOREIGN KEY, NOT NULL | Tag ID |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `(user_id, tag_id)`
- INDEX on `user_id`
- INDEX on `tag_id`

**Relationships**:
- Many-to-One with `users`
- Many-to-One with `tags`

**Cascade Rules**:
- ON DELETE CASCADE: When user is deleted, assignments are deleted
- ON DELETE CASCADE: When tag is deleted, assignments are deleted

**Business Logic**:
- A user can have the same tag assigned only once (enforced by unique constraint)
- Tag assignments are idempotent

---

## Data Integrity

### Foreign Key Constraints

All foreign keys are enforced at the database level:

1. **wiki_pages.creator_id** → users.id
   - ON DELETE CASCADE
   - ON UPDATE CASCADE

2. **wiki_page_permissions.page_id** → wiki_pages.id
   - ON DELETE CASCADE
   - ON UPDATE CASCADE

3. **wiki_page_permissions.user_id** → users.id
   - ON DELETE CASCADE
   - ON UPDATE CASCADE

4. **tags.creator_id** → users.id
   - ON DELETE CASCADE
   - ON UPDATE CASCADE

5. **user_tags.user_id** → users.id
   - ON DELETE CASCADE
   - ON UPDATE CASCADE

6. **user_tags.tag_id** → tags.id
   - ON DELETE CASCADE
   - ON UPDATE CASCADE

### Unique Constraints

1. **users.username**: Prevent duplicate usernames
2. **users.email**: Prevent duplicate emails
3. **users.gakuseki_bango**: Prevent duplicate student/staff IDs
4. **tags.name**: Prevent duplicate tag names
5. **(wiki_page_permissions.page_id, user_id)**: One permission per user per page
6. **(user_tags.user_id, tag_id)**: One tag assignment per user

---

## Indexes and Performance

### Primary Keys
All tables use appropriate primary keys (UUID for users, INTEGER for others).

### Foreign Key Indexes
All foreign key columns have indexes for JOIN performance.

### Search Optimization
Consider adding full-text search indexes for:
- `wiki_pages.title`
- `wiki_pages.content`
- `users.username`

**Recommendation for PostgreSQL**:
```sql
CREATE INDEX idx_wiki_pages_title_search ON wiki_pages USING gin(to_tsvector('english', title));
CREATE INDEX idx_wiki_pages_content_search ON wiki_pages USING gin(to_tsvector('english', content));
```

---

## Migration Strategy

### Alembic Migrations

Migrations are managed using Alembic:

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Version History

| Version | Date | Description |
|---------|------|-------------|
| initial | 2025-11-09 | Initial schema with users table |
| v2 | 2025-11-09 | Add wiki pages and permissions |
| v3 | 2025-11-10 | Add tags and user_tags |

---

## Security Considerations

### Password Storage
- Passwords are hashed using bcrypt with automatic salt generation
- Never store plain-text passwords
- Password complexity is enforced at the application level

### SQL Injection Prevention
- SQLAlchemy ORM provides automatic parameterization
- Raw SQL queries should use bound parameters

### Data Access
- All queries are permission-aware
- Row-level security is enforced at the application level
- Future: Consider PostgreSQL Row-Level Security (RLS) policies

---

## Backup and Recovery

### Backup Strategy

**Daily Backups**:
```bash
pg_dump -U postgres university_communication > backup_$(date +%Y%m%d).sql
```

**Point-in-Time Recovery**:
Enable WAL archiving in `postgresql.conf`:
```conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'
```

### Recovery Procedure

```bash
# Restore from backup
psql -U postgres university_communication < backup_20251110.sql

# Verify data integrity
psql -U postgres university_communication
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM wiki_pages;
```

---

## Monitoring

### Key Metrics

1. **Table Sizes**:
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

2. **Index Usage**:
```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

3. **Slow Queries**:
Enable `pg_stat_statements` extension and monitor query performance.

---

## Phase 4: Channels and Direct Messages

### Channels Table

**Table Name**: `channels`

Real-time communication channels for group messaging.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Channel ID |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Channel name |
| description | VARCHAR(500) | NULLABLE | Channel description |
| is_private | BOOLEAN | DEFAULT FALSE, NOT NULL | Private/Public flag |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `name`

**Relationships**:
- One-to-Many with `messages`

**Business Logic**:
- All users can create channels
- Channel names must be unique across the system
- Private channels are reserved for future implementation

---

### Messages Table

**Table Name**: `messages`

Unified message storage for both channel messages and direct messages.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Message ID |
| content | TEXT | NOT NULL | Message content |
| sender_id | UUID | FOREIGN KEY, NOT NULL | Sender user ID |
| channel_id | INTEGER | FOREIGN KEY, NULLABLE | Channel ID (for channel messages) |
| receiver_id | UUID | FOREIGN KEY, NULLABLE | Receiver user ID (for DMs) |
| created_at | TIMESTAMP | DEFAULT NOW() | Message creation timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `sender_id`
- INDEX on `channel_id`
- INDEX on `receiver_id`
- INDEX on `created_at`

**Relationships**:
- Many-to-One with `users` (sender)
- Many-to-One with `channels` (for channel messages)
- Many-to-One with `users` (receiver, for DMs)
- One-to-Many with `files` (for attachments)

**Cascade Rules**:
- ON DELETE CASCADE: When sender is deleted, messages are deleted
- ON DELETE CASCADE: When channel is deleted, channel messages are deleted
- ON DELETE CASCADE: When receiver is deleted, DMs are deleted

**Message Type Determination**:
```sql
-- Channel Message: channel_id IS NOT NULL AND receiver_id IS NULL
-- Direct Message: channel_id IS NULL AND receiver_id IS NOT NULL
```

**Business Logic**:
- Messages are sorted by `created_at DESC` (newest first)
- DM history includes bidirectional messages between two users
- Channel messages are visible to all users (Phase 4 implementation)
- Message persistence enables offline access via REST API

---

## Future Enhancements

### Phase 5: Advanced Features

Planned additions:
- `channel_members` table (many-to-many for channel membership)
- `typing_indicators` table (real-time typing status)
- `message_reactions` table (emoji reactions)
- `message_threads` table (threaded conversations)

### Potential Optimizations

1. **Partitioning**: Consider partitioning `messages` table by date for performance
2. **Materialized Views**: Create materialized views for message statistics
3. **Read Replicas**: Implement read replicas for scalability
4. **Caching**: Add Redis for frequently accessed data (channel lists, recent messages)

---

## Appendix

### SQLAlchemy Models

Models are defined in `app/models/`:
- `user.py`: User model
- `wiki.py`: WikiPage and WikiPagePermission models
- `tag.py`: Tag and UserTag models

### Database Connection

Connection string format:
```
postgresql://{user}:{password}@{host}:{port}/{database}
```

Example:
```
postgresql://postgres:password@localhost:5432/university_communication
```

---

## Contact

For schema-related questions, contact the backend team.

For migration issues, see [deployment.md](deployment.md).
