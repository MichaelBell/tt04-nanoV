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

    wire spi_data_in = uio_in[3];
    wire spi_select = uio_out[1];
    wire spi_out = uio_out[2];
    wire spi_clk_enable;
    assign uio_out[0] = !clk && spi_clk_enable;

    wire uart_txd = uio_out[4];
    wire uart_rxd = uio_in[5];

    assign uio_oe[7:0] = 8'h17;

    // Bidi outputs used as inputs
    assign uio_out[3] = 0;
    assign uio_out[5] = 0;

    // Bidi not used (yet)
    assign uio_out[6] = 0;
    assign uio_out[7] = 0;

    wire [31:0] data_out;
    wire is_data;
    wire is_addr;
    reg [7:0] output_data;
    assign uo_out = output_data;

    nanoV_cpu #(.NUM_REGS(8)) nano(
        .clk(clk), 
        .rstn(rst_n),
        .spi_data_in(spi_data_in), 
        .spi_select(spi_select), 
        .spi_out(spi_out), 
        .spi_clk_enable(spi_clk_enable),
        .data_out(data_out),
        .store_data_out(is_data),
        .store_addr_out(is_addr));

    reg set_outputs, set_uart_tx;
    
    always @(posedge clk) begin
        if (!rst_n) begin 
            set_outputs <= 0;
            set_uart_tx <= 0;
        end
        else if (is_addr) begin
            set_outputs <= (data_out == 32'h10000000);
            set_uart_tx <= (data_out == 32'h10000100);
        end

        if (is_data && set_outputs) output_data <= data_out[7:0];
    end

    wire uart_tx_start = is_data && set_uart_tx;
    wire [7:0] uart_tx_data = data_out[7:0];

    uart_tx #(.CLK_HZ(24_000_000), .BIT_RATE(115_200)) i_uart_tx(
        .clk(clk),
        .resetn(rst_n),
        .uart_txd(uart_txd),
        .uart_tx_en(uart_tx_start),
        .uart_tx_data(uart_tx_data) 
    );

endmodule
