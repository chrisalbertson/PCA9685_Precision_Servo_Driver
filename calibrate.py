"""User facing applcation to create a calibration file for a set of serves."""
import logging
import math

import yaml
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import PySimpleGUI as sg
import pca9685

pca = pca9685.PCA9685()

log = logging.getLogger(__name__)

# This is the dictionary that is written as a YAML file.
servo_cal = dict()
current_channel = 0
units = {
    '-RAD-': {'sgtext': 'Radians'},
    '-DEG-': {'sgtext': 'Degrees'}
    }
current_units = '-DEG-'


default180_points = [
    [1000.0, 0.0],
    [1500.0, math.radians(90.0)],
    [2000.0, math.radians(180.0)]
    ]

default270_points = [
    [1000.0, 0.0],
    [1500.0, math.radians(270.0 / 2.0)],
    [2000.0, math.radians(270.0)]
    ]

default_cal = default180_points

def to_rad(angle: float) -> float:
    """Convert and angle whatever is the current unit to radians"""

    if current_units == '-DEG-':
        rad = math.radians(angle)
    elif current_units == '-RAD-':
        rad = angle
    else:
        raise ValueError

    return rad % (2.0 * math.pi)


def from_deg(deg: float) -> float:
    """Convert and angle from degrees to whatever is the current unit"""

    if current_units == '-DEG-':
        current = deg
    elif current_units == '-RAD-':
        current = math.radians(deg)
    else:
        raise ValueError

    return current


def from_rad(rad: float) -> float:
    """Convert and angle from radians to whatever is the current unit"""

    if current_units == '-DEG-':
        current = math.degrees(rad)
    elif current_units == '-RAD-':
        current = rad
    else:
        raise ValueError

    return current

def point_key_funct(point):
    return point[0]


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
    global default_cal

    default_channel = {
        'active': True,
        'valid fit': False,
        'name': '',
        'angle lower limit':   0.0,
        'angle upper limit': math.radians(180.0),
        'slope': 0.0,
        'intercept': 0.0,
        'rvalue': 0.0,
        'points': []
        }

    for ch_indx in range(16):
        default_channel['name']   = 'servo'+str(ch_indx)
        default_channel['points'] = default_cal.copy()
        servo_cal[ch_indx] = default_channel.copy()

def points_current(points: list) -> list:
    disp = []
    for pnt in points:
        disp.append([pnt[0], from_rad(pnt[1])])
    return disp


