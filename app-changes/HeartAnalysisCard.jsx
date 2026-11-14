import React, { useCallback, useEffect, useState } from "react";
import { base44 } from "@/api/base44Client";
import { useLanguage } from "@/lib/i18n";
import { hasAudio, resolveAudioSrc } from "@/lib/audioSource";
import { analyzeHeart } from "@/lib/heartAnalyzer";
import InferenceLoader from "@/components/brand/InferenceLoader";
import { HeartPulse, Activity, AlertTriangle, CheckCircle2, RotateCcw, Loader2 } from "lucide-react";

// Heart-sound analysis for one heart recording: estimated heart rate and a murmur screening flag, from the
// Resondi heart models v1 (src/lib/heartAnalyzer.js). Saved as a HeartAnalysis record, kept apart from
// AIAnalysis so the lung charts, trends and severity code never read a heart result.
// Text is kept here in English and Filipino so no shared translation file has to change.

const TEXT = {
  en: {
    title: "Heart-sound analysis",
    run: "Analyse heart sound",
    rerun: "Run again",
    pending: "Estimates the heart rate and checks for a possible murmur. A practitioner reviews every result.",
    rate: "Estimated heart rate",
    bpm: "BPM",
    noRate: "Could not find a regular heartbeat in this recording. Try recording again with firmer contact.",
    murmur: "Murmur screening",
    flag: "Possible murmur: a practitioner should listen to this recording.",
    noFlag: "No murmur flagged. This does not rule out a murmur.",
    beats: (n, s) => `${n} first heart sounds found in ${s} s`,
    note:
      "Screening aid, not a diagnosis. The heart models were tested on public recordings of children (CirCor), " +
      "not yet on Resondi device recordings. They miss about 1 in 3 murmurs.",
    noAudio: "This recording has no audio file to analyse.",
    compactPending: "Heart-sound analysis not run yet",
  },
  fil: {
    title: "Pagsusuri ng tunog ng puso",
    run: "Suriin ang tunog ng puso",
    rerun: "Patakbuhin muli",
    pending: "Tinataya ang heart rate at sinusuri kung may posibleng murmur. Sinusuri ng praktisyuner ang bawat resulta.",
    rate: "Tinatayang heart rate",
    bpm: "BPM",
    noRate: "Walang nakitang regular na tibok ng puso sa rekording na ito. Subukang mag-record muli nang mas mahigpit ang dikit.",
    murmur: "Pagsusuri sa murmur",
    flag: "Posibleng murmur: dapat itong pakinggan ng isang praktisyuner.",
    noFlag: "Walang na-flag na murmur. Hindi ito nangangahulugang walang murmur.",
    beats: (n, s) => `${n} unang tunog ng puso ang nakita sa ${s} s`,
    note:
      "Tulong sa screening, hindi diagnosis. Sinubok ang mga heart model sa pampublikong rekording ng mga bata " +
      "(CirCor), hindi pa sa mga rekording ng Resondi device. Nakakaligtaan nila ang humigit-kumulang 1 sa 3 murmur.",
    noAudio: "Walang audio file ang rekording na ito para suriin.",
    compactPending: "Hindi pa nasusuri ang tunog ng puso",
  },
};

