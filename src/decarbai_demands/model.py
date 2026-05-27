"""Inference model: PCA + XGBoost ensemble loaded from a zstd-compressed tar archive."""

import tarfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import numpy as np
import zstandard as zstd
from xgboost import XGBRegressor


@dataclass
class Model:
    pca_components: np.ndarray
    pca_mean: np.ndarray
    scaler_mean: np.ndarray
    scaler_std: np.ndarray
    models: list[XGBRegressor]

    def predict(self, features: np.ndarray) -> np.ndarray:
        scaled = self.scale_features(features).reshape(1, -1)
        scores = np.column_stack([m.predict(scaled) for m in self.models])
        series = scores @ self.pca_components + self.pca_mean
        result: np.ndarray = np.clip(series, 0, None).ravel().round(4)
        return result

    def scale_features(self, features: np.ndarray) -> np.ndarray:
        safe_std = np.where(self.scaler_std == 0, 1.0, self.scaler_std)
        scaled: np.ndarray = (features - self.scaler_mean) / safe_std
        return scaled


def load_artifacts(path: Path) -> Model:
    dctx = zstd.ZstdDecompressor()

    with path.open("rb") as f, dctx.stream_reader(f) as zst, tarfile.open(fileobj=zst, mode="r|") as tar:
        arrays = {}
        models = []

        for member in tar:
            name = member.name
            file_obj = tar.extractfile(member)
            if file_obj is None:
                continue
            data = file_obj.read()

            if name == "scaler_pca.npz":
                arrays = dict(np.load(BytesIO(data)))
            elif name.endswith(".ubj"):
                model = XGBRegressor()
                model.load_model(bytearray(data))
                # Extract index: "model_0.ubj" -> 0
                idx = int(name.rsplit("_", 1)[1].split(".", 1)[0])
                models.append((idx, model))

        sorted_models: list[XGBRegressor] = [m for _, m in sorted(models)]

    return Model(
        pca_components=arrays["pca_components"],
        pca_mean=arrays["pca_mean"],
        scaler_mean=arrays["scaler_mean"],
        scaler_std=arrays["scaler_std"],
        models=sorted_models,
    )
