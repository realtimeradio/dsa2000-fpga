import numpy as np
from matplotlib import pyplot as plt

PADDING_FACTOR = 8
NFFT = 64

def plot_pfb(ntaps, window_func):
    nfft = NFFT*ntaps
    
    PI = np.pi
    
    sinc = np.sinc(np.linspace(-ntaps/2., ntaps/2., nfft))
    window = window_func(nfft)
    coeffs = sinc * window
    
    #plt.plot(sinc)
    #plt.show()
    
    resp = np.abs(np.fft.fft(coeffs, nfft*PADDING_FACTOR))**2
    resp_db = 10*np.log10(resp)
    resp_db -= np.max(resp_db)
    
    plt.subplot(1,2,1)
    plt.plot(np.linspace(0,nfft/ntaps,nfft*PADDING_FACTOR), resp_db, label='%d taps' % ntaps)
    plt.xlim(0, 4)
    plt.ylim(-120, 3)
    
    plt.subplot(1,2,2)
    plt.plot(np.linspace(0,nfft/ntaps,nfft*PADDING_FACTOR), resp_db, label='%d taps' % ntaps)
    plt.xlim(0,0.5)
    plt.ylim(-6, 3)

for wf in [np.ones, np.hanning, np.hamming]:
    plt.figure()
    for taps in np.arange(4,32+4,4):
        plot_pfb(taps, wf)
    
    plt.subplot(1,2,1)
    plt.legend()
    plt.subplot(1,2,2)
    plt.legend()
plt.show()

