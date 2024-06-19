mpremote a0 exec "machine.reset()"
sleep 1
mpremote a0 mount . + exec "os.chdir('/'); import run_nanov; run_nanov.execute('/remote/$1')"
