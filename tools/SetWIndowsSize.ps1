Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
}
"@

# 替换为你目标窗口的部分或完整标题
$windowTitle = "Blue Archive"

# 支持部分窗口标题匹配，改用 Get-Process 获取主窗口句柄
$hwnd = (Get-Process | Where-Object { $_.MainWindowTitle -and $_.MainWindowTitle -like "*$windowTitle*" } | Select-Object -First 1).MainWindowHandle

if ([IntPtr]$hwnd -ne [IntPtr]::Zero) {
    # 设置窗口位置 (X=100, Y=100) 和大小 (宽=1280, 高=720)
    Add-Type -AssemblyName System.Windows.Forms
    $screen = [System.Windows.Forms.Screen]::FromHandle([IntPtr]$hwnd)
    $monitorBounds = $screen.Bounds

    $targetWidth = 1280 / 1.5
    $targetHeight = 720 / 1.5

    # 在目标显示器内选择相对于显示器左上角偏移 (100,100)，并确保不会超出显示器边界
    $desiredX = $monitorBounds.Left + 100
    $desiredY = $monitorBounds.Top + 100

    $targetX = [Math]::Max($monitorBounds.Left, [Math]::Min($monitorBounds.Right - $targetWidth, $desiredX))
    $targetY = [Math]::Max($monitorBounds.Top,  [Math]::Min($monitorBounds.Bottom - $targetHeight, $desiredY))

    [Win32]::MoveWindow($hwnd, $targetX, $targetY, $targetWidth, $targetHeight, $true)
    Write-Host "窗口已调整为 1280x720"
} else {
    Write-Host "未找到窗口: $windowTitle"
}