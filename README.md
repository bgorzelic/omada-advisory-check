# omada-advisory-check

Offline checker: flags Omada gateways running firmware older than the builds fixed in
[TP-Link bulletin 132084](https://support.omadanetworks.com/en/bulletin/132084/) (2026-08-20;
CVE-2026-19586 pre-auth command injection in the OpenVPN server, plus CVE-2026-9033 and CVE-2026-19683).

Unofficial. Not affiliated with TP-Link. Contains no exploit code, firmware, or TP-Link branding.

## Use

    python3 omada_advisory_check.py devices.csv     # columns: model,hw,firmware
    pytest

Exit code 1 if any device is `BELOW_FIXED`. See `example-devices.csv`.

## Limits (read these)

- `UNKNOWN` means the model/hardware version is not in the data file. It is **not** clean.
- The data file holds the 19 rows of the bulletin table, transcribed 2026-11-06. Re-verify against the
  live bulletin before relying on results.
- Hardware versions match on the major number (`v2`, `2.0` -> 2); a region suffix like `ER605(UN)` is ignored.
- Status compares against fixed builds only. CVE-2026-19586 is reachable only when the OpenVPN
  server is enabled; the vendor workaround is to disable it or restrict source IPs.
- Version compare assumes the dotted version then the build date, as in `2.4.4 Build 20260630 Rel.14398`.

    open web/index.html   # offline browser version; same data, same rules
