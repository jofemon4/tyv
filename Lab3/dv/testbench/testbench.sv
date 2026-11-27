import uvm_pkg::*;
`include "uvm_macros.svh"

`include "dut_if.sv"
`include "lib_test.sv"
`include "adc_dms_model.sv"

module top;
  dut_if dut_if();
  
  adc_dms_model#(.nlevels(`ADC_NLEVELS)) dut(
    .clk(dut_if.clk),
    .rst_n(dut_if.reset_n),
    .v_in(dut_if.v_in),
    .v_ref(dut_if.v_ref),
    .enable(dut_if.enable),
    .data_ready(dut_if.data_ready),
    .adc_q(dut_if.adc_q)
  );
  
  initial begin
    $dumpfile("dump.vcd"); $dumpvars;
    $shm_open("waves.shm");
    $shm_probe("ASM");
    dut_if.reset_n = 0;
    dut_if.enable = 0;
    dut_if.v_ref = 0;
    #50ns dut_if.reset_n = 1;
    dut_if.enable = 1;
    dut_if.v_ref = 1.0;
  end
  
  initial begin
    dut_if.clk = 0;
    forever begin
      #5ns dut_if.clk = ~dut_if.clk;
    end
  end
  
  initial begin
    //interface to database
    run_test(); //+UVM_TESTNAME=test_i2c_write
  end
    
endmodule : top
