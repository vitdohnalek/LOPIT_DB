#!/bin/bash

# Configuration
DB_NAME="lopit_db"
BACKUP_DIR="/tmp/db_backups"
S3_BUCKET="s3://first-floor-lab/vitek"
S3_PATH="database-backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${DB_NAME}_${TIMESTAMP}.sql"
BACKUP_FILE_GZ="${BACKUP_FILE}.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}Starting database backup...${NC}"

# Dump the database
echo "Dumping database: $DB_NAME"
mysqldump --no-tablespaces "$DB_NAME" > "$BACKUP_DIR/$BACKUP_FILE"

# Check if dump was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Database dump failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Database dump completed successfully${NC}"

# Compress the backup
echo "Compressing backup file..."
gzip "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Compression failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Compression completed${NC}"

# Upload to S3
echo "Uploading to S3..."
s3cmd put "$BACKUP_DIR/$BACKUP_FILE_GZ" "$S3_BUCKET/$S3_PATH/$BACKUP_FILE_GZ"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: S3 upload failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Upload to S3 completed successfully${NC}"

# Remove local backup file
echo "Cleaning up local backup..."
rm "$BACKUP_DIR/$BACKUP_FILE_GZ"

echo -e "${GREEN}Backup process completed!${NC}"
echo "Backup file: $BACKUP_FILE_GZ"
echo "S3 location: $S3_BUCKET/$S3_PATH/$BACKUP_FILE_GZ"

# Optional: Keep only last N backups in S3 (uncomment to use)
# KEEP_BACKUPS=3
# s3cmd ls "$S3_BUCKET/$S3_PATH/" | sort -r | tail -n +$((KEEP_BACKUPS + 1)) | awk '{print $4}' | xargs -I {} s3cmd del {}
