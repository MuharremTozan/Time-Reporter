import customtkinter as ctk
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

# Set matplotlib to work with tkinter
matplotlib.use("TkAgg")


class DashboardApp(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()

        self.db = db_manager
        self.title("Time Reporter - Dashboard")
        self.geometry("1100x700")

        # Set appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Time Reporter",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.dashboard_button = ctk.CTkButton(
            self.sidebar_frame, text="Dashboard", command=self.show_dashboard
        )
        self.dashboard_button.grid(row=1, column=0, padx=20, pady=10)

        self.stats_button = ctk.CTkButton(
            self.sidebar_frame, text="Statistics", command=self.show_stats
        )
        self.stats_button.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame, text="Appearance Mode:", anchor="w"
        )
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(20, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode,
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu.set("Dark")

        # View Frames
        self.dashboard_frame = ctk.CTkFrame(self, corner_radius=15)
        self.stats_frame = ctk.CTkFrame(self, corner_radius=15)

        self._setup_dashboard_view()
        self._setup_stats_view()

        # Show initial view
        self.show_dashboard()

        # Initial refresh
        self.refresh_data()

    def _setup_dashboard_view(self):
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_rowconfigure(2, weight=1)

        header = ctk.CTkLabel(
            self.dashboard_frame,
            text="Daily Activity Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.status_card = ctk.CTkFrame(
            self.dashboard_frame, height=100, fg_color=("#DBDBDB", "#2B2B2B")
        )
        self.status_card.grid(row=1, column=0, padx=20, pady=10, sticky="new")

        ctk.CTkLabel(
            self.status_card, text="Current Activity", font=ctk.CTkFont(size=14)
        ).pack(pady=(10, 0))
        self.live_app_label = ctk.CTkLabel(
            self.status_card,
            text="Fetching data...",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.live_app_label.pack(pady=(5, 10))

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.dashboard_frame, label_text="Recent Blocks"
        )
        self.scrollable_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

    def _setup_stats_view(self):
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_rowconfigure(1, weight=1)

        header = ctk.CTkLabel(
            self.stats_frame,
            text="Usage Statistics (Today)",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Container for the chart
        self.chart_container = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        self.chart_container.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    def show_dashboard(self):
        self.stats_frame.grid_forget()
        self.dashboard_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.dashboard_button.configure(fg_color=("gray75", "gray25"))
        self.stats_button.configure(
            fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        )

    def show_stats(self):
        self.dashboard_frame.grid_forget()
        self.stats_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.stats_button.configure(fg_color=("gray75", "gray25"))
        self.dashboard_button.configure(
            fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        )
        self.render_stats_chart()

    def refresh_data(self):
        """Fetches data from DB and updates UI components."""
        # Update Live Card
        last_block = self.db.get_last_block()
        if last_block:
            self.live_app_label.configure(
                text=f"{last_block['app_name']} - {last_block['duration_minutes']} min"
            )

        # Update Recent Blocks List
        recent_blocks = self.db.get_recent_blocks(limit=15)
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for block in recent_blocks:
            row = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)

            time_str = (
                datetime.fromisoformat(block["start_time"]).strftime("%H:%M")
                if isinstance(block["start_time"], str)
                else block["start_time"].strftime("%H:%M")
            )

            ctk.CTkLabel(row, text=time_str, width=60).pack(side="left")
            ctk.CTkLabel(
                row, text=block["app_name"], font=ctk.CTkFont(weight="bold")
            ).pack(side="left", padx=20)
            ctk.CTkLabel(row, text=f"{block['duration_minutes']} min").pack(
                side="right"
            )

        # Auto refresh chart if stats view is active
        if self.stats_frame.winfo_viewable():
            self.render_stats_chart()

        self.after(30000, self.refresh_data)

    def render_stats_chart(self):
        """Renders the pie chart based on usage stats."""
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        stats = self.db.get_app_usage_stats()
        if not stats:
            ctk.CTkLabel(
                self.chart_container, text="No data available for today yet."
            ).pack(expand=True)
            return

        # Prepare data for pie chart
        top_stats = stats[:5]  # Top 5
        labels = [s["app_name"] for s in top_stats]
        sizes = [s["total_duration"] for s in top_stats]

        if len(stats) > 5:
            others_duration = sum(s["total_duration"] for s in stats[5:])
            labels.append("Others")
            sizes.append(others_duration)

        # Create Matplotlib figure
        fig, ax = plt.subplots(figsize=(6, 6), facecolor="#2B2B2B")
        ax.set_facecolor("#2B2B2B")

        # Styling the pie chart
        colors = plt.cm.Paired(range(len(labels)))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            textprops={"color": "w"},
        )
        ax.set_title("App Usage Distribution", color="white", pad=20)

        # Draw the chart in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)  # Close to free memory

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    from src.db.manager import DatabaseManager

    db = DatabaseManager()
    app = DashboardApp(db)
    app.mainloop()
