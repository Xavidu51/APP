import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog

DB_NAME = "clientes_prestamos.db"


def init_db():
    """
    Inicializa la base de datos creando las tablas necesarias si no existen.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Crear tabla 'clientes'
    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            cliente_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            direccion TEXT,
            telefono TEXT,
            correo TEXT,
            fecha_registro TEXT
        )
    ''')
    # Crear tabla 'prestamos'
    c.execute('''
        CREATE TABLE IF NOT EXISTS prestamos (
            prestamo_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            monto REAL NOT NULL,
            estado TEXT NOT NULL,
            fecha_solicitud TEXT NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
        )
    ''')
    conn.commit()
    conn.close()


class LoanDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dashboard de Préstamos")
        self.geometry("900x700")
        init_db()
        self.create_dashboard()

    def create_dashboard(self):
        # Encabezado
        header_frame = ttk.Frame(self, padding=10)
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="[Logo]", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Dashboard de Préstamos", font=("Arial", 18)).pack(side=tk.LEFT, expand=True)
        ttk.Button(header_frame, text="Usuario | Salir", command=self.quit).pack(side=tk.RIGHT)

        # Botón para abrir perfil de cliente
        ttk.Button(header_frame, text="Perfil", command=self.buscar_cliente).pack(side=tk.RIGHT, padx=10)

    def buscar_cliente(self):
        """
        Solicita un nombre o ID de cliente, y muestra su perfil si existe.
        """
        input_cliente = simpledialog.askstring(
            "Buscar Cliente", "Ingrese el Nombre o ID del Cliente:"
        )

        if input_cliente:
            try:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()

                # Verificar si es un ID o un Nombre
                if input_cliente.isdigit():
                    c.execute("SELECT * FROM clientes WHERE cliente_id = ?", (input_cliente,))
                else:
                    c.execute("SELECT * FROM clientes WHERE nombre LIKE ?", (f"%{input_cliente}%",))

                cliente = c.fetchone()
                conn.close()

                if cliente:
                    self.mostrar_perfil(cliente)
                else:
                    # Si no existe el cliente, ofrecer registrar uno nuevo
                    respuesta = messagebox.askyesno(
                        "Cliente no encontrado", "¿Desea registrar un nuevo cliente?"
                    )
                    if respuesta:
                        self.registrar_nuevo_cliente(input_cliente)
            except Exception as e:
                messagebox.showerror("Error", f"Error al buscar cliente: {str(e)}")

    def mostrar_perfil(self, cliente):
        """
        Muestra el perfil del cliente, con la opción de editar datos,
        ver historial de préstamos y crear nuevos préstamos.
        """
        dialog = tk.Toplevel(self)
        dialog.title(f"Perfil de {cliente[1]}")

        # Datos personales
        ttk.Label(dialog, text="Datos Personales:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)

        datos_frame = ttk.Frame(dialog, padding=10)
        datos_frame.pack(fill=tk.X)
        ttk.Label(datos_frame, text=f"ID: {cliente[0]}").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(datos_frame, text=f"Nombre: {cliente[1]}").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(datos_frame, text=f"Dirección: {cliente[2]}").grid(row=2, column=0, padx=5, pady=5)
        ttk.Label(datos_frame, text=f"Teléfono: {cliente[3]}").grid(row=3, column=0, padx=5, pady=5)
        ttk.Label(datos_frame, text=f"Correo: {cliente[4]}").grid(row=4, column=0, padx=5, pady=5)
        ttk.Label(datos_frame, text=f"Fecha de Registro: {cliente[5]}").grid(row=5, column=0, padx=5, pady=5)

        ttk.Button(datos_frame, text="Editar Datos", command=lambda: self.editar_datos(cliente)).grid(row=6, column=0, pady=5)

        # Historial de préstamos
        ttk.Label(dialog, text="Historial de Préstamos:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        prestamos_frame = scrolledtext.ScrolledText(dialog, height=10, width=80)
        prestamos_frame.pack(padx=10, pady=5)
        self.cargar_historial_prestamos(cliente[0], prestamos_frame)

        # Botón para nuevo préstamo
        ttk.Button(dialog, text="Crear Nuevo Préstamo", command=lambda: self.crear_prestamo(cliente[0])).pack(pady=10)

        ttk.Button(dialog, text="Cerrar", command=dialog.destroy).pack(pady=10)

    def cargar_historial_prestamos(self, cliente_id, prestamos_frame):
        """
        Carga el historial de préstamos del cliente y lo muestra en un cuadro de texto desplazable.
        """
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute(
                """
                SELECT prestamo_id, monto, estado, fecha_solicitud
                FROM prestamos
                WHERE cliente_id = ?
                """,
                (cliente_id,),
            )
            prestamos = c.fetchall()
            conn.close()

            prestamos_frame.delete("1.0", tk.END)
            if prestamos:
                for prestamo in prestamos:
                    prestamos_frame.insert(
                        tk.END,
                        f"ID: {prestamo[0]}, Monto: {prestamo[1]}, Estado: {prestamo[2]}, Fecha: {prestamo[3]}\n"
                    )
            else:
                prestamos_frame.insert(tk.END, "No hay préstamos registrados.\n")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial de préstamos: {str(e)}")

    def registrar_nuevo_cliente(self, nombre_sugerido):
        """
        Permite registrar un nuevo cliente.
        """
        dialog = tk.Toplevel(self)
        dialog.title("Registrar Nuevo Cliente")

        ttk.Label(dialog, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        nombre_entry = ttk.Entry(dialog)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        nombre_entry.insert(0, nombre_sugerido)

        ttk.Label(dialog, text="Dirección:").grid(row=1, column=0, padx=5, pady=5)
        direccion_entry = ttk.Entry(dialog)
        direccion_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5)
        telefono_entry = ttk.Entry(dialog)
        telefono_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Correo:").grid(row=3, column=0, padx=5, pady=5)
        correo_entry = ttk.Entry(dialog)
        correo_entry.grid(row=3, column=1, padx=5, pady=5)

        def guardar_cliente():
            try:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute(
                    """
                    INSERT INTO clientes (nombre, direccion, telefono, correo, fecha_registro)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        nombre_entry.get(),
                        direccion_entry.get(),
                        telefono_entry.get(),
                        correo_entry.get(),
                        datetime.now().strftime("%Y-%m-%d"),
                    ),
                )
                cliente_id = c.lastrowid  # Obtener el ID del cliente recién registrado
                conn.commit()
                conn.close()
                dialog.destroy()
                # Abrir automáticamente el perfil del cliente recién creado
                self.mostrar_perfil((cliente_id, nombre_entry.get(), direccion_entry.get(), telefono_entry.get(), correo_entry.get(), datetime.now().strftime("%Y-%m-%d")))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar el cliente: {str(e)}")

        ttk.Button(dialog, text="Guardar", command=guardar_cliente).grid(row=4, columnspan=2, pady=10)

    def crear_prestamo(self, cliente_id):
        """
        Permite registrar un nuevo préstamo para un cliente.
        """
        dialog = tk.Toplevel(self)
        dialog.title("Nuevo Préstamo")

        ttk.Label(dialog, text="Monto del Préstamo:").grid(row=0, column=0, padx=5, pady=5)
        monto_entry = ttk.Entry(dialog)
        monto_entry.grid(row=0, column=1, padx=5, pady=5)

        def guardar_prestamo():
            try:
                monto = float(monto_entry.get())
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute(
                    """
                    INSERT INTO prestamos (cliente_id, monto, estado, fecha_solicitud)
                    VALUES (?, ?, ?, ?)
                    """,
                    (cliente_id, monto, "Vigente", datetime.now().strftime("%Y-%m-%d")),
                )
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Préstamo registrado correctamente")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar el préstamo: {str(e)}")

        ttk.Button(dialog, text="Guardar", command=guardar_prestamo).grid(row=1, columnspan=2, pady=10)


if __name__ == "__main__":
    app = LoanDashboard()
    app.mainloop()