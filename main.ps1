.\.venv\Scripts\activate
$timestamp = Get-Date -Format o | ForEach-Object { $_ -replace ":", "." }
python main.py > scraper_log_$timestamp.log