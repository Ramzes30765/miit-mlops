import onnx, onnxruntime as ort
import numpy as np
from openvino.runtime import Core
import tensorrt as trt

onnx_model = "onnx_model.onnx"
x = np.random.randn(1,3,224,224).astype(np.float32)

print("=== ONNXRuntime ===")
sess = ort.InferenceSession(onnx_model, providers=['CUDAExecutionProvider'])
y_ort = sess.run(None, {'input': x})[0]
print(y_ort.shape)

print("=== OpenVINO ===")
core = Core()
ov_model = core.read_model(onnx_model)
compiled = core.compile_model(ov_model, "CPU")
infer = compiled.create_infer_request()
infer.infer({'images': x})
print(infer.get_output_tensor(0).data.shape)

print("=== TensorRT ===")
logger = trt.Logger(trt.Logger.ERROR)
with open(onnx_model, 'rb') as f, trt.Runtime(logger) as runtime:
    engine = runtime.deserialize_cuda_engine(f.read())
    print("TensorRT engine loaded successfully")