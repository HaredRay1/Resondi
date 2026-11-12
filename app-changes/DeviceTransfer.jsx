import React, { useRef, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "@/lib/AuthContext";
import { useT, useLanguage } from "@/lib/i18n";
import { base44 } from "@/api/base44Client";
import { FULL_SITES, STANDARD_SITES, getSiteMode } from "@/lib/examSites";
import Disclaimer from "@/components/Disclaimer";
import { ArrowLeft, Wifi, ExternalLink, Download, Upload, Check, Loader2, AlertCircle, Trash2, ListOrdered } from "lucide-react";

// Transfer recordings from the Resondi device to the app over the device's own Wi-Fi.
//
// The device raises the access point RESONDI_WIFI and serves its own page at http://192.168.4.1,
// where its recordings can be downloaded. This app is served over HTTPS, and browsers block an
// HTTPS page from reading an http:// address, so the app cannot pull the files itself. The phone
// carries them instead: download from the device page, reconnect to the internet, then choose the
// files here and upload them. Automatic upload from the device (the gateway) is not built yet.
//
// Text is kept here rather than in i18n.jsx so the page could ship without a builder turn.

const DEVICE_URL = "http://192.168.4.1/";
const DEVICE_SSID = "RESONDI_WIFI";

const TEXT = {
  en: {
    title: "Transfer from Resondi device",
    subtitle: "Move recordings from the stethoscope to your account over the device's Wi-Fi.",
    step1: "Connect to the device",
    step1Body: `Turn on the Resondi device. On this phone, open Wi-Fi settings and join ${DEVICE_SSID}. Enter the device password. Your phone may warn that this network has no internet; stay connected.`,
    step2: "Download the recordings",
    step2Body: "Open the device page and download the recordings you want (files named like AUSCULTA0012.WAV). They are saved to this phone's Downloads.",
    openDevice: "Open device page (192.168.4.1)",
    step3: "Reconnect to the internet",
    step3Body: `Leave ${DEVICE_SSID} and reconnect to your usual Wi-Fi or mobile data. Uploading needs the internet.`,
    step4: "Choose the files and their chest sites",
    step4Body: "Select the downloaded files, then set the chest site of each recording.",
    choose: "Choose recordings",
    guidedOrder: "Fill sites in guided exam order",
    site: "Chest site",
    pickSite: "Choose a site",
    lung: "Lung",
    heart: "Heart",
    seconds: "s",
    notWav: "Not a WAV file",
    upload: (n) => `Upload ${n} recording${n === 1 ? "" : "s"}`,
    uploading: "Uploading",
    uploaded: "Uploaded",
    failed: "Upload failed. Check the internet connection and try again.",
    allDone: "All recordings uploaded. Open the exam to run the analysis and send it for review.",
    toExam: "Open exam and run analysis",
    toHistory: "Go to recording history",
    remove: "Remove",
    needSites: "Choose a chest site for every recording first.",
    note: "Transfer is manual for now: the phone carries each recording from the device to the app. Automatic upload from the device is planned, not built.",
  },
  fil: {
    title: "Ilipat mula sa Resondi device",
    subtitle: "Ilipat ang mga recording mula sa stethoscope papunta sa iyong account gamit ang Wi-Fi ng device.",
    step1: "Kumonekta sa device",
    step1Body: `Buksan ang Resondi device. Sa teleponong ito, buksan ang Wi-Fi settings at kumonekta sa ${DEVICE_SSID}. Ilagay ang password ng device. Maaaring sabihin ng telepono na walang internet ang network na ito; manatiling nakakonekta.`,
    step2: "I-download ang mga recording",
    step2Body: "Buksan ang pahina ng device at i-download ang mga recording na kailangan mo (mga file na tulad ng AUSCULTA0012.WAV). Mase-save ang mga ito sa Downloads ng teleponong ito.",
    openDevice: "Buksan ang pahina ng device (192.168.4.1)",
    step3: "Kumonekta muli sa internet",
    step3Body: `Umalis sa ${DEVICE_SSID} at kumonekta muli sa karaniwan mong Wi-Fi o mobile data. Kailangan ng internet para mag-upload.`,
    step4: "Piliin ang mga file at ang bahagi ng dibdib",
    step4Body: "Piliin ang mga na-download na file, saka itakda ang bahagi ng dibdib ng bawat recording.",
    choose: "Pumili ng mga recording",
    guidedOrder: "Punan ang mga bahagi ayon sa gabay na pagkakasunod",
    site: "Bahagi ng dibdib",
    pickSite: "Pumili ng bahagi",
    lung: "Baga",
    heart: "Puso",
    seconds: "s",
    notWav: "Hindi WAV file",
    upload: (n) => `I-upload ang ${n} recording`,
    uploading: "Ina-upload",
    uploaded: "Na-upload",
    failed: "Hindi na-upload. Suriin ang koneksyon sa internet at subukang muli.",
    allDone: "Na-upload na ang lahat ng recording. Buksan ang pagsusuri upang patakbuhin ang analysis at ipadala ito para sa review.",
    toExam: "Buksan ang pagsusuri at patakbuhin ang analysis",
    toHistory: "Pumunta sa history ng recording",
    remove: "Alisin",
    needSites: "Pumili muna ng bahagi ng dibdib para sa bawat recording.",
    note: "Mano-mano pa ang paglipat sa ngayon: dinadala ng telepono ang bawat recording mula sa device papunta sa app. Nakaplano, ngunit hindi pa nagagawa, ang awtomatikong pag-upload mula sa device.",
  },
};

// Duration and format from the WAV header (RIFF chunks), so the app stores the real length.
async function readWavInfo(file) {
  try {
    const buf = await file.slice(0, 65536).arrayBuffer();
    const v = new DataView(buf);
    const tag = (o) => String.fromCharCode(v.getUint8(o), v.getUint8(o + 1), v.getUint8(o + 2), v.getUint8(o + 3));
    if (buf.byteLength < 12 || tag(0) !== "RIFF" || tag(8) !== "WAVE") return { isWav: false, seconds: 0 };
    let o = 12, byteRate = 0, sampleRate = 0, dataBytes = 0;
    while (o + 8 <= buf.byteLength) {
      const id = tag(o), size = v.getUint32(o + 4, true);
      if (id === "fmt " && o + 20 <= buf.byteLength) { sampleRate = v.getUint32(o + 12, true); byteRate = v.getUint32(o + 16, true); }
      if (id === "data") { dataBytes = Math.min(size, file.size - (o + 8)); break; }
      o += 8 + size + (size % 2);
    }
    return { isWav: true, sampleRate, seconds: byteRate ? Math.round((dataBytes / byteRate) * 10) / 10 : 0 };
  } catch {
    return { isWav: false, seconds: 0 };
  }
}

// Defined outside the page so its children are not remounted on every state change.
function Step({ n, title, children }) {
  return (
    <div className="card-base p-5">
      <div className="flex items-start gap-3">
        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full flex-shrink-0 font-extrabold text-sm"
          style={{ background: "var(--brand-muted)", color: "var(--brand-primary)" }}>{n}</span>
        <div className="flex-1 space-y-3">
          <p className="font-bold text-sm" style={{ color: "var(--brand-text)" }}>{title}</p>
          {children}
        </div>
      </div>
    </div>
  );
}

const body = (text) => <p className="text-sm leading-relaxed" style={{ color: "var(--brand-muted-foreground)" }}>{text}</p>;

export default function DeviceTransfer() {
  const { user } = useAuth();
  const t = useT();
  const { lang } = useLanguage();
  const L = TEXT[lang] || TEXT.en;
  const navigate = useNavigate();
  const fileRef = useRef(null);
  const [rows, setRows] = useState([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  // One group per transfer, kept across retries, so the uploads open together as one exam summary.
  const [groupId, setGroupId] = useState(null);

  const onChoose = async (e) => {
    const files = Array.from(e.target.files || []);
    e.target.value = "";
    if (!files.length) return;
    files.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));
    const added = await Promise.all(files.map(async (file) => ({
      key: `${file.name}-${file.size}-${file.lastModified}`,
      file,
      site: "",
      status: "ready",
      ...(await readWavInfo(file)),
    })));
    setRows((prev) => {
      const seen = new Set(prev.map((r) => r.key));
      return [...prev, ...added.filter((r) => !seen.has(r.key))];
    });
    setMessage("");
  };

  const setSite = (key, site) => setRows((prev) => prev.map((r) => (r.key === key ? { ...r, site } : r)));
  const remove = (key) => setRows((prev) => prev.filter((r) => r.key !== key));

  // Assigns sites in the order the guided exam visits them (lung sites, then cardiac points),
  // for a device session recorded in that order. Every site can still be changed afterwards.
  const fillGuidedOrder = () => {
    const order = rows.filter((r) => r.status !== "done").length > STANDARD_SITES.length ? FULL_SITES : STANDARD_SITES;
    let i = 0;
    setRows((prev) => prev.map((r) => (r.status === "done" ? r : { ...r, site: order[i++] || r.site })));
  };

  const pending = rows.filter((r) => r.status !== "done" && r.isWav);
  const allDone = rows.some((r) => r.status === "done") && rows.every((r) => r.status === "done" || !r.isWav);

  const uploadAll = async () => {
    if (pending.some((r) => !r.site)) { setMessage(L.needSites); return; }
    setBusy(true);
    setMessage("");
    const gid = groupId || `device-${user.id}-${Date.now()}`;
    if (!groupId) setGroupId(gid);
    let order = rows.filter((x) => x.status === "done").length;
    for (const r of pending) {
      setRows((prev) => prev.map((x) => (x.key === r.key ? { ...x, status: "uploading" } : x)));
      try {
        const { file_uri } = await base44.integrations.Core.UploadPrivateFile({ file: r.file });
        await base44.entities.AuscultationSession.create({
          patient_id: user.id,
          patient_name: user.full_name || user.email,
          mode: getSiteMode(r.site),
          body_location: r.site,
          recording_date: new Date(r.file.lastModified || Date.now()).toISOString(),
          duration_seconds: r.seconds || 0,
          audio_file_uri: file_uri,
          status: "completed",
          submission_status: "not_sent",
          exam_group_id: gid,
          exam_order: order++,
        });
        setRows((prev) => prev.map((x) => (x.key === r.key ? { ...x, status: "done" } : x)));
      } catch {
        setRows((prev) => prev.map((x) => (x.key === r.key ? { ...x, status: "failed" } : x)));
        setMessage(L.failed);
        break; // most likely still on the device's Wi-Fi; stop so the rest are not marked failed too
      }
    }
    setBusy(false);
  };

  return (
    <div className="space-y-5 fade-in">
      <button onClick={() => navigate("/patient/record")} className="btn-text">
        <ArrowLeft className="w-4 h-4" /> {t("common.back")}
      </button>
      <div>
        <h1 className="text-2xl font-extrabold" style={{ color: "var(--brand-text)" }}>{L.title}</h1>
        <p className="text-sm" style={{ color: "var(--brand-muted-foreground)" }}>{L.subtitle}</p>
      </div>

      <Step n={1} title={L.step1}>
        {body(L.step1Body)}
        <p className="text-xs font-bold flex items-center gap-1.5" style={{ color: "var(--brand-secondary)" }}>
          <Wifi className="w-4 h-4" /> {DEVICE_SSID}
        </p>
      </Step>

      <Step n={2} title={L.step2}>
        {body(L.step2Body)}
        <a href={DEVICE_URL} target="_blank" rel="noopener noreferrer" className="btn-outline w-full justify-center">
          <ExternalLink className="w-4 h-4" /> {L.openDevice}
        </a>
      </Step>

      <Step n={3} title={L.step3}>{body(L.step3Body)}</Step>

      <Step n={4} title={L.step4}>
        {body(L.step4Body)}
        <input ref={fileRef} type="file" multiple accept=".wav,audio/wav,audio/x-wav" onChange={onChoose} className="hidden" />
        <button onClick={() => fileRef.current?.click()} className="btn-outline w-full justify-center" disabled={busy}>
          <Download className="w-4 h-4" /> {L.choose}
        </button>

        {rows.length > 1 && (
          <button onClick={fillGuidedOrder} className="btn-text w-full justify-center" disabled={busy}>
            <ListOrdered className="w-4 h-4" /> {L.guidedOrder}
          </button>
        )}

        {rows.length > 0 && (
          <ul className="space-y-2">
            {rows.map((r) => (
              <li key={r.key} className="p-3 rounded-xl border" style={{ borderColor: "var(--brand-border)", background: "var(--brand-surface)" }}>
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-bold truncate" style={{ color: "var(--brand-text)" }}>{r.file.name}</p>
                  <span className="text-xs flex-shrink-0" style={{ color: "var(--brand-muted-foreground)" }}>
                    {r.isWav ? `${r.seconds}${L.seconds}` : L.notWav}
                  </span>
                </div>
                {r.isWav && (
                  <div className="flex items-center gap-2 mt-2">
                    <select
                      aria-label={L.site}
                      value={r.site}
                      onChange={(e) => setSite(r.key, e.target.value)}
                      disabled={busy || r.status === "done"}
                      className="flex-1 p-2 rounded-lg border text-sm"
                      style={{ background: "var(--brand-surface)", borderColor: "var(--brand-border)", color: "var(--brand-text)" }}
                    >
                      <option value="">{L.pickSite}</option>
                      <optgroup label={L.lung}>
                        {FULL_SITES.filter((s) => getSiteMode(s) === "lung").map((s) => <option key={s} value={s}>{t(`loc.${s}`)}</option>)}
                      </optgroup>
                      <optgroup label={L.heart}>
                        {FULL_SITES.filter((s) => getSiteMode(s) === "heart").map((s) => <option key={s} value={s}>{t(`loc.${s}`)}</option>)}
                      </optgroup>
                    </select>
                    {r.status === "done" && <Check className="w-5 h-5" style={{ color: "var(--brand-success)" }} aria-label={L.uploaded} />}
                    {r.status === "uploading" && <Loader2 className="w-5 h-5 animate-spin" style={{ color: "var(--brand-primary)" }} aria-label={L.uploading} />}
                    {r.status === "failed" && <AlertCircle className="w-5 h-5" style={{ color: "var(--brand-destructive)" }} />}
                    {(r.status === "ready" || r.status === "failed") && !busy && (
                      <button onClick={() => remove(r.key)} className="btn-text is-sm" aria-label={L.remove}>
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}

        {message && <p className="text-sm font-semibold" style={{ color: "var(--brand-destructive)" }}>{message}</p>}

        {pending.length > 0 && (
          <button onClick={uploadAll} disabled={busy} className="btn-primary w-full justify-center">
            {busy ? <><Loader2 className="w-4 h-4 animate-spin" /> {L.uploading}</> : <><Upload className="w-4 h-4" /> {L.upload(pending.length)}</>}
          </button>
        )}

        {allDone && (
          <div className="space-y-3">
            <p className="text-sm font-semibold flex items-center gap-1.5" style={{ color: "var(--brand-success)" }}>
              <Check className="w-4 h-4" /> {L.allDone}
            </p>
            {groupId && <Link to={`/patient/exam/${groupId}`} className="btn-primary w-full justify-center">{L.toExam}</Link>}
            <Link to="/patient/history" className="btn-text w-full justify-center">{L.toHistory}</Link>
          </div>
        )}
      </Step>

      <Disclaimer text={L.note} />
    </div>
  );
}
