`ifndef _DUT_IF
`define _DUT_IF
`define ADC_NLEVELS 8

interface dut_if();
  logic reset_n;
  logic clk;
  logic enable;
  real v_in;
  real v_ref;

  logic data_ready;
  logic[`ADC_NLEVELS-1:0] adc_q;

endinterface

`endif // _DUT_IF
