include adi_hdl/quiet.mk

.PHONY: all lib
all: lib

lib:
	$(MAKE) -C adi_hdl/library/axi_dmac
	$(MAKE) -C adi_hdl/library/axi_sysid
	$(MAKE) -C adi_hdl/library/axi_tdd
	$(MAKE) -C adi_hdl/library/data_offload
	$(MAKE) -C adi_hdl/library/jesd204/ad_ip_jesd204_tpl_adc
	$(MAKE) -C adi_hdl/library/jesd204/ad_ip_jesd204_tpl_dac
	$(MAKE) -C adi_hdl/library/jesd204/axi_jesd204_rx
	$(MAKE) -C adi_hdl/library/jesd204/axi_jesd204_tx
	$(MAKE) -C adi_hdl/library/jesd204/jesd204_rx
	$(MAKE) -C adi_hdl/library/jesd204/jesd204_tx
	$(MAKE) -C adi_hdl/library/jesd204/jesd204_versal_gt_adapter_rx
	$(MAKE) -C adi_hdl/library/jesd204/jesd204_versal_gt_adapter_tx
	$(MAKE) -C adi_hdl/library/sysid_rom
	$(MAKE) -C adi_hdl/library/util_adcfifo
	$(MAKE) -C adi_hdl/library/util_dacfifo
	$(MAKE) -C adi_hdl/library/util_do_ram
	$(MAKE) -C adi_hdl/library/util_hbm
	$(MAKE) -C adi_hdl/library/util_pack/util_cpack2
	$(MAKE) -C adi_hdl/library/util_pack/util_upack2
	$(MAKE) -C adi_hdl/library/util_tdd_sync
	$(MAKE) -C adi_hdl/library/xilinx/axi_adxcvr
	$(MAKE) -C adi_hdl/library/xilinx/util_adxcvr
