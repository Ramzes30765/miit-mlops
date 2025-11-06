# python 3.10.16
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install onnx onnxruntime-gpu onnxsim
pip install openvino openvino-dev
pip install --extra-index-url https://pypi.nvidia.com \
  tensorrt-cu12==10.13.3.9 \
  tensorrt-cu12-bindings==10.13.3.9 \
  tensorrt-cu12-libs==10.13.3.9
pip install timm