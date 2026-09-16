function tokenize(text: string): string {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function inline(text: string): string {
  let out = tokenize(text);
  out = out.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  out = out.replace(/`([^`]+)`/g, '<code>$1</code>');
  out = out.replace(
    /\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>',
  );
  return out;
}

// Minimal, safe markdown renderer. All input is HTML-escaped before transformation.
export function Markdown({ content }: { content: string }) {
  const blocks = content.split(/\n{2,}/);
  const html = blocks
    .map((block) => {
      const trimmed = block.trim();
      if (trimmed.startsWith('#')) {
        const level = trimmed.match(/^#{1,3}/)?.[0].length ?? 1;
        const rest = trimmed.replace(/^#{1,3}\s*/, '');
        return `<h${level}>${inline(rest)}</h${level}>`;
      }
      if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        const items = trimmed
          .split(/\n/)
          .map((line) => `<li>${inline(line.replace(/^[-*]\s*/, ''))}</li>`)
          .join('');
        return `<ul>${items}</ul>`;
      }
      if (/^\d+\.\s/.test(trimmed)) {
        const items = trimmed
          .split(/\n/)
          .map((line) => `<li>${inline(line.replace(/^\d+\.\s*/, ''))}</li>`)
          .join('');
        return `<ol>${items}</ol>`;
      }
      return `<p>${inline(trimmed.replace(/\n/g, '<br/>'))}</p>`;
    })
    .join('');

  return <div className="mab-markdown" dangerouslySetInnerHTML={{ __html: html }} />;
}