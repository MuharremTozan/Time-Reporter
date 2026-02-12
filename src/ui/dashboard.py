import customtkinter as ctk
from datetime import datetime, timedelta
import logging
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from src.utils.startup import StartupManager
from src.utils.exporter import ExportManager
from src.utils.resources import get_resource_path

# Set matplotlib to work with tkinter
matplotlib.use("TkAgg")


class DashboardApp(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()

        self.db = db_manager
        self.engine = None
        self.exporter = ExportManager(db_manager)
        self.title("Time Reporter")
        self.geometry("1100x750")

        # Set Icon
        try:
            icon_path = get_resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            logging.error(f"Could not load window icon: {e}")

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
            text=" Time Reporter",
            font=ctk.CTkFont(size=20, weight="bold"),
        )

        # Load sidebar logo
        try:
            from PIL import Image

            logo_path = get_resource_path("Time Reporter.png")
            if os.path.exists(logo_path):
                logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(40, 40),
                )
                self.logo_label.configure(image=logo_image, compound="left")
        except Exception as e:
            logging.error(f"Could not load sidebar logo: {e}")

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

        self.settings_button = ctk.CTkButton(
            self.sidebar_frame, text="Settings", command=self.show_settings
        )
        self.settings_button.grid(row=4, column=0, padx=20, pady=10)

        # Export Section at bottom
        self.sidebar_frame.grid_rowconfigure(5, weight=1)  # Spacer

        self.export_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.export_frame.grid(row=6, column=0, padx=10, pady=20, sticky="ew")

        self.export_button = ctk.CTkButton(
            self.export_frame,
            text="Export Today",
            command=self.manual_export,
            fg_color="transparent",
            border_width=2,
            width=120,
        )
        self.export_button.pack(side="left", padx=(10, 5), pady=10)

        self.browse_button = ctk.CTkButton(
            self.export_frame,
            text="📁",
            command=self.open_export_folder,
            fg_color="transparent",
            border_width=2,
            width=40,
        )
        self.browse_button.pack(side="left", padx=(5, 10), pady=10)

        # View Frames
        self.dashboard_frame = ctk.CTkFrame(self, corner_radius=15)
        self.stats_frame = ctk.CTkFrame(self, corner_radius=15)
        self.categories_frame = ctk.CTkFrame(self, corner_radius=15)
        self.settings_frame = ctk.CTkFrame(self, corner_radius=15)

        self._setup_dashboard_view()
        self._setup_stats_view()
        self._setup_categories_view()
        self._setup_settings_view()

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
        self.categories_frame.grid_rowconfigure(2, weight=1)

        header = ctk.CTkLabel(
            self.categories_frame,
            text="Manage Application Categories",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Category Management Section
        self.cat_mgmt_frame = ctk.CTkFrame(self.categories_frame)
        self.cat_mgmt_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.new_cat_entry = ctk.CTkEntry(
            self.cat_mgmt_frame, placeholder_text="New category name..."
        )
        self.new_cat_entry.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.add_cat_btn = ctk.CTkButton(
            self.cat_mgmt_frame, text="Add", width=60, command=self.add_custom_category
        )
        self.add_cat_btn.pack(side="left", padx=10, pady=10)

        # TabView for Apps and Categories list
        self.cat_tabview = ctk.CTkTabview(self.categories_frame)
        self.cat_tabview.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.cat_tabview.add("App Assignments")
        self.cat_tabview.add("Category List")

        self.cat_scrollable = ctk.CTkScrollableFrame(
            self.cat_tabview.tab("App Assignments"), label_text="Known Applications"
        )
        self.cat_scrollable.pack(fill="both", expand=True)

        self.cat_list_scrollable = ctk.CTkScrollableFrame(
            self.cat_tabview.tab("Category List"), label_text="Available Categories"
        )
        self.cat_list_scrollable.pack(fill="both", expand=True)

    def _setup_settings_view(self):
        self.settings_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            self.settings_frame,
            text="Application Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Settings Container
        container = ctk.CTkScrollableFrame(self.settings_frame, fg_color="transparent")
        container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.settings_frame.grid_rowconfigure(1, weight=1)

        # 1. Idle Threshold
        idle_group = ctk.CTkFrame(container)
        idle_group.pack(fill="x", pady=10)

        ctk.CTkLabel(
            idle_group, text="Idle Detection Threshold (minutes):", anchor="w"
        ).pack(side="left", padx=20, pady=10)

        current_idle_min = int(self.db.get_setting("idle_threshold", "300")) // 60
        self.idle_entry = ctk.CTkEntry(idle_group, width=60)
        self.idle_entry.insert(0, str(current_idle_min))
        self.idle_entry.pack(side="right", padx=20, pady=10)

        # 2. DB Cleanup
        cleanup_group = ctk.CTkFrame(container)
        cleanup_group.pack(fill="x", pady=10)

        ctk.CTkLabel(
            cleanup_group, text="Data Retention Policy (days):", anchor="w"
        ).pack(side="left", padx=20, pady=10)

        current_cleanup = self.db.get_setting("db_cleanup_days", "30")
        self.cleanup_entry = ctk.CTkEntry(cleanup_group, width=60)
        self.cleanup_entry.insert(0, current_cleanup)
        self.cleanup_entry.pack(side="right", padx=20, pady=10)

        # 3. Export on Exit
        export_group = ctk.CTkFrame(container)
        export_group.pack(fill="x", pady=10)

        self.export_on_exit_var = ctk.BooleanVar(
            value=self.db.get_setting("export_on_exit", "True") == "True"
        )
        ctk.CTkCheckBox(
            export_group,
            text="Auto-export report on exit",
            variable=self.export_on_exit_var,
        ).pack(side="left", padx=20, pady=10)

        # 4. Startup (Moved here from sidebar)
        startup_group = ctk.CTkFrame(container)
        startup_group.pack(fill="x", pady=10)

        self.startup_var = ctk.BooleanVar(value=StartupManager.is_startup_enabled())
        ctk.CTkCheckBox(
            startup_group,
            text="Run automatically when Windows starts",
            variable=self.startup_var,
        ).pack(side="left", padx=20, pady=10)

        # 5. Theme
        theme_group = ctk.CTkFrame(container)
        theme_group.pack(fill="x", pady=10)

        ctk.CTkLabel(theme_group, text="Visual Theme:", anchor="w").pack(
            side="left", padx=20, pady=10
        )
        self.theme_option = ctk.CTkOptionMenu(
            theme_group,
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode,
        )
        self.theme_option.set("Dark")
        self.theme_option.pack(side="right", padx=20, pady=10)

        # Save Button
        self.save_settings_btn = ctk.CTkButton(
            self.settings_frame,
            text="Save & Apply Settings",
            command=self.save_settings,
        )
        self.save_settings_btn.grid(row=2, column=0, padx=20, pady=20)

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

    def show_settings(self):
        self._hide_all_frames()
        self.settings_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self._update_button_colors(self.settings_button)

    def _hide_all_frames(self):
        self.dashboard_frame.grid_forget()
        self.stats_frame.grid_forget()
        self.categories_frame.grid_forget()
        self.settings_frame.grid_forget()

    def _update_button_colors(self, active_button):
        for btn in [
            self.dashboard_button,
            self.stats_button,
            self.categories_button,
            self.settings_button,
        ]:
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
        """Renders both app assignments and category management list."""
        # 1. App Assignments
        for widget in self.cat_scrollable.winfo_children():
            widget.destroy()

        with self.db._get_connection() as conn:
            cursor = conn.execute("SELECT DISTINCT app_name FROM activity_blocks")
            apps = [row[0] for row in cursor.fetchall()]

        all_categories = self.db.get_categories()

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
                values=all_categories,
                command=lambda v, a=app_name: self.update_category(a, v),
            )
            cat_menu.set(current_cat)
            cat_menu.pack(side="right")

        # 2. Category List Management
        for widget in self.cat_list_scrollable.winfo_children():
            widget.destroy()

        for cat in all_categories:
            row = ctk.CTkFrame(self.cat_list_scrollable, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(row, text=cat, anchor="w").pack(side="left", padx=10)
            if cat != "Uncategorized":
                del_btn = ctk.CTkButton(
                    row,
                    text="Delete",
                    width=60,
                    fg_color="#A30000",
                    hover_color="#7A0000",
                    command=lambda c=cat: self.delete_custom_category(c),
                )
                del_btn.pack(side="right", padx=10)

    def add_custom_category(self):
        name = self.new_cat_entry.get().strip()
        if name:
            self.db.add_category(name)
            self.new_cat_entry.delete(0, "end")
            self.render_categories_list()

    def save_settings(self):
        try:
            # 1. Idle Threshold (minutes to seconds)
            idle_min = int(self.idle_entry.get())
            if idle_min < 1:
                idle_min = 1
            self.db.set_setting("idle_threshold", str(idle_min * 60))

            # 2. Cleanup Days
            cleanup_days = int(self.cleanup_entry.get())
            if cleanup_days < 1:
                cleanup_days = 1
            self.db.set_setting("db_cleanup_days", str(cleanup_days))

            # 3. Export on Exit
            export_val = "True" if self.export_on_exit_var.get() else "False"
            self.db.set_setting("export_on_exit", export_val)

            # 4. Startup Toggle
            enabled = self.startup_var.get()
            StartupManager.set_startup(enabled)

            # 5. Appearance
            ctk.set_appearance_mode(self.theme_option.get())

            # Notify Engine
            if self.engine:
                self.engine.reload_settings()

            logging.info("Settings saved and applied.")

            # Visual feedback
            self.save_settings_btn.configure(fg_color="green", text="Settings Saved! ✓")
            self.after(
                2000,
                lambda: self.save_settings_btn.configure(
                    fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                    text="Save & Apply Settings",
                ),
            )

        except ValueError:
            logging.error("Invalid input in settings entries.")
            self.save_settings_btn.configure(
                fg_color="red", text="Error: Invalid Numbers"
            )
            self.after(
                2000,
                lambda: self.save_settings_btn.configure(
                    fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                    text="Save & Apply Settings",
                ),
            )

    def delete_custom_category(self, name):
        if self.db.delete_category(name):
            self.render_categories_list()

    def update_category(self, app_name, new_cat):
        self.db.set_app_category(app_name, new_cat)
        logging.info(f"Updated {app_name} to category {new_cat}")

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

    def set_engine(self, engine):
        self.engine = engine

    def show_idle_confirmation(self, idle_start, idle_end):
        """Called by the engine when user returns from idle."""
        logging.info(f"Idle return callback received: {idle_start} to {idle_end}")
        self.after(0, lambda: self._open_idle_popup(idle_start, idle_end))

    def _open_idle_popup(self, idle_start, idle_end):
        logging.info("Opening idle detection popup...")
        popup = ctk.CTkToplevel(self)
        popup.title("Smart Idle Detection")
        popup.geometry("450x250")

        # Ensure it's on top and visible
        popup.attributes("-topmost", True)
        popup.deiconify()
        popup.focus_force()
        popup.grab_set()  # Focus on this window

        # Center the popup
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width // 2) - (450 // 2)
        y = (screen_height // 2) - (250 // 2)
        popup.geometry(f"+{x}+{y}")

        # If main app is withdrawn, we need to make sure this toplevel still shows
        # Some systems require the parent to be mapped.
        # But withdrawing the main app is standard for tray apps.

        ctk.CTkLabel(
            popup, text="Hala burada mısın?", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 10))

        diff_min = int((idle_end - idle_start).total_seconds() / 60)
        ctk.CTkLabel(
            popup,
            text=f"Yaklaşık {diff_min} dakikadır işlem yapmadın.\nBu süreyi nasıl kaydedelim?",
            font=ctk.CTkFont(size=14),
        ).pack(pady=10)

        # Countdown timer
        timer_label = ctk.CTkLabel(
            popup, text="Otomatik karar: 60s", font=ctk.CTkFont(size=12)
        )
        timer_label.pack(pady=5)

        self.popup_timer = 60

        def countdown():
            if not popup.winfo_exists():
                return
            if self.popup_timer <= 0:
                make_decision("break")
                return
            self.popup_timer -= 1
            timer_label.configure(text=f"Otomatik karar: {self.popup_timer}s")
            popup.after(1000, countdown)

        def make_decision(decision):
            if self.engine:
                self.engine.handle_idle_decision(decision, idle_start, idle_end)
            popup.destroy()
            self.refresh_data()

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="☕ Mola Say",
            fg_color="#A30000",
            hover_color="#7A0000",
            command=lambda: make_decision("break"),
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="📖 Çalışıyordum",
            fg_color="#1f538d",
            command=lambda: make_decision("work"),
        ).pack(side="left", padx=10)

        popup.after(1000, countdown)

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    from src.db.manager import DatabaseManager

    db = DatabaseManager()
    app = DashboardApp(db)
    app.mainloop()
