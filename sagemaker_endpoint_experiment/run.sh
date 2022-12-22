for instance in mlm5large mlm5xlarge mlm52xlarge mlm54xlarge mlm512xlarge mlm524xlarge
do
locust -f locust/locust_script.py -u 1 --headless --host="http://latency-experiment-endpoint-${instance}" --stop-timeout 60 -L DEBUG -t 1m --logfile=logfile.log --csv=results/$instance --csv-full-history --reset-stats
done