import numpy as np

CLASS_NAMES = [
    'person',
    'bicycle',
    'car',
    'motorcycle',
    'airplane',
    'bus',
    'train',
    'truck',
    'boat',
    'traffic light',
    'fire hydrant',
    'stop sign',
    'parking meter',
    'bench',
    'bird',
    'cat',
    'dog',
    'horse',
    'sheep',
    'cow',
    'elephant',
    'bear',
    'zebra',
    'giraffe',
    'backpack',
    'umbrella',
    'handbag',
    'tie',
    'suitcase',
    'frisbee',
    'skis',
    'snowboard',
    'sports ball',
    'kite',
    'baseball bat',
    'baseball glove',
    'skateboard',
    'surfboard',
    'tennis racket',
    'bottle',
    'wine glass',
    'cup',
    'fork',
    'knife',
    'spoon',
    'bowl',
    'banana',
    'apple',
    'sandwich',
    'orange',
    'broccoli',
    'carrot',
    'hot dog',
    'pizza',
    'donut',
    'cake',
    'chair',
    'couch',
    'potted plant',
    'bed',
    'dining table',
    'toilet',
    'tv',
    'laptop',
    'mouse',
    'remote',
    'keyboard',
    'cell phone',
    'microwave',
    'oven',
    'toaster',
    'sink',
    'refrigerator',
    'book',
    'clock',
    'vase',
    'scissors',
    'teddy bear',
    'hair drier',
    'toothbrush'
 ]

def nms_numpy(boxes, scores, iou_thres=0.45):
    if boxes.size == 0:
        return np.array([], dtype=int)

    order = scores.argsort()[::-1]
    keep = []

    while order.size > 0:
        i = order[0]
        keep.append(i)

        if order.size == 1:
            break

        xx1 = np.maximum(boxes[i, 0], boxes[order[1:], 0])
        yy1 = np.maximum(boxes[i, 1], boxes[order[1:], 1])
        xx2 = np.minimum(boxes[i, 2], boxes[order[1:], 2])
        yy2 = np.minimum(boxes[i, 3], boxes[order[1:], 3])

        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h

        area_i = (boxes[i, 2] - boxes[i, 0]) * (boxes[i, 3] - boxes[i, 1])
        area_o = (boxes[order[1:], 2] - boxes[order[1:], 0]) * (
            boxes[order[1:], 3] - boxes[order[1:], 1]
        )

        iou = inter / (area_i + area_o - inter + 1e-6)
        inds = np.where(iou <= iou_thres)[0]
        order = order[inds + 1]

    return np.array(keep, dtype=int)


def postprocess_yolo_det(
    out0: np.ndarray,
    orig_size,
    img_size=(640, 640),
    conf_thres=0.25,
    iou_thres=0.45,
):

    pred = out0[0].transpose(1, 0)  # [N, C]

    boxes_cxcywh = pred[:, :4]
    cls_scores  = pred[:, 4:]

    # if cls_scores.max() > 1.0 or cls_scores.min() < 0.0:
    #     cls_scores = 1 / (1 + np.exp(-cls_scores))
    
    cls_ids = cls_scores.argmax(axis=1)
    cls_conf = cls_scores.max(axis=1)

    keep_mask = cls_conf >= conf_thres
    boxes_cxcywh = boxes_cxcywh[keep_mask]
    cls_ids      = cls_ids[keep_mask]
    cls_conf     = cls_conf[keep_mask]

    if boxes_cxcywh.shape[0] == 0:
        return []

    x, y, w, h = (
        boxes_cxcywh[:, 0],
        boxes_cxcywh[:, 1],
        boxes_cxcywh[:, 2],
        boxes_cxcywh[:, 3],
    )
    x1 = x - w / 2
    y1 = y - h / 2
    x2 = x + w / 2
    y2 = y + h / 2
    boxes_xyxy = np.stack([x1, y1, x2, y2], axis=1)  # [M,4]

    final = []
    for cls in np.unique(cls_ids):
        idxs = np.where(cls_ids == cls)[0]
        b_cls = boxes_xyxy[idxs]
        s_cls = cls_conf[idxs]

        keep = nms_numpy(b_cls, s_cls, iou_thres)
        for j in keep:
            final.append((b_cls[j], int(cls), float(s_cls[j])))

    orig_w, orig_h = orig_size
    img_w, img_h = img_size
    sx = orig_w / img_w
    sy = orig_h / img_h

    detections = []
    for (x1, y1, x2, y2), cls, score in final:
        x1 *= sx
        x2 *= sx
        y1 *= sy
        y2 *= sy

        detections.append(
            {
                "x1": float(max(0.0, x1)),
                "y1": float(max(0.0, y1)),
                "x2": float(x2),
                "y2": float(y2),
                "score": float(score),
                "cls": cls,
                "label": CLASS_NAMES[cls] if 0 <= cls < len(CLASS_NAMES) else None,
            }
        )

    return detections
