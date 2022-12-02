"""Manually control the servos using calibrated driver"""
#import numpy as np
import math
import PySimpleGUI as sg
import servo


def main():

    current_chan = 0
    do_not_move = False
    mid_usec = 1500.0

    last_usec = [mid_usec for i in range(16)]

    layout = [
        [sg.Combo([c for c in range(16)],default_value=0,
                  enable_events=True,key='-CHAN-'),
         sg.Checkbox('Do Not Move Servo',default=do_not_move,
                     enable_events=True,key='-DONOTMOVE-')
        ],

        [sg.Text('Microseconds'),
         sg.Push(),
         sg.Slider((500,2500),default_value=mid_usec,orientation='horizontal',
                   enable_events=True,key='-USEC-')
        ],

        [sg.Text('Degrees'),
         sg.Push(),
         sg.Slider((0,180),default_value=90,orientation='horizontal',
                   enable_events=True,key='-DEG-')
        ],

        [sg.Text('Radians'),
         sg.Push(),
         sg.Slider((0.0, math.pi),resolution=0.01,default_value=math.pi/2.0,orientation='horizontal',
                   enable_events=True,key='-RAD-')
        ],

        [sg.HorizontalSeparator()],

        [sg.Button('Reset',enable_events=True,key='-RESET-'),
         sg.Push(),
         sg.Button('Quit',enable_events=True,key='-QUIT-')
        ]
    ]

    window = sg.Window('Servo Check', layout, finalize=True)

    s = servo.Servo()

    while True:  # Event Loop
        event, values = window.read()

        if event in (None, 'Exit', '-QUIT-'):
            break

        elif event == '-CHAN-':
            current_chan = values['-CHAN-']

            usec = last_usec[current_chan]
            rad = s.usec_to_radian(current_chan, usec)
            deg = math.degrees(rad)

            window['-USEC-'].update(usec)
            window['-DEG-'].update(deg)
            window['-RAD-'].update(rad)

        elif event == '-DONOTMOVE-':
            do_not_move = values['-DONOTMOVE-']

        elif event == '-USEC-':
            usec = values['-USEC-']
            rad = s.usec_to_radian(current_chan, usec)
            deg = math.degrees(rad)
            last_usec[current_chan] = usec

            window['-DEG-'].update(deg)
            window['-RAD-'].update(rad)

            if not do_not_move:
                s.move_usec(current_chan, usec)

        elif event == '-DEG-':
            deg = values['-DEG-']
            rad = math.radians(deg)
            usec = s.radian_to_usec(current_chan, rad)
            last_usec[current_chan] = usec

            window['-USEC-'].update(usec)
            window['-RAD-'].update(rad)

            if not do_not_move:
                s.move_radian(current_chan, rad)


        elif event == '-RAD-':
            rad = values['-RAD-']
            deg = math.degrees(rad)
            usec = s.radian_to_usec(current_chan, rad)
            last_usec[current_chan] = usec

            window['-DEG-'].update(deg)
            window['-USEC-'].update(usec)

            if not do_not_move:
                s.move_radian(current_chan, rad)

        elif event == '-RESET-':
            last_usec = [mid_usec for i in range(16)]

            usec = mid_usec
            rad = s.usec_to_radian(current_chan, usec)
            deg = math.degrees(rad)

            window['-USEC-'].update(usec)
            window['-DEG-'].update(deg)
            window['-RAD-'].update(rad)


if __name__ == '__main__':
    main()