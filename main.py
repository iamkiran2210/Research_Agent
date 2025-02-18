import customtkinter as ctk
import threading
import os
import time
from tkinter import filedialog, messagebox
from PIL import Image

# Configure appearance
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class PromptReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Research Report Generator")
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Custom fonts
        self.heading_font = ctk.CTkFont(family="Helvetica", size=24, weight="bold")
        self.subheading_font = ctk.CTkFont(family="Helvetica", size=18, weight="bold")
        self.normal_font = ctk.CTkFont(family="Helvetica", size=14)
        self.status_font = ctk.CTkFont(family="Helvetica", size=16, weight="bold")

        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=0)  # Sidebar
        self.main_frame.grid_columnconfigure(1, weight=1)  # Content area
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.sidebar = ctk.CTkFrame(self.main_frame, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)  # Push settings to bottom

        # Sidebar elements
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Research Report\nGenerator",
                                       font=self.heading_font)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.new_report_button = ctk.CTkButton(self.sidebar, text="New Report",
                                               font=self.normal_font,
                                               command=self.clear_fields)
        self.new_report_button.grid(row=1, column=0, padx=20, pady=10)

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar, text="Appearance Mode:",
                                                  font=self.normal_font, anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")

        self.appearance_mode_menu = ctk.CTkOptionMenu(self.sidebar, values=["Light", "Dark", "System"],
                                                      font=self.normal_font,
                                                      command=self.change_appearance_mode)
        self.appearance_mode_menu.grid(row=8, column=0, padx=20, pady=(5, 20))
        self.appearance_mode_menu.set("System")

        # Create content area
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Configure content frame grid
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)  # Prompt area
        self.content_frame.grid_rowconfigure(1, weight=0)  # Status area
        self.content_frame.grid_rowconfigure(2, weight=1)  # Report area
        self.content_frame.grid_rowconfigure(3, weight=0)  # Actions area

        # Prompt area with rounded ChatGPT-like input
        self.prompt_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.prompt_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.prompt_frame.grid_columnconfigure(0, weight=1)

        self.prompt_input_frame = ctk.CTkFrame(self.prompt_frame,
                                               fg_color="#f0f0f0" if ctk.get_appearance_mode() == "Light" else "#2b2b2b")
        self.prompt_input_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.prompt_input_frame.grid_columnconfigure(0, weight=1)

        self.prompt_input = ctk.CTkEntry(self.prompt_input_frame,
                                         placeholder_text="Enter your research topic...",
                                         border_width=0,
                                         height=50,
                                         font=self.normal_font)
        self.prompt_input.grid(row=0, column=0, sticky="ew", padx=(20, 5), pady=5)

        self.submit_button = ctk.CTkButton(self.prompt_input_frame,
                                           text="Generate",
                                           width=100,
                                           height=40,
                                           font=self.normal_font,
                                           command=self.submit_prompt)
        self.submit_button.grid(row=0, column=1, padx=(5, 20), pady=5)

        # Status indicator
        self.status_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.status_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.status_label = ctk.CTkLabel(self.status_frame, text="",
                                         font=self.status_font)
        self.status_label.pack(side="left", padx=5, pady=5)

        # Report area (ChatGPT-like message bubbles)
        self.reports_container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        self.reports_container.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.reports_container.grid_columnconfigure(0, weight=1)

        # Track the current row in the scrollable frame
        self.current_row = 0

        # Actions frame at the bottom
        self.actions_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.actions_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.download_button = ctk.CTkButton(self.actions_frame,
                                             text="Download Report",
                                             font=self.normal_font,
                                             command=self.download_report,
                                             state="disabled")
        self.download_button.pack(side="right", padx=5, pady=5)

        # Initialize report data
        self.current_report = None
        self.current_topic = None
        self.default_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.md")

    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
        # Update input frame color when appearance changes
        input_color = "#f0f0f0" if new_appearance_mode == "Light" else "#2b2b2b"
        self.prompt_input_frame.configure(fg_color=input_color)

    def submit_prompt(self):
        topic = self.prompt_input.get().strip()
        if not topic:
            messagebox.showerror("Error", "Please enter a research topic.")
            return

        # This is where we check for the Crews module - do it before launching the thread
        try:
            from Crews import crew
        except ImportError:
            messagebox.showerror("Error", "The Crews module is not available. Please try again later.")
            return

        self.current_topic = topic
        self.status_label.configure(text="Researching....")  # Start with Researching message immediately
        self.submit_button.configure(state="disabled")
        self.download_button.configure(state="disabled")

        # Add the user's query as a message bubble
        # self.add_user_message(topic)

        # Run the research process in a separate thread
        threading.Thread(target=self.process_topic, args=(topic,), daemon=True).start()

    # def add_user_message(self, message):
    #     message_frame = ctk.CTkFrame(self.reports_container,
    #                                  fg_color="#e1f5fe" if ctk.get_appearance_mode() == "Light" else "#1e3a5f")
    #     message_frame.grid(row=self.current_row, column=0, padx=(80, 20), pady=10, sticky="e")
    #     self.current_row += 1
    #
    #     user_label = ctk.CTkLabel(message_frame, text="You", font=self.subheading_font)
    #     user_label.pack(anchor="w", padx=10, pady=(10, 0))
    #
    #     message_label = ctk.CTkLabel(message_frame, text=message,
    #                                  font=self.normal_font,
    #                                  wraplength=500, justify="left")
    #     message_label.pack(anchor="w", padx=10, pady=(5, 10))

    def add_assistant_message(self, title=None, message=None):
        message_frame = ctk.CTkFrame(self.reports_container,
                                     fg_color="#f5f5f5" if ctk.get_appearance_mode() == "Light" else "#2d2d2d")
        message_frame.grid(row=self.current_row, column=0, padx=(20, 80), pady=10, sticky="w")
        self.current_row += 1

        # Add the assistant label
        assistant_label = ctk.CTkLabel(message_frame, text="Research Assistant",
                                       font=self.subheading_font)
        assistant_label.pack(anchor="w", padx=10, pady=(10, 0))

        # Add the title if provided
        if title:
            title_label = ctk.CTkLabel(message_frame, text=title,
                                       font=self.subheading_font)
            title_label.pack(anchor="w", padx=10, pady=(5, 0))

        # Add the message text if provided
        if message:
            # Create a scrollable text area for the report
            message_text = ctk.CTkTextbox(message_frame, wrap="word",
                                          height=400, width=600,
                                          font=self.normal_font)
            message_text.pack(padx=10, pady=10, fill="both", expand=True)
            message_text.insert("1.0", message)
            message_text.configure(state="disabled")

    def process_topic(self, topic):
        try:
            # Import inside the function to avoid global import issues
            from Crews import crew

            # Add a placeholder for the assistant's response
            self.root.after(0, self.add_assistant_message, "Researching...")

            result = crew.kickoff(inputs={"topic": topic})
            result_str = str(result)

            # Show Analyzing for 4 seconds
            self.root.after(0, self.update_status, "Analyzing....")
            time.sleep(3)  # Exact same delay as original script

            # Show Writing Report for 2 seconds
            self.root.after(0, self.update_status, "Writing Report....")
            time.sleep(3)  # Exact same delay as original script


            # Write result to file exactly as in original script
            with open(self.default_file_path, "w", encoding="utf-8") as file:
                file.write(result_str)

            # Update UI with completion message
            self.current_report = result_str
            self.root.after(0, self.update_status, "Report has successfully completed.")
            self.root.after(0, self.update_assistant_message, result_str)

        except ImportError:
            self.root.after(0, self.show_error, "The Crews module is not available. Please try again later.")
        except Exception as e:
            self.root.after(0, self.show_error, str(e))

    def update_status(self, message):
        self.status_label.configure(text=message)

    def update_assistant_message(self, result):
        # Enable the download button
        self.download_button.configure(state="normal")
        self.submit_button.configure(state="normal")

        # Remove the placeholder message and add the complete report
        for widget in self.reports_container.winfo_children():
            widget.destroy()

        # Reset row counter
        self.current_row = 0

        # Re-add the messages
        #self.add_user_message(self.current_topic)
        self.add_assistant_message(f"Research Report on: {self.current_topic}", result)

    def download_report(self):
        if not self.current_report or not self.current_topic:
            messagebox.showerror("Error", "No report available to download.")
            return

        # Ask user for save location with default being report.md in current directory
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"{self.current_topic.replace(' ', '_')}_report.md"
        )

        if not file_path:  # User cancelled
            return

        try:
            with open(file_path, 'w', encoding="utf-8") as f:
                # Write the topic at the top of the file
                f.write(f"# Research Report: {self.current_topic}\n\n")
                f.write(self.current_report)

            messagebox.showinfo("Success", f"Report saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {str(e)}")

    def clear_fields(self):
        self.prompt_input.delete(0, "end")

        # Clear the report container
        for widget in self.reports_container.winfo_children():
            widget.destroy()

        # Reset row counter
        self.current_row = 0

        self.download_button.configure(state="disabled")
        self.current_report = None
        self.current_topic = None
        self.status_label.configure(text="")  # Set to blank instead of "Ready"

    def show_error(self, error_message):
        messagebox.showerror("Error", error_message)
        self.status_label.configure(text="Error encountered")
        self.submit_button.configure(state="normal")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()


def main():
    root = ctk.CTk()
    app = PromptReportApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()