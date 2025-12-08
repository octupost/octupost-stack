import fs from "fs"
import path from "path"
import matter from "gray-matter"

export type DocMeta = {
  slug: string
  title: string
  summary: string
  tags: string[]
}

export type Doc = DocMeta & {
  content: string
}

const docsDir = path.join(process.cwd(), "docs", "architecture")

function readFrontmatter(filePath: string): Doc | null {
  const raw = fs.readFileSync(filePath, "utf8")
  const parsed = matter(raw)

  const title = parsed.data.title as string | undefined
  const summary = parsed.data.summary as string | undefined
  const tags = (parsed.data.tags as string[] | undefined) ?? []

  const slug = path.basename(filePath).replace(/\.md$/, "")

  if (!title || !summary) {
    // Skip docs missing required fields.
    return null
  }

  return {
    slug,
    title,
    summary,
    tags,
    content: parsed.content.trim(),
  }
}

export function listDocs(): Doc[] {
  if (!fs.existsSync(docsDir)) return []

  const files = fs.readdirSync(docsDir).filter((f) => f.endsWith(".md"))

  return files
    .map((file) => readFrontmatter(path.join(docsDir, file)))
    .filter((doc): doc is Doc => Boolean(doc))
    .sort((a, b) => a.title.localeCompare(b.title))
}

export function getDoc(slug: string): Doc | null {
  const target = path.join(docsDir, `${slug}.md`)
  if (!fs.existsSync(target)) return null
  return readFrontmatter(target)
}

