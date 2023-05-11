import struct
import time
import numpy as np
from .block import Block
from dsa2k_f.error_levels import *

class Input(Block):
    """
    Instantiate a control interface for an Input block. This block
    allows switching data streams between constant-zeros, digital noise,
    and ADC streams.

    A statistics interface is also provided, providing bit statistics and
    histograms.

    :param host: CasperFpga interface for host.
    :type host: casperfpga.CasperFpga

    :param name: Name of block in Simulink hierarchy.
    :type name: str

    :param logger: Logger instance to which log messages should be emitted.
    :type logger: logging.Logger

    :param n_signals: Number of independent signals
    :type n_signals: int

    :param dtype: Numpy-style data type specification for an ADC sample
    :type dtype: str

    :ivar n_streams: Number of parallel samples per signal.
    :ivar n_streams: int
    """
    _SNAPSHOT_SAMPLES_PER_POL = 16384

    def __init__(self, host, name, n_signals=2, n_streams=16, dtype='>i2', logger=None):
        super(Input, self).__init__(host, name, logger)
        self.n_streams = n_streams
        self.n_signals = n_signals
        self.dtype = dtype
        self.n_sample_bytes = np.dtype(dtype).itemsize
        self._n_sample_bits = 8* self.n_sample_bytes
        self._n_ram_per_pol = self.n_streams * self._n_sample_bits // 128
        self._n_stream_per_ram = self.n_streams // self._n_ram_per_pol
        self._n_bytes_per_ram = self._SNAPSHOT_SAMPLES_PER_POL * self.n_sample_bytes // self._n_ram_per_pol

    def _trigger_snapshot(self):
        """
        Trigger a new ADC snapshot capture.
        """
        self.write_int('snapshot_arm', 0)
        self.write_int('snapshot_trig', 0)
        self.write_int('snapshot_arm', 1)
        self.write_int('snapshot_arm', 0)
        self.write_int('snapshot_trig', 1)
        self.write_int('snapshot_trig', 0)

    def _read_snapshot(self):
        """
        Read snapshot brams and format appropriately.
        """
        d = np.zeros([self.n_signals, self._SNAPSHOT_SAMPLES_PER_POL], dtype=int)
        for sig in range(self.n_signals):
            for ram in range(self._n_ram_per_pol):
                ram_id = sig * self._n_ram_per_pol + ram
                ram_name = f'ss_{ram_id}_bram'
                dram = np.frombuffer(self.read(ram_name, self._n_bytes_per_ram), dtype=self.dtype)
                for i in range(self._n_stream_per_ram):
                    d[sig, self._n_stream_per_ram*ram + i::self.n_streams] = dram[i::self._n_stream_per_ram]
        return d

    def get_snapshot(self):
        """
        Get a snapshot of ADC samples

        :return: (signal0, signal1) tuple, each a numpy array of ADC samples
        :rval: (numpy.ndarray, nump.ndarray)
        """
        self._trigger_snapshot()
        return self._read_snapshot()

    def plot_snapshot(self, n_sample=-1):
        from matplotlib import pyplot as plt
        d = self.get_snapshot()
        nsig, nsample = d.shape
        for i in range(nsig):
            plt.plot(d[i, 0:n_sample], label=f'signal_{i}')
        plt.legend()
        plt.show()

    def get_bit_stats(self):
        """
        Get the mean, RMS, and mean powers of all ADC streams.

        :return: (means, powers, rmss) tuple. Each member of the tuple is an
            array with ``self.n_streams`` elements.
        :rval: (numpy.ndarray, numpy.ndarray, numpy.ndarray)

        """
        d = self.get_snapshot()
        means = d.mean(axis=1)
        powers = (d**2).mean(axis=1)
        rmss = np.sqrt(powers)
        return means, powers, rmss

    def initialize(self, read_only=False):
        """
        Initialize the block.

        :param read_only: If True, do nothing. If False, set the input
            multiplexers to ADC data and enable statistic computation.
        :type read_only: bool

        """
        if read_only:
            pass
        else:
            self.use_adc()
            self.write_int('rms_enable', 1)

    def get_status(self):
        """
        Get status and error flag dictionaries.

        Status keys:

            - power<n> (float) : Mean power of input stream ``n``, where ``n`` is a
              two-digit integer starting at 00. In units of (ADC LSBs)**2.

            - rms<n> (float) : RMS of input stream ``n``, where ``n`` is a
              two-digit integer starting at 00. In units of ADC LSBs. Value is
              flagged as a warning if it is >30 or <5.

            - mean<n> (float) : Mean sample value of input stream ``n``, where ``n`` is a
              two-digit integer starting at 00. In units of ADC LSBs. Value
              is flagged as a warning if it is > 2.

        :return: (status_dict, flags_dict) tuple. `status_dict` is a dictionary of
            status key-value pairs. flags_dict is
            a dictionary with all, or a sub-set, of the keys in `status_dict`. The values
            held in this dictionary are as defined in `error_levels.py` and indicate
            that values in the status dictionary are outside normal ranges.

        """
        stats = {}
        flags = {}
        mean, power, rms = self.get_bit_stats()
        for i in range(self.n_signals):
            stats['power%.2d' % i] = power[i]
            stats['rms%.2d' % i]   = rms[i]
            stats['mean%.2d' % i]  = mean[i]
            if rms[i] > 30 or rms[i] < 5:
                flags['rms%.2d' % i] = FENG_WARNING
            if np.abs(mean[i]) > 2:
                flags['mean%.2d' % i] = FENG_WARNING
        return stats, flags

    def _set_histogram_input(self, stream):
        """
        Set input of histogram block computation core.

        :param stream: Stream number to select.
        :type stream: int
        """
        assert (stream < self.n_streams), "Can't switch stream >= self.n_streams" 
        self.write_int('bit_stats_input_sel', stream)

    def get_histogram(self, stream, sum_cores=True):
        """
        Get a histogram for an ADC stream.
        
        :param stream: ADC stream from which to get data.
        :type stream: int

        :param sum_cores: If True, compute one histogram from both pairs of
            interleaved ADC cores associated with an analog input.
            If False, compute separate histograms.
        :type sum_cores: bool

        :return: If ``sum_cores`` is True, return ``(vals, hist)``, where ``vals``
            is a list of histogram bin centers, and ``hist`` is a list of
            histogram data points. If ``sum_cores`` is False, return
            ``(vals, hist_a, hist_b)``, where ``hist_a`` and ``hist_b``
            are separate histogram data sets for the even-sample and odd-sample
            ADC cores, respectively.
        """
        self._info("Getting histogram for stream %d" % stream)
        self._set_histogram_input(stream)
        time.sleep(0.1)
        v = np.array(struct.unpack('>%dH' % (2*2**self.n_bits), self.read('bit_stats_histogram_output', 2*2*2**self.n_bits)))
        a = v[0:2**self.n_bits]
        b = v[2**self.n_bits : 2*2**self.n_bits]
        a = np.roll(a, 2**(self.n_bits - 1)) # roll so that array counts -128, -127, ..., 0, ..., 126, 127
        b = np.roll(b, 2**(self.n_bits - 1)) # roll so that array counts -128, -127, ..., 0, ..., 126, 127
        vals = np.arange(-2**(self.n_bits - 1), 2**(self.n_bits - 1))
        if sum_cores:
            return vals.tolist(), (a+b).tolist()
        else:
            return vals.tolist(), a.tolist(), b.tolist()

    def get_all_histograms(self):
        """
        Get histograms for all signals, summing over all interleaving cores.

        :return: (vals, hists). ``vals`` is a list of histogram bin centers.
            ``hists`` is an ``[n_stream x 2**n_bits]`` list of histogram
            data.
        """
        out = np.zeros([self.n_streams, 2**self.n_bits])
        for stream in range(self.n_streams):
            x, out[stream,:] = self.get_histogram(stream, sum_cores=True)
        return x, out.tolist()

    def print_histograms(self):
        """
        Print histogram stats to screen.
        """
        x, hist = self.get_all_histograms()
        hist = np.array(hist)
        hist /= 1024.*1024
        for vn, v in enumerate(x):
            print('%5d:'%v, end=' ')
            for an, ant in enumerate(hist):
                print('%.3f'%ant[vn], end=' ')
            print()

    def plot_histogram(self, stream):
        """
        Plot a histogram.

        :param stream: ADC stream from which to get data.
        :type stream: int
        """
        
        from matplotlib import pyplot as plt
        bins, d = self.get_histogram(stream)
        plt.bar(np.array(bins)-0.5, d, width=1)
        plt.xlim((np.min(bins)*1.1, np.max(bins)*1.1))
        plt.show()
