import numpy as np
import scipy.signal
from matplotlib import pyplot as plt

def dpss(M):
    NW=2.0
    return scipy.signal.windows.dpss(M, NW, Kmax=None, sym=True, norm=None, return_ratios=False)

PI = np.pi

PADDING_FACTOR = 32
NFFT = 16
YMIN = -120
YMAX = 3

def get_coeffs(ntaps, nfft, window_func, scale=1.):
    sinc = np.sinc(np.linspace(-ntaps/2./scale, ntaps/2./scale, nfft*ntaps))
    window = window_func(nfft*ntaps)
    coeffs = sinc * window
    return coeffs

def get_response(coeffs, ntaps, nfft, padding_factor):
    resp = np.abs(np.fft.fft(coeffs, ntaps*nfft*PADDING_FACTOR))**2
    resp = np.fft.fftshift(resp)
    #for i,r in enumerate(resp):
    #    print(i,r)
    resp /= (resp[padding_factor*nfft*ntaps//2])
    resp_db = 10*np.log10(resp)
    #resp_db -= np.max(resp_db)
    return resp_db

def get_faxis(ntaps, nfft, padding_factor):
    return np.linspace(0,nfft,ntaps*nfft*PADDING_FACTOR)

ntaps = 24
os_ratio_n = 1
os_ratio_d = 1
os_ratio = float(os_ratio_n) / os_ratio_d
window_name = 'HANN'
windows = {'HANN':np.hanning, 'HAMMING':np.hamming, 'DPSS':dpss}
window = windows[window_name]
shrink_factor = 0.85
scale = 1./shrink_factor

coeffs = get_coeffs(ntaps, NFFT, window, scale=scale)
resp_db = get_response(coeffs, ntaps, NFFT, PADDING_FACTOR)
x = (get_faxis(ntaps, NFFT, PADDING_FACTOR) - NFFT/2) * os_ratio # Normalized so bin centers are on integers

colors = ['r', 'b', 'm', 'g', 'y']

plt.figure(figsize=(14,6))
plt.suptitle(f'{window_name} WINDOW, {ntaps} TAP, {os_ratio_n}/{os_ratio_d} OVERSAMPLE, {shrink_factor} WIDTH')
plt.subplot(1,2,1)
plt.plot(x+0, resp_db, colors[0])
plt.plot(x+1, resp_db, colors[1])
plt.plot(x+2, resp_db, colors[2])
plt.plot(x+3, resp_db, colors[3])
plt.plot(x+4, resp_db, colors[4])
plt.xlim(0, 4)
plt.ylim(YMIN, YMAX)
plt.xlabel('Normalized Frequency')
plt.ylabel('Response [dB]')

#plt.hlines(-6, 0, NFFT, colors='k', linestyles='solid')
for i in range(5):
    #plt.vlines(NFFT/2 + i/float(os_ratio), YMIN, YMAX, colors='k')
    # Solid lines at bin centers
    # Dashed lines encompass region where a bin is used
    # Dotted red lines at the Nyquist edge of a bin
    plt.vlines(i, YMIN, YMAX, colors='k', linestyles='solid')
    plt.vlines(i + 0.5, YMIN, YMAX, colors='k', linestyles='dashed')
    plt.vlines(i - 0.5, YMIN, YMAX, colors='k', linestyles='dashed')
    plt.vlines(i + 0.5*os_ratio, YMIN, YMAX, colors='r', linestyles='dotted')
    plt.vlines(i - 0.5*os_ratio, YMIN, YMAX, colors='r', linestyles='dotted')
    plt.axvspan(i - 0.5, i + 0.5, facecolor=colors[i], alpha=0.3)
    
plt.subplot(1,2,2)
plt.plot(x+0., resp_db, colors[0])
plt.plot(x+1., resp_db, colors[1])
plt.plot(x+2., resp_db, colors[2])
plt.xlim(0, 2)
plt.ylim(-0.1, 0.1)
plt.xlabel('Normalized Frequency')
plt.ylabel('Response [dB]')

for i in range(4):
    #plt.vlines(NFFT/2 + i/float(os_ratio), YMIN, YMAX, colors='k')
    plt.vlines(i + 1., YMIN, YMAX, colors='k', linestyles='solid')
    plt.vlines(i - 1., YMIN, YMAX, colors='k', linestyles='solid')
    plt.vlines(i + 0.5, YMIN, YMAX, colors='k', linestyles='dashed')
    plt.vlines(i - 0.5, YMIN, YMAX, colors='k', linestyles='dashed')
    plt.axvspan(i - 0.5, i + 0.5, facecolor=colors[i], alpha=0.3)


plt.show()

