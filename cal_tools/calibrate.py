"""User facing applcation to create a calibration file for a set of serves."""
import logging
import math

import yaml
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import PySimpleGUI as sg
import pca9685_psd

pca = pca9685_psd.PCA9685()

log = logging.getLogger(__name__)

# This is the dictionary that is written as a YAML file.
servo_cal = dict()
current_channel = 0
units = {
    '-RAD-': {'sgtext': 'Radians'},
    '-DEG-': {'sgtext': 'Degrees'}
    }
current_units = '-DEG-'


default180_points = (
    [1000.0, math.radians(-90.0)],
    [1500.0, 0.0],
    [2000.0, math.radians( 90.0)]
)

default270_points = (
    [ 500.0, math.radians(-270.0 / 2.0)],
    [1500.0, 0.0],
    [2500.0, math.radians(270.0 / 2.0)]
)

default_cal = default180_points


def points_are_close(p1: tuple[float, float], p2: tuple[float, float],
                     tolerance0: float = 0.001, tolerance1: float = 0.001) -> bool:
    if (abs(p1[0] - p2[0]) < tolerance0) and   \
       (abs(p1[1] - p2[1]) < tolerance1):
        return True
    else:
        return False


def to_rad(angle: float) -> float:
    """Convert and angle whatever is the current unit to radians"""

    if current_units == '-DEG-':
        rad = math.radians(angle)
    elif current_units == '-RAD-':
        rad = angle
    else:
        raise ValueError

    return rad


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

def point_key_funct(point: list[float]) -> float:
    """extract a sort key from a list, pased to sort function."""
    return point[0]


def active_channels() -> list[int]:
    """Scan an aray and make a list of i where array[i] == True"""
    global servo_cal
    ch_list = []
    for ch_indx in range(16):
        if servo_cal[ch_indx]['active']:
            ch_list.append(str(ch_indx))
    return ch_list


def unique(list1: list) -> list:
    """Find the list of unique elements in a list."""
    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def init_cal_data() -> None:
    """Sets all channels to a reasonable default."""

    global servo_cal
    global default_cal

    default_channel = {
        'active': True,
        'valid fit': False,
        'name': '',
        'usec lower limit': 1000.0,
        'usec upper limit': 2000.0,
        'slope': 0.0,
        'intercept': 0.0,
        'rvalue': 0.0,
        'points': []
        }

    for ch_indx in range(16):
        default_channel['name']   = 'servo'+str(ch_indx)
        default_channel['points'] = list(default_cal)
        servo_cal[ch_indx] = default_channel.copy()
        fit_cal_funtion(ch_indx)


def points_current(points: list) -> list:
    """Converts the set of cal points from radians to the current display unit"""
    disp = []
    for pnt in points:
        disp.append([pnt[0], from_rad(pnt[1])])
    return disp


def fit_cal_funtion(chan_num: int) -> None:
    global servo_cal

    pnts = np.array(servo_cal[chan_num]['points'])

    if len(pnts) >= 2:
        x = pnts[:, 1]  # Angles
        y = pnts[:, 0]  # Pulse Width in microseconds
        res = stats.linregress(x, y)

        servo_cal[chan_num]['intercept'] = float(res.intercept)
        servo_cal[chan_num]['slope']     = float(res.slope)
        servo_cal[chan_num]['rvalue']    = float(res.rvalue)
        servo_cal[chan_num]['valid fit'] = True
    else:
        servo_cal[chan_num]['active']    = False
        servo_cal[chan_num]['valid fit'] = False

def usec_to_radian(chan_num: int, usec: float) -> float:
    global servo_cal

    if servo_cal[chan_num]['valid fit']:
        slope = servo_cal[chan_num]['slope']
        inter = servo_cal[chan_num]['intercept']
        rad = (usec - inter) / slope
    else:
        rad = math.nan

    return rad


