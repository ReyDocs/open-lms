import React from 'react';
import { EditorContent, useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { Bold, Heading2, Italic, List, ListOrdered, Quote } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface RichTextEditorProps {
  value: string;
  onChange: (html: string) => void;
}

export const RichTextEditor: React.FC<RichTextEditorProps> = ({ value, onChange }) => {
  const editor = useEditor({
    extensions: [StarterKit],
    content: value,
    editorProps: {
      attributes: {
        class: 'min-h-[140px] prose prose-sm dark:prose-invert max-w-none px-3 py-2 outline-none',
      },
    },
    onUpdate: ({ editor: activeEditor }) => onChange(activeEditor.getHTML()),
  });

  if (!editor) return null;

  const actions = [
    { label: 'Bold', icon: Bold, run: () => editor.chain().focus().toggleBold().run(), active: editor.isActive('bold') },
    { label: 'Italic', icon: Italic, run: () => editor.chain().focus().toggleItalic().run(), active: editor.isActive('italic') },
    { label: 'Heading', icon: Heading2, run: () => editor.chain().focus().toggleHeading({ level: 2 }).run(), active: editor.isActive('heading', { level: 2 }) },
    { label: 'Bullet list', icon: List, run: () => editor.chain().focus().toggleBulletList().run(), active: editor.isActive('bulletList') },
    { label: 'Numbered list', icon: ListOrdered, run: () => editor.chain().focus().toggleOrderedList().run(), active: editor.isActive('orderedList') },
    { label: 'Quote', icon: Quote, run: () => editor.chain().focus().toggleBlockquote().run(), active: editor.isActive('blockquote') },
  ];

  return (
    <div className="rounded-md border border-input bg-background">
      <div className="flex flex-wrap gap-1 border-b p-1">
        {actions.map(({ label, icon: Icon, run, active }) => (
          <Button
            key={label}
            type="button"
            size="icon"
            variant={active ? 'secondary' : 'ghost'}
            aria-label={label}
            title={label}
            onClick={run}
            className="h-8 w-8"
          >
            <Icon className="h-4 w-4" />
          </Button>
        ))}
      </div>
      <EditorContent editor={editor} />
    </div>
  );
};
