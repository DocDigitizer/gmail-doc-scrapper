# Invoice Classification Algorithm Explained

This document explains exactly how the Gmail Document Scraper classifies documents as invoices.

## Overview

The classifier uses a **3-tier hybrid approach** combining:
1. **Pattern Matching** (Regex) - Most reliable
2. **NLP Entity Recognition** (spaCy) - Context understanding
3. **Keyword Matching** (Fallback) - Simple word counting

All methods run independently, and the **best result** (highest confidence) wins.

---

## Classification Rules for Invoices

### From `config/rules.yaml`:

```yaml
invoices:
  display_name: "Invoices"

  keywords: [15 keywords]
    - invoice, bill, fatura, receipt, nota fiscal
    - NIF, NIPC
    - total to pay, total amount, total a pagar, valor total
    - VAT, IVA, tax, impostos

  patterns: [4 regex patterns]
    - Invoice #123
    - Fatura Nº 123
    - NIF: 123456789
    - Total: €150.00

  entities: [3 NLP entities]
    - MONEY   (amounts like €150.00)
    - ORG     (company names)
    - DATE    (dates like 2024-12-31)

  confidence_boost: 0.1  # Extra 10% if patterns match
```

---

## How It Works - Step by Step

### Step 1: Extract Text

Extracts all text from PDF or DOCX document.

**Example extracted text:**
```
FATURA Nº 2024/001
Data: 31/12/2024
Cliente: ABC Company
NIF: 123456789

Descrição         Quantidade    Preço
Serviços IT       1             €1,500.00

Subtotal:                       €1,500.00
IVA (23%):                      €345.00
Total a Pagar:                  €1,845.00
```

### Step 2: Run 3 Classification Methods

#### **Method 1: Pattern Matching** ⭐ Most Important

Searches for specific regex patterns:

**Patterns checked:**
- ✅ `Fatura Nº 2024/001` → Matches "Fatura\\s+N[ºo.:]?\\s*\\d+"
- ✅ `NIF: 123456789` → Matches "NIF\\s*:?\\s*\\d{9}"
- ✅ `Total a Pagar: €1,845.00` → Matches "Total.*€.*\\d+"
- ❌ `Invoice #` → Not found (Portuguese invoice)

**Calculation:**
```
3 patterns matched out of 4 total
confidence = (3/4) × 0.8 + 0.2 = 0.80  (80%)
confidence = 0.80 + 0.1 boost = 0.90   (90%)
```

**Result:** invoices (90% confidence, method: pattern)

#### **Method 2: NLP Entity Recognition** (If available)

Uses spaCy to find entities:

**Entities found:**
- ✅ MONEY: €1,500.00, €345.00, €1,845.00
- ✅ ORG: ABC Company
- ✅ DATE: 31/12/2024

**Calculation:**
```
3 entities found out of 3 required
confidence = (3/3) × 0.7 + 0.2 = 0.90  (90%)
confidence = 0.90 + 0.1 boost = 1.00   (100%, capped)
```

**Result:** invoices (100% confidence, method: nlp)

#### **Method 3: Keyword Matching** (Fallback)

Counts keyword occurrences:

**Keywords found:**
- ✅ fatura
- ✅ NIF
- ✅ total a pagar
- ✅ IVA

**Calculation:**
```
4 keywords found out of 15 total
confidence = (4/15) × 0.6 + 0.15 = 0.31  (31%)
```

**Result:** invoices (31% confidence, method: keyword)

### Step 3: Select Best Result

```
Results from 3 methods:
- Pattern: 90%
- NLP: 100%
- Keyword: 31%

Best result: NLP with 100% confidence

Threshold check: 100% >= 70% ✅

FINAL: Classified as "invoices"
       (confidence: 100%, method: nlp)
```

---

## Confidence Formulas

### Pattern Matching
```
Base confidence = (patterns_matched / total_patterns) × 0.8 + 0.2
Final confidence = min(0.95, base + confidence_boost)
```

