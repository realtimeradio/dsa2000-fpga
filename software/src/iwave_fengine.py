import logging
import socket
import inspect
import numpy as np
import struct
import time
import datetime
import os
import yaml
import casperfpga
from . import helpers
from . import __version__
from .error_levels import *
from .blocks import block
from .blocks import fpga
from .blocks import adc
from .blocks import sync
from .blocks import noisegen
from .blocks import input
from .blocks import delay
from .blocks import pfb
from .blocks import mask
from .blocks import autocorr
from .blocks import eq
from .blocks import eqtvg
from .blocks import chanreorder
from .blocks import packetizer
from .blocks import eth
from .blocks import corr
from .blocks import powermon

FENG_40G_SOURCE_PORT = 10000
MAC_BASE = 0x020203030400
IP_BASE = (10 << 24) + (41 << 16) + (0 << 8) + 100
PIPELINES_PER_XENG = 4
FS_HZ = 196000000 # ADC sample rate in Hz

class IwaveFengine():
    """
    A control class for DSA2k's iWave SoM F-Engine firmware.

    :param host: Hostname of iWave board
    :type host: str

    :param logger: Logger instance to which log messages should be emitted.
    :type logger: logging.Logger

    """
    def __init__(self, host, logger=None):
        self.hostname = host #: hostname of the F-Engine's host SNAP2 board
        #: Python Logger instance
        self.logger = logger or helpers.add_default_log_handlers(logging.getLogger(__name__ + ":%s" % (host)))
        #: Underlying CasperFpga control instance
        self._cfpga = casperfpga.CasperFpga(
                        host=self.hostname,
                        transport=casperfpga.KatcpTransport,
                    )
        #try:
        #    self._cfpga.get_system_information()
        #except:
        #    self.logger.error("Failed to read and decode .fpg header from flash")
        self.blocks = {}
        try:
            self._initialize_blocks()
        except:
            self.logger.exception("Failed to inialize firmware blocks. "
                                  "Maybe the board needs programming.")

    def is_connected(self):
        """
        :return: True if there is a working connection to a SNAP2. False otherwise.
        :rtype: bool
        """
        return self._cfpga.is_connected()

    def _initialize_blocks(self, passive=False):
        """
        Initialize firmware blocks, populating the ``blocks`` attribute.

        :param passive: If True, don't attempt to do anything to interact with the FPGAs
            when creating their block control instances.
        :type passive: bool
        """

        # blocks
        #: Control interface to high-level FPGA functionality
        self.fpga        = fpga.Fpga(self._cfpga, "")
        ##: Control interface to ADC block
        #self.adc         = adc.Adc(self._cfpga, 'adc', passive=passive)
        #: Control interface to Synchronization / Timing block
        self.sync        = sync.Sync(self._cfpga, 'sync')
        ##: Control interface to Noise Generation block
        #self.noise       = noisegen.NoiseGen(self._cfpga, 'noise', n_noise=2, n_outputs=64)
        #: Control interface to Input Multiplex block
        self.input       = input.Input(self._cfpga, 'input', n_signals=2, n_streams=16)
        ##: Control interface to Coarse Delay block
        #self.delay       = delay.Delay(self._cfpga, 'delay', n_streams=64)
        #: Control interface to PFB block
        self.pfb         = pfb.Pfb(self._cfpga, 'pfb')
        ##: Control interface to Mask (flagging) block
        #self.mask        = mask.Mask(self._cfpga, 'mask')
        #: Control interface to Autocorrelation block
        self.autocorr    = autocorr.AutoCorr(self._cfpga, 'autocorr',
                                             n_signals=2,
                                             n_parallel_streams=8,
                                             n_cores=2,
                                             use_mux=False,
                                             )
        ##: Control interface to Equalization block
        #self.eq          = eq.Eq(self._cfpga, 'eq', n_streams=64, n_coeffs=2**9)
        #: Control interface to post-equalization Test Vector Generator block
        #self.eqtvg       = eqtvg.EqTvg(self._cfpga, 'post_eq_tvg', n_streams=64, n_chans=2**12)
        ##: Control interface to Channel Reorder block
        #self.reorder     = chanreorder.ChanReorder(self._cfpga, 'chan_reorder', n_chans=2**12)
        ##: Control interface to Packetizer block
        #self.packetizer  = packetizer.Packetizer(self._cfpga, 'packetizer', sample_rate_mhz=196.608)
        ##: Control interface to 40GbE interface block
        #self.eth         = eth.Eth(self._cfpga, 'eth')
        ##: Control interface to Correlation block
        #self.corr        = corr.Corr(self._cfpga,'corr_0', n_chans=2**12 // 8) # Corr module collapses channels by 8x
        ##: Control interface to Power Monitor block
        #self.powermon    = powermon.PowerMon(self._cfpga, 'powermon', passive=passive)

        # The order here can be important, blocks are initialized in the
        # order they appear here

        #: Dictionary of all control blocks in the firmware system.
        self.blocks = {
            'fpga'      : self.fpga,
            #'adc'       : self.adc,
            'sync'      : self.sync,
            #'noise'     : self.noise,
            'input'     : self.input,
            #'delay'     : self.delay,
            'pfb'       : self.pfb,
            #'mask'      : self.mask,
            #'eq'        : self.eq,
            #'eqtvg'     : self.eqtvg,
            #'reorder'   : self.reorder,
            #'packetizer': self.packetizer,
            #'eth'       : self.eth,
            'autocorr'  : self.autocorr,
            #'corr'      : self.corr,
            #'powermon'  : self.powermon,
        }

    def initialize(self, read_only=True):
        """
        Call the ```initialize`` methods of all underlying blocks, then
        optionally issue a software global reset.

        :param read_only: If True, call the underlying initialization methods
            in a read_only manner, and skip software reset.
        :type read_only: bool
        """
        for blockname, block in self.blocks.items():
            if read_only:
                self.logger.info("Initializing block (read only): %s" % blockname)
            else:
                self.logger.info("Initializing block (writable): %s" % blockname)
            block.initialize(read_only=read_only)
        if not read_only:
            self.logger.info("Performing software global reset")
            self.sync.arm_sync()
            self.sync.sw_sync()

    def get_status_all(self):
        """
        Call the ``get_status`` methods of all blocks in ``self.blocks``.
        If the FPGA is not programmed with F-engine firmware, will only
        return basic FPGA status.

        :return: (status_dict, flags_dict) tuple.
            Each is a dictionary, keyed by the names of the blocks in
            ``self.blocks``. These dictionaries contain, respectively, the
            status and flags returned by the ``get_status`` calls of
            each of this F-Engine's blocks.
        """
        stats = {}
        flags = {}
        if not self.blocks['fpga'].is_programmed():
            stats['fpga'], flags['fpga'] = self.blocks['fpga'].get_status()
        else:
            for blockname, block in self.blocks.items():
                try:
                    stats[blockname], flags[blockname] = block.get_status()
                except:
                    self.logger.info("Failed to poll stats from block %s" % blockname)
        return stats, flags

    def print_status_all(self, use_color=True, ignore_ok=False):
        """
        Print the status returned by ``get_status`` for all blocks in the system.
        If the FPGA is not programmed with F-engine firmware, will only
        print basic FPGA status.

        :param use_color: If True, highlight values with colors based on
            error codes.
        :type use_color: bool

        :param ignore_ok: If True, only print status values which are outside the
           normal range.
        :type ignore_ok: bool

        """
        if not self.blocks['fpga'].is_programmed():
            print('FPGA stats (not programmed with F-engine image):')
            self.blocks['fpga'].print_status()
        else:
            for blockname, block in self.blocks.items():
                print('Block %s stats:' % blockname)
                block.print_status(use_color=use_color, ignore_ok=ignore_ok)

    def deprogram(self):
        """
        Reprogram the FPGA into its default boot image.
        """
        self._cfpga.transport.progdev(0)

    def set_equalization(self, eq_start_chan=1000, eq_stop_chan=3300, 
            start_chan=512, stop_chan=3584, filter_ksize=21, target_rms=0.125*3):
        """
        Set the equalization coefficients to realize a target RMS.

        :param eq_start_chan: Frequency channels below ``eq_start_chan`` will be given the same EQ coefficient
            as ``eq_start_chan``.
        :type eq_start_chan: int

        :param eq_stop_chan: Frequency channels above ``eq_stop_chan`` will be given the same EQ coefficient
            as ``eq_stop_chan``.
        :type eq_stop_chan: int

        :param start_chan: Frequency channels below ``start_chan`` will be given zero EQ coefficients.
        :type start_chan: int

        :param stop_chan: Frequency channels above ``stop_chan`` will be given zero EQ coefficients.
        :type stop_chan: int

        :param filter_ksize: Filter kernel size, for rudimentary RFI removal. This should be an odd value.
        :type filter_ksize: int

        :param target_rms: The target post-EQ RMS. This is normalized such that 0.875 is the saturation level.
            I.e., an RMS of 0.125 means that the RMS is one LSB of a 4-bit signed signal.
        :type target_rms: float

        """
        n_cores = self.autocorr.n_signals // self.autocorr.n_signals_per_block
        for i in range(n_cores):
            spectra = self.autocorr.get_new_spectra(i, filter_ksize=filter_ksize)
            n_signals, n_chans = spectra.shape
            coeff_repeat_factor = n_chans // self.eq.n_coeffs
            for j in range(n_signals):
                stream_id = i*n_signals + j
                self.logger.info("Trying to EQ input %d" % stream_id)
                pre_quant_rms = np.sqrt(spectra[j] / 2) # RMS of each real / imag component making up spectra
                eq_scale = self.eq.get_coeffs(stream_id)
                eq_scale = eq_scale.repeat(coeff_repeat_factor)
                curr_rms = pre_quant_rms * eq_scale
                diff = target_rms / curr_rms
                new_eq = eq_scale * diff
                # stretch the edge coefficients outside the pass band to avoid them heading to infinity
                new_eq[0:eq_start_chan] = new_eq[eq_start_chan]
                new_eq[eq_stop_chan:] = new_eq[eq_stop_chan]
                new_eq[0:start_chan] = 0
                new_eq[stop_chan:] = 0
                self.eq.set_coeffs(stream_id, new_eq[::coeff_repeat_factor])

    def program(self, fpgfile):
        """
        Program an .fpg file to an FPGA. 

        :param fpgfile: The .fpg file to be loaded. Should be a path to a
            valid .fpg file. If None is given, the image currently in flash
            will be loaded.
        :type fpgfile: str

        """

        if not isinstance(fpgfile, str):
            raise TypeError("wrong type for fpgfile")

        # Resolve symlinks
        if fpgfile:
            fpgfile = os.path.realpath(fpgfile)

        if fpgfile and not os.path.exists(fpgfile):
            raise RuntimeError("Path %s doesn't exist" % fpgfile)

        self._cfpga.upload_to_ram_and_program(fpgfile)
