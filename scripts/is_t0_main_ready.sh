until systemctl status t0_main.service -n 1000 | grep -q "Application startup complete"
do
  sleep 1
done
