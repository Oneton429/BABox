taskkill /f /im MFAAvalonia.exe && timeout /T 1 /NOBREAK
python -u .\install.py v1.0.3 win x86_64 && start ..\install\MFAAvalonia.exe