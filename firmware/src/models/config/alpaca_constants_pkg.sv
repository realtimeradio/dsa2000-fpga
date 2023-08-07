`default_nettype none

package alpaca_constants_pkg;

// Module instantiation parameters

parameter WIDTH = 16;                   // axi-sample word width, ADC samples padded to this width
parameter FRAC_WIDTH = 0;

parameter PHASE_WIDTH = 23;             // precision for parallel fft twiddle factors
parameter PHASE_FRAC_WIDTH = PHASE_WIDTH-1;

parameter COEFF_WID = 16;               // filter coefficient word width
parameter COEFF_FRAC_WID = COEFF_WID-1;
parameter SAMP_PER_CLK = 16;             // number of samples in adc packet

parameter FFT_CONF_WID = 16;         // fft configuration width (set inverse and scale schedule
parameter FFT_STAT_WID = 8;          // fft status width (overflow and optional Xk index)
parameter FFT_USER_WID = 8;

// TODO: should have an 'effective' FFT_LEN and DEC_FAC that are M/SAMP_PER_CLK and
// D/SAM_PER_CLK as to not have to carry FFT_LEN/samp_per_clk or DEC_FAC/samp_per_clk
// everywhere. Would really simplify understanding the code and limitations.
// Will do this once all the new latency and cores are added

// *NOTE*: FFT_LEN and DEC_FAC must be divisiable by `samp_per_clk`
parameter FFT_LEN = 2048;            // (M)   polyphase branches
parameter OSRATIO = 3.0/4.0;
parameter DEC_FAC = FFT_LEN*OSRATIO; // (D)   decimation factor
parameter PTAPS = 8;                 // (P)   polyphase taps corresponds to number of PEs

parameter DC_FIFO_DEPTH = FFT_LEN/2;

// Simulation parameters
parameter ADC_BITS = 14;             // simulation ADC effective bit resolution
parameter ADC_GAIN = 0.50;
parameter SIGMA_BIT = 10;
parameter F_SOI_NORM = 0.27001953125;        // normalized sampling frequency for ADC tonegeneration

// determine ADC clk period given the DSP clk
parameter real ADC_PERIOD = 12;                 // ADC simulation clock period
parameter real DSP_PERIOD = OSRATIO*ADC_PERIOD; // oversampled DSP simulation clock period
parameter real PERIOD = ADC_PERIOD;             // general period for other modules

//typedef struct {
//  /* is it possible to parameterize a struct or just a class?
//  /* looks like the answer is yes... example in rfdc demo_tb_fft_checker.sv from xilinx rfdc
//  /* project
//  /* eg.,
//  /* parameter FFT_LEN = 1024;
//  /* typedef struct {
//  /*  complex_t arr[FFT_LEN];
//  /* } cplxArray_t;
//   
//} ospfb_cfg_t;

endpackage : alpaca_constants_pkg
