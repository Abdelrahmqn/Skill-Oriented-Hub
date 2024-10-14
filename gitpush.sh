#!/bin/bash

# Specify the file that contains the commit message
commit_file="commitMsg.txt"

# Check if the commit message file exists
if [ ! -f "$commit_file" ]; then
    echo "Commit message file '$commit_file' does not exist. Please create it and add your message."
    exit 1
fi

# Read the commit message from the file
commit=$(<"$commit_file")

# Stage all changes
git add .

# Commit with the message from the file
git commit -m "${commit}"

# Push the changes to the remote repository
git push

# Clear the commit message file and add the recommended structure
cat <<EOL > "$commit_file"

A brief summary of the changes (50 characters or less).

## Details
A more detailed explanation of the changes, including:
- What was changed and why
- Any relevant context or background information
- Impact on the system or users

## Related Issues
- List any related issue numbers or links (if applicable):
  - Issue #123
  - Issue #456

## Changes Made
- Bullet points summarizing the main changes:
  - Added feature X
  - Fixed bug Y
  - Updated documentation for Z
EOL

echo "The commit message file has been cleared and reset to the recommended structure."
