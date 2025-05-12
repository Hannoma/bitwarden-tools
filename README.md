# Bitwarden Cleanup & Merge Tool

A Python-based command-line utility designed to clean up and enhance your Bitwarden vault exports. This tool helps you deduplicate login entries, merge passwords from a Google Chrome CSV export, and interactively consolidate entries that share common credentials across different services.

## Features

*   **Deduplicate Bitwarden Entries:** Automatically identifies and merges duplicate login items based on a combination of domain, username, and password. Unique URIs from duplicates are consolidated into a single entry.
*   **Merge Chrome Passwords:** Import passwords from a Google Chrome CSV export and seamlessly merge them into your Bitwarden data, applying the same deduplication logic.
*   **Interactive Common Credential Consolidation:** Identifies groups of login entries that share the exact same username and password (even if for different domains). It then interactively prompts you to:
    *   Choose a primary entry for the group.
    *   Merge other entries in the group into the chosen primary, consolidating their URIs.
*   **Preserves Vault Structure:** Non-login items (like notes, cards) and other vault metadata (folders, etc.) from your original Bitwarden export are preserved and included in the cleaned output.
*   **Enhanced CLI Output:** Uses the `rich` library for clear and user-friendly tables, prompts, and logging in the terminal.
*   **Merge Decision Caching:** Remembers your decisions during the interactive common credential merge process, allowing for easier re-runs if you update your vault export.

## Requirements

*   Python 3.8+
*   `rich` library (for the enhanced terminal interface)

## Installation

1.  **Clone the repository or download the source code.**
2.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1.  **Prepare your Bitwarden export and Chrome CSV files.**
    *   Ensure your Bitwarden export is in JSON format.
    *   Ensure your Chrome CSV export is in CSV format.
    *  Place both files in the same directory as the script or provide their paths when prompted.

2.  **Run the script:**
    ```bash
    python bitwarden_cleanup.py INPUT_FILE.json -c CHROME_FILE.csv -o OUTPUT_FILE.json
    ```
    Replace `INPUT_FILE.json` with your Bitwarden export file, `CHROME_FILE.csv` with your Chrome CSV file, and `OUTPUT_FILE.json` with the desired output filename.
3. **Follow the prompts:**
    *   The script will guide you through the deduplication and merging process.
    *   You can choose to skip or merge entries interactively.
    *  The script will display a summary of the changes made and the final output file location.
    *  The script will also cache your decisions for future runs, allowing you to skip the interactive prompts if desired.
4. **Review the output:**
    *   The cleaned and merged Bitwarden export will be saved in the specified output file.
    *   You can import this file back into Bitwarden for a cleaner vault (Purge existing vault items before importing).

## How it works
* **Data Representation:** Uses Python dataclasses (BitwardenEntry, LoginData, UriEntry) for type-safe handling of Bitwarden data.
* **Deduplication Logic:**
  * Login items are considered duplicates if they share the same normalized domain (e.g., www.example.com and example.com are treated as the same), username, and password.
  * When duplicates are found, the merge method on the BitwardenEntry class is used to consolidate URIs from the source entry into the target entry, avoiding duplicate URIs within the merged entry. URIs are also shortened (query parameters/fragments removed) during this process.
* **Common Credential Grouping:** After the initial deduplication, the tool groups entries solely by matching username and password. This helps identify situations where the same credential is used across entirely different websites/services.
* **BitwardenWrapper:** The BitwardenWrapper class handles loading the full JSON export, separating login items for processing, and then re-integrating them with other item types (notes, cards, etc.) and vault metadata (folders) before saving. This ensures that only login items are modified and the rest of your vault structure remains intact.

## Contributing
Contributions are welcome! If you find a bug or have a feature request, please open an issue on GitHub. Pull requests are also welcome.