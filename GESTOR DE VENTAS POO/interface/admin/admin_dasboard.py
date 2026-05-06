import customtkinter as ctk

def abrir_dashboard(root):
    root.withdraw()

    ventana = ctk.CTkToplevel()
    ventana.title("ElectroGestión - Administrador")
    ventana.geometry("1100x650")
    ventana.configure(fg_color="#f1f5f9")

    # ---- MENU LATERAL ----
    menu = ctk.CTkFrame(ventana, fg_color="white", width=220, corner_radius=0)
    menu.pack(side="left", fill="y")
    menu.pack_propagate(False)

    ctk.CTkLabel(menu, text="⚡ ElectroGestión",
                 font=("Arial", 15, "bold"),
                 text_color="#2563eb").pack(pady=(20,2), padx=15, anchor="w")

    ctk.CTkLabel(menu, text="Panel Administrador",
                 font=("Arial", 11),
                 text_color="gray").pack(padx=15, anchor="w")

    ctk.CTkFrame(menu, height=1, fg_color="#e2e8f0").pack(fill="x", pady=10)

    perfil = ctk.CTkFrame(menu, fg_color="#f1f5f9", corner_radius=8)
    perfil.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(perfil, text="Administrador Principal",
                 font=("Arial", 12, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=10, pady=(8,0))

    ctk.CTkLabel(perfil, text="Admin",
                 font=("Arial", 11),
                 text_color="gray").pack(anchor="w", padx=10, pady=(0,8))

    ctk.CTkFrame(menu, height=1, fg_color="#e2e8f0").pack(fill="x", pady=10)

    botones = ["Inicio", "Productos", "Clientes", "Empleados", "Ventas", "Reportes"]
    for boton in botones:
        btn = ctk.CTkButton(menu, text=boton, width=180, height=40,
                            fg_color="transparent", text_color="#1e293b",
                            hover_color="#f1f5f9", anchor="w")
        btn.pack(pady=2, padx=10)

    ctk.CTkFrame(menu, height=1, fg_color="#e2e8f0").pack(fill="x", pady=10)
    ctk.CTkButton(menu, text="Cerrar Sesión", width=180, height=40,
                  fg_color="transparent", text_color="red",
                  hover_color="#fee2e2", anchor="w").pack(padx=10)

    # ---- CONTENIDO PRINCIPAL ----
    contenido = ctk.CTkFrame(ventana, fg_color="#f1f5f9")
    contenido.pack(side="left", fill="both", expand=True)

    ctk.CTkLabel(contenido, text="Dashboard Administrador",
                 font=("Arial", 26, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=30, pady=(30,5))

    ctk.CTkLabel(contenido, text="Resumen general del sistema",
                 font=("Arial", 13),
                 text_color="gray").pack(anchor="w", padx=30, pady=(0,20))

    # ---- FILA 1: 3 tarjetas ----
    fila1 = ctk.CTkFrame(contenido, fg_color="transparent")
    fila1.pack(fill="x", padx=30, pady=(0,10))

    # Tarjeta Ventas del dia
    t1 = ctk.CTkFrame(fila1, fg_color="white", corner_radius=12, height=160)
    t1.pack(side="left", expand=True, fill="both", padx=(0,10))
    t1.pack_propagate(False)
    ctk.CTkLabel(t1, text="↗", font=("Arial", 20, "bold"),
                 fg_color="#22c55e", text_color="white",
                 width=45, height=45, corner_radius=10).pack(anchor="w", padx=20, pady=(20,10))
    ctk.CTkLabel(t1, text="$0.00", font=("Arial", 22, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(t1, text="Ventas del Día", font=("Arial", 13, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(t1, text="0 transacciones", font=("Arial", 11),
                 text_color="gray").pack(anchor="w", padx=20, pady=(0,20))

    # Tarjeta Ingresos Totales
    t2 = ctk.CTkFrame(fila1, fg_color="white", corner_radius=12, height=160)
    t2.pack(side="left", expand=True, fill="both", padx=(0,10))
    t2.pack_propagate(False)
    ctk.CTkLabel(t2, text="$", font=("Arial", 20, "bold"),
                 fg_color="#2563eb", text_color="white",
                 width=45, height=45, corner_radius=10).pack(anchor="w", padx=20, pady=(20,10))
    ctk.CTkLabel(t2, text="$0.00", font=("Arial", 22, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(t2, text="Ingresos Totales", font=("Arial", 13, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(t2, text="Acumulado histórico", font=("Arial", 11),
                 text_color="gray").pack(anchor="w", padx=20, pady=(0,20))

    # Tarjeta Productos
    t3 = ctk.CTkFrame(fila1, fg_color="white", corner_radius=12, height=160)
    t3.pack(side="left", expand=True, fill="both")
    t3.pack_propagate(False)
    ctk.CTkLabel(t3, text="📦", font=("Arial", 20),
                 fg_color="#a855f7", text_color="white",
                 width=45, height=45, corner_radius=10).pack(anchor="w", padx=20, pady=(20,10))
    ctk.CTkLabel(t3, text="0", font=("Arial", 22, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(t3, text="Productos", font=("Arial", 13, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(t3, text="0 disponibles", font=("Arial", 11),
                 text_color="gray").pack(anchor="w", padx=20, pady=(0,20))

   
    fila2 = ctk.CTkFrame(contenido, fg_color="transparent")
    fila2.pack(fill="x", padx=30, pady=(0,10))

    
    t4 = ctk.CTkFrame(fila2, fg_color="white", corner_radius=12, height=160)
    t4.pack(side="left", expand=True, fill="both", padx=(0,10))
    t4.pack_propagate(False)
    ctk.CTkLabel(t4, text="👤", font=("Arial", 20),
                 fg_color="#f97316", text_color="white",
                 width=45, height=45, corner_radius=10).pack(anchor="w", padx=20, pady=(20,10))
    ctk.CTkLabel(t4, text="1", font=("Arial", 22, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(t4, text="Empleados", font=("Arial", 13, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(t4, text="Personal activo", font=("Arial", 11),
                 text_color="gray").pack(anchor="w", padx=20, pady=(0,20))

    
    t5 = ctk.CTkFrame(fila2, fg_color="white", corner_radius=12, height=160)
    t5.pack(side="left", expand=True, fill="both", padx=(0,10))
    t5.pack_propagate(False)
    ctk.CTkLabel(t5, text="👥", font=("Arial", 20),
                 fg_color="#ec4899", text_color="white",
                 width=45, height=45, corner_radius=10).pack(anchor="w", padx=20, pady=(20,10))
    ctk.CTkLabel(t5, text="0", font=("Arial", 22, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(t5, text="Clientes", font=("Arial", 13, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(t5, text="Registrados", font=("Arial", 11),
                 text_color="gray").pack(anchor="w", padx=20, pady=(0,20))

  
    t6 = ctk.CTkFrame(fila2, fg_color="white", corner_radius=12, height=160)
    t6.pack(side="left", expand=True, fill="both")
    t6.pack_propagate(False)
    ctk.CTkLabel(t6, text="🛒", font=("Arial", 20),
                 fg_color="#06b6d4", text_color="white",
                 width=45, height=45, corner_radius=10).pack(anchor="w", padx=20, pady=(20,10))
    ctk.CTkLabel(t6, text="0", font=("Arial", 22, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(t6, text="Ventas Totales", font=("Arial", 13, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(t6, text="Transacciones", font=("Arial", 11),
                 text_color="gray").pack(anchor="w", padx=20, pady=(0,20))
    
    fila3 = ctk.CTkFrame(contenido, fg_color="transparent")
    fila3.pack(fill="x", padx=30, pady=(0,10))

    alertas = ctk.CTkFrame(fila3, fg_color="white", corner_radius=12)
    alertas.pack(side="left", expand=True, fill="both", padx=(0,10))

    ctk.CTkLabel(alertas, text="Alertas de inventario",
                 font=("Arial", 14, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20, pady=(20,10))
    
    alerta1 = ctk.CTkLabel(alertas, fg_color="#dcfce7", corner_radius=8)
    alerta1.pack(fill="x", padx=20, pady=(0,10))
    ctk.CTkLabel(alerta1, text="✓  Inventario en niveles óptimos",
                 font=("Arial", 12),
                 text_color="#16a34a").pack(anchor="w", padx=10, pady=10)
