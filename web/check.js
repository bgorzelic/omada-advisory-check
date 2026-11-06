// Port of omada_advisory_check.py. Keep behavior identical; tests/test_web.py checks parity.
(function (root) {
  const FW_RE = /^\s*(\d+(?:\.\d+)*)\s+Build\s+(\d{8})/i;
  const normHw = (s) => { const m = /^v?(\d+)/i.exec(s.trim()); return m ? m[1] : s.trim(); };
  const normModel = (s) => s.trim().replace(/\s*\([^)]*\)\s*$/, "").toUpperCase();
  function parseFw(s) {
    const m = FW_RE.exec(s);
    return m ? { v: m[1].split(".").map(Number), b: Number(m[2]) } : null;
  }
  function cmp(a, b) {
    const n = Math.max(a.v.length, b.v.length);
    for (let i = 0; i < n; i++) { const d = (a.v[i] || 0) - (b.v[i] || 0); if (d) return d; }
    return a.b - b.b;
  }
  function buildIndex(data) {
    const idx = new Map();
    for (const r of data.fixed) idx.set(normModel(r.model) + "|" + normHw(r.hw), r.firmware);
    return idx;
  }
  function check(model, hw, firmware, idx) {
    const target = idx.get(normModel(model) + "|" + normHw(hw));
    if (!target) return ["UNKNOWN", "model/hardware version not in transcribed bulletin table"];
    const have = parseFw(firmware);
    if (!have) return ["UNKNOWN", "cannot parse firmware"];
    return [cmp(have, parseFw(target)) < 0 ? "BELOW_FIXED" : "AT_OR_ABOVE_FIXED", target];
  }
  // CSV with header model,hw,firmware. Firmware contains no commas; quoted fields not supported.
  function parseCsv(text) {
    const lines = text.split(/\r?\n/).filter((l) => l.trim());
    if (!lines.length) return [];
    const head = lines[0].split(",").map((h) => h.trim().toLowerCase());
    return lines.slice(1).map((l) => {
      const c = l.split(","); const o = {};
      head.forEach((h, i) => (o[h] = (c[i] || "").trim()));
      return o;
    });
  }
  const api = { check, buildIndex, parseCsv, parseFw };
  if (typeof module !== "undefined") module.exports = api; else root.OmadaCheck = api;
})(typeof window !== "undefined" ? window : globalThis);
