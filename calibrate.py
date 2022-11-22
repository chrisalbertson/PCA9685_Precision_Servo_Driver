"""User facing applcation to create a calibration file for a set of serves."""
from typing import Tuple
import logging
import math
import yaml
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import PySimpleGUI as sg
log = logging.getLogger(__name__)

# Tis is the dictionary that is written as a YAML file.
servo_cal = dict()
current_channel = 0

def point_key_funct(point):
    return point[0]


def printcal():
    for x in servo_cal:
        print(servo_cal[x])


def active_channels():
    global servo_cal
    ch_list = []
    for ch_indx in range(16):
        if servo_cal[ch_indx]['active']:
            ch_list.append(str(ch_indx))
    return ch_list


def unique(list1):
    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

def init_cal_data():

    global servo_cal

    default_cal = [
        (1000.0,   0.0),
        (1500.0,  90.0),
        (2000.0, 180.0)
        ]

    default_channel = {
        'active': True,
        'valid fit': True,
        'name': '',
        'angle lower limit':   0.0,
        'angle upper limit': 180.0,
        'slope': 0.5,
        'intercept': -180.0,
        'rvalue': 1.0,
        'points': []
        }

    for ch_indx in range(16):
        default_channel['name']   = 'servo'+str(ch_indx)
        default_channel['points'] = default_cal.copy()
        servo_cal[ch_indx] = default_channel.copy()


