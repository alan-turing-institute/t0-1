until systemctl status qwen_with_tools.service -n 1000 | grep -q "Application startup complete"
do
  sleep 1
done
