import frappe


def before_validate(doc, method=None):
    """
    SALES INVOICE RULE

    If:
    - At least one item MAINTAINS STOCK (Item.is_stock_item = 1)
    - AND NO Delivery Note exists against this Sales Invoice

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
    # 2. Check if Delivery Note already exists
    # --------------------------------------------------
    dn_exists = False

    # Standard linkage
    if frappe.db.exists(
        "Delivery Note Item",
        {"against_sales_invoice": doc.name}
    ):
        dn_exists = True

    # Fallback linkage (older flows)
    if not dn_exists and frappe.db.exists(
        "Delivery Note Item",
        {"prevdoc_docname": doc.name}
    ):
        dn_exists = True

    # --------------------------------------------------
    # 3. Apply business rule
    # --------------------------------------------------
    # If NO Delivery Note exists → Update Stock must be checked
    if not dn_exists:
        doc.update_stock = 1
