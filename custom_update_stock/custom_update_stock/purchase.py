import frappe


def before_validate(doc, method=None):
    """
    PURCHASE INVOICE RULE

    If:
    - At least one item MAINTAINS STOCK (Item.is_stock_item = 1)
    - AND NO Purchase Receipt exists against this Purchase Invoice

    Then:
    - Automatically check Update Stock
    """

    # --------------------------------------------------
    # 1. Detect stock-maintained items (from Item master)
    # --------------------------------------------------
    has_stock_item = False
    item_cache = {}

    for row in doc.items:
        if not row.item_code:
            continue

        if row.item_code not in item_cache:
            item_cache[row.item_code] = frappe.db.get_value(
                "Item",
                row.item_code,
                "is_stock_item"
            )

        if item_cache[row.item_code]:
            has_stock_item = True
            break

    # No stock items → do nothing
    if not has_stock_item:
        return

    # --------------------------------------------------
    # 2. Check if Purchase Receipt already exists
    # --------------------------------------------------
    pr_exists = False

    # Standard linkage
    if frappe.db.exists(
        "Purchase Receipt Item",
        {"against_purchase_invoice": doc.name}
    ):
        pr_exists = True

    # Fallback linkage
    if not pr_exists and frappe.db.exists(
        "Purchase Receipt Item",
        {"prevdoc_docname": doc.name}
    ):
        pr_exists = True

    # --------------------------------------------------
    # 3. Apply business rule
    # --------------------------------------------------
    # If NO Purchase Receipt exists → Update Stock must be checked
    if not pr_exists:
        doc.update_stock = 1
