"""User facing applcation to creat calibration files for a set of serves."""
from typing import Tuple
import logging
import math
import yaml
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import PySimpleGUI as sg
log = logging.getLogger(__name__)


def point_key_funct(point):
    return point[0]


def unique(list1):
    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def run_gui():
    num_input_sz = 15

    lower_limit = 0.0
    upper_limit = 180.0

    # This is a list of points entered by the user.
    # Each point is a tuple of (micro_seconds, degrees)
    cal_points = []

    default180_points = [[1000.0, 0.0],
                         [1500.0, 90.0],
                         [2000.0, 180.0]]
    default270_points = [[1000.0, 0.0],
                         [1500.0, 270.0/2.0],
                         [2000.0, 270.0]]

    ch_active = []
    for i in range(16):
        ch_active.append(True)

    ch_key = []
    for i in range(16):
        ch_key.append('CH'+str(i))

    ch_list = []
    for ch_index, ch in enumerate(ch_active):
        if ch:
            ch_list.append(str(ch_index))

    layout = [[sg.Radio('degrees', 'UNITS', default=True, key='RADIO_DEG'),
               sg.Radio('radians', 'UNITS', key='RADIO_RAD')],

              [sg.HSep()],

              [sg.Checkbox('0', default=ch_active[0], size=2, enable_events=True, key=ch_key[0]),
               sg.Checkbox('1', default=ch_active[1], size=2, enable_events=True, key=ch_key[1]),
               sg.Checkbox('2', default=ch_active[2], size=2, enable_events=True, key=ch_key[2]),
               sg.Checkbox('3', default=ch_active[3], size=2, enable_events=True, key=ch_key[3]),
               sg.VSep(),
               sg.Checkbox('4', default=ch_active[4], size=2, enable_events=True, key=ch_key[4]),
               sg.Checkbox('5', default=ch_active[5], size=2, enable_events=True, key=ch_key[5]),
               sg.Checkbox('6', default=ch_active[6], size=2, enable_events=True, key=ch_key[6]),
               sg.Checkbox('7', default=ch_active[7], size=2, enable_events=True, key=ch_key[7])],

              [sg.Checkbox('8', default=ch_active[8], size=2, enable_events=True, key=ch_key[8]),
               sg.Checkbox('9', default=ch_active[9], size=2, enable_events=True, key=ch_key[9]),
               sg.Checkbox('10', default=ch_active[10], size=2, enable_events=True, key=ch_key[10]),
               sg.Checkbox('11', default=ch_active[11], size=2, enable_events=True, key=ch_key[11]),
               sg.VSep(),
               sg.Checkbox('12', default=ch_active[12], size=2, enable_events=True, key=ch_key[12]),
               sg.Checkbox('13', default=ch_active[13], size=2, enable_events=True, key=ch_key[13]),
               sg.Checkbox('14', default=ch_active[14], size=2, enable_events=True, key=ch_key[14]),
               sg.Checkbox('15', default=ch_active[15], size=2, enable_events=True, key=ch_key[15])],

              [sg.HSep()],

              [sg.Text('            Channel Number'),
               sg.Listbox(ch_list, key='CHAN_NUM', default_values=['0'], size=(3,1),
                          enable_events=True)],

              [ sg.InputText(str(lower_limit), key='LOWER_LIMIT', size=num_input_sz,),
                sg.InputText(str(upper_limit), key='UPPER_LIMIT', size=num_input_sz)],

              [sg.Text('Angle, lower limit', size=num_input_sz),
               sg.Text('Angle, upper limit', size=num_input_sz)],

              [sg.Table(cal_points,
                        key='POINT_TABLE',
                        col_widths=[15,15,15],
                        headings=['   usec   ', '   angle   '],
                        enable_events=True,
                        )],

              [sg.Button('Clear', key ='CLEAR'),
               sg.Button('default 180', key='DEF180'),
               sg.Button('default 270', key='DEF270')
              ],

              [sg.InputText( key='USEC',  size=num_input_sz),
               sg.InputText( key='ANGLE', size=num_input_sz),
               sg.Button('add', key='ADD'),
               sg.Button('remove', key='REMOVE')],

              [sg.Text('micro seconds', size=num_input_sz),
               sg.Text('measured angle', size=num_input_sz)
              ],

              [sg.HSep()],

              [sg.Multiline(default_text="",
                            size=(30,4),
                           #font='Courier',
                            key='MULTI')],

              [sg.Button('Fit', key='FIT'),
               sg.Button('Save', key='SAVE'),
               sg.Button('Quit', key='QUIT')
              ]
             ]
    window = sg.Window('Servo Calibration', layout)


    while True:  # Event Loop
        event, values = window.read()

        if event in (None, 'Exit', 'QUIT'):
            break

        elif event == 'RADIO_DEG':
            pass

        elif event == 'RADIO_RAD':
            pass

        elif event in ch_key:

            ch_state = values[event]
            ch_index = int(event[2:])
            ch_active[ch_index] = ch_state

            ch_list = []
            for ch_index, ch in enumerate(ch_active):
                if ch:
                    ch_list.append(str(ch_index))

            window['CHAN_NUM'].update(values=ch_list)

        elif event == 'CHAN_NUM':
            print(values['CHAN_NUM'])
            #channel_number = int(values['CHAN_NUM'])

        elif event == 'LOWER_LIMIT':
            pass

        elif event == 'UPPER_LIMIT':
            pass

        elif event == 'USEC':
            pass

        elif event == 'ANGLE':
            pass

        elif event == 'ADD':

            angle_val = float(values['ANGLE'])
            usec_val  = float(values['USEC'])

            cal_points.append([usec_val, angle_val])
            cal_points = unique(cal_points)
            cal_points.sort(key=point_key_funct)

            window['POINT_TABLE'].update(cal_points)

        elif event == 'REMOVE':

            angle_val = float(values['ANGLE'])
            usec_val  = float(values['USEC'])

            for pnt_index, pnt in enumerate(cal_points):
                if pnt == [usec_val, angle_val]:
                    cal_points.pop(pnt_index)
                    break

            window['POINT_TABLE'].update(cal_points)

        elif event == 'CLEAR':
            cal_points = []
            window['POINT_TABLE'].update(cal_points)

        elif event == 'DEF180':
            cal_points = default180_points
            window['POINT_TABLE'].update(cal_points)

        elif event == 'DEF270':
            cal_points = default270_points
            window['POINT_TABLE'].update(cal_points)

        elif event == 'POINT_TABLE':

            if values['POINT_TABLE'] != []:
                row_index = values['POINT_TABLE'][0]
                row = cal_points[row_index]
                print(row)

                window['USEC'].update(row[0])
                window['ANGLE'].update(row[1])

        elif event == 'FIT':

            if len(cal_points) >= 2:
                lower_limit_val = float(values['LOWER_LIMIT'])
                upper_limit_val = float(values['UPPER_LIMIT'])

                pnts = np.array(cal_points)
                x = pnts[:,1]   # Angles
                y = pnts[:,0]   # Pulse Width in microseconds
                res = stats.linregress(x, y)

                plt.clf()
                plt.plot(x, y, 'o', label='calibration points')
                plt.plot(x, res.intercept + res.slope * x, 'r', label='fitted line')
                plt.vlines(lower_limit_val,
                           ymin=min(y),
                           ymax=0.8*max(y),
                           linestyles='dashed',
                           colors='green',
                           label='lower limit')
                plt.vlines(upper_limit_val,
                           ymin=min(y),
                           ymax=max(y),
                           linestyles='dashed',
                           label='upper limit')
                plt.legend()
                ch_num = values['CHAN_NUM'][0]
                plt.title('Fit for Channel Number ' + ch_num)
                plt.xlabel('degrees')
                plt.ylabel('microseconds')

                summary = ('number of points = %3d\n' +
                           'slope\t= %4.5f\n' +
                           'intercept\t= %4.5f\n' +
                           'rvalue\t= %4.5f'
                           ) % (len(x), res.slope, res.intercept, res.rvalue)
                window['MULTI'].update(summary)

                plt.show()



            else:
                sg.popup('At least two points are required to fit a line.',
                         title='ERROR')

        elif event == 'SAVE':
            with open('servo_cal.yaml', mode="wt", encoding="utf-8") as file:
                yaml.dump(cal_points, file)


if __name__ == "__main__":
    logging.basicConfig(filename='calibrate.log',
                        filemode='w',
                        level=logging.WARNING)

    log.info('Starting GUI')
    run_gui()
    log.info('normal termination')
