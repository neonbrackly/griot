'use client';

import { useState } from 'react';

/**
 * YamlPreview Component
 *
 * Displays syntax-highlighted YAML content with copy functionality.
 */
interface YamlPreviewProps {
  content: string;
  onCopy?: () => void;
}

export function YamlPreview({ content, onCopy }: YamlPreviewProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      onCopy?.();
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Basic syntax highlighting for YAML
  const highlightYaml = (yaml: string) => {
    return yaml
      .split('\n')
      .map((line, i) => {
        // Comments
        if (line.trim().startsWith('#')) {
          return (
            <div key={i} className="text-gray-400">
              {line}
            </div>
          );
        }

        // Key-value pairs
        const match = line.match(/^(\s*)([^:]+)(:)(.*)$/);
        if (match) {
          const [, indent, key, colon, value] = match;
          return (
            <div key={i}>
              <span>{indent}</span>
              <span className="text-primary-600">{key}</span>
              <span>{colon}</span>
              <span className="text-gray-700">{value}</span>
            </div>
          );
        }

        // List items
        if (line.trim().startsWith('-')) {
          const match = line.match(/^(\s*)(-)(.*)$/);
          if (match) {
            const [, indent, dash, rest] = match;
            return (
              <div key={i}>
                <span>{indent}</span>
                <span className="text-warning-600">{dash}</span>
                <span className="text-gray-700">{rest}</span>
              </div>
            );
          }
        }

        return <div key={i}>{line}</div>;
      });
  };

  return (
    <div className="relative">
      <div className="absolute top-2 right-2">
        <button
          onClick={handleCopy}
          className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm text-gray-600"
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm font-mono">
        {highlightYaml(content)}
      </pre>
    </div>
  );
}

export default YamlPreview;
