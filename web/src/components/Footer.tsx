import { FOOTER_LINKS } from "@/lib/links";

/**
 * フッタ(F-12)。リンク列は画面下端に固定してスクロールに追従させる。
 * 出典とライセンスの記載(N-05)は行数が可変なので固定バーには載せず、
 * 本文の流れの末尾に置いて常設する。
 */
export default function Footer({
  sources,
  jis,
}: {
  sources?: Record<string, { title: string; url: string; license: string }>;
  jis?: { name: string; url: string; note: string };
}) {
  return (
    <>
      <footer className="foot">
        {sources ? (
          <p>
            色票の出典:{" "}
            {Object.values(sources).map((s, i) => (
              <span key={s.url}>
                {i > 0 ? " / " : ""}
                <a href={s.url}>{s.title}</a>（{s.license}）
              </span>
            ))}
            。両出典とも HEX の典拠を示していない。
            {jis ? ` ${jis.name}: ${jis.note}` : ""}
          </p>
        ) : null}
      </footer>
      <nav className="foot-bar" aria-label="サイト内リンク">
        <ul>
          {FOOTER_LINKS.map((l) => (
            <li key={l.label}>
              <a href={l.href}>{l.label}</a>
            </li>
          ))}
        </ul>
        <span className="lic">色票データ CC BY-SA 4.0 ／ コード MIT</span>
      </nav>
    </>
  );
}