export default function HeartAnalysisCard({ session, compact = false, canRun = true }) {
  const { lang } = useLanguage();
  const L = TEXT[lang] || TEXT.en;
  const [result, setResult] = useState(null);
  const [loaded, setLoaded] = useState(false);
  const [running, setRunning] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    if (!session?.id) return;
    try {
      const found = await base44.entities.HeartAnalysis.filter({ session_id: session.id }, "-created_date", 1);
      setResult(found[0] || null);
    } catch (e) {
      setResult(null);
    } finally {
      setLoaded(true);
    }
  }, [session?.id]);

  useEffect(() => { load(); }, [load]);

  const run = async () => {
    if (!hasAudio(session)) { setError(L.noAudio); return; }
    setRunning(true);
    setStatus("loading");
    setError("");
    try {
      const url = await resolveAudioSrc(session);
      if (!url) throw new Error(L.noAudio);
      const r = await analyzeHeart(url, setStatus);
      const previous = await base44.entities.HeartAnalysis.filter({ session_id: session.id }, "-created_date", 20);
      await base44.entities.HeartAnalysis.create({
        session_id: session.id,
        // Carries the session's reviewers, so a practitioner who already has the case can read it.
        practitioner_ids: Array.isArray(session.practitioner_ids) ? session.practitioner_ids : [],
        heart_rate_bpm: r.heartRate ?? undefined,
        beats_detected: r.beats,
        murmur_score: Math.round(r.murmurScore * 1000) / 1000,
        murmur_flag: r.murmurFlag,
        seconds_analyzed: r.seconds,
        model_version: r.modelVersion,
        generated_at: new Date().toISOString(),
      });
      for (const p of previous) {
        try { await base44.entities.HeartAnalysis.delete(p.id); } catch (e) { /* not the owner: keep it */ }
      }
      await load();
    } catch (e) {
      setError(e?.message || "Error");
    } finally {
      setRunning(false);
      setStatus("");
    }
  };

  if (!loaded) return null;

  if (compact) {
    return (
      <div className="flex flex-wrap items-center gap-2 p-2.5 rounded-lg" style={{ background: "var(--brand-muted)" }}>
        <HeartPulse className="w-4 h-4 flex-shrink-0" style={{ color: "var(--brand-primary)" }} strokeWidth={1.8} />
        {result ? (
          <>
            <span className="text-sm font-bold flex-1 min-w-0" style={{ color: "var(--brand-text)" }}>
              {result.heart_rate_bpm ? `${result.heart_rate_bpm} ${L.bpm}` : "—"}
            </span>
            <span className="text-xs font-bold flex-shrink-0" style={{ color: result.murmur_flag ? "var(--brand-destructive)" : "var(--brand-secondary)" }}>
              {result.murmur_flag ? L.flag.split(":")[0] : L.noFlag.split(".")[0]}
            </span>
          </>
        ) : running ? (
          <span className="text-xs flex-1 inline-flex items-center gap-1.5" style={{ color: "var(--brand-secondary)" }}>
            <Loader2 className="w-3.5 h-3.5 animate-spin" /> {L.title}
          </span>
        ) : (
          <>
            <span className="text-xs italic flex-1" style={{ color: "var(--brand-muted-foreground)" }}>{L.compactPending}</span>
            {canRun && hasAudio(session) && (
              <button onClick={run} className="btn-outline is-sm">
                <HeartPulse className="w-3.5 h-3.5" /> {L.run}
              </button>
            )}
          </>
        )}
        {error && !running && <p className="w-full text-xs font-semibold" role="alert" style={{ color: "var(--brand-destructive)" }}>{error}</p>}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {running ? (
        <InferenceLoader status={status} error={error} />
      ) : result ? (
        <div className="space-y-3 fade-in">
          <div className="p-3 rounded-xl" style={{ background: "var(--brand-muted)" }}>
            <p className="text-xs font-bold uppercase mb-1" style={{ color: "var(--brand-muted-foreground)" }}>{L.rate}</p>
            {result.heart_rate_bpm ? (
              <p className="text-2xl font-extrabold" style={{ color: "var(--brand-text)" }}>
                {result.heart_rate_bpm} <span className="text-sm font-bold">{L.bpm}</span>
              </p>
            ) : (
              <p className="text-sm" style={{ color: "var(--brand-secondary)" }}>{L.noRate}</p>
            )}
            {typeof result.beats_detected === "number" && result.seconds_analyzed > 0 && (
              <p className="text-xs mt-1" style={{ color: "var(--brand-muted-foreground)" }}>{L.beats(result.beats_detected, result.seconds_analyzed)}</p>
            )}
          </div>
          <div className="p-3 rounded-xl flex items-start gap-2" style={{ background: result.murmur_flag ? "rgba(216,70,43,.08)" : "var(--brand-muted)" }}>
            {result.murmur_flag
              ? <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: "var(--brand-destructive)" }} />
              : <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: "var(--brand-secondary)" }} />}
            <div>
              <p className="text-xs font-bold uppercase mb-0.5" style={{ color: "var(--brand-muted-foreground)" }}>{L.murmur}</p>
              <p className="text-sm font-semibold" style={{ color: "var(--brand-text)" }}>{result.murmur_flag ? L.flag : L.noFlag}</p>
            </div>
          </div>
          <p className="text-xs leading-relaxed" style={{ color: "var(--brand-muted-foreground)" }}>{L.note}</p>
          {canRun && (
            <button onClick={run} className="btn-outline">
              <RotateCcw className="w-4 h-4" /> {L.rerun}
            </button>
          )}
        </div>
      ) : (
        <div className="text-center py-4">
          <p className="text-sm mb-1" style={{ color: "var(--brand-secondary)" }}>{L.pending}</p>
          <p className="text-xs mb-4" style={{ color: "var(--brand-muted-foreground)" }}>{L.note}</p>
          {canRun ? (
            <button onClick={run} className="btn-primary">
              <Activity className="w-4 h-4" /> {L.run}
            </button>
          ) : null}
        </div>
      )}
      {error && !running && (
        <p className="text-xs font-semibold text-center" role="alert" style={{ color: "var(--brand-destructive)" }}>{error}</p>
      )}
    </div>
  );
}
