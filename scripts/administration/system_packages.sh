

# Check for python3.12
if ! command -v python3.12 &> /dev/null; then
  echo "python3.12 not found. Attempting to install..."

  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt &> /dev/null; then
      sudo apt update
      sudo apt install -y python3.12
    else
      echo "apt not found. Please install Python 3.12 manually."
      exit 1
    fi
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &> /dev/null; then
      brew install python@3.12
    else
      echo "Homebrew not found. Please install Python 3.12 manually."
      exit 1
    fi
  else
    echo "Unsupported OS. Please install Python 3.12 manually."
    exit 1
  fi
fi

# Check for yarn
if ! command -v yarn &> /dev/null; then
  echo "yarn not found. Attempting to install..."

  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt &> /dev/null; then
      sudo apt update
      sudo apt install -y yarn
    else
      echo "apt not found. Please install yarn manually."
      exit 1
    fi
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &> /dev/null; then
      brew install yarn
    else
      echo "Homebrew not found. Please install yarn manually."
      exit 1
    fi
  else
    echo "Unsupported OS. Please install yarn manually."
    exit 1
  fi
fi