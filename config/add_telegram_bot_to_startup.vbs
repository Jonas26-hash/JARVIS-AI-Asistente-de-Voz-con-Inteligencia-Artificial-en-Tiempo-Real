' add_telegram_bot_to_startup.vbs — Agrega telegram_bot.vbs al inicio de Windows
Dim shell, fso, startup, project, shortcut, vbs_path
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Obtener la raiz del proyecto (padre de config/)
project = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
vbs_path = project & "\telegram_bot.vbs"

If Not fso.FileExists(vbs_path) Then
    MsgBox "No se encontro " & vbs_path, 16, "JARVIS Telegram Bot"
    WScript.Quit 1
End If

startup = shell.SpecialFolders("Startup")
If startup = "" Then
    MsgBox "No se pudo obtener la carpeta de inicio de Windows.", 16, "JARVIS Telegram Bot"
    WScript.Quit 1
End If

On Error Resume Next
Set shortcut = shell.CreateShortcut(startup & "\JARVIS Telegram Bot.lnk")
If Err.Number <> 0 Then
    MsgBox "Error al crear acceso directo:" & vbCrLf & Err.Description, 16, "JARVIS Telegram Bot"
    WScript.Quit 1
End If
On Error Goto 0

shortcut.TargetPath = vbs_path
shortcut.WorkingDirectory = project
shortcut.WindowStyle = 0
shortcut.Description = "JARVIS Telegram Bot — Control remoto"
shortcut.Save()

Set shell = Nothing
Set fso = Nothing
MsgBox "Listo. El bot de Telegram arrancara solo cuando inicies sesion.", 64, "JARVIS Telegram Bot"