def run_gui() -> None:
    """The main function, creates the window and runs the GUI event loop"""

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

    chan_def_color      = 'grey'
    chan_selected_color = 'yellow'
    chan_disabled_color = 'red'

    ch_key = []
    for i in range(16):
        ch_key.append('CH'+str(i))

    edit_section = [
        [sg.Text('Channel Name'),
         sg.InputText('', key='CHAN_NAME', enable_events=True,
                      tooltip='The channel may be given a name, but the name is not used.')
         ],

        [sg.HSep()],

        [sg.Push(),
         sg.Text('    ', size=8),
         sg.Text('lower limit', size=num_input_sz),
         sg.Text('upper limit', size=num_input_sz),
         sg.Push()
         ],

        [sg.Push(),
         sg.Text('uSec', size=8),
         sg.InputText(str(lower_limit), key='LOWER_LIMIT', size=num_input_sz, enable_events=True),
         sg.InputText(str(upper_limit), key='UPPER_LIMIT', size=num_input_sz, enable_events=True),
         sg.Push()
         ],

        [sg.Push(),
         sg.Text('units', size=8, key='LIMIT_ANGLE_UNITS'),
         sg.Text('angle', key='LOWER_LIMIT_ANGLE', size=num_input_sz),
         sg.Text('angle', key='UPPER_LIMIT_ANGLE', size=num_input_sz),
         sg.Push()
         ],

        [sg.HSep()],

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
         ],

        [sg.Text('Adjust zero point, uSec'),
         sg.InputText(key='-ZERO_POINT-', size=num_input_sz),
         sg.Button('Set', key='-SET_ZERO-')
         ],

        [sg.HSep()],

        [sg.Text('move servo, uSec\n(no effect on calibration)'),
         sg.Slider(range=(500.0, 2500.0), default_value=1500.0,resolution=1.0,orientation='horizontal',
                   size=(35,20), tick_interval=500.0,
                   enable_events=True,key='-MOVE_SLIDER-')
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

        [sg.Button('Plot', key='FIT'),
         sg.Push(),
         sg.Button('Save', key='SAVE'),
         sg.Button('Quit', key='QUIT')
        ]
    ]

    window = sg.Window('Servo Calibration', layout, finalize=True)
    window['LOWER_LIMIT'].bind('<FocusOut>', '+FOCUSOUT')
    window['UPPER_LIMIT'].bind('<FocusOut>', '+FOCUSOUT')

    def update_limit_angles(window):
        fit_cal_funtion(current_channel)
        ll_txt = str(round(from_rad(usec_to_radian(current_channel,
                                             servo_cal[current_channel]['usec lower limit'])),
                           3))
        ul_txt = str(round(from_rad(usec_to_radian(current_channel,
                                             servo_cal[current_channel]['usec upper limit'])),
                           3))
        window['LOWER_LIMIT_ANGLE'].update(ll_txt)
        window['UPPER_LIMIT_ANGLE'].update(ul_txt)

    def update_window(window):
        """Update dynamic data when window needs to be refreshed."""
        window['CH' + str(current_channel)].update(background_color=chan_selected_color)
        window['CHAN_NAME'].update(servo_cal[current_channel]['name'])
        window['CHAN_ENABLED'].update(servo_cal[current_channel]['active'],
                                      text_color='black')
        unit_txt = units[current_units]['sgtext']
        window['LIMIT_ANGLE_UNITS'].update(unit_txt)
        window['LOWER_LIMIT'].update(str(servo_cal[current_channel]['usec lower limit']))
        window['UPPER_LIMIT'].update(str(servo_cal[current_channel]['usec upper limit']))
        update_limit_angles(window)
        window['-MEASURED_ANGLE-'].update(unit_txt)

        pts = points_current(servo_cal[current_channel]['points']).copy()
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
            window[event].update(background_color=chan_selected_color)
            window['-CHNUM-'].update(str(current_channel))
            pts = points_current(servo_cal[current_channel]['points']).copy()
            window['POINT_TABLE'].update(pts)
            window['USEC'].update('')
            window['ANGLE'].update('')
            window['LOWER_LIMIT'].update(str(servo_cal[current_channel]['usec lower limit']))
            window['UPPER_LIMIT'].update(str(servo_cal[current_channel]['usec upper limit']))
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
                ll = float(ll_str)
                servo_cal[current_channel]['usec lower limit'] = ll
                update_limit_angles(window)
            except (ValueError, TypeError):
                sg.popup('Lower Limit should be a number', title='ERROR')

        elif event == 'UPPER_LIMIT':
            pass

        elif event == 'UPPER_LIMIT+FOCUSOUT':
            ul_str = values['UPPER_LIMIT']
            try:
                ul = float(ul_str)
                servo_cal[current_channel]['usec upper limit'] = ul
                update_limit_angles(window)
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
                if points_are_close(pt, (usec_val, angle_val)):
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
            servo_cal[current_channel]['points'] = list(default180_points)
            window['POINT_TABLE'].update(points_current(servo_cal[current_channel]['points']))

        elif event == 'DEF270':
            servo_cal[current_channel]['points'] = list(default270_points)
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
                lower_limit_val = servo_cal[current_channel]['usec lower limit']
                upper_limit_val = servo_cal[current_channel]['usec upper limit']


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
                plt.hlines(lower_limit_val,
                           xmin=min(x),
                           xmax=max(x),
                           linestyles='dashed',
                           colors='green',
                           label='lower limit')
                plt.hlines(upper_limit_val,
                           xmin=min(x),
                           xmax=max(x),
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
            with open('servo_cal.yaml', mode="wt", encoding="utf-8") as cal_file:

                for ch in range(16):
                    fit_cal_funtion(ch)

                yaml.dump(servo_cal, cal_file)

        elif event == '-SET_ZERO-':
            fit_cal_funtion(current_channel)
            new_intercept = float(values['-ZERO_POINT-'])
            delta = new_intercept - servo_cal[current_channel]['intercept']

            new_pts = []
            for p in servo_cal[current_channel]['points']:
                new_pts.append([p[0]+delta, p[1]])
            servo_cal[current_channel]['points'] = new_pts

            fit_cal_funtion(current_channel)
            update_window(window)

        elif event == '-MOVE_SLIDER-':
            usec_val = values[event]
            pca.goto_usec(current_channel, usec_val)


if __name__ == "__main__":
    logging.basicConfig(filename='calibrate.log',
                        filemode='w',
                        level=logging.WARNING)

    log.info('Starting GUI')
    run_gui()
    log.info('normal termination')
