from PySide6.QtCore import QPropertyAnimation

def animation(widget, duration=450):
    widget.setWindowOpacity(0)

    widget.show()

    anim = QPropertyAnimation(widget, b"windowOpacity")
    anim.setDuration(duration)
    anim.setStartValue(0)
    anim.setEndValue(1)

    widget.animation = anim

    anim.start()