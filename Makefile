COMPRESSED_ISA = C

spec: testbench.vcd
	python3 rtlkon.py testbench.vcd
	java -cp /daikon.jar testbench.dtrace testbench.decls >spec.out

testbench.vcd: testbench_ez.vvp
	vvp -N $< +vcd >/dev/null

testbench_ez.vvp: testbench_ez.v picorv32.v
	iverilog -o $@ -DCOMPRESSED_ISA $^
	chmod -x $@

clean:
	rm -f *.vvp *.vcd *.dtrace *.decls