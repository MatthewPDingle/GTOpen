# N15: eligible for fresh accuracy testing

Reducing the N06 correction to 75% produced 6.283723% pot mean hand-value
error: 8.79% lower than the ordinary control, with the worst family 2.12%
worse. Both fixed gates passed. This revision was chosen using known training
results; it is not independent evaluation evidence.

All 26 ordinary and unshrunk N06 control errors reproduced within 1e-9.
The initial direct launch used default 24-thread BLAS because NumPy loaded
before the environment setting. The control check rejected that attempt.
The dedicated launcher restores original BLAS1/Torch2 settings; no numerical
or accuracy tolerance was relaxed. See training-runtime.json.

The final model is frozen and registered before any of its 400 fresh reference
outcomes exist. Accuracy evaluation is queued. GPU implementation, runtime
and changed-policy checks remain necessary; no model has been deployed.

[Training screen](training-screen.json) · [Registration](evaluation-registration.json)
