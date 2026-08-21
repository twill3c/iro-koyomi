import { FOOTER_LINKS } from "@/lib/links";

export default function Footer({
  sources,
  jis,
}: {
  sources?: Record<string, { title: string; url: string; license: string }>;
  jis?: { name: string; url: string; note: string };
}) {
  return (
    <footer className="foot">
      <ul>
        {FOOTER_LINKS.map((l) => (
          <li key={l.label}>
            <a href={l.href}>{l.label}</a>
          </li>
        ))}
      </ul>
      {sources ? (
        <p>
          色票の出典:{" "}
          {Object.values(sources).map((s, i) => (
            <span key={s.url}>
              {i > 0 ? " / " : ""}
              <a href={s.url}>{s.title}</a>（{s.license}）
            </span>
          ))}
          。両出典とも HEX の典拠を示していない。色票データは CC BY-SA 4.0、コードは MIT。
          {jis ? ` ${jis.name}: ${jis.note}` : ""}
        </p>
      ) : null}
    </footer>
  );
}
