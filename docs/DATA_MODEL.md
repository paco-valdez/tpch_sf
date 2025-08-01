The cubes implement the TPC-H schema with proper relationships:
- **Customer** → Nation (many-to-one)
- **Orders** → Customer (many-to-one)  
- **Lineitem** → Orders, Supplier, Part (many-to-one)
- **Nation** → Region (many-to-one)
- **Supplier** → Nation (many-to-one)
- **Partsupp** → Part, Supplier (many-to-one)

Key architectural patterns:
- Cubes use Snowflake SQL with `SNOWFLAKE_SAMPLE_DATA.TPCH_SF100` schema
- Filtered datasets (e.g., lineitem only includes open orders with 'O' status)
- Primary keys use composite keys where needed (lineitemkey = orderkey + line_number)
- Views define join paths for cross-cube analytics

### Data Source
- Uses Snowflake sample data: `SNOWFLAKE_SAMPLE_DATA.TPCH_SF100`
- Connection configuration should be set via environment variables or Cube.js config

## Key Files

- **cube.py:13-24**: Security context and query rewriting configuration
- **model/views/item_information.yml**: Complex view demonstrating join path patterns across all TPC-H entities
- **model/cubes/lineitem.yml:4-7**: Example of filtered cube using custom SQL instead of direct table reference
- **model/cubes/customer.yml:5-8**: Standard cube-to-cube join relationship pattern


