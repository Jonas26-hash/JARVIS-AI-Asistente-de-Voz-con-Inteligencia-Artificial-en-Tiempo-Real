"""accessibility_overlay.py — Floating accessibility toolbar overlay."""
from __future__ import annotations


def accessibility_overlay(parameters=None, player=None, **kwargs):
    if parameters is None:
        parameters = {}
    action = parameters.get("action", "show")

    if action == "show":
        try:
            import tkinter as tk
            root = tk.Tk()
            root.title("JARVIS Accesibilidad")
            root.geometry("300x400+{}+{}".format(root.winfo_screenwidth()-320, 100))
            root.attributes("-topmost", True)
            root.configure(bg="#1a1a2e")
            tk.Label(root, text="JARVIS Accesibilidad", fg="white", bg="#1a1a2e",
                     font=("Segoe UI", 14, "bold")).pack(pady=10)
            actions_frame = tk.Frame(root, bg="#1a1a2e")
            actions_frame.pack(pady=10)
            buttons = [
                ("🎯 Simplificar tarea", "task_simplify"),
                ("🧘 Regulación emocional", "emotional"),
                ("📋 Mis rutinas", "routine"),
                ("👁️ Seguimiento ocular", "eye_tracking"),
                ("🎤 Configurar voz", "speech_config"),
            ]
            for label, _ in buttons:
                tk.Button(actions_frame, text=label, bg="#16213e", fg="white",
                          font=("Segoe UI", 10), width=25, height=2,
                          border=0).pack(pady=4)
            tk.Button(root, text="Cerrar", command=root.destroy,
                      bg="#e94560", fg="white", font=("Segoe UI", 10),
                      width=25, height=1, border=0).pack(pady=10)
            root.mainloop()
            return "Overlay de accesibilidad mostrado."
        except Exception as e:
            return f"Error: {e}"

    elif action == "hide":
        return "Overlay cerrado."

    return f"Accessibility overlay action '{action}'."
