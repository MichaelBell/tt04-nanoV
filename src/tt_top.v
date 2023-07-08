`default_nettype none

module tt_um_MichaelBell_nanoV (
    input  wire [7:0] ui_in,    // Dedicated inputs - connected to the input switches
    output wire [7:0] uo_out,   // Dedicated outputs - connected to the 7 segment display
    input  wire [7:0] uio_in,   // IOs: Bidirectional Input path
    output wire [7:0] uio_out,  // IOs: Bidirectional Output path
    output wire [7:0] uio_oe,   // IOs: Bidirectional Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // will go high when the design is enabled
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
    
    wire spi_data_in = ui_in[0];
    wire spi_select = uo_out[1];
    wire spi_out = uo_out[2];
    wire spi_clk_enable;
    assign uo_out[0] = !clk && spi_clk_enable;

    nanoV_cpu nano(
        .clk(clk), 
        .rstn(rst_n),
        .spi_data_in(spi_data_in), 
        .spi_select(spi_select), 
        .spi_out(spi_out), 
        .spi_clk_enable(spi_clk_enable));

endmodule
