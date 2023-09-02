import numpy as np
from matplotlib import pyplot as plt

c = 3e8
def kps_to_khz(res_kps, fobs_mhz):
    return res_kps * 1e3 / c * fobs_mhz * 1e3

def khz_to_kps(res_khz, fobs_mhz):
    return res_khz / (fobs_mhz * 1e3) * c / 1e3

fh1_mhz = 1420
fobs_mhz = np.arange(700, 2000)

res_trials_kps = [30, 40, 50, 60]

plt.subplot(2,1,1)
for res_kps in res_trials_kps:
    df_khz = kps_to_khz(res_kps, fobs_mhz)
    plt.plot(fobs_mhz, df_khz, label='%d km/s' % res_kps)
plt.legend()
#plt.xlabel('Observing Frequency [MHz]')
plt.ylabel('Frequency Resolution [kHz]')

res_trials_khz = [73.5, 2*73.5, 98, 2*98, 84, 2*84, 134]
plt.subplot(2,1,2)
for res_khz in res_trials_khz:
    dv_kps = khz_to_kps(res_khz, fobs_mhz)
    plt.plot(fobs_mhz, dv_kps, label='%d kHz' % res_khz)
for res_kps in res_trials_kps:
    plt.axhline(res_kps, color='k')
plt.legend()
plt.ylabel('Velocity Resolution [km/s]')

plt.xlabel('Observing Frequency [MHz]')

# Zoom band resolution
zoom_a_res_kps = 2
zoom_b_res_kps = 0.3
zoom_a_res_khz = kps_to_khz(zoom_a_res_kps, fh1_mhz/1.02) # to 100Mpc -> 7000 km/s -> 0.02c
zoom_b_res_khz = kps_to_khz(zoom_b_res_kps, fh1_mhz) # z=0
print('Zoom A: %.2f km/s (at %.1f MHz) -> %.1f kHz' % (zoom_a_res_kps, fh1_mhz/1.02, zoom_a_res_khz))
print('Zoom B: %.2f km/s (at %.1f MHz) -> %.1f kHz' % (zoom_b_res_kps, fh1_mhz, zoom_b_res_khz))

plt.show()
