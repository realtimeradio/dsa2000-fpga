-- Generated from Simulink block 
library IEEE;
use IEEE.std_logic_1164.all;
library xil_defaultlib;
use xil_defaultlib.conv_pkg.all;
entity pfb_fir_2p_2kpt_12i_18o_os2_core_ip_struct is
  port (
    pol_in0 : in std_logic_vector( 192-1 downto 0 );
    pol_in1 : in std_logic_vector( 192-1 downto 0 );
    sync : in std_logic_vector( 1-1 downto 0 );
    clk_1 : in std_logic;
    ce_1 : in std_logic;
    pol_out0 : out std_logic_vector( 576-1 downto 0 );
    pol_out1 : out std_logic_vector( 576-1 downto 0 );
    sync_out : out std_logic_vector( 1-1 downto 0 )
  );
end pfb_fir_2p_2kpt_12i_18o_os2_core_ip_struct;

architecture structural of pfb_fir_2p_2kpt_12i_18o_os2_core_ip_struct is
  component pfb_fir_2p_2kpt_12i_18o_os2_core
    port (
      pol_in0 : in std_logic_vector( 192-1 downto 0 );
      pol_in1 : in std_logic_vector( 192-1 downto 0 );
      sync : in std_logic_vector( 1-1 downto 0 );
      clk : in std_logic;
      pol_out0 : out std_logic_vector( 576-1 downto 0 );
      pol_out1 : out std_logic_vector( 576-1 downto 0 );
      sync_out : out std_logic_vector( 1-1 downto 0 )
    );
  end component;
begin
  pfb_fir_2p_2kpt_12i_18o_os2_core_ip_inst : pfb_fir_2p_2kpt_12i_18o_os2_core
  port map (
    pol_in0  => pol_in0,
    pol_in1  => pol_in1,
    sync     => sync,
    clk      => clk_1,
    pol_out0 => pol_out0,
    pol_out1 => pol_out1,
    sync_out => sync_out 
  );
end structural; 