def run_gui():

    #global cal_data
    global servo_cal
    global current_channel

    init_cal_data()
    print(servo_cal)

    num_input_sz = 15

    lower_limit = 0.0
    upper_limit = 180.0

    default180_points = [
        (1000.0, 0.0),
        (1500.0, 90.0),
        (2000.0, 180.0)
        ]

    default270_points = [
        (1000.0, 0.0),
        (1500.0, 270.0/2.0),
        (2000.0, 270.0)
        ]

    chan_def_color = 'grey'
    chan_active_color = 'yellow'

    ch_key = []
    for i in range(16):
        ch_key.append('CH'+str(i))

    layout = [[sg.Radio('degrees', 'UNITS', default=True, key='RADIO_DEG', size=10),
               sg.Radio('radians', 'UNITS', key='RADIO_RAD', size=10)],

              [sg.HSep()],

              [sg.Radio(' 0', 'CHAN', enable_events=True, key=ch_key[0], s=2, background_color=chan_def_color),
               sg.Radio(' 1', 'CHAN', enable_events=True, key=ch_key[1], s=2,  background_color=chan_def_color),
               sg.Radio(' 2', 'CHAN', enable_events=True, key=ch_key[2], s=2,  background_color=chan_def_color),
               sg.Radio(' 3', 'CHAN', enable_events=True, key=ch_key[3], s=2,  background_color=chan_def_color),
               sg.VSep(),
               sg.Radio(' 4', 'CHAN', enable_events=True, key=ch_key[4], s=2,  background_color=chan_def_color),
               sg.Radio(' 5', 'CHAN', enable_events=True, key=ch_key[5], s=2,  background_color=chan_def_color),
               sg.Radio(' 6', 'CHAN', enable_events=True, key=ch_key[6], s=2,  background_color=chan_def_color),
               sg.Radio(' 7', 'CHAN', enable_events=True, key=ch_key[7], s=2,  background_color=chan_def_color)],

              [sg.Radio(' 8', 'CHAN', enable_events=True, key=ch_key[8], s=2,  background_color=chan_def_color),
               sg.Radio(' 9', 'CHAN', enable_events=True, key=ch_key[9], s=2,  background_color=chan_def_color),
               sg.Radio('10', 'CHAN', enable_events=True, key=ch_key[10], s=2,  background_color=chan_def_color),
               sg.Radio('11', 'CHAN', enable_events=True, key=ch_key[11], s=2,  background_color=chan_def_color),
               sg.VSep(),
               sg.Radio('12', 'CHAN', enable_events=True, key=ch_key[12], s=2,  background_color=chan_def_color),
               sg.Radio('13', 'CHAN', enable_events=True, key=ch_key[13], s=2,  background_color=chan_def_color),
               sg.Radio('14', 'CHAN', enable_events=True, key=ch_key[14], s=2,  background_color=chan_def_color),
               sg.Radio('15', 'CHAN', enable_events=True, key=ch_key[15], s=2,  background_color=chan_def_color)],

              [sg.HSep()],

              [sg.Push(),
               sg.Text('Editing Channel Number'),
               sg.Push()
              ],

              [sg.Push(),
               sg.Text(str(current_channel), font=('courier', 24, 'bold'), key='-CHNUM-'),
               sg.Push()
              ],

              [sg.HSep()],

              [sg.Push(),
               sg.InputText(str(lower_limit), key='LOWER_LIMIT', size=num_input_sz, enable_events=True),
               sg.InputText(str(upper_limit), key='UPPER_LIMIT', size=num_input_sz, enable_events=True),
               sg.Push()
              ],

              [sg.Push(),
               sg.Text('Angle, lower limit', size=num_input_sz),
               sg.Text('Angle, upper limit', size=num_input_sz),
               sg.Push()
              ],

              [sg.Push(),
               sg.Table(servo_cal[current_channel]['points'],
                        key='POINT_TABLE',
                        col_widths=[15,15,15],
                        headings=['   usec   ', '   angle   '],
                        enable_events=True,
                        ),
               sg.Push(),
              ],

              [sg.Push(),
               sg.Button('Clear', key ='CLEAR'),
               sg.Button('default 180', key='DEF180'),
               sg.Button('default 270', key='DEF270'),
               sg.Push()
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
               sg.Push(),
               sg.Button('Save', key='SAVE'),
               sg.Button('Quit', key='QUIT')
              ]
             ]
    window = sg.Window('Servo Calibration', layout, finalize=True)

    window['LOWER_LIMIT'].bind('<FocusOut>', '+FOCUSOUT')
    window['UPPER_LIMIT'].bind('<FocusOut>', '+FOCUSOUT')
    window['CH' + str(current_channel)].update(background_color=chan_active_color)

    while True:  # Event Loop
        event, values = window.read()

        if event in (None, 'Exit', 'QUIT'):
            break

        elif event == 'RADIO_DEG':
            pass

        elif event == 'RADIO_RAD':
            pass

        elif event in ch_key:
            window['CH'+str(current_channel)].update(background_color=chan_def_color)
            current_channel = int(event[2:])
            window[event].update(background_color=chan_active_color)
            window['-CHNUM-'].update(str(current_channel))
            window['POINT_TABLE'].update(servo_cal[current_channel]['points'])
            window['USEC'].update('')
            window['ANGLE'].update('')
            window['LOWER_LIMIT'].update(str(servo_cal[current_channel]['angle lower limit']))
            window['UPPER_LIMIT'].update(str(servo_cal[current_channel]['angle upper limit']))

        elif event == 'LOWER_LIMIT':
            pass

        elif event == 'LOWER_LIMIT+FOCUSOUT':
            ll_str = values['LOWER_LIMIT']
            try:
                ll = float(ll_str)
                servo_cal[current_channel]['angle lower limit'] = ll
            except (ValueError, TypeError):
                sg.popup('Lower Limit should be a number', title='ERROR')

        elif event == 'UPPER_LIMIT':
            pass

        elif event == 'UPPER_LIMIT+FOCUSOUT':
            ul_str = values['UPPER_LIMIT']
            try:
                ul = float(ul_str)
                servo_cal[current_channel]['angle upper limit'] = ul
            except (ValueError, TypeError):
                sg.popup   ('Upper Limit should be a number', title='ERROR')

        elif event == 'USEC':
            pass

        elif event == 'ANGLE':
            pass

        elif event == 'ADD':

            angle_val = float(values['ANGLE'])
            usec_val  = float(values['USEC'])

            servo_cal[current_channel]['points'].append((usec_val, angle_val))

            pts = unique(servo_cal[current_channel]['points'])
            pts.sort(key=point_key_funct)
            servo_cal[current_channel]['points'] = pts

            window['POINT_TABLE'].update(pts)

        elif event == 'REMOVE':

            angle_val = float(values['ANGLE'])
            usec_val  = float(values['USEC'])

            for pt_index, pt in enumerate(servo_cal[current_channel]['points']):
                if pt == (usec_val, angle_val):
                    servo_cal[current_channel]['points'].pop(pt_index)
                    break

            window['POINT_TABLE'].update(servo_cal[current_channel]['points'])

        elif event == 'CLEAR':
            servo_cal[current_channel]['points'] = []
            window['POINT_TABLE'].update([])

        elif event == 'DEF180':
            servo_cal[current_channel]['points'] = default180_points.copy()
            window['POINT_TABLE'].update(servo_cal[current_channel]['points'])

        elif event == 'DEF270':
            servo_cal[current_channel]['points'] = default270_points.copy()
            window['POINT_TABLE'].update(servo_cal[current_channel]['points'])

        elif event == 'POINT_TABLE':

            if values['POINT_TABLE'] != []:
                row_index = values['POINT_TABLE'][0]
                row = servo_cal[current_channel]['points'][row_index]

                window['USEC'].update(row[0])
                window['ANGLE'].update(row[1])

        elif event == 'FIT':

            pnts = np.array(servo_cal[current_channel]['points'])

            if len(pnts) >= 2:
                lower_limit_val = float(values['LOWER_LIMIT'])
                upper_limit_val = float(values['UPPER_LIMIT'])


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
                plt.title('Fit for Channel Number ' + str(current_channel))
                plt.xlabel('degrees')
                plt.ylabel('microseconds')

                summary = ('number of points = %3d\n' +
                           'slope\t= %4.5f\n' +
                           'intercept\t= %4.5f\n' +
                           'rvalue\t= %4.5f'
                           ) % (len(x), res.slope, res.intercept, res.rvalue)
                window['MULTI'].update(summary)

                plt_summary = ('number of points = %3d\n' +
                               'slope = %4.5f\n' +
                               'intercept = %4.5f\n' +
                               'rvalue = %4.5f'
                               ) % (len(x), res.slope, res.intercept, res.rvalue)
                plt.text((min(x)+max(x))/2.0, min(y), plt_summary)
                plt.show()



            else:
                sg.popup('At least two points are required to fit a line.',
                         title='ERROR')

        elif event == 'SAVE':
            with open('servo_cal.yaml', mode="wt", encoding="utf-8") as file:
                yaml.dump(servo_cal, file)


if __name__ == "__main__":
    logging.basicConfig(filename='calibrate.log',
                        filemode='w',
                        level=logging.WARNING)

    log.info('Starting GUI')
    run_gui()
    log.info('normal termination')
