#!/bin/bash

# Expands an .env.example file by fetching secrets from Bitwarden
#
# Usage: ./expand_env.sh <input.env.example> [output.env]
#
# Values with bw: prefix are fetched from Bitwarden. Plain values pass through unchanged.
#
# Syntax:
#   VAR=bw:<item-name>                    # Gets the password field
#   VAR=bw:<item-name>/password           # Gets the password field (explicit)
#   VAR=bw:<item-name>/username           # Gets the username field
#   VAR=bw:<item-name>/notes              # Gets the secure notes
#   VAR=bw:<item-name>/uri                # Gets the first URI
#   VAR=bw:<item-name>/field/<field-name> # Gets a custom field by name
#
# Requirements:
#   - Bitwarden CLI: brew install bitwarden-cli
#   - jq: brew install jq
#   - Must be logged in: bw login

set -e

# =============================================================================
# CONFIGURATION: BW_FOLDER is read from the input .env file, or falls back
# to the BW_FOLDER env var, or defaults to "Lavender"
# =============================================================================
# BW_FOLDER is set after parsing input file (see extract_bw_folder function)
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <input.env.example> [output.env]${NC}"
    echo ""
    echo "If output.env is not specified, the result is printed to stdout."
    echo "Secrets are fetched from Bitwarden folder: $BW_FOLDER"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-}"

# Will be populated after vault is unlocked
FOLDER_ID=""

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}Error: Input file '$INPUT_FILE' not found${NC}"
    exit 1
fi

# Extract BW_FOLDER from input file (priority: input file > env var > default)
extract_bw_folder() {
    local file="$1"
    local folder_value

    # Look for BW_FOLDER= line in the input file
    folder_value=$(grep -E '^BW_FOLDER=' "$file" 2>/dev/null | head -1 | cut -d'=' -f2-)

    # Remove surrounding quotes if present
    folder_value="${folder_value#\"}"
    folder_value="${folder_value%\"}"
    folder_value="${folder_value#\'}"
    folder_value="${folder_value%\'}"

    if [ -n "$folder_value" ]; then
        echo "$folder_value"
    elif [ -n "$BW_FOLDER" ]; then
        echo "$BW_FOLDER"
    else
        echo "Lavender"
    fi
}

BW_FOLDER=$(extract_bw_folder "$INPUT_FILE")

# Check if bw CLI is installed
if ! command -v bw &> /dev/null; then
    echo -e "${RED}Error: Bitwarden CLI (bw) is not installed${NC}"
    echo "Install it with: brew install bitwarden-cli"
    exit 1
fi

# Check if jq is installed (needed for parsing JSON)
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is not installed${NC}"
    echo "Install it with: brew install jq"
    exit 1
fi

# Check login status
LOGIN_STATUS=$(bw status | jq -r '.status')

if [ "$LOGIN_STATUS" = "unauthenticated" ]; then
    echo -e "${RED}Error: Not logged in to Bitwarden${NC}"
    echo "Run: bw login"
    exit 1
fi

# Check if vault is unlocked, prompt to unlock if needed
if [ "$LOGIN_STATUS" = "locked" ]; then
    echo -e "${YELLOW}Bitwarden vault is locked. Unlocking...${NC}"

    # Check if BW_SESSION is already set
    if [ -z "$BW_SESSION" ]; then
        BW_SESSION=$(bw unlock --raw)
        if [ -z "$BW_SESSION" ]; then
            echo -e "${RED}Error: Failed to unlock vault${NC}"
            exit 1
        fi
        export BW_SESSION
    fi
fi

# Sync vault to get latest data
echo -e "${YELLOW}Syncing Bitwarden vault...${NC}" >&2
bw sync > /dev/null 2>&1

# Cache folder list JSON (fetched once)
FOLDERS_JSON=""

# Function to get folder ID from folder name
get_folder_id() {
    local folder_name="$1"

    # Empty folder name means no folder filter
    if [ -z "$folder_name" ]; then
        echo ""
        return 0
    fi

    # Fetch folders list once and cache it
    if [ -z "$FOLDERS_JSON" ]; then
        FOLDERS_JSON=$(bw list folders 2>/dev/null)
    fi

    # Look up folder by name
    local folder_id
    folder_id=$(echo "$FOLDERS_JSON" | jq -r --arg name "$folder_name" '.[] | select(.name == $name) | .id' | head -1)

    if [ -z "$folder_id" ] || [ "$folder_id" = "null" ]; then
        echo -e "${RED}Error: Could not find Bitwarden folder '$folder_name'${NC}" >&2
        return 1
    fi

    echo "$folder_id"
}

