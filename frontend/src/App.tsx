import { FormEvent, useEffect, useRef, useState } from "react";

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
const LANGUAGE_KEY = "language";
const THEME_KEY = "theme";

type Language = "fi" | "en";
type Theme = "light" | "dark";

const copy = {
  fi: {
    about: "Tietoja", aboutTitle: "WorkHunter", aboutText: "Työpaikkahaku kysyy yleensä ammattinimikettä. Entä jos et tiedä oikeaa nimikettä? Ehkä tiedät vain vahvuutesi ja toiveesi. Niillä tavallinen haku ei löydä mitään.\n\nWorkHunter toimii toisin. Kerro toiveesi omin sanoin. Esimerkiksi: “Olen hyvä Excelissä ja viihdyn ihmisten parissa. Myyntityö ei kiinnosta.” Saat vastaukseksi juuri nyt avoinna olevia työpaikkoja. Joukossa on usein yllättäviäkin nimikkeitä.\n\nHaku perustuu Exaan, tekoälyä varten rakennettuun hakukoneeseen.", close: "Sulje",
    darkMode: "Tumma tila", lightMode: "Vaalea tila", headline: "Työpaikkahaku",
    area: "Hakukohde", areaPlaceholder: "Kaupunki tai alue", wishLabel: "Kerro osaamisestasi ja toiveistasi",
    wishPlaceholder: "Esim. taidot, työajat tai mitä haluat välttää",
    privacy: "Älä lisää henkilötietoja.", search: "Etsi työpaikkoja", searching: "Haetaan…", suggestions: "Työpaikat",
    noResults: "Ei uusia ilmoituksia.", deadline: "Haku päättyy",
    why: "Miksi sinulle:", saved: "Tallennettu", save: "Tallenna", feedbackLabel: "Mitä haluat muuttaa haussa?",
    feedbackPlaceholder: "Tarkenna hakua (valinnainen)", next: "Näytä kolme uutta",
    savedTitle: "Tallennetut työpaikat", emptySaved: "Ei tallennettuja työpaikkoja.", remove: "Poista",
    legal: "Tarkista tiedot ja hakuajat aina alkuperäisestä ilmoituksesta. WorkHunter ei hae työpaikkoja puolestasi.",
    connectionError: "Palvelimeen ei saatu yhteyttä.", searchError: "Haku epäonnistui. Yritä hetken kuluttua uudelleen.",
  },
  en: {
    about: "About", aboutTitle: "WorkHunter", aboutText: "Job searches usually ask for a job title. But what if you don’t know the right title? Maybe you only know your strengths and what you want. A regular search won’t find much with that.\n\nWorkHunter works differently. Describe what you want in your own words. For example: “I’m good with Excel and enjoy working with people. I’m not interested in sales.” You’ll get jobs that are open right now. Some may have unexpected titles.\n\nThe search is powered by Exa, a search engine built for AI.", close: "Close",
    darkMode: "Dark mode", lightMode: "Light mode", headline: "Job search",
    area: "Location", areaPlaceholder: "City or region", wishLabel: "Tell us about your skills and preferences",
    wishPlaceholder: "E.g. skills, hours, or what you want to avoid",
    privacy: "Don’t include personal information.", search: "Find jobs", searching: "Searching…", suggestions: "Jobs",
    noResults: "No new listings.", deadline: "Apply by",
    why: "Why it may suit you:", saved: "Saved", save: "Save", feedbackLabel: "What would you change?",
    feedbackPlaceholder: "Refine your search (optional)", next: "Show three more",
    savedTitle: "Saved jobs", emptySaved: "No saved jobs.", remove: "Remove",
    legal: "Check details and deadlines on the original listing. WorkHunter never applies for jobs on your behalf.",
    connectionError: "Could not connect to the server.", searchError: "Search failed. Please try again in a moment.",
  },
} as const;

function preference<T extends string>(key: string, allowed: readonly T[], fallback: T): T {
  try {
    const value = localStorage.getItem(key);
    return allowed.includes(value as T) ? value as T : fallback;
  } catch {
    return fallback;
  }
}

