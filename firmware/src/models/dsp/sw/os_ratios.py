import numpy as np
import scipy.signal
from matplotlib import pyplot as plt

def dpss(M):
    NW=2.0
    return scipy.signal.windows.dpss(M, NW, Kmax=None, sym=True, norm=None, return_ratios=False)

PI = np.pi

PADDING_FACTOR = 32
NFFT = 128
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
    resp_db = 10*np.log10(resp)
    resp_db -= np.max(resp_db)
    return resp_db

def get_faxis(ntaps, nfft, padding_factor):
    return np.linspace(0,nfft,ntaps*nfft*PADDING_FACTOR)

ntaps = 24
os_ratio = 16./11
window = np.hanning
scale = 1# + 0.1*os_ratio

coeffs = get_coeffs(ntaps, NFFT, window, scale=scale)
resp_db = get_response(coeffs, ntaps, NFFT, PADDING_FACTOR)
x = get_faxis(ntaps, NFFT, PADDING_FACTOR)

plt.figure()
plt.subplot(1,2,1)
plt.plot(x, resp_db)
plt.plot(x+1./os_ratio, resp_db)
plt.plot(x+2./os_ratio, resp_db)
plt.xlim(NFFT/2, NFFT/2 + 3)
plt.ylim(YMIN, YMAX)

plt.hlines(-6, 0, NFFT, colors='k', linestyles='solid')
for i in range(4):
    #plt.vlines(NFFT/2 + i/float(os_ratio), YMIN, YMAX, colors='k')
    plt.vlines(NFFT/2 + i/float(os_ratio) + 1./os_ratio, YMIN, YMAX, colors='k', linestyles='solid')
    plt.vlines(NFFT/2 + i/float(os_ratio) - 1./os_ratio, YMIN, YMAX, colors='k', linestyles='solid')
    plt.vlines(NFFT/2 + i/float(os_ratio) + 0.5/os_ratio, YMIN, YMAX, colors='k', linestyles='dashed')
    plt.vlines(NFFT/2 + i/float(os_ratio) - 0.5/os_ratio, YMIN, YMAX, colors='k', linestyles='dashed')
    plt.vlines(NFFT/2 + i/float(os_ratio) + 0.5, YMIN, YMAX, colors='r', linestyles='dotted')
    plt.vlines(NFFT/2 + i/float(os_ratio) - 0.5, YMIN, YMAX, colors='r', linestyles='dotted')
    
plt.subplot(1,2,2)
plt.plot(x, resp_db)
plt.plot(x+1./os_ratio, resp_db)
plt.plot(x+2./os_ratio, resp_db)
plt.xlim(NFFT/2,NFFT/2 + 1)
plt.ylim(-1, 1)

for i in range(4):
    #plt.vlines(NFFT/2 + i/float(os_ratio), YMIN, YMAX, colors='k')
    plt.vlines(NFFT/2 + i/float(os_ratio) + 1./os_ratio, YMIN, YMAX, colors='k', linestyles='solid')
    plt.vlines(NFFT/2 + i/float(os_ratio) - 1./os_ratio, YMIN, YMAX, colors='k', linestyles='solid')
    plt.vlines(NFFT/2 + i/float(os_ratio) + 0.5/os_ratio, YMIN, YMAX, colors='k', linestyles='dashed')
    plt.vlines(NFFT/2 + i/float(os_ratio) - 0.5/os_ratio, YMIN, YMAX, colors='k', linestyles='dashed')


plt.show()

