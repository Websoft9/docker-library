"""Seed a small TensorBoard demo run so the dashboard is not empty on first start.

This is onboarding data, not real training output. It is written under the
`demo` subdirectory of the TensorBoard logdir and can be disabled by setting
TENSORBOARD_DEMO=false.
"""

import math
import os

import tensorflow as tf

logdir = os.environ.get("TENSORBOARD_DEMO_LOGDIR", "/tf/notebooks/logs/demo")
os.makedirs(logdir, exist_ok=True)

writer = tf.summary.create_file_writer(logdir)
with writer.as_default():
    for step in range(1, 51):
        accuracy = 0.50 + 0.009 * step
        loss = 1.30 * math.exp(-0.05 * step)
        tf.summary.scalar("demo/accuracy", accuracy, step=step)
        tf.summary.scalar("demo/loss", loss, step=step)
        tf.summary.scalar("demo/learning_rate", 0.01 * (0.95 ** step), step=step)
    tf.summary.histogram("demo/weights", tf.random.normal([1000]), step=1)
    tf.summary.text(
        "demo/about",
        "Demo data seeded by the Websoft9 TensorFlow package. "
        "Run tensorboard_demo.py for a real training run, or set "
        "TENSORBOARD_DEMO=false to disable this sample.",
        step=1,
    )
writer.flush()

print(f"Seeded TensorBoard demo data in {logdir}")
