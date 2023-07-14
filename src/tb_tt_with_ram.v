/* Tiny Tapeout nanoV test harness */

module tb_tt_with_ram (
    input clk,
    input rstn,
    input [7:0] ui_in,
    output [7:0] uo_out,
    output uart_tx
);

`ifdef COCOTB_SIM
initial begin
  $dumpfile ("tb.vcd");
  $dumpvars (0, tb_tt_with_ram);
  #1;
end
`endif

    wire [7:0] uio_in;
    wire [7:0] uio_out;
    wire [7:0] uio_oe;

    wire spi_miso, spi_select, spi_clk, spi_mosi;
    assign uio_in[3] = spi_miso;
    assign spi_select = uio_out[1];
    assign spi_clk = uio_out[0];
    assign spi_mosi = uio_out[2];

    assign uio_in[2:0] = 0;
    assign uio_in[7:4] = 0;

    tt_um_MichaelBell_nanoV top (
        `ifdef GL_TEST
            .vccd1( 1'b1),
            .vssd1( 1'b0),
        `endif        
        .clk(clk),
        .rst_n(rstn),
        .ena(1'b1),
        .ui_in(ui_in),
        .uo_out(uo_out),
        .uio_in(uio_in),
        .uio_out(uio_out),
        .uio_oe(uio_oe)
    );

    assign uart_tx = uio_out[4];

    wire debug_clk;
    wire [23:0] debug_addr;
    wire [31:0] debug_data;
    sim_spi_ram spi_ram(
        spi_clk,
        spi_mosi,
        spi_select,
        spi_miso,

        debug_clk,
        debug_addr,
        debug_data
    );

    defparam spi_ram.INIT_FILE = `PROG_FILE;

    wire is_buffered = 1;

endmodule