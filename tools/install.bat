taskkill /f /im MFAAvalonia.exe && timeout /T 1 /NOBREAK
python -u .\install.py ci win x86_64 && start ..\install\MFAAvalonia.exe