def run_gui():

    global servo_cal
    global current_channel
    global default180_points
    global default270_points
    global units
    global current_units

    init_cal_data()

    num_input_sz = 20

    lower_limit = 0.0
    upper_limit = 0.0

    chan_def_color = 'grey'
    chan_active_color = 'yellow'

    ch_key = []
    for i in range(16):
        ch_key.append('CH'+str(i))

    edit_section = [
        [sg.Text('Channel Name'),
         sg.InputText('', key='CHAN_NAME', enable_events=True,
                      tooltip='The channel may be given a name, but the name is not used.')
         ],

        [sg.Push(),
         sg.InputText(str(from_rad(lower_limit)), key='LOWER_LIMIT', size=num_input_sz, enable_events=True),
         sg.InputText(str(from_rad(upper_limit)), key='UPPER_LIMIT', size=num_input_sz, enable_events=True),
         sg.Push()
         ],

        [sg.Push(),
         sg.Text(' ', key='-LL_TXT-', size=num_input_sz),
         sg.Text(' ', key='-UL_TXT-', size=num_input_sz),
         sg.Push()
         ],

        [sg.Push(),
         sg.Table([],
                  key='POINT_TABLE',
                  col_widths=[15, 15, 15],
                  headings=['   usec   ', '   angle   '],
                  enable_events=True,
                  ),
         sg.Push(),
         ],

        [sg.Push(),
         sg.Button('Clear', key='CLEAR'),
         sg.Button('default 180', key='DEF180'),
         sg.Button('default 270', key='DEF270'),
         sg.Push()
         ],

        [sg.Text('micro seconds', size=num_input_sz),
         sg.Text(' ', key='-MEASURED_ANGLE-', size=num_input_sz)
         ],

        [sg.InputText(key='USEC', size=num_input_sz),
         sg.InputText(key='ANGLE', size=num_input_sz),
         sg.Button('add', key='ADD'),
         sg.Button('remove', key='REMOVE')
         ],

        [sg.Button('Move To', key='-MOVE-'),
         sg.Push()
         ]
    ]

    layout = [
        [sg.Radio(units['-DEG-']['sgtext'], 'UNITS', key='-DEG-', size=10, enable_events=True, default=True),
         sg.Radio(units['-RAD-']['sgtext'], 'UNITS', key='-RAD-', size=10, enable_events=True)
        ],

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

        [sg.Checkbox('Channel Enabled, if checked',
                   enable_events=True, default=True, key='CHAN_ENABLED',
                   tooltip='Disable the channel (uncheck) if there is no servo connected.')
        ],

        [sg.pin(sg.Column(edit_section, key='EDIT_SECTION'))],

        [sg.HSep()],

        [sg.Multiline(default_text="",
                    size=(30,4),
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

    def update_window(window):
        window['CH' + str(current_channel)].update(background_color=chan_active_color)
        window['CHAN_NAME'].update(servo_cal[current_channel]['name'])
        window['CHAN_ENABLED'].update(servo_cal[current_channel]['active'],
                                      text_color='black')
        unit_txt = units[current_units]['sgtext']
        window['-LL_TXT-'].update(unit_txt + ', lower limit')
        window['-UL_TXT-'].update(unit_txt + ', upper limit')
        window['LOWER_LIMIT'].update(str(from_rad(servo_cal[current_channel]['angle lower limit'])))
        window['UPPER_LIMIT'].update(str(from_rad(servo_cal[current_channel]['angle upper limit'])))
        window['-MEASURED_ANGLE-'].update(unit_txt)

        pts = points_current(servo_cal[current_channel]['points'])
        window['POINT_TABLE'].update(pts)
        window['USEC'].update('')
        window['ANGLE'].update('')

    update_window(window)

    while True:  # Event Loop
        event, values = window.read()

        if event in (None, 'Exit', 'QUIT'):
            break

        elif event in units:
            current_units = event
            update_window(window)

        elif event in ch_key:
            window['CH'+str(current_channel)].update(background_color=chan_def_color)
            current_channel = int(event[2:])
            window[event].update(background_color=chan_active_color)
            window['-CHNUM-'].update(str(current_channel))
            pts = points_current(servo_cal[current_channel]['points'])
            window['POINT_TABLE'].update(pts)
            window['USEC'].update('')
            window['ANGLE'].update('')
            window['LOWER_LIMIT'].update(str(from_rad(servo_cal[current_channel]['angle lower limit'])))
            window['UPPER_LIMIT'].update(str(from_rad(servo_cal[current_channel]['angle upper limit'])))
            window['CHAN_NAME'].update(servo_cal[current_channel]['name'])

            ch_active = servo_cal[current_channel]['active']
            window['EDIT_SECTION'].update(visible=ch_active)

            if ch_active:
                window['CHAN_ENABLED'].update(servo_cal[current_channel]['active'],
                                              text_color='black')
            else:
                window['CHAN_ENABLED'].update(servo_cal[current_channel]['active'],
                                              text_color='red')

        elif event == 'CHAN_ENABLED':
            ch_active = values['CHAN_ENABLED']
            servo_cal[current_channel]['active'] = ch_active
            window['EDIT_SECTION'].update(visible=ch_active)

            if ch_active:
                window['CHAN_ENABLED'].update(servo_cal[current_channel]['active'],
                                              text_color='black')
            else:
                window['CHAN_ENABLED'].update(servo_cal[current_channel]['active'],
                                              text_color='red')

        elif event == 'CHAN_NAME':
            servo_cal[current_channel]['name'] = values['CHAN_NAME']

        elif event == 'LOWER_LIMIT':
            pass

        elif event == 'LOWER_LIMIT+FOCUSOUT':
            ll_str = values['LOWER_LIMIT']
            try:
                ll = to_rad(float(ll_str))
                servo_cal[current_channel]['angle lower limit'] = ll
            except (ValueError, TypeError):
                sg.popup('Lower Limit should be a number', title='ERROR')

        elif event == 'UPPER_LIMIT':
            pass

        elif event == 'UPPER_LIMIT+FOCUSOUT':
            ul_str = values['UPPER_LIMIT']
            try:
                ul = to_rad(float(ul_str))
                servo_cal[current_channel]['angle upper limit'] = ul
            except (ValueError, TypeError):
                sg.popup   ('Upper Limit should be a number', title='ERROR')
                continue

        elif event == 'USEC':
            pass

        elif event == 'ANGLE':
            pass

        elif event == 'ADD':

            try:
                angle_val = float(values['ANGLE'])
            except (ValueError, TypeError):
                sg.popup('Angle should be a number', title='ERROR')
                continue

            try:
                usec_val = float(values['USEC'])
            except (ValueError, TypeError):
                sg.popup('Microseconds should be a number', title='ERROR')
                continue

            servo_cal[current_channel]['points'].append([usec_val, to_rad(angle_val)])

            pts = unique(servo_cal[current_channel]['points'])
            pts.sort(key=point_key_funct)
            servo_cal[current_channel]['points'] = pts

            window['POINT_TABLE'].update(points_current(pts))

        elif event == 'REMOVE':

            try:
                angle_val = float(values['ANGLE'])
            except (ValueError, TypeError):
                sg.popup('Angle should be a number', title='ERROR')
                continue

            try:
                usec_val = float(values['USEC'])
            except (ValueError, TypeError):
                sg.popup('Microseconds should be a number', title='ERROR')
                continue

            for pt_index, pt in enumerate(servo_cal[current_channel]['points']):
                if pt == (usec_val, angle_val):
                    servo_cal[current_channel]['points'].pop(pt_index)
                    break

            window['POINT_TABLE'].update(points_current(servo_cal[current_channel]['points']))

        elif event == '-MOVE-':
            try:
                usec_val  = float(values['USEC'])
                pca.goto_usec(current_channel, usec_val)
            except (ValueError, TypeError):
                sg.popup   ('Microseconds should be a number', title='ERROR')
                continue

        elif event == 'CLEAR':
            servo_cal[current_channel]['points'] = []
            window['POINT_TABLE'].update([])

        elif event == 'DEF180':
            servo_cal[current_channel]['points'] = default180_points.copy()
            window['POINT_TABLE'].update(points_current(servo_cal[current_channel]['points']))

        elif event == 'DEF270':
            servo_cal[current_channel]['points'] = default270_points.copy()
            window['POINT_TABLE'].update(points_current(servo_cal[current_channel]['points']))

        elif event == 'POINT_TABLE':

            if values['POINT_TABLE'] != []:
                row_index = values['POINT_TABLE'][0]
                row = servo_cal[current_channel]['points'][row_index]

                window['USEC'].update(row[0])
                window['ANGLE'].update(from_rad(row[1]))

        elif event == 'FIT':

            pnts = np.array(servo_cal[current_channel]['points'])

            if len(pnts) >= 2:
                lower_limit_val = from_rad(servo_cal[current_channel]['angle lower limit'])
                upper_limit_val = from_rad(servo_cal[current_channel]['angle upper limit'])


                x = pnts[:,1]   # Angles
                x = x * from_rad(1.0)
                y = pnts[:,0]   # Pulse Width in microseconds
                res = stats.linregress(x, y)

                servo_cal[current_channel]['intercept'] = float(res.intercept)
                servo_cal[current_channel]['slope']     = float(res.slope)
                servo_cal[current_channel]['rvalue']    = float(res.rvalue)

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
                plt.xlabel(units[current_units]['sgtext'])
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

                for ch in range(16):
                    pnts = np.array(servo_cal[ch]['points'])

                    if len(pnts) >= 2:
                        x = pnts[:, 1]  # Angles
                        y = pnts[:, 0]  # Pulse Width in microseconds
                        res = stats.linregress(x, y)

                        servo_cal[ch]['intercept'] = float(res.intercept)
                        servo_cal[ch]['slope']     = float(res.slope)
                        servo_cal[ch]['rvalue']    = float(res.rvalue)
                        servo_cal[ch]['valid fit'] = True
                    else:
                        servo_cal[ch]['active']    = False
                        servo_cal[ch]['valid fit'] = False

                yaml.dump(servo_cal, file)


if __name__ == "__main__":
    logging.basicConfig(filename='calibrate.log',
                        filemode='w',
                        level=logging.WARNING)

    log.info('Starting GUI')
    run_gui()
    log.info('normal termination')
