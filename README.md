# IoTBay — Device Ordering Web App

A full-stack web application for ordering IoT devices, built as a group project.
This repo reflects my individual contributions to the codebase.

## My Contributions

**Order Management** — Designed and implemented the full order feature end-to-end, covering data modelling (`order.py`, `order_item.py`), CRUD API routes (routes/api/order.py, templates/order/)
- Implemented a workflow where users add to their orders from the device    catalogue,then proceed to checkout (`routes/api/order.py`).
- Modelled `OrderItem` as a join between `Order` and `Device`, storing both foreign keys to link ordered devices back to their respective orders.
- Built per-item quantity controls in the device catalogue row (`templates/device/row.html`), with each line mapping to an `OrderItem` record on submission.
- Rendered order listings in `templates/order/`, with role-based visibility: 
  staff can view all orders while customers are restricted to their own.
  Users can edit, cancel, or proceed to a dummy payment for each order.

## Tech Stack
Python · Flask · HTMX · Peewee ORM · SQLite

## Getting Started
1. Clone the repo
2. uv sync
3. uv run dev