### NLP Entity Recognition
```
Base confidence = (entities_found / required_entities) × 0.7 + 0.2
Final confidence = min(1.0, base + confidence_boost)
```

### Keyword Matching
```
confidence = (keywords_found / total_keywords) × 0.6 + 0.15
Max confidence = 0.85 (no boost)
```

---

## Decision Threshold

**Default: 70% confidence required**

Can be changed in `config/config.yaml`:
```yaml
classification:
  confidence_threshold: 0.7  # Change to 0.8 for stricter
```

| Confidence | Classification |
|------------|----------------|
| 90% | ✅ Invoice |
| 75% | ✅ Invoice |
| 65% | ❌ Rejected (below 70%) |
| 50% | ❌ Rejected |

---

## Real Examples

### Example 1: Portuguese Invoice ✅

**Text:** "FATURA Nº 2024/123, NIF: 501234567, Total: 250,00 EUR"

- Pattern match: Fatura Nº, NIF, Total → **90%**
- Keywords: fatura, NIF → **25%**
- **Decision: Invoice (90%)**

### Example 2: English Invoice ✅

**Text:** "INVOICE #456, Tax ID: 123456789, Total Amount: $1,200.00"

- Pattern match: Invoice #, Total → **85%**
- Keywords: invoice, total amount → **20%**
- **Decision: Invoice (85%)**

### Example 3: Email Body ❌

**Text:** "Hi, please see the attached invoice for review. Thanks!"

- Pattern match: None → **0%**
- Keywords: invoice → **7%**
- **Decision: NOT classified (below 70%)**

### Example 4: Contract ❌

**Text:** "This contract...payment upon invoice...Party A agrees..."

- Pattern match: contract patterns matched → **82%**
- **Decision: Contract (not invoice)**

---

## What Makes a Good Invoice Detection

✅ **Strong indicators:**
- "Fatura Nº" or "Invoice #" with number
- NIF/Tax ID with 9 digits
- Total amount with currency symbol
- Date in header
- Company name

❌ **Weak indicators:**
- Just the word "invoice" in text
- Email discussing invoices
- References to invoices in contracts

---

## Tuning the Classification

### Make it Stricter (fewer false positives):

**Option 1:** Increase threshold
```yaml
# config/config.yaml
classification:
  confidence_threshold: 0.85  # Require 85%
```

**Option 2:** Add more specific patterns
```yaml
# config/rules.yaml
patterns:
  - "Invoice\\s+Date"
  - "Due\\s+Date"
```

### Make it More Lenient (catch more):

**Option 1:** Decrease threshold
```yaml
classification:
  confidence_threshold: 0.6  # Accept 60%
```

**Option 2:** Add more keywords
```yaml
keywords:
  - payment
  - billing
  - charge
```

---

## Why This Approach Works

✅ **Multi-method** - Not reliant on single approach
✅ **Language-agnostic** - Works with PT, EN, ES
✅ **Structure-aware** - Patterns catch invoice formats
✅ **Context-aware** - NLP understands document meaning
✅ **Tunable** - Easy to adjust via config files
✅ **Transparent** - Shows confidence and method used

---

## Current Configuration

**Thresholds:**
- Minimum confidence: **70%**
- Minimum text length: **100 characters**
- Pattern confidence boost: **+10%**

**Priority:**
1. Pattern matching (most reliable)
2. NLP entity recognition (if available)
3. Keyword matching (fallback)

**Best method wins** - Highest confidence is selected

---

## Summary

**To classify as invoice, the document must:**

1. ✅ Have extractable text (PDF/DOCX)
2. ✅ Match invoice patterns OR contain invoice entities
3. ✅ Score >= 70% confidence
4. ✅ Beat confidence scores of other document types

**The algorithm ensures:**
- Accurate classification using multiple methods
- Transparent confidence scoring
- Easy customization via YAML configs
- Support for multiple languages and formats

---

**Want to customize?** Edit:
- `config/rules.yaml` - Add patterns, keywords, entities
- `config/config.yaml` - Adjust confidence threshold
