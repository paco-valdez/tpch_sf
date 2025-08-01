# Cube Cloud - Claude Code Template

A comprehensive template for building Cube applications using Claude Code (claude.ai/code) and Cube. This template implements a TPC-H SF100 data model with OLAP cubes and views for analytical queries on the TPC-H benchmark dataset using Snowflake as the data source.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+  
- [Claude Code](https://claude.ai/code) (recommended for AI-assisted development)
- Access to a SQL data warehouse (Snowflake, PostgreSQL, MySQL, etc.)
- Cube Cloud account

### 1. Fork and Clone
```bash
git clone <your-forked-repo-url>
cd <repo-name>
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env-example .env

# Edit .env with your Cube Cloud credentials
# API_SECRET=your-cube-cloud-api-secret
# API_URL=https://your-tenant.aws-us-east-1.cubecloudapp.dev/cubejs-api/v1/
# STAGING_ENV_BRANCH=your-staging-branch
# STAGING_ENV_API_URL=https://your-tenant.aws-us-east-1.cubecloudapp.dev/staging/branch-name/cubejs-api/v1/
```

## 🔄 Adapting to Your Data Schema

### Step 1: Database Schema Discovery

Run these SQL queries against your data warehouse to understand your schema structure:

#### List All Tables
```sql
-- For Snowflake
SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_schema = 'YOUR_SCHEMA_NAME'
ORDER BY table_name;

-- For PostgreSQL
SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_schema = 'your_schema_name' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- For MySQL
SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_schema = 'your_schema_name'
ORDER BY table_name;
```

#### Analyze Table Structure
```sql
-- For Snowflake
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_schema = 'YOUR_SCHEMA' 
AND table_name = 'YOUR_TABLE'
ORDER BY ordinal_position;

-- For PostgreSQL
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_schema = 'your_schema' 
AND table_name = 'your_table'
ORDER BY ordinal_position;
```

#### Discover Foreign Key Relationships
```sql
-- For Snowflake
SELECT 
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
AND tc.table_schema = 'YOUR_SCHEMA';

-- For PostgreSQL (similar structure, adjust schema names)
```

#### Sample Data Inspection
```sql
-- Get sample data and value distributions
SELECT * FROM your_schema.your_table LIMIT 10;

-- Check for null values in key columns
SELECT 
    column_name,
    COUNT(*) as total_rows,
    COUNT(column_name) as non_null_rows,
    COUNT(*) - COUNT(column_name) as null_rows
FROM your_table;

-- Find distinct values for categorical columns
SELECT column_name, COUNT(DISTINCT column_name) as distinct_values
FROM your_table;
```

### Step 2: Update Data Model Documentation

1. **Update `docs/DATA_MODEL.md`**: Document your database schema, relationships, and key architectural patterns
2. **Identify fact and dimension tables**: Determine which tables contain metrics (facts) vs. descriptive attributes (dimensions)
3. **Map relationships**: Document foreign key relationships and join paths

### Step 3: Generate Cube Definitions

Use Claude Code to help generate cube definitions based on your schema:

**Example prompt for Claude Code:**
```
Based on this database schema information:
[Paste your SQL query results here]

Generate Cube.js YAML cube definitions following the patterns in this template. I need:
1. Dimension cubes for [list your dimension tables]
2. Fact cubes for [list your fact tables] 
3. Proper join relationships between them
4. Key measures and dimensions for analytical queries
```

### Step 4: Create Cubes and Views

1. **Replace cube files**: Update files in `model/cubes/` with your own cube definitions
2. **Update joins**: Ensure proper `joins` configuration between related cubes
3. **Create views**: Build analytical views in `model/views/` that combine multiple cubes
4. **Configure cube.py**: Update any security context or query rewriting logic

### Step 5: Testing and Deployment

```bash
# Test your changes locally (if applicable)
python scripts/test_api.py

# Create staging branch in Cube Cloud UI first, then:
git checkout -b your-staging-branch
git add .
git commit -m "Initial cube model setup"
git push origin your-staging-branch

# Test with staging environment
python scripts/fetch_meta.py --staging
python scripts/test_api.py --staging

# Deploy to production when ready
```

## 📁 Project Structure

```
├── cube.py                 # Main Cube.js configuration
├── model/
│   ├── cubes/             # Individual cube definitions (YAML)
│   └── views/             # Analytical views combining cubes
├── scripts/
│   ├── fetch_meta.py      # Fetch cube metadata from deployment
│   └── test_api.py        # Test API endpoints
├── docs/
│   ├── DATA_MODEL.md      # Database schema documentation
│   ├── META_CURRENT.md    # Current cube metadata (auto-generated)
│   └── REST_API_REFERENCE.md  # API usage examples
└── .env                   # Environment configuration
```

## 🛠 Development Workflow

### Working with Staging Environment

This template supports both production and staging environments:

- **Production**: Use default environment variables from `.env`
- **Staging**: Add `--staging` flag to scripts (e.g., `python scripts/fetch_meta.py --staging`)

### Key Commands

```bash
# Fetch current cube metadata
python scripts/fetch_meta.py

# Test API endpoints  
python scripts/test_api.py

# Work with staging environment
python scripts/fetch_meta.py --staging
python scripts/test_api.py --staging
```

### Branch Management

- **Never commit to master/main**: Always work in feature branches
- **Use staging branches**: Create staging branches in Cube Cloud UI before testing
- **Environment variables**: `STAGING_ENV_BRANCH` defines your staging branch name

## 📊 Example Cube Structure

This template includes TPC-H benchmark cubes as examples:

### Dimension Cubes
- `customer`: Customer information with nation relationship
- `nation`: Country/nation data with region relationship  
- `region`: Geographic regions
- `supplier`: Supplier information
- `part`: Product/part catalog

### Fact Cubes
- `orders`: Customer orders with measures like total price
- `lineitem`: Order line items with quantity, price, discount measures
- `partsupp`: Part-supplier relationships with cost information

### Analytical Views
- `item_information`: Complex view joining multiple cubes for product analysis
- `supplier_sales_analysis`: Supplier performance metrics

## 🔧 Customization Tips

### Adding New Measures
```yaml
measures:
  - name: total_revenue
    sql: "SUM({CUBE}.amount * {CUBE}.quantity)"
    type: number
    format: currency
```

### Creating Joins
```yaml
joins:
  - name: related_cube
    sql: "{CUBE.foreign_key} = {related_cube.primary_key}"
    relationship: many_to_one
```

### Time Dimensions
```yaml
dimensions:
  - name: created_date
    sql: "{CUBE}.created_at"
    type: time
    time_dimension: true
```

## 🤖 AI-Assisted Development

This template is designed to work seamlessly with [Claude Code](https://claude.ai/code):

### Useful Prompts
- "Generate a cube definition for my `sales` table with these columns: [list columns]"
- "Create a view that joins `orders`, `customers`, and `products` for sales analysis"
- "Add time-based measures for month-over-month growth analysis"
- "Optimize this cube definition for better performance"

### Code Analysis
- "Explain the relationships between cubes in this project"
- "What measures are available in the `lineitem` cube?"
- "How can I add a new dimension to track customer segments?"

## 🔍 Troubleshooting

### Common Issues
1. **Schema mismatch**: Ensure table names and column names match your database exactly
2. **Join failures**: Verify foreign key relationships and data types match
3. **API errors**: Check API credentials and URL configuration in `.env`
4. **Staging deployment**: Ensure staging branch exists in Cube Cloud UI before pushing

### Getting Help
- Check `docs/REST_API_REFERENCE.md` for API usage examples
- Use Claude Code for debugging and code generation
- Review `docs/META_CURRENT.md` for current cube structure

## 📝 License

PRIVATE LICENSE - Do not distribute without permission.

## 🤝 Contributing

If you have suggestions or improvements, please create a pull request or open an issue in the repository.