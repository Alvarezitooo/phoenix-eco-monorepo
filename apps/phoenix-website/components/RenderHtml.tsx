'use client';
import DOMPurify from 'isomorphic-dompurify';

export function RenderHtml({ html }: { html: string }) {
  const safe = DOMPurify.sanitize(html, { USE_PROFILES: { html: true } });
  return <div dangerouslySetInnerHTML={{ __html: safe }} />;
}
