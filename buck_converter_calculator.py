import argparse
import pint

ureg = pint.UnitRegistry()

## Defaults ##
default_input_voltage = 24.0
default_output_voltage = 5.0
default_output_current = 2.0
default_switching_frequency = 500e3
default_efficiency = 0.9
default_v_pp_max = 75e-3
default_i_out_tr_max = 2
default_v_out_tr_max_allowed = 0.1

###
# Based on TI SLTA055 Input and Output Capacitor Selection
#
#

def get_duty_cycle(v_in, v_out, efficiency):
    return v_out / (v_in * efficiency)

def get_min_input_capacitance_for_ripple_reduction(v_in: float, v_out: float, i_out: float, efficiency: float, f_sw: float, V_pp_max: float):
    duty_cycle = get_duty_cycle(v_in, v_out, efficiency)
    c_min = (i_out * duty_cycle * (1 - duty_cycle) * 1000 * 1000) / (f_sw * V_pp_max)
    return c_min * ureg.uF

def get_min_input_bulk_capacitance(v_in: float, v_out: float, efficiency: float, max_output_transient_current: float, max_allowed_voltage_change: float, input_filter_inductance: float):
    input_current_transient = v_out / (v_in * efficiency) * max_output_transient_current
    input_inductance = 50 + input_filter_inductance # Add in some parasitics and also for when no inductor included
    c_min = 1.21 * (input_current_transient ** 2) * (input_inductance * 1e-9) / (max_allowed_voltage_change ** 2)
    c_min = c_min * ureg.F
    return c_min.to(ureg.uF)

def main():
    parser = argparse.ArgumentParser(description='Buck Converter Calculator')
    parser.add_argument('--v-in', type=float, default=default_input_voltage, help='Input voltage in volts')
    parser.add_argument('--v-out', type=float, default=default_output_voltage, help='Output voltage in volts')
    parser.add_argument('--i-out', type=float, default=default_output_current, help='Output current in amps')
    parser.add_argument('--f-sw', type=float, default=default_switching_frequency, help='Switching frequency in Hz')
    parser.add_argument('--efficiency', type=float, default=default_efficiency, help='Switcher efficiency as decimal value (e.g. 0.9 for 90%% efficiency)')
    parser.add_argument('--v-pp-max', type=float, default=default_v_pp_max, help='Maximum peak-to-peak voltage in volts')
    parser.add_argument('--i-out-tr-max', type=float, default=default_i_out_tr_max, help='Maximum transient output current in amps. So if expected that converter will need to output 0.1A one moment then 2.5A next, will be 2.4A')
    parser.add_argument('--v-out-tr-max-allowed', type=float, default=default_v_out_tr_max_allowed, help='Max allowed voltage deviation in volts. So, what is the max allowed voltage change on load change')
    parser.add_argument('--input-inductor', type=float, default=default_v_out_tr_max_allowed, help='Input inductor value in nH')
    args = parser.parse_args()
    
    duty_cycle = get_duty_cycle(args.v_in, args.v_out, args.efficiency)
    input_ceramic_c_min = get_min_input_capacitance_for_ripple_reduction(args.v_in, args.v_out, args.i_out, args.efficiency, args.f_sw, args.v_pp_max)
    input_bulk_c_min = get_min_input_bulk_capacitance(args.v_in, args.v_out, args.efficiency, args.i_out_tr_max, args.v_out_tr_max_allowed, args.input_inductor)
    
    print(f"Duty Cycle: {duty_cycle:.2f}")
    print(f"Min ceramic capacitance: {input_ceramic_c_min:~.3f}")
    print(f"Min bulk capacitance: {input_bulk_c_min:~.1f}")

if __name__ == '__main__':
    main()