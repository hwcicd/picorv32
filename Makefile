test: testbench_ez.vvp
	vvp -N $< +vcd

testbench_ez.vvp: testbench_ez.v picorv32.v
	iverilog -o $@ -DCOMPRESSED_ISA $^
	chmod -x $@

clean:
	rm -f *.vvp *.vcd
