# Staging Data Model Metadata

Generated on: 2025-08-01 16:43:50 UTC
Environment: STAGING

## Overview

- **Total Entities**: 10
- **Cubes**: 8  
- **Views**: 2

## Data Model Relationships

- **customer**:
  - many-to-one → `nation`
- **lineitem**:
  - many-to-one → `orders`
  - many-to-one → `supplier`
  - many-to-one → `part`
- **nation**:
  - many-to-one → `region`
- **orders**:
  - many-to-one → `customer`
- **partsupp**:
  - many-to-one → `part`
  - many-to-one → `supplier`
- **supplier**:
  - many-to-one → `nation`

## Cubes

### Customer (`customer`)
*Source: cubes/customer.yml*

**Dimensions:**
- `Nationkey` (number)
- `Customer Account Balance` (number)
- `Customer Address` (string)
- `Customer Name` (string)
- `Customer Phone` (string)
- `Comment` (string)
- `Market Segment` (string)

**Measures:**
- `Count` (count)

**Joins:**
- many-to-one → `nation`

---

### Lineitem (`lineitem`)
*Source: cubes/lineitem.yml*

**Dimensions:**
- `Suppkey` (number)
- `Partkey` (number)
- `Ship Date` (time)
- `Commit Date` (time)
- `Receipt Date` (time)
- `Line Number` (number)
- `Quantity` (number)
- `Extended Price` (number)
- `Discount` (number)
- `Tax` (number)
- `Return Flag` (string)
- `Line Status` (string)
- `Ship Mode` (string)
- `Comment` (string)
- `Ship Instruct` (string)

**Measures:**
- `Count` (count)
- `Total Quantity` (sum)
- `Total Price` (sum)
- `Total Discount` (sum)
- `Total Tax` (sum)
- `Total Revenue` (number)
- `Total Profit` (number)
- `Supplier Sales Contribution` (number)
- `Avg Item Price` (avg)
- `Avg Discount Rate` (avg)

**Joins:**
- many-to-one → `orders`
- many-to-one → `supplier`
- many-to-one → `part`

**Pre-aggregations:** 1 defined

---

### Nation (`nation`)
*Source: cubes/nation.yml*

**Dimensions:**
- `Regionkey` (number)
- `Nation Name` (string)
- `Comment` (string)

**Measures:**
- `Count` (count)

**Joins:**
- many-to-one → `region`

---

### Orders (`orders`)
*Source: cubes/orders.yml*

**Dimensions:**
- `Custkey` (number)
- `Order Date` (time)
- `Previous Order Date` (time)
- `Total Price` (number)
- `Ship Priority` (number)
- `Comment` (string)
- `Order Priority` (string)
- `Order Status` (string)
- `Clerk` (string)

**Measures:**
- `Count` (count)

**Joins:**
- many-to-one → `customer`

---

### Part (`part`)
*Source: cubes/part.yml*

**Dimensions:**
- `Retail Price` (number)
- `Size` (number)
- `Comment` (string)
- `Part Type` (string)
- `Container` (string)
- `Part Brand` (string)
- `Part Name` (string)
- `Manufacturer` (string)

**Measures:**
- `Count` (count)

---

### Partsupp (`partsupp`)
*Source: cubes/partsupp.yml*

**Dimensions:**
- `Partkey` (number)
- `Supply Cost` (number)
- `Available Quantity` (number)
- `Comment` (string)

**Measures:**
- `Count` (count)
- `Total Supply Cost` (sum)
- `Total Available Quantity` (sum)
- `Avg Supply Cost` (avg)
- `Total Inventory Value` (number)

**Joins:**
- many-to-one → `part`
- many-to-one → `supplier`

---

### Region (`region`)
*Source: cubes/region.yml*

**Dimensions:**
- `Comment` (string)
- `Region Name` (string)

**Measures:**
- `Count` (count)

---

### Supplier (`supplier`)
*Source: cubes/supplier.yml*

**Dimensions:**
- `Nationkey` (number)
- `Supplier Account Balance` (number)
- `Comment` (string)
- `Supplier Phone` (string)
- `Supplier Name` (string)
- `Supplier Address` (string)

**Measures:**
- `Count` (count)
- `Total Account Balance` (sum)
- `Avg Account Balance` (avg)

**Joins:**
- many-to-one → `nation`

---

## Views

### Item Information (`item_information`)
*Type: View*

**Available Measures:**
- `Total Quantity` (sum)
- `Total Discount` (sum)
- `Total Price` (sum)
- `Total Profit` (number)
- `Total Revenue` (number)
- `Count` (count)

**Available Dimensions:**
- `Ship Date` (time)
- `Line Status` (string)
- `Return Flag` (string)
- `Quantity` (number)
- `Extended Price` (number)
- `Ship Mode` (string)
- `Ship Instruct` (string)
- `Supplier Name` (string)
- `Part Name` (string)
- `Part Type` (string)
- `Order Status` (string)
- `Customer Name` (string)
- `Market Segment` (string)
- `Nation Name` (string)
- `Region Name` (string)

---

### Supplier Sales Analysis (`supplier_sales_analysis`)
*Type: View*

**Available Measures:**
- `Supplier Sales Contribution` (number)
- `Total Quantity` (sum)
- `Total Revenue` (number)
- `Total Profit` (number)
- `Avg Item Price` (avg)
- `Avg Discount Rate` (avg)
- `Count` (count)
- `Total Account Balance` (sum)
- `Avg Account Balance` (avg)

**Available Dimensions:**
- `Suppkey` (number)
- `Partkey` (number)
- `Ship Date` (time)
- `Quantity` (number)
- `Extended Price` (number)
- `Discount` (number)
- `Supplier Name` (string)
- `Supplier Account Balance` (number)
- `Part Name` (string)
- `Part Type` (string)
- `Part Brand` (string)
- `Manufacturer` (string)
- `Retail Price` (number)
- `Nation Name` (string)
- `Order Date` (time)
- `Total Price` (number)
- `Order Status` (string)
- `Customer Name` (string)
- `Market Segment` (string)

---

