import { FormEvent, useEffect, useState } from "react";

// Mirrors backend/app/schemas.py
type Job = {
  title: string;
  employer?: string | null;
  location?: string | null;
  url: string;
  deadline?: string | null;
  summary: string;
  why?: string | null;
};
type JobSearchResponse = { jobs: Job[] };

// Dev talks to the local backend; the production build calls the same origin that served it.
const API_URL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? "http://localhost:8000" : "");
const PAGE_SIZE = 3;
const SAVED_KEY = "saved-jobs";

const EXAMPLES = [
  { label: "Excel ja ihmiset", area: "Tampere tai etä", wish: "Olen hyvä Excelissä ja tulen toimeen ihmisten kanssa, mutta en halua myyntityötä." },
  { label: "Junior-koodari", area: "Helsinki", wish: "Vastavalmistunut ohjelmistokehittäjä, Python ja React, haluan junioripaikan." },
  { label: "Pois vuorotyöstä", area: "Turku", wish: "Sairaanhoitaja, haluan pois vuorotyöstä. Päivätyö kelpaa vaikka toimistossa." },
];

function loadSaved(): Job[] {
  try {
    return JSON.parse(localStorage.getItem(SAVED_KEY) ?? "[]") as Job[];
  } catch {
    return [];
  }
}

async function post(path: string, body: unknown): Promise<Job[]> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error("Haku epäonnistui. Yritä hetken kuluttua uudelleen.");
  return ((await response.json()) as JobSearchResponse).jobs;
}