# Resolve folder ID
echo -e "${YELLOW}Using Bitwarden folder: $BW_FOLDER${NC}" >&2
FOLDER_ID=$(get_folder_id "$BW_FOLDER") || exit 1

# Function to fetch a secret from Bitwarden
fetch_bw_secret() {
    local bw_ref="$1"

    # Remove the "bw:" prefix
    local ref="${bw_ref#bw:}"

    # Parse item name and field
    local item_name
    local field_type
    local field_name

    if [[ "$ref" == *"/field/"* ]]; then
        # Custom field: item-name/field/field-name
        item_name="${ref%%/field/*}"
        field_type="field"
        field_name="${ref#*/field/}"
    elif [[ "$ref" == *"/"* ]]; then
        # Standard field: item-name/field-type
        item_name="${ref%/*}"
        field_type="${ref##*/}"
        field_name=""
    else
        # Just item name, default to password
        item_name="$ref"
        field_type="password"
        field_name=""
    fi

    # Fetch the item from the configured folder
    local item_json
    item_json=$(bw list items --folderid "$FOLDER_ID" 2>/dev/null | jq -r --arg name "$item_name" '[.[] | select(.name == $name)] | first')

    if [ -z "$item_json" ] || [ "$item_json" = "null" ]; then
        echo -e "${RED}Error: Could not find Bitwarden item '$item_name' in folder '$BW_FOLDER'${NC}" >&2
        return 1
    fi

    local value
    case "$field_type" in
        "password")
            value=$(echo "$item_json" | jq -r '.login.password // empty')
            ;;
        "username")
            value=$(echo "$item_json" | jq -r '.login.username // empty')
            ;;
        "uri")
            value=$(echo "$item_json" | jq -r '.login.uris[0].uri // empty')
            ;;
        "notes")
            value=$(echo "$item_json" | jq -r '.notes // empty')
            ;;
        "field")
            value=$(echo "$item_json" | jq -r --arg name "$field_name" '.fields[]? | select(.name == $name) | .value // empty')
            ;;
        *)
            echo -e "${RED}Error: Unknown field type '$field_type'${NC}" >&2
            return 1
            ;;
    esac

    if [ -z "$value" ] || [ "$value" = "null" ]; then
        echo -e "${RED}Error: Could not extract '$field_type${field_name:+/$field_name}' from item '$item_name'${NC}" >&2
        return 1
    fi

    echo "$value"
}

# Process the input file
process_env_file() {
    local output=""
    local line_num=0
    local errors=0

    while IFS= read -r line || [ -n "$line" ]; do
        ((line_num++))

        # Skip empty lines and comments
        if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
            output+="$line"$'\n'
            continue
        fi

        # Check if line is a variable assignment
        if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
            local var_name="${BASH_REMATCH[1]}"
            local var_value="${BASH_REMATCH[2]}"

            # Remove surrounding quotes if present
            var_value="${var_value#\"}"
            var_value="${var_value%\"}"
            var_value="${var_value#\'}"
            var_value="${var_value%\'}"

            # Check if value is a Bitwarden reference
            if [[ "$var_value" =~ ^bw: ]]; then
                echo -e "${YELLOW}Fetching ${var_name} from Bitwarden...${NC}" >&2
                local secret
                if secret=$(fetch_bw_secret "$var_value"); then
                    # Quote the value if it contains special characters
                    if [[ "$secret" =~ [[:space:]\"\'\$\`\\] ]]; then
                        output+="${var_name}=\"${secret}\""$'\n'
                    else
                        output+="${var_name}=${secret}"$'\n'
                    fi
                    echo -e "${GREEN}✓ ${var_name}${NC}" >&2
                else
                    echo -e "${RED}✗ ${var_name} (line $line_num): Failed to fetch from Bitwarden${NC}" >&2
                    ((errors++))
                    # Keep the original line as a comment so it's visible
                    output+="# FAILED: $line"$'\n'
                fi
            else
                # Not a Bitwarden reference, keep as-is
                output+="$line"$'\n'
            fi
        else
            # Not a variable assignment, keep as-is
            output+="$line"$'\n'
        fi
    done < "$INPUT_FILE"

    # Remove trailing newline
    output="${output%$'\n'}"

    if [ $errors -gt 0 ]; then
        echo -e "${RED}Warning: $errors secret(s) failed to fetch${NC}" >&2
    fi

    echo "$output"
}

# Main execution
echo -e "${GREEN}Processing $INPUT_FILE...${NC}" >&2

RESULT=$(process_env_file)

if [ -n "$OUTPUT_FILE" ]; then
    echo "$RESULT" > "$OUTPUT_FILE"
    echo -e "${GREEN}Output written to $OUTPUT_FILE${NC}" >&2
else
    echo "$RESULT"
fi
