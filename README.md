
# Smart Personal Finance & Expense Tracker (SPFET)

## Features
- Secure multi-user system: Register and log in (passwords hashed with PBKDF2)
- Per-user data isolation (JSON files)
- Add, view, and manage income/expense transactions
- Set/view monthly budgets per category, with real-time alerts if exceeded
- Statistics: category breakdowns, monthly trends, and graphs (matplotlib)
- Income and expense statistics shown separately
- Export transactions to CSV
- Professional GUI (Tkinter) with modern design
- Change password functionality
- Input validation and error handling throughout
- Modular, PEP8-compliant codebase

## Installation
1. Clone or download this repository.
2. Install Python 3.x and pip.
3. Install required packages:
   ```
   pip install matplotlib
   ```

## Usage
- **Run the GUI (recommended):**
  ```
  python -m spfet
  ```
- **Register/Login:**
  Use the GUI to register a new user or log in.
- **Main Menu:**
  - Add Transaction (income or expense)
  - View Transactions
  - Set/View Budgets
  - Show Statistics (with graphs for both income and expenses)
  - Export to CSV
  - Change Password
  - Logout

## Data Format
- Each user has a JSON file in the `data/` folder.
- Transactions, budgets, and authentication info are stored securely (passwords hashed, no plain text).

## Example Data
See the `data/` folder for sample user files after registration and usage.

