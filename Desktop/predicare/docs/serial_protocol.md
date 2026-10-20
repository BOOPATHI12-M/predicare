# Serial protocol

Transport is USB serial at **115200 8-N-1**. Each message is one UTF-8 JSON
object terminated by `\n`; receivers must reject malformed JSON and validate
the numeric ranges before persistence.

```json
{"type":"measurement","heart_rate":72.0,"spo2":98.0,"temperature":36.6,"source":"device","timestamp":12345}
```

`heart_rate` is BPM (20-250), `spo2` is percent (50-100), and `temperature`
is Celsius (20-45). `source` is `device` for firmware readings and
`simulation` for backend-generated readings.
