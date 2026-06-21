' telegram_bot.vbs — Lanzador sin consola para telegram_bot.py
Dim shell, fso, base, python, script
Set fso = CreateObject("Scripting.FileSystemObject")
base = fso.GetParentFolderName(WScript.ScriptFullName)
python = base & "\.venv\Scripts\python.exe"
script = base & "\telegram_bot.py"
Set shell = CreateObject("WScript.Shell")
shell.Run """" & python & """ """ & script & """", 0, False
Set shell = Nothing
Set fso = Nothing