function inputLanguage(text: string, fallback: Language): Language {
  const normalized = text.toLocaleLowerCase();
  if (/[äöå]/.test(normalized)) return "fi";
  const english = (normalized.match(/\b(i|the|and|with|want|looking|for|my|not|good|experience|remote|work|job|years|can|prefer|no|enjoy)\b/g) ?? []).length;
  const finnish = (normalized.match(/\b(olen|hyvä|haluan|etsin|työ|työtä|tyopaikka|osaaminen|kokemus|etä|enkä|en|ei|ihmisten|vuoro|myynti)\b/g) ?? []).length;
  if (english > finnish) return "en";
  if (finnish > english) return "fi";
  return fallback;
}

function loadSaved(): Job[] {
  try {
    return JSON.parse(localStorage.getItem(SAVED_KEY) ?? "[]") as Job[];
  } catch {
    return [];
  }
}

async function post(path: string, body: unknown, errorMessage: string): Promise<Job[]> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(errorMessage);
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
  const [aboutOpen, setAboutOpen] = useState(false);
  const [language, setLanguage] = useState<Language>(() => preference(LANGUAGE_KEY, ["fi", "en"], "fi"));
  const [theme, setTheme] = useState<Theme>(() => preference(THEME_KEY, ["light", "dark"], "light"));
  const firstJobRef = useRef<HTMLElement>(null);
  const t = copy[language];

  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", theme === "dark" ? "#131313" : "#EFEBE4");
    document.title = language === "fi" ? "WorkHunter — Työpaikkahaku" : "WorkHunter — Job search";
    try {
      localStorage.setItem(LANGUAGE_KEY, language);
      localStorage.setItem(THEME_KEY, theme);
    } catch {
      /* preferences still apply for this tab */
    }
  }, [language, theme]);

  useEffect(() => {
    try {
      localStorage.setItem(SAVED_KEY, JSON.stringify(saved));
    } catch {
      /* storage unavailable: saved list lives only in this tab */
    }
  }, [saved]);

  useEffect(() => {
    if (!searched || loading || shown.length === 0) return;
    const behavior = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
    firstJobRef.current?.scrollIntoView({ behavior, block: "center" });
  }, [searched, loading, shown]);

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
      setError(cause instanceof Error ? cause.message : t.connectionError);
    } finally {
      setLoading(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFeedback("");
    const responseLanguage = inputLanguage(wish, language);
    run(() => post("/jobs/search", { area, wish: wish.trim(), response_language: responseLanguage, ...skipList([]) }, t.searchError), []);
  }

  function nextThree() {
    // Feedback means the user wants a different direction: ask Exa again.
    if (queue.length > 0 && !feedback.trim()) {
      showFrom(queue, seen);
      return;
    }
    const note = feedback.trim() || null;
    setFeedback("");
    const responseLanguage = inputLanguage(wish, language);
    run(() => post("/jobs/search", { area, wish: wish.trim(), response_language: responseLanguage, ...skipList(seen), feedback: note }, t.searchError), seen);
  }

  const isSaved = (job: Job) => saved.some((item) => item.url === job.url);
  const toggleSave = (job: Job) =>
    setSaved((items) => (isSaved(job) ? items.filter((item) => item.url !== job.url) : [job, ...items]));

  return (
    <div className="shell" id="top">
      <header className="topbar">
        <a className="wordmark" href="#top">WorkHunter</a>
        <div className="header-tools">
          <div className="language-switch" role="group" aria-label={language === "fi" ? "Kieli" : "Language"}>
            <button type="button" aria-pressed={language === "fi"} onClick={() => setLanguage("fi")}>FI</button>
            <button type="button" aria-pressed={language === "en"} onClick={() => setLanguage("en")}>EN</button>
          </div>
          <button className="text-button" type="button" onClick={() => setAboutOpen(true)}>{t.about}</button>
          <button className="theme-button" type="button" aria-pressed={theme === "dark"}
            aria-label={theme === "dark" ? t.lightMode : t.darkMode}
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
            <span aria-hidden="true">{theme === "dark" ? "☼" : "◐"}</span>
            {theme === "dark" ? t.lightMode : t.darkMode}
          </button>
        </div>
      </header>

      {aboutOpen && (
        <div className="modal-backdrop" role="presentation" onMouseDown={(event) => {
          if (event.target === event.currentTarget) setAboutOpen(false);
        }}>
          <section className="about-dialog" role="dialog" aria-modal="true" aria-labelledby="about-title">
            <button className="close-button" type="button" aria-label={t.close} onClick={() => setAboutOpen(false)}>×</button>
            <h2 id="about-title">{t.aboutTitle}</h2>
            <p>{t.aboutText}</p>
          </section>
        </div>
      )}

      <main className="main-content">
        <section className="search-panel" aria-labelledby="search-title">
          <h1 id="search-title">{t.headline}</h1>
          <form className="search-form" id="search" onSubmit={submit}>
            <label htmlFor="area">{t.area}</label>
            <input id="area" value={area} onChange={(e) => setArea(e.target.value)} placeholder={t.areaPlaceholder} />
            <label htmlFor="wish">{t.wishLabel}</label>
            <textarea id="wish" required rows={4} value={wish} onChange={(e) => setWish(e.target.value)}
              placeholder={t.wishPlaceholder} />
            <div className="form-footer">
              <span>{t.privacy}</span>
              <button className="primary-button" type="submit" disabled={loading || !wish.trim()}>
                {loading ? <><span className="spinner" aria-hidden="true" /> {t.searching}</> : t.search}
              </button>
            </div>
          </form>
        </section>

        {error && <p className="error" role="alert">{error}</p>}
        {searched && !loading && (
          <section className="results" aria-live="polite">
            <div className="results-heading">
              <h2>{t.suggestions}</h2>
              <span>{shown.length}</span>
            </div>
            {shown.length === 0 && <p className="empty">{t.noResults}</p>}
            {shown.length > 0 && (
              <div className="results-list" tabIndex={0} aria-label={t.suggestions}>
              {shown.map((job, index) => (
                <article className="job-card" key={job.url} ref={index === 0 ? firstJobRef : undefined}>
                  <div className="job-head">
                    <div>
                      <h2><a href={job.url} target="_blank" rel="noreferrer">{job.title}<span aria-hidden="true"> ↗</span></a></h2>
                      <p className="job-meta">{[job.employer, job.location].filter(Boolean).join(" · ")}</p>
                    </div>
                    {job.deadline && <span className="deadline">{t.deadline} {job.deadline}</span>}
                  </div>
                  {job.summary && <p className="job-summary">{job.summary}</p>}
                  {job.why && <p className="job-why"><strong>{t.why}</strong> {job.why}</p>}
                  <div className="job-actions">
                    <button className="secondary-button" type="button" onClick={() => toggleSave(job)}>
                      {isSaved(job) ? `✓ ${t.saved}` : `☆ ${t.save}`}
                    </button>
                  </div>
                </article>
              ))}
              </div>
            )}
            <div className="next-box">
              <input aria-label={t.feedbackLabel} value={feedback} onChange={(e) => setFeedback(e.target.value)}
                placeholder={t.feedbackPlaceholder} />
              <button className="primary-button" type="button" onClick={nextThree}>{t.next}</button>
            </div>
          </section>
        )}
      </main>

      <footer className="footer" id="saved">
        <section className="saved-section" aria-labelledby="saved-title">
          <div className="saved-heading">
            <h2 id="saved-title">{t.savedTitle}</h2>
            <span>{saved.length}</span>
          </div>
          {saved.length === 0 ? <p className="empty saved-empty">{t.emptySaved}</p> : (
            <div className="saved-list" tabIndex={0} aria-label={t.savedTitle}>
              {saved.map((job) => (
                <article className="saved-card" key={job.url}>
                  <a href={job.url} target="_blank" rel="noreferrer">{job.title}</a>
                  <p>{[job.employer, job.location, job.deadline && `${t.deadline} ${job.deadline}`].filter(Boolean).join(" · ")}</p>
                  <button className="remove-button" type="button" aria-label={`${t.remove} ${job.title}`} onClick={() => toggleSave(job)}>×</button>
                </article>
              ))}
            </div>
          )}
        </section>
        <p className="legal">{t.legal}</p>
      </footer>
    </div>
  );
}
