REPO_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "REPO_ROOT_DIR is: $REPO_ROOT_DIR"

if ! tmux has-session -t t0-1 2>/dev/null; then
    tmux new-session -d -s t0-1

    # Common setup for all panes
    # tmux send-keys "cd $REPO_ROOT_DIR" C-m
    # tmux send-keys 'source .env' C-m
    # tmux send-keys 'source .venv/bin/activate' C-m


    # Create three panes and run the commands in each pane
    PANE0=$(tmux display-message -p '#{pane_id}')
    tmux split-window -h
    PANE1=$(tmux display-message -p '#{pane_id}')
    tmux split-window -v
    PANE2=$(tmux display-message -p '#{pane_id}')

    # Start the scripts in each pane
    tmux select-pane -t $PANE0
    tmux send-keys "cd $REPO_ROOT_DIR" C-m
    tmux send-keys 'uv run ./scripts/serve_rag_conversational.sh' C-m
    tmux select-pane -t $PANE1
    tmux send-keys "cd $REPO_ROOT_DIR" C-m
    tmux send-keys 'CUDA_VISIBLE_DEVICES=4,5,6,7 uv run ./scripts/isambard-ai/serve_t0.sh TomasLaz/t0-2.5-gemma-3-27b-it' C-m
    tmux select-pane -t $PANE2
    tmux send-keys "cd $REPO_ROOT_DIR" C-m
    tmux send-keys 'CUDA_VISIBLE_DEVICES=0,1,2,3 uv run ./scripts/isambard-ai/serve_qwen_with_tools.sh' C-m
fi

# Finally, attach to the tmux session
tmux attach -t t0-1
