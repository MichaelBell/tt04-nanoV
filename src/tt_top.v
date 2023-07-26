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

    reg spi_select, spi_mosi;
    wire spi_clk_enable;
    assign uio_out[1] = spi_select;
    assign uio_out[2] = spi_mosi;
    assign uio_out[0] = !clk && spi_clk_enable;
    reg buffered_spi_in;

    wire uart_txd;
    assign uio_out[4] = uart_txd;
    wire uart_rxd = uio_in[5];

    // Switch all bidis to inputs when in reset (allows external programming of SPI RAM
    // while in reset).
    assign uio_oe[7:0] = rst_n ? 8'h17: 8'h00;

    // Bidi outputs used as inputs
    assign uio_out[3] = 0;
    assign uio_out[5] = 0;

    // Bidi not used (yet)
    assign uio_out[6] = 0;
    assign uio_out[7] = 0;

    always @(negedge clk) begin
        buffered_spi_in <= uio_in[3];
    end

    wire spi_data_nano, spi_select_nano;
    always @(posedge clk) begin
        if (!rst_n)
            spi_select <= 1;
        else
            spi_select <= spi_select_nano;

        spi_mosi <= spi_data_nano;
    end
    
    wire [31:0] data_in;
    wire [31:0] data_out;
    wire is_data;
    wire is_addr;
    reg [7:0] output_data;
    assign uo_out = output_data;

    nanoV_cpu #(.NUM_REGS(16)) nano(
        .clk(clk), 
        .rstn(rst_n),
        .spi_data_in(buffered_spi_in), 
        .spi_select(spi_select_nano), 
        .spi_out(spi_data_nano),
        .spi_clk_enable(spi_clk_enable),
        .ext_data_in(data_in),
        .data_out(data_out),
        .store_data_out(is_data),
        .store_addr_out(is_addr));

    reg connect_gpios, connect_uart, connect_uart_status;
    
    wire [31:0] reversed_data_out;
    genvar i;
    generate 
      for (i=0; i<32; i=i+1) assign reversed_data_out[i] = data_out[31-i]; 
    endgenerate

    always @(posedge clk) begin
        if (!rst_n) begin 
            connect_gpios <= 0;
            connect_uart <= 0;
            connect_uart_status <= 0;
        end
        else if (is_addr) begin
            connect_gpios <= (data_out == 32'h10000000);
            connect_uart <= (data_out == 32'h10001000);
            connect_uart_status <= (data_out == 32'h10001004);
        end

        if (is_data && connect_gpios) output_data <= reversed_data_out[7:0];
    end

    wire uart_tx_busy;
    wire uart_rx_valid;
    wire [7:0] uart_rx_data;
    assign data_in[31:8] = 0;
    assign data_in[7:0] = connect_gpios ? ui_in : 
                          connect_uart ? uart_rx_data :
                          connect_uart_status ? {7'b0, uart_tx_busy} : 0;

    wire uart_tx_start = is_data && connect_uart;
    wire [7:0] uart_tx_data = reversed_data_out[7:0];

    uart_tx #(.CLK_HZ(12_000_000), .BIT_RATE(115_200)) i_uart_tx(
        .clk(clk),
        .resetn(rst_n),
        .uart_txd(uart_txd),
        .uart_tx_en(uart_tx_start),
        .uart_tx_data(uart_tx_data),
        .uart_tx_busy(uart_tx_busy) 
    );

    uart_rx #(.CLK_HZ(12_000_000), .BIT_RATE(115_200)) i_uart_rx(
        .clk(clk),
        .resetn(rst_n),
        .uart_rxd(uart_rxd),
        .uart_rx_read(connect_uart && is_data),
        .uart_rx_valid(uart_rx_valid),
        .uart_rx_data(uart_rx_data) 
    );

endmodule
