# IOTBay Marketplace

IOT marketplace app by Savio, Tomas, Felix, Jonathan, Brad and Charlie.

For teammates - read [CONTRIBUTING.md](https://github.com/isd-2026/project-assignment-iotbay-marketplace-superawesometeamname/blob/main/CONTRIBUTING.md) to learn how to set up the project and make changes.

## Tutor Guide

Follow this guide if you are a tutor to run and test the program.

| Step | MacOS/Linux | Windows |
| :--- | :--- | :--- |
| Run the program | <pre><code>curl -LsSf https://f.tomasvana.dev/isd/run.sh \| sh</code></pre> | <pre><code>powershell -ExecutionPolicy ByPass -c "irm https://f.tomasvana.dev/isd/run.ps1 \| iex"</code></pre> |
| Test the program | <pre><code>curl -LsSf https://f.tomasvana.dev/isd/test.sh \| sh</code></pre> | <pre><code>powershell -ExecutionPolicy ByPass -c "irm https://f.tomasvana.dev/isd/test.ps1 \| iex"</code></pre> |
| Remove `uv` (optional) | <pre><code>curl -LsSf https://f.tomasvana.dev/isd/rm-uv.sh \| sh</code></pre> | <pre><code>powershell -ExecutionPolicy ByPass -c "irm https://f.tomasvana.dev/isd/rm-uv.ps1 \| iex"</code></pre> |


## Project Reference

### Directories

| Path | Description |
|---|---|
| `iotbay/` | Source code for the iotbay marketplace |
| `iotbay/model/` | Database table definitions using Peewee ORM |
| `iotbay/routes/` | Page routes and blueprint registration |
| `iotbay/routes/api/` | REST API endpoints for features |
| `iotbay/templates/` | HTML pages |
| `iotbay/templates/static/` | CSS and JavaScript assets |
| `tests/` | Feature tests |

### Features

| ID | Feature | `model/` files | `routes/api/` files | `templates/` files |
|---|---|---|---|---|
| 00 | User Registration and Auth | `user.py` | `api/auth.py`, `api/user.py` | `register.html`, `sign-in.html`, `account.html` |
| 01 | User Access Logs | `access_log.py` | `api/user.py` | `account.html` |
| 02 | IoT Device Catalogue | `device.py` | `api/device.py` | `home.html` |
| 03 | Orders | `order.py`, `order_item.py` | `api/order.py` | `orders.html` |
| 04 | Payment Methods | `payment_method.py` | `api/payment_method.py` | `account.html` |
| 05 | Payments | `payment.py` | `api/payment.py` | `orders.html` |