export default function App() {
  const [area, setArea] = useState("");
  const [wish, setWish] = useState("");
  const [feedback, setFeedback] = useState("");
  const [shown, setShown] = useState<Job[]>([]);
  const [queue, setQueue] = useState<Job[]>([]);
  const [seen, setSeen] = useState<Job[]>([]); // every job shown so far
  const [saved, setSaved] = useState<Job[]>(loadSaved);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    try {
      localStorage.setItem(SAVED_KEY, JSON.stringify(saved));
    } catch {
      /* storage unavailable: saved list lives only in this tab */
    }
  }, [saved]);

  function showFrom(jobs: Job[], alreadySeen: Job[]) {
    const fresh = jobs.filter((job) => !alreadySeen.some((old) => old.url === job.url));
    const page = fresh.slice(0, PAGE_SIZE);
    setShown(page);
    setQueue(fresh.slice(PAGE_SIZE));
    setSeen([...alreadySeen, ...page]);
  }

  // The backend skips these URLs and the same positions posted on other sites.
  function skipList(alreadySeen: Job[]) {
    return {
      exclude_urls: alreadySeen.map((job) => job.url),
      seen_jobs: alreadySeen.map((job) => ({ title: job.title, employer: job.employer ?? null })),
    };
  }

  async function run(load: () => Promise<Job[]>, alreadySeen: Job[]) {
    setLoading(true);
    setError("");
    try {
      showFrom(await load(), alreadySeen);
      setSearched(true);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Palvelimeen ei saatu yhteyttä.");
    } finally {
      setLoading(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFeedback("");
    run(() => post("/jobs/search", { area, wish: wish.trim(), ...skipList([]) }), []);
  }

  function nextThree() {
    // Feedback means the user wants a different direction: ask Exa again.
    if (queue.length > 0 && !feedback.trim()) {
      showFrom(queue, seen);
      return;
    }
    const note = feedback.trim() || null;
    setFeedback("");
    run(() => post("/jobs/search", { area, wish: wish.trim(), ...skipList(seen), feedback: note }), seen);
  }

  const isSaved = (job: Job) => saved.some((item) => item.url === job.url);
  const toggleSave = (job: Job) =>
    setSaved((items) => (isSaved(job) ? items.filter((item) => item.url !== job.url) : [job, ...items]));

  return (
    <div className="shell" id="top">
      <header className="topbar">
        <a className="wordmark" href="#top" aria-label="Etusivu">paikka<span>.</span></a>
        <span className="topnote">TUORE TYÖPAIKKAHAKU</span>
      </header>

      <div className="layout">
        <main>
          <section className="hero">
            <p className="eyebrow">KERRO OMIN SANOIN</p>
            <h1>Löydä työ, jota et<br />osannut hakea.</h1>
            <p className="intro">Kuvaile, missä olet hyvä ja millaista työtä haluat. Haemme juuri nyt avoinna olevia ilmoituksia koko verkosta, myös yritysten omilta rekrysivuilta.</p>
          </section>

          <form className="search-form" onSubmit={submit}>
            <label htmlFor="area">Alue</label>
            <input id="area" value={area} onChange={(e) => setArea(e.target.value)} placeholder="Esim. Tampere, Uusimaa tai etä" />
            <label htmlFor="wish">Mitä toivot työltä?</label>
            <textarea id="wish" required rows={4} value={wish} onChange={(e) => setWish(e.target.value)}
              placeholder="Esim. olen hyvä Excelissä ja ihmisten kanssa, en halua myyntityötä." />
            <div className="examples" aria-label="Esimerkkejä">
              <span className="examples-label">Kokeile esimerkkiä</span>
              <div className="example-list">
                {EXAMPLES.map((example) => (
                  <button className="example-chip" key={example.label} type="button"
                    onClick={() => { setArea(example.area); setWish(example.wish); }}>
                    {example.label}<span aria-hidden="true"> ↗</span>
                  </button>
                ))}
              </div>
            </div>
            <div className="form-footer">
              <span>Älä kirjoita henkilötietoja.</span>
              <button className="primary-button" type="submit" disabled={loading || !wish.trim()}>
                {loading ? <><span className="spinner" aria-hidden="true" /> Haetaan…</> : <>Hae työpaikkoja <span aria-hidden="true">↗</span></>}
              </button>
            </div>
          </form>

          {error && <p className="error" role="alert">{error}</p>}
          {loading && <p className="loading-note" role="status">Exa käy läpi tuoreita ilmoituksia. Tämä kestää noin 10–20 sekuntia.</p>}

          {searched && !loading && (
            <section className="results" aria-live="polite">
              <p className="eyebrow">EHDOTUKSET</p>
              {shown.length === 0 && <p className="empty">Uusia ilmoituksia ei löytynyt. Kokeile väljempää toivetta tai toista aluetta.</p>}
              {shown.map((job) => (
                <article className="job-card" key={job.url}>
                  <div className="job-head">
                    <div>
                      <h2><a href={job.url} target="_blank" rel="noreferrer">{job.title}<span aria-hidden="true"> ↗</span></a></h2>
                      <p className="job-meta">{[job.employer, job.location].filter(Boolean).join(" · ")}</p>
                    </div>
                    {job.deadline && <span className="deadline">Haku päättyy {job.deadline}</span>}
                  </div>
                  {job.summary && <p className="job-summary">{job.summary}</p>}
                  {job.why && <p className="job-why"><strong>Miksi sinulle:</strong> {job.why}</p>}
                  <div className="job-actions">
                    <button className="secondary-button" type="button" onClick={() => toggleSave(job)}>
                      {isSaved(job) ? "✓ Tallennettu" : "☆ Tallenna"}
                    </button>
                  </div>
                </article>
              ))}
              <div className="next-box">
                <input aria-label="Miksi nämä eivät sopineet?" value={feedback} onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Miksi nämä eivät sopineet? (vapaaehtoinen, esim. liian kaukana)" />
                <button className="primary-button" type="button" onClick={nextThree}>Näytä kolme uutta</button>
              </div>
            </section>
          )}
        </main>

        <aside className="sidebar" aria-label="Tallennetut ilmoitukset">
          <p className="section-label">TALLENNETUT ({saved.length})</p>
          {saved.length === 0 && <p className="empty">Tallenna kiinnostavat ilmoitukset tähän.</p>}
          <ul>
            {saved.map((job) => (
              <li key={job.url}>
                <a href={job.url} target="_blank" rel="noreferrer">{job.title}</a>
                <span>{[job.employer, job.deadline && `päättyy ${job.deadline}`].filter(Boolean).join(" · ")}</span>
                <button type="button" aria-label={`Poista ${job.title}`} onClick={() => toggleSave(job)}>×</button>
              </li>
            ))}
          </ul>
        </aside>
      </div>

      <footer>
        <p className="legal">Ilmoitukset haetaan julkisista lähteistä Exan avulla. Tarkista tiedot ja hakuaika aina alkuperäisestä ilmoituksesta. Palvelu ei hae työpaikkoja puolestasi.</p>
      </footer>
    </div>
  );
}
