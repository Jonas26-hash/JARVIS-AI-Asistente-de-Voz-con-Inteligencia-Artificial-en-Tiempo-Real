' J.A.R.V.I.S — Lanzador sin consola
Option Explicit
Dim ws, fso, d, py, cmd
Set ws  = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
d = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
py = d & ".venv\Scripts\pythonw.exe"
If Not fso.FileExists(py) Then
    py = d & ".venv\Scripts\python.exe"
End If
If Not fso.FileExists(py) Then
    MsgBox "JARVIS: ejecuta JARVIS_Beta_Installer.exe primero.", 16, "JARVIS"
    WScript.Quit 1
End If
cmd = Chr(34) & py & Chr(34) & " " & Chr(34) & d & "main.py" & Chr(34)
ws.Run cmd, 0, False
Set ws  = Nothing
Set fso = Nothing
