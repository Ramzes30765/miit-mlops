from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
from PIL import Image
import io
import tritonclient.http as httpclient

from utils import postprocess_yolo_det

TRITON_URL = "localhost:8000"
IMG_SIZE = (640, 640)

app = FastAPI()

triton_client = httpclient.InferenceServerClient(url=TRITON_URL)


def preprocess_image(file_bytes: bytes) -> np.ndarray:

    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    orig_w, orig_h = img.size 

    img = img.resize(IMG_SIZE, Image.BILINEAR)
    img_np = np.array(img).astype(np.float32) / 255.0
    img_np = np.transpose(img_np, (2, 0, 1))
    img_np = np.expand_dims(img_np, axis=0)

    return img_np, (orig_w, orig_h)


@app.post("/infer")
async def infer(
    model_name: str = Form(...),
    file: UploadFile = File(...)
):
    if model_name not in ["yolo_det", "yolo_seg"]:
        raise HTTPException(status_code=400, detail="Unknown model_name")

    file_bytes = await file.read()
    input_tensor, orig_size = preprocess_image(file_bytes)

    inputs = [
        httpclient.InferInput(
            name="images",
            shape=list(input_tensor.shape),
            datatype="FP32",
        )
    ]
    inputs[0].set_data_from_numpy(input_tensor)

    outputs = [
        httpclient.InferRequestedOutput("output0"),
    ]
    if model_name == "yolo_seg":
        outputs.append(httpclient.InferRequestedOutput("output1"))

    response = triton_client.infer(
        model_name=model_name,
        inputs=inputs,
        outputs=outputs,
    )

    out0 = response.as_numpy("output0")

    if model_name == "yolo_det":
        detections = postprocess_yolo_det(
            out0,
            orig_size=orig_size,
            img_size=IMG_SIZE,
            conf_thres=0.25,
            iou_thres=0.45,
        )
        return JSONResponse(
            {
                "model_name": model_name,
                "num_detections": len(detections),
                "detections": detections,
            }
        )

    if model_name == "yolo_seg":
        out1 = response.as_numpy("output1")
        return JSONResponse(
            {
                "model_name": model_name,
                "output0_shape": out0.shape,
                "output1_shape": out1.shape,
            }
        )

