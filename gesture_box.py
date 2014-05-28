from kivy.gesture import GestureDatabase
from kivy.uix.boxlayout import BoxLayout

gesture_strings = {
        'left_to_right_line': 'eNp91XtsU...<snip>...4hSE=',
        'right_to_left_line': 'eNp91UlME...<snip>...Erg==',
        'bottom_to_top_line': 'eNp91HlsD...<snip>...NMndJz'
    }

gestures = GestureDatabase()
for name, gesture_string in gesture_strings.items():
    gesture = gestures.str_to_gesture(gesture_string)
    gesture.name = name
    gestures.add_gesture(gesture)


class GestureBox(BoxLayout):

    def on_touch_down(self, touch):
        touch.ud['gesture_path'] = [(touch.x, touch.y)]
        super(GestureBox, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        touch.ud['gesture_path'].append((touch.x, touch.y))
        super(GestureBox, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if 'gesture_path' in touch.ud:
            gesture = Gesture()
            gesture.add_stroke(touch.ud['gesture_path'])
            gesture.normalize()
            match = gestures.find(gesture, minscore=0.99)
            if match:
                print("{} happened".format(match[1].name))
        super(GestureBox, self).on_touch_up(touch)