until systemctl status rag_conversation.service -n 1000 | grep -q "Application startup complete"
do
  sleep 1
done
