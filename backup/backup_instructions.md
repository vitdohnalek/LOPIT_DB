# Database Backup to S3 - Setup Instructions

This guide will help you set up and run the automated database backup script for `lopit_db`.

## Prerequisites

- MySQL installed
- `s3cmd` installed
- Access to an S3-compatible storage service (CESNET S3)
- Database user credentials

## Step 1: Configure MySQL Credentials

Create or edit the `~/.my.cnf` file to store your MySQL credentials securely:

```bash
vim ~/.my.cnf
```

Add the following content:

```ini
[client]
user=your_username
password=your_password

[mysqldump]
user=your_username
password=your_password
```

Replace `your_username` and `your_password` with your actual MySQL credentials.

### Secure the file

Set proper permissions to protect your credentials:

```bash
chmod 600 ~/.my.cnf
```

This ensures only your user can read the file.

## Step 2: Install and Configure s3cmd

### Install s3cmd

```bash
sudo apt-get update
sudo apt-get install s3cmd
```

### Configure s3cmd

Create or edit the `/home/user/.s3cfg` file to store the s3cmd configuration:

```bash
vim /home/user/.s3cfg
```
Add the following content:

```ini
[default]
host_base = https://s3.clX.du.cesnet.cz
use_https = True
access_key = xxxxxxxxxxxxxxxxxxxxxx
secret_key = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
host_bucket = s3.clX.du.cesnet.cz
```

Test the configuration:

```bash
s3cmd ls
```

This should list your S3 buckets if configured correctly.

## Step 3: Configure the Backup Script

Edit the backup script and update these variables:

```bash
vim lopit_backup_s3.sh
```

Configure:
- `S3_BUCKET`: Your S3 bucket name (e.g., `s3://my-backup-bucket`)
- `S3_PATH`: Folder path inside the bucket (e.g., `database-backups`)
- `BACKUP_DIR`: Local temporary directory (default: `/tmp/db_backups`)

## Step 4: Make the Script Executable

```bash
chmod +x lopit_backup_s3.sh
```

## Step 5: Run the Backup

Execute the script:

```bash
./lopit_backup_s3.sh
```

The script will:
1. Dump the `lopit_db` database to SQL
2. Compress the dump file with gzip
3. Upload to S3
4. Clean up local files
5. Display the S3 location of the backup

## Step 6: Automate with Cron (Optional)

To run backups automatically, add a cron job:

```bash
crontab -e
```

Add this line:

**Weekly on Sunday at 3 AM:**
```
0 3 * * 0 /path/to/lopit_backup_s3.sh >> /var/log/db_backup.log 2>&1
```

Replace `/path/to/lopit_backup_s3.sh` with the actual path to your script.

