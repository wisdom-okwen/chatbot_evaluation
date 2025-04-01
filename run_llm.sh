#!/bin/bash

# --- Assumptions ---
# 1. The model weights provided in MODEL_PATH are already quantized versions.
# 2. A vLLM server requires full memory of a GPU to run (i.e., if a GPU has an active process, it is considered unavailable).
# 3. The model's parameter count (in billions) is embedded in its path name (e.g., "Meta-Llama-3.1-8B-Instruct" means 8B parameters).
# 4. The server will be shut down if inactive for 10 minutes (600 seconds).

# --- Pseudocode ---
# 1. Parse input arguments (model path and quantization type).
# 2. Identify available GPUs by checking for currently running processes.
# 3. Find the first available network port in a specified range.
# 4. Determine tensor-parallelism (TP) based on model size and quantization type.
# 5. Adjust the set of visible GPUs based on the computed TP requirement.
# 6. Start the vLLM server with the selected model, port, and TP settings.
# 7. Monitor the server logs for activity, shutting down if idle for a specified duration.



# --- Step 1: Parse Input Arguments ---
MODEL_PATH=$1
QUANT_TYPE=${2:-fp16}   # Default quantization type is fp16.
LOGFILE=$(mktemp /tmp/log.XXXXXX)  # Create a temporary log file
IDLE_TIMEOUT=600   # Idle timeout in seconds (5 minutes)
CHECK_INTERVAL=10  # Log check interval in seconds
PORT=10000  # Initialize the port variable

# --- Step 2: Identify Available GPUs ---
DEVICES=$(nvidia-smi --query-gpu=index --format=csv,noheader | paste -sd " " -) # Get all available GPUs
available_gpus=()  # Array to store available GPUs
# 2.1: Check each GPU for running processes
for gpu in $DEVICES; do
    processes=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader -i $gpu)
    if [ -z "$processes" ]; then
        available_gpus+=("$gpu")
    fi
done

# 2.2: Display available GPUs and exit if none are free
if [ ${#available_gpus[@]} -eq 0 ]; then
    echo "No available GPUs. All GPUs are currently in use."
    exit 1
else
    echo "Available GPUs: ${available_gpus[@]}"
fi

# --- Step 3: Find an Available Port ---
for port in {7471..7590}; do
    if ! lsof -nP -iTCP:$port -sTCP:LISTEN > /dev/null 2>&1; then
        PORT=$port
        echo "Port $PORT is free."
        break
    fi
done

echo "The first available port is: $PORT"

# --- Step 4: Determine Tensor-Parallelism (TP) ---
PARAM_CANDIDATES=($(echo "$MODEL_PATH" | grep -oP '\d+(?:\.\d+)?(?=B)'))
MAX_PARAM=0

if [ -z "$PARAM_CANDIDATES" ]; then
    echo "No parameter count found in the model path."
    PARAM_CANDIDATES=($(echo "${MODEL_PATH^^}" | grep -oP '\d+(?:\.\d+)?(?=B)'))
fi

# 4.1: Extract and determine the largest parameter value
for param in "${PARAM_CANDIDATES[@]}"; do
    if (( $(echo "$param > $MAX_PARAM" | bc -l) )); then
        MAX_PARAM=$param
    fi
done

# 4.2: Set tensor parallelism based on model size and quantization type
TP=1
if [ "$QUANT_TYPE" == "fp16" ]; then
    if (( $(echo "$MAX_PARAM > 48" | bc -l) )); then
        TP=4
    elif (( $(echo "$MAX_PARAM > 20" | bc -l) )); then
        TP=2
    fi
elif [ "$QUANT_TYPE" == "int8" ]; then
    if (( $(echo "$MAX_PARAM > 48" | bc -l) )); then
        TP=2
    elif (( $(echo "$MAX_PARAM > 20" | bc -l) )); then
        TP=1
    fi
elif [ "$QUANT_TYPE" == "int4" ]; then
    TP=1
else
    echo "Unknown quantization type: $QUANT_TYPE. Using default thresholds for fp16."
    if (( $(echo "$MAX_PARAM > 48" | bc -l) )); then
        TP=4
    elif (( $(echo "$MAX_PARAM > 20" | bc -l) )); then
        TP=2
    fi
fi

echo "Detected model with ${MAX_PARAM}B parameters. Using tensor-parallelism: $TP."

# --- Step 5: Adjust Visible Devices Based on TP ---
NUM_AVAILABLE=${#available_gpus[@]}

if [ "$NUM_AVAILABLE" -gt "$TP" ]; then
    SELECTED_DEVICES=$(IFS=,; echo "${available_gpus[*]:0:$TP}")
    echo "Trimming devices from ${available_gpus[@]} to $SELECTED_DEVICES based on tensor parallelism requirement."
else
    SELECTED_DEVICES=$(IFS=,; echo "${available_gpus[*]}")
fi

export CUDA_VISIBLE_DEVICES=$SELECTED_DEVICES

# --- Step 6: Start the vLLM Server ---
touch "$LOGFILE"
echo "Logfile created at $LOGFILE."

echo "Starting vLLM server on port $PORT..."
python -m sglang.launch_server --model-path "$MODEL_PATH" --port "$PORT" --tp ${TP} >> "$LOGFILE" 2>&1 &
SERVER_PID=$!

# 6.1: Wait for server startup
sleep 60
echo "Server started with PID $SERVER_PID. Logging to $LOGFILE."

# --- Step 7: Monitor Server Activity and Shutdown on Inactivity ---
LAST_MOD=$(stat -c %Y "$LOGFILE")

while kill -0 $SERVER_PID 2>/dev/null; do
    CURRENT_MOD=$(stat -c %Y "$LOGFILE")

    if [ "$CURRENT_MOD" -gt "$LAST_MOD" ]; then
        LAST_MOD=$CURRENT_MOD
        echo "Detected log update at $(date -d @$LAST_MOD). Resetting idle timer."
    fi

    CURRENT_TIME=$(date +%s)
    INACTIVE_FOR=$(( CURRENT_TIME - LAST_MOD ))
    echo "No log update for ${INACTIVE_FOR} seconds."

    if [ "$INACTIVE_FOR" -ge "$IDLE_TIMEOUT" ]; then
        echo "Idle timeout reached (>$IDLE_TIMEOUT seconds without log updates). Shutting down server..."
        kill $SERVER_PID
        break
    fi

    sleep $CHECK_INTERVAL
done

# 7.1: Wait for the server process to exit
wait $SERVER_PID
echo "Server has been shut down due to inactivity."