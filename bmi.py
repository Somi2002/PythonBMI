import customtkinter as ctk
import threading
import time
from settings import *

try:
    from ctypes import windll, byref, sizeof, c_int
except ImportError:
    pass

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BACKGROUND_COLOR)
        self.title("Sazid's BMI Calculator")
        self.geometry('400x400')
        self.resizable(False, False)
        self.change_title_bar_color()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=2)

        # Data - using Imperial units
        self.height_inches = ctk.IntVar(value=67)  # Height in inches
        self.height_inches.trace_add("write", lambda *args: self.update_bmi())
        self.weight_pounds = ctk.DoubleVar(value=150)  # Weight in pounds
        self.bmi_string = ctk.StringVar()
        self.update_bmi()

        # Widgets
        self.result_text = ResultText(self, self.bmi_string)
        self.result_text.grid(column=0, row=0, sticky='nsew')
        self.weight_input = WeightInput(self, self.weight_pounds)
        self.weight_input.grid(column=0, row=1, sticky='nsew')
        HeightInput(self, self.height_inches)  # Adjusted to pass only height_inches
        UnitSwitcher(self)
        self.mainloop()

    def update_bmi(self, *args):
        # Calculate the total height in inches
        total_height_inches = self.height_inches.get()
        # Calculate the BMI using Imperial formula
        bmi_result = 703 * self.weight_pounds.get() / (total_height_inches ** 2)
        self.bmi_string.set(round(bmi_result, 2))

    def change_title_bar_color(self):
        try:
            HWND = windll.user32.GetParent(self.winfo_id())
            DWMWA_ATTRIBUTE = 35
            windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_ATTRIBUTE, byref(c_int(TITLE_HEX_COLOR)), sizeof(c_int))
        except Exception as e:
            print(f"Error changing title bar color: {e}")


class ResultText(ctk.CTkLabel):
    def __init__(self, parent, bmi_string):
        font = ctk.CTkFont(family=FONT, size=MAIN_TEXT_SIZE, weight='bold')
        super().__init__(master=parent, textvariable=bmi_string, font=font, anchor='center', text_color=TEXT_COLOR)

class WeightInput(ctk.CTkFrame):
    def __init__(self, parent, weight_pounds):
        super().__init__(master=parent, fg_color=LIGHT_BACKGROUND_COLOR, height=80)
        self.weight_pounds = weight_pounds
        self.grid(column=0, row=2, sticky='nsew', padx=10, pady=10)
        self.columnconfigure((0, 5), weight=1)
        self.columnconfigure((1, 4), weight=0)
        self.columnconfigure((2, 3), weight=0)
        self.rowconfigure(0, weight=1)
        font = ctk.CTkFont(family=FONT, size=INPUT_FONT_SIZE)
        self.create_widgets(font)

    def create_widgets(self, font):
        self.minus_button = self.create_button('-', 0, font, TEXT_COLOR, SECONDARY_COLOR)
        self.bind_button_events(self.minus_button, lambda: self.adjust_weight(-1))
        self.small_minus_button = self.create_button('-', 1, font, TEXT_COLOR, PRIMARY_COLOR)
        self.bind_button_events(self.small_minus_button, lambda: self.adjust_weight(-0.1))

        self.weight_label = self.create_label(f'{self.weight_pounds.get():.1f}', 2, font, TEXT_COLOR)
        self.kg_label = self.create_label('lb', 3, font, TEXT_COLOR)

        self.plus_button = self.create_button('+', 5, font, TEXT_COLOR, SECONDARY_COLOR)
        self.bind_button_events(self.plus_button, lambda: self.adjust_weight(1))
        self.small_plus_button = self.create_button('+', 4, font, TEXT_COLOR, PRIMARY_COLOR)
        self.bind_button_events(self.small_plus_button, lambda: self.adjust_weight(0.1))

    def adjust_weight(self, adjustment):
        current_weight = self.weight_pounds.get()
        new_weight = max(current_weight + adjustment, 0)
        self.weight_pounds.set(new_weight)
        self.weight_label.configure(text=f'{new_weight:.1f}')
        self.master.update_bmi()

    def create_button(self, text, column, font, text_color, bg_color):
        button = ctk.CTkButton(self, text=text, font=font, text_color=text_color,
                               fg_color=bg_color, hover_color=ACCENT_COLOR,
                               corner_radius=BUTTON_CORNER_RADIUS)
        button.grid(row=0, column=column, sticky='ew', padx=4, pady=4)
        return button
    
    def bind_button_events(self, button, command):
        button.bind('<ButtonPress-1>', lambda event: self.start_auto_repeat(command))
        button.bind('<ButtonRelease-1>', lambda event: self.stop_auto_repeat())
    
    def start_auto_repeat(self, command):
        self.stop = False
        def repeat_command():
            while not self.stop:
                command()
                time.sleep(0.1)  # Adjust the speed of auto-repeat here
        self.auto_repeat_thread = threading.Thread(target=repeat_command)
        self.auto_repeat_thread.start()
    
    def stop_auto_repeat(self):
        self.stop = True

    def create_label(self, text, column, font, text_color):
        label = ctk.CTkLabel(self, text=text, text_color=text_color, font=font)
        label.grid(row=0, column=column, sticky='ew')
        return label

class HeightInput(ctk.CTkFrame):
    def __init__(self, parent, height_inches):
        super().__init__(master=parent, fg_color=PRIMARY_COLOR)
        self.grid(row=3, column=0, sticky='nsew', padx=10, pady=10)
        
        # Assuming the height range to be from 4'0" (48 inches) to 7'0" (84 inches)
        self.slider = ctk.CTkSlider(master=self, from_=48, to=84, variable=height_inches,
                                    button_color=SECONDARY_COLOR, progress_color=SECONDARY_COLOR)
        self.slider.pack(side='left', fill='x', expand=True, pady=10, padx=10)

        # Label to display the height
        self.height_label = ctk.CTkLabel(self, textvariable=self.construct_height_string(height_inches), 
                                         font=ctk.CTkFont(family=FONT, size=INPUT_FONT_SIZE))
        self.height_label.pack(side='left', padx=20)

    def construct_height_string(self, height_inches):
        height_string = ctk.StringVar()
        
        def update_height_string(*args):
            total_inches = height_inches.get()
            feet = total_inches // 12
            inches = total_inches % 12
            formatted_height = f"{feet}'{inches:02}\"" 
            height_string.set(formatted_height)

            
        # Trace changes to the slider
        height_inches.trace('w', update_height_string)
        update_height_string()  # Initial update to display the default height
        
        return height_string

class UnitSwitcher(ctk.CTkLabel):
    def __init__(self, parent):
        super().__init__(master=parent, text='imperial', text_color=SECONDARY_COLOR, font=ctk.CTkFont(family=FONT, size=SWITCH_FONT_SIZE, weight='bold'))
        self.place(relx=0.98, rely=0.01, anchor='ne')

if __name__ == '__main__':
    App()

