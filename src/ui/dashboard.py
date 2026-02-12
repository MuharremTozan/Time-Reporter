import customtkinter as ctk
from datetime import datetime, timedelta
import logging
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from src.utils.startup import StartupManager
from src.utils.exporter import ExportManager

# Set matplotlib to work with tkinter
matplotlib.use("TkAgg")


class DashboardApp(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()

        self.db = db_manager
        self.exporter = ExportManager(db_manager)
        self.title("Time Reporter - Dashboard")
        self.geometry("1100x750")

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

        self.categories_button = ctk.CTkButton(
            self.sidebar_frame, text="App Categories", command=self.show_categories
        )
        self.categories_button.grid(row=3, column=0, padx=20, pady=10)

        self.export_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Export Today",
            command=self.manual_export,
            fg_color="transparent",
            border_width=2,
            width=100,
        )
        self.export_button.grid(row=4, column=0, padx=(20, 5), pady=10, sticky="w")

        self.browse_button = ctk.CTkButton(
            self.sidebar_frame,
            text="📁",
            command=self.open_export_folder,
            fg_color="transparent",
            border_width=2,
            width=40,
        )
        self.browse_button.grid(row=4, column=0, padx=(5, 20), pady=10, sticky="e")

        # Startup toggle
        self.startup_var = ctk.BooleanVar(value=StartupManager.is_startup_enabled())
        self.startup_checkbox = ctk.CTkCheckBox(
            self.sidebar_frame,
            text="Run at Startup",
            variable=self.startup_var,
            command=self.toggle_startup,
        )
        self.startup_checkbox.grid(row=5, column=0, padx=20, pady=(20, 10))

        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame, text="Appearance Mode:", anchor="w"
        )
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
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
        self.categories_frame = ctk.CTkFrame(self, corner_radius=15)

        self._setup_dashboard_view()
        self._setup_stats_view()
        self._setup_categories_view()

        # Show initial view
        self.show_dashboard()

        # Initial refresh
        self.refresh_data()

        # Handle close button
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

    def hide_window(self):
        self.withdraw()

    def show_window(self):
        self.deiconify()
        self.focus_force()

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
            text="Usage Statistics",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Range selector
        self.range_selector = ctk.CTkSegmentedButton(
            self.stats_frame,
            values=["Today", "Last 7 Days", "Last 30 Days"],
            command=lambda v: self.render_stats_charts(),
        )
        self.range_selector.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="e")
        self.range_selector.set("Today")

        # TabView for different chart types
        self.stats_tabview = ctk.CTkTabview(self.stats_frame)
        self.stats_tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.stats_tabview.add("By Application")
        self.stats_tabview.add("By Category")

        # Containers for the charts
        self.app_chart_container = ctk.CTkFrame(
            self.stats_tabview.tab("By Application"), fg_color="transparent"
        )
        self.app_chart_container.pack(fill="both", expand=True)

        self.cat_chart_container = ctk.CTkFrame(
            self.stats_tabview.tab("By Category"), fg_color="transparent"
        )
        self.cat_chart_container.pack(fill="both", expand=True)

    def _setup_categories_view(self):
        self.categories_frame.grid_columnconfigure(0, weight=1)
        self.categories_frame.grid_rowconfigure(1, weight=1)

        header = ctk.CTkLabel(
            self.categories_frame,
            text="Manage Application Categories",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.cat_scrollable = ctk.CTkScrollableFrame(
            self.categories_frame, label_text="Known Applications"
        )
        self.cat_scrollable.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    def show_dashboard(self):
        self._hide_all_frames()
        self.dashboard_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self._update_button_colors(self.dashboard_button)

    def show_stats(self):
        self._hide_all_frames()
        self.stats_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self._update_button_colors(self.stats_button)
        self.render_stats_charts()

    def show_categories(self):
        self._hide_all_frames()
        self.categories_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self._update_button_colors(self.categories_button)
        self.render_categories_list()

    def _hide_all_frames(self):
        self.dashboard_frame.grid_forget()
        self.stats_frame.grid_forget()
        self.categories_frame.grid_forget()

    def _update_button_colors(self, active_button):
        for btn in [self.dashboard_button, self.stats_button, self.categories_button]:
            if btn == active_button:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def refresh_data(self):
        """Fetches data from DB and updates UI components."""
        # Update Live Card
        last_block = self.db.get_last_block()
        if last_block:
            cat = self.db.get_app_category(last_block["app_name"])
            self.live_app_label.configure(
                text=f"{last_block['app_name']} [{cat}] - {last_block['duration_minutes']} min"
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

        # Auto refresh charts if stats view is active
        if self.stats_frame.winfo_viewable():
            self.render_stats_charts()

        self.after(30000, self.refresh_data)

    def render_stats_charts(self):
        """Renders both application and category pie charts."""
        # Clear containers
        for container in [self.app_chart_container, self.cat_chart_container]:
            for widget in container.winfo_children():
                widget.destroy()

        # Calculate date range
        range_val = self.range_selector.get()
        end_date = datetime.now().strftime("%Y-%m-%d")

        if range_val == "Today":
            start_date = end_date
        elif range_val == "Last 7 Days":
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        elif range_val == "Last 30 Days":
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        else:
            start_date = end_date

        # 1. Application Chart
        app_stats = self.db.get_app_usage_stats(start_date, end_date)
        self._draw_pie_chart(
            self.app_chart_container, app_stats, "app_name", f"App Usage ({range_val})"
        )

        # 2. Category Chart
        cat_stats = self.db.get_category_usage_stats(start_date, end_date)
        self._draw_pie_chart(
            self.cat_chart_container,
            cat_stats,
            "category",
            f"Category Usage ({range_val})",
        )

    def _draw_pie_chart(self, container, stats, label_key, title):
        if not stats:
            ctk.CTkLabel(container, text="No data available yet.").pack(expand=True)
            return

        top_stats = stats[:6]
        labels = [s[label_key] for s in top_stats]
        sizes = [s["total_duration"] for s in top_stats]

        if len(stats) > 6:
            others_duration = sum(s["total_duration"] for s in stats[6:])
            labels.append("Others")
            sizes.append(others_duration)

        fig, ax = plt.subplots(figsize=(5, 5), facecolor="#2B2B2B")
        ax.set_facecolor("#2B2B2B")
        colors = plt.cm.Paired(range(len(labels)))
        ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            textprops={"color": "w"},
        )
        ax.set_title(title, color="white", pad=10)

        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def render_categories_list(self):
        """Renders the list of apps and their categories for editing."""
        for widget in self.cat_scrollable.winfo_children():
            widget.destroy()

        # Get all apps ever tracked
        with self.db._get_connection() as conn:
            cursor = conn.execute("SELECT DISTINCT app_name FROM activity_blocks")
            apps = [row[0] for row in cursor.fetchall()]

        categories = [
            "Development",
            "Browsing",
            "Entertainment",
            "Social",
            "System",
            "Work",
            "Education",
            "Uncategorized",
        ]

        for app_name in apps:
            current_cat = self.db.get_app_category(app_name)

            row = ctk.CTkFrame(self.cat_scrollable, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(
                row,
                text=app_name,
                width=200,
                anchor="w",
                font=ctk.CTkFont(weight="bold"),
            ).pack(side="left")

            cat_menu = ctk.CTkOptionMenu(
                row,
                values=categories,
                command=lambda v, a=app_name: self.update_category(a, v),
            )
            cat_menu.set(current_cat)
            cat_menu.pack(side="right")

    def update_category(self, app_name, new_cat):
        self.db.set_app_category(app_name, new_cat)
        logging.info(f"Updated {app_name} to category {new_cat}")

    def toggle_startup(self):
        enabled = self.startup_var.get()
        if StartupManager.set_startup(enabled):
            status = "enabled" if enabled else "disabled"
            logging.info(f"Startup {status}")
        else:
            logging.error("Failed to update startup settings")

    def manual_export(self):
        path = self.exporter.export_today()
        if path:
            logging.info(f"Manual export successful: {path}")
        else:
            logging.error("Manual export failed or no data available.")

    def open_export_folder(self):
        if os.path.exists(self.exporter.export_dir):
            os.startfile(self.exporter.export_dir)
        else:
            logging.error("Export folder does not exist yet.")

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    from src.db.manager import DatabaseManager

    db = DatabaseManager()
    app = DashboardApp(db)
    app.mainloop()
