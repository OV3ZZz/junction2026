import { FormEvent, useState } from "react";

type Source = { title: string; url: string; quote?: string | null };
type ClaimResponse = { answer: string; sources: Source[]; draft_letter: string };
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function App() {
  const [description, setDescription] = useState("");
  const [result, setResult] = useState<ClaimResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [approved, setApproved] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    setApproved(false);
    try {
      const response = await fetch(`${API_URL}/claim`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description }),
      });
      if (!response.ok) throw new Error("Pyyntö epäonnistui. Yritä uudelleen.");
      setResult((await response.json()) as ClaimResponse);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Palvelimeen ei saatu yhteyttä.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar"><a className="wordmark" href="#top">reklama<span>.</span></a><span className="topnote">KULUTTAJAN PUOLELLA</span></header>
      <section className="hero" id="top">
        <p className="eyebrow">OIKEUTESI, SELVÄKSI</p>
        <h1>Sinulle kuuluu se,<br />mitä sinulle luvattiin.</h1>
        <p className="intro">Kerro, mitä tapahtui. Selvitämme, mihin sinulla voi olla oikeus, ja valmistelemme viestin yritykselle.</p>
      </section>
      <form className="claim-form" onSubmit={submit}>
        <label htmlFor="description">Mitä tapahtui?</label>
        <textarea id="description" required minLength={1} rows={5} value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Esimerkiksi: Lentoni saapui neljä tuntia myöhässä…" />
        <div className="form-footer"><span>Voit kirjoittaa omin sanoin.</span><button type="submit" disabled={loading || !description.trim()}>{loading ? "Selvitetään…" : "Selvitä oikeuteni"}<span aria-hidden="true"> ↗</span></button></div>
      </form>
      {error && <p className="error" role="alert">{error}</p>}
      {result && <section className="results" aria-live="polite">
        <div className="result-block"><p className="eyebrow">ARVIO</p><h2>Mitä tilanteestasi selvisi</h2><p className="answer">{result.answer}</p></div>
        <div className="result-block"><p className="eyebrow">LÄHTEET</p><ul className="sources">{result.sources.map((source) => <li key={source.url}><a href={source.url} target="_blank" rel="noreferrer">{source.title}<span aria-hidden="true"> ↗</span></a>{source.quote && <p>{source.quote}</p>}</li>)}</ul></div>
        <div className="result-block"><p className="eyebrow">LUONNOS</p><h2>Viesti yritykselle</h2><textarea className="draft" aria-label="Valmis viestiluonnos" rows={8} value={result.draft_letter} readOnly /></div>
        <button className="approve" type="button" onClick={() => setApproved(true)}>{approved ? "Luonnos hyväksytty" : "Hyväksy luonnos"}</button>
        {approved && <p className="approval-note">Luonnos on valmis sinun lähetettäväksesi. Reklama ei lähetä viestejä puolestasi.</p>}
      </section>}
      <footer><p className="legal">Tämä palvelu ei anna oikeudellista neuvontaa. Tarkista tiedot ja luonnos ennen kuin toimit.</p><span>REKLAMA · SINUN PUOLELLASI</span></footer>
    </main>
  );
}
