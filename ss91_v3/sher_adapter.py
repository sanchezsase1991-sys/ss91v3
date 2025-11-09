#!/usr/bin/env python3
"""
Adapter to interact with your Sherloock class.
Assumes Sherloock is installed/available as a module. If Sherloock lacks predict(),
this adapter will call the hybrid classifier and wrap outputs.
"""
import logging
import numpy as np
from ss91_v3.utils import setup_logger
from sherloock import Sherloock  # your module

log = setup_logger("sher_adapter")
LABEL_MAP = {0: "HOLD", 1: "BUY", 2: "SELL"}

class SherAdapter:
    def __init__(self, model_path=None):
        self.model = Sherloock()
        # optionally load artifacts if you serialized them
        self.model_path = model_path

    def _vec(self, features):
        keys = sorted(features.keys())
        vec = np.array([0.0 if features[k] is None else float(features[k]) for k in keys], dtype=float).reshape(1, -1)
        return vec, keys

    def predict(self, features):
        # Preferred: Sherloock.predict(features) if implemented
        try:
            if hasattr(self.model, "predict"):
                out = self.model.predict(features)
                # ensure structure
                return {
                    "signal": out.get("signal", "HOLD"),
                    "confidence": float(out.get("confidence", 0.0)),
                    "meta": out.get("meta", {})
                }
            else:
                # fallback to hybrid text classifier
                res = self.model._handle_hybrid_classify(str(features))
                return {"signal":"HOLD","confidence":0.0,"meta":{"raw":res}}
        except Exception as e:
            log.exception("SherAdapter.predict failed")
            return {"signal":"HOLD","confidence":0.0,"meta":{"error":str(e)}}
