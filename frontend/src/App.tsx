import { FormEvent, useState } from "react";

type Source = { title: string; url: string; quote?: string | null };
type ClaimResponse = { answer: string; sources: Source[]; draft_letter: string };

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const EXAMPLES = [
  {
    label: "Myöhästynyt lento",
    text: "Lentoni saapui määränpäähän neljä tuntia myöhässä. Lentoyhtiö ei ole vastannut korvauspyyntööni.",
  },
  {
    label: "Viallinen tuote",
    text: "Ostin kuulokkeet kaksi kuukautta sitten, ja niiden vasen kuuloke lakkasi toimimasta. Myyjä ei suostu korjaamaan tuotetta.",
  },
  {
    label: "Virheellinen lasku",
    text: "Sain laskun palvelusta, jonka olen jo irtisanonut. Yritys ei ole korjannut laskua yhteydenotostani huolimatta.",
  },
];

export default function App() {
  const [description, setDescription] = useState("");
  const [result, setResult] = useState<ClaimResponse | null>(null);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copyStatus, setCopyStatus] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    setDraft("");
    setCopyStatus("");

    try {
      const response = await fetch(`${API_URL}/claim`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: description.trim() }),
      });
      if (!response.ok) throw new Error("Pyyntö epäonnistui. Yritä hetken kuluttua uudelleen.");

      const claim = (await response.json()) as ClaimResponse;
      setResult(claim);
      setDraft(claim.draft_letter);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Palvelimeen ei saatu yhteyttä.");
    } finally {
      setLoading(false);
    }
  }

  async function copyDraft() {
    try {
      await navigator.clipboard.writeText(draft);
      setCopyStatus("Luonnos kopioitu leikepöydälle.");
    } catch {
      setCopyStatus("Kopiointi ei onnistunut. Voit valita ja kopioida tekstin itse.");
    }
  }

  function useExample(text: string) {
    setDescription(text);
    setError("");
  }

  return (
    <main className="shell" id="top">
      <header className="topbar">
        <a className="wordmark" href="#top" aria-label="Reklama, etusivu">reklama<span>.</span></a>
        <span className="topnote">KULUTTAJAN PUOLELLA</span>
      </header>

      <section className="hero">
        <p className="eyebrow">OIKEUTESI, SELVÄKSI</p>
        <h1>Sinulle kuuluu se,<br />mitä sinulle luvattiin.</h1>
        <p className="intro">Kerro, mitä tapahtui. Selvitämme, mihin sinulla voi olla oikeus, ja valmistelemme viestin yritykselle.</p>
      </section>

      <form className="claim-form" onSubmit={submit}>
        <div className="form-heading">
          <label htmlFor="description">Mitä tapahtui?</label>
          <span className="form-step">01 <span>/ 02</span></span>
        </div>
        <textarea
          id="description"
          required
          minLength={1}
          rows={5}
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="Kuvaile tilannetta omin sanoin. Mitä tapahtui ja milloin?"
          aria-describedby="description-hint"
        />
        <div className="examples" aria-label="Esimerkkejä tilanteista">
          <span className="examples-label">Kokeile esimerkkiä</span>
          <div className="example-list">
            {EXAMPLES.map((example) => (
              <button className="example-chip" key={example.label} type="button" onClick={() => useExample(example.text)}>
                {example.label}<span aria-hidden="true"> ↗</span>
              </button>
            ))}
          </div>
        </div>
        <div className="form-footer">
          <span id="description-hint">Kuvaile omin sanoin, voit jättää henkilötiedot pois.</span>
          <button className="primary-button" type="submit" disabled={loading || !description.trim()}>
            {loading ? <><span className="spinner" aria-hidden="true" /> Selvitetään…</> : <>Selvitä oikeuteni <span aria-hidden="true">↗</span></>}
          </button>
        </div>
      </form>

      {error && <p className="error" role="alert">{error}</p>}
      {loading && <p className="loading-note" role="status">Käymme tilannettasi läpi. Tämä voi kestää hetken.</p>}

      {result && <section className="results" aria-live="polite">
        <div className="result-heading">
          <div><p className="eyebrow">SELVITYS VALMIS</p><h2>Tilanteesi ja seuraavat askeleet</h2></div>
          <span className="form-step">02 <span>/ 02</span></span>
        </div>
        <div className="result-card answer-card">
          <p className="section-label">ARVIO</p>
          <p className="answer">{result.answer}</p>
        </div>
        <div className="result-card">
          <p className="section-label">LÄHTEET</p>
          {result.sources.length > 0 ? <ul className="sources">
            {result.sources.map((source) => <li key={source.url}>
              <a href={source.url} target="_blank" rel="noreferrer">{source.title}<span aria-hidden="true"> ↗</span></a>
              {source.quote && <p>{source.quote}</p>}
            </li>)}
          </ul> : <p className="empty-sources">Tähän selvitykseen ei löytynyt lähteitä.</p>}
        </div>
        <div className="result-card draft-card">
          <div className="draft-heading">
            <div><p className="section-label">VIESTILUONNOS</p><h2>Tarkista ja muokkaa</h2></div>
            <span className="editable-tag"><span aria-hidden="true">✎</span> Muokattavissa</span>
          </div>
          <p className="draft-hint">Muokkaa viestiä tilanteeseesi sopivaksi ennen kuin lähetät sen.</p>
          <textarea className="draft" aria-label="Muokattava viestiluonnos" rows={10} value={draft} onChange={(event) => { setDraft(event.target.value); setCopyStatus(""); }} />
          <div className="draft-footer">
            <p className="draft-safety">Reklama ei lähetä viestiä puolestasi.</p>
            <button className="secondary-button" type="button" onClick={copyDraft} disabled={!draft.trim()}>
              <span aria-hidden="true">▢</span> Kopioi luonnos
            </button>
          </div>
          {copyStatus && <p className="copy-status" role="status">{copyStatus}</p>}
        </div>
      </section>}

      <footer>
        <p className="legal">Tämä palvelu ei anna oikeudellista neuvontaa. Tarkista tiedot ja luonnos ennen kuin toimit.</p>
        <span>REKLAMA · SINUN PUOLELLASI</span>
      </footer>
    </main>
  );
}
