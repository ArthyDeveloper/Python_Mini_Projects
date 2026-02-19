import pynput, pyautogui, time
from pynput.mouse import Controller, Button
click_count = 1
toggled = False

def main():
  #mouse = Controller()
  def toggle_aim(x, y, button, pressed):
    global toggled, click_count
    print(f"Click: {x}, {y} | Button: {button}, {button.name} | Pressed: {pressed}")
    button_clicked = button.name
    is_pressed = pressed
    if button_clicked == "right":
      click_count += 1
      if click_count % 3 == 0:
        toggled = not toggled
        click_count = 0
        print("Toggling Aim" if toggled else "Disabling Aim")
        if toggled:
          pyautogui.mouseDown(button="right")
        else:
          pyautogui.mouseUp(button="right")

  with pynput.mouse.Listener(on_click=toggle_aim) as listener: listener.join()
  listener.start()

if __name__ == "__main__":
  main()
