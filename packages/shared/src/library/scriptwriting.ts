/**
 * Scriptwriting techniques library
 *
 * Structured recipes the agent can use to scaffold scripts across platforms.
 */

export type ScriptwritingStep = {
  title: string
  goal: string
  prompt: string
  example?: string
}

export type ScriptwritingTechnique = {
  id: string
  name: string
  summary: string
  platforms: string[]
  useWhen: string[]
  avoidWhen: string[]
  triggerWords: string[]
  steps: ScriptwritingStep[]
  lengthHint?: string
  ctaIdeas?: string[]
}

export type ScriptwritingTechniqueOption = Pick<
  ScriptwritingTechnique,
  "id" | "name" | "summary" | "platforms" | "lengthHint"
>

const techniques: ScriptwritingTechnique[] = [
  {
    id: "aida",
    name: "AIDA (Attention, Interest, Desire, Action)",
    summary: "Classic conversion structure: grab attention, build intrigue, prove value, then ask for a clear action.",
    platforms: ["YouTube Shorts", "TikTok", "Instagram Reels", "LinkedIn"],
    useWhen: [
      "You have a clear offer or next step",
      "You need a short, persuasive arc",
      "You want a direct CTA that feels earned",
    ],
    avoidWhen: [
      "Long tutorials with many steps",
      "Sensitive topics that need more nuance",
    ],
    triggerWords: ["imagine", "here's why", "because", "right now", "today", "get", "so"],
    lengthHint: "30-75s or 120-180 words",
    ctaIdeas: [
      "Grab the template",
      "Try it free today",
      "Comment 'guide' and I’ll send it",
      "Link in bio to start",
    ],
    steps: [
      {
        title: "Attention",
        goal: "Stop the scroll with a bold claim, stat, or pain the audience feels.",
        prompt: "Lead with a vivid pain or surprising stat; speak to one person (“you”).",
        example: "You're wasting 6 hours a week editing captions the slow way.",
      },
      {
        title: "Interest",
        goal: "Show there's a simple path out of the pain.",
        prompt: "Name the specific problem and tease the mechanism/tool/framework.",
        example: "It’s not your writing—it’s the way you start. One tweak fixes it.",
      },
      {
        title: "Desire",
        goal: "Paint the outcome and proof that it works.",
        prompt: "Describe the result with numbers or a mini-proof; keep it concrete.",
        example: "This 3-line opener cut my bounce by 42% last month.",
      },
      {
        title: "Action",
        goal: "Give one crystal-clear next step.",
        prompt: "Use one CTA; remove friction words; make it time-bound if possible.",
        example: "Comment “hook” and I’ll DM you the template.",
      },
    ],
  },
  {
    id: "pas",
    name: "PAS (+ Proof) (Problem, Agitate, Solve)",
    summary: "Highlight a painful problem, make the cost felt, then deliver the fix with quick proof.",
    platforms: ["LinkedIn", "YouTube", "TikTok", "Email"],
    useWhen: [
      "You know the audience pain viscerally",
      "You have a single, clean solution to pitch",
      "You need urgency without hype",
    ],
    avoidWhen: [
      "When the problem is unfamiliar to the audience",
      "When you can't show any proof or outcome",
    ],
    triggerWords: ["ever notice", "the worst part", "hurts because", "fix", "so you can", "without"],
    lengthHint: "45-90s or 150-220 words",
    ctaIdeas: [
      "Grab the checklist",
      "Save this for when it hits",
      "DM me 'fix' for the playbook",
    ],
    steps: [
      {
        title: "Problem",
        goal: "State the pain in their words; make it obvious you 'get it'.",
        prompt: "Use a direct question or observation that matches their day-to-day.",
        example: "Ever notice how your 'quick update' turns into 9 slide rewrites?",
      },
      {
        title: "Agitate",
        goal: "Turn up the cost of doing nothing.",
        prompt: "Mention wasted time, money, or missed upside; keep it specific, not dramatic.",
        example: "Those rewrites cost you 2-3 hours per deck and still miss the point.",
      },
      {
        title: "Solve",
        goal: "Deliver the remedy in one beat.",
        prompt: "Name the fix and the simple steps to use it; keep verbs active.",
        example: "Use the 1-3-1 rule: 1-line goal, 3 proof points, 1 CTA—done in 4 minutes.",
      },
      {
        title: "Proof (optional)",
        goal: "De-risk the promise with a quick receipt.",
        prompt: "Drop a stat, a mini-case, or a before/after screenshot.",
        example: "We cut deck prep by 38% last sprint with this outline.",
      },
      {
        title: "CTA",
        goal: "Invite a low-friction next step.",
        prompt: "Make the CTA feel like the natural next move after solving the pain.",
        example: "Comment 'outline' and I’ll send the 1-3-1 template.",
      },
    ],
  },
  {
    id: "open-loop",
    name: "Open Loop → Payoff",
    summary: "Create curiosity with a gap, then close it with a satisfying reveal or lesson.",
    platforms: ["YouTube Shorts", "TikTok", "Instagram Reels", "Stories"],
    useWhen: [
      "You have a surprising answer or reveal",
      "You need strong retention through the middle",
    ],
    avoidWhen: [
      "When you can’t deliver a clear payoff",
      "When the topic is purely informational with no twist",
    ],
    triggerWords: ["what happened", "until", "but then", "the mistake", "no one tells you", "here's the catch"],
    lengthHint: "25-60s or 90-160 words",
    ctaIdeas: [
      "Watch the full breakdown",
      "Save so you don’t forget the payoff",
      "Follow for the next experiment",
    ],
    steps: [
      {
        title: "Open Loop",
        goal: "Pose a question or tease an outcome without giving it away.",
        prompt: "Use a cliffhanger or 'I tried X so you don’t have to' setup.",
        example: "I asked 3 AI tools to rewrite my hook. Only one actually boosted watch time.",
      },
      {
        title: "Build Tension",
        goal: "Show stakes, attempts, or mini-failures.",
        prompt: "Share 1-2 beats of the process; keep shots quick and visual.",
        example: "First tool? Too robotic. Second? Pretty, but killed my click-through.",
      },
      {
        title: "Payoff",
        goal: "Deliver the answer clearly and quickly.",
        prompt: "Reveal the pick/lesson; show evidence (metric or clip).",
        example: "The winner cut bounce by 31%—because it front-loaded the outcome.",
      },
      {
        title: "Takeaway",
        goal: "Give a portable rule they can use now.",
        prompt: "State the rule in one line; avoid jargon.",
        example: "Front-load the 'after' before you explain the 'how'.",
      },
      {
        title: "CTA",
        goal: "Invite the next action tied to the reveal.",
        prompt: "Keep it curiosity-aligned (e.g., more tests, full breakdown).",
        example: "Follow for the full script teardown tomorrow.",
      },
    ],
  },
  {
    id: "heros-mini-journey",
    name: "Hero’s Mini-Journey",
    summary: "A compressed story arc: setup, conflict, turning point, win, lesson.",
    platforms: ["YouTube", "TikTok", "Podcast intro", "Twitter/X"],
    useWhen: [
      "You have a personal or customer story",
      "You need emotional buy-in before teaching",
    ],
    avoidWhen: [
      "Purely technical explainers",
      "Topics where personal anecdotes feel off-brand",
    ],
    triggerWords: ["back when", "then it hit", "the wall", "turning point", "here’s what changed", "the lesson"],
    lengthHint: "60-120s or 200-350 words",
    ctaIdeas: [
      "Apply the same steps with my checklist",
      "Share your version in the comments",
      "Join the live teardown",
    ],
    steps: [
      {
        title: "Setup",
        goal: "Establish who, where, and the goal.",
        prompt: "Open with the goal and the stakes; keep it tight.",
        example: "Two months ago I had to ship 10 videos in 10 days—solo.",
      },
      {
        title: "Conflict",
        goal: "Show the obstacle and the cost.",
        prompt: "Name the hardest constraint; show emotion without drama.",
        example: "By day 3 I was drowning in B-roll and missed two deadlines.",
      },
      {
        title: "Turning Point",
        goal: "Reveal the shift or decision.",
        prompt: "Describe the specific change, not just 'I worked harder'.",
        example: "I built a 3-beat template and forced every script into it.",
      },
      {
        title: "Win",
        goal: "Show the concrete outcome.",
        prompt: "Use numbers, screenshots, or a short clip as proof.",
        example: "We shipped all 10, and avg retention jumped from 41% to 58%.",
      },
      {
        title: "Lesson + CTA",
        goal: "Extract the principle and invite action.",
        prompt: "State the rule, then point to the resource or next step.",
        example: "Template first, footage second. Comment 'template' for mine.",
      },
    ],
  },
  {
    id: "tiktok-listicle",
    name: "TikTok/Shorts Listicle",
    summary: "Fast, numbered beats that promise quick wins or mistakes to avoid.",
    platforms: ["TikTok", "YouTube Shorts", "Instagram Reels"],
    useWhen: [
      "You need rapid-fire delivery",
      "You have multiple small tips or warnings",
      "You want easy hook variety with numbers",
    ],
    avoidWhen: [
      "Deep dives that need context",
      "Abstract ideas without concrete examples",
    ],
    triggerWords: ["3 ways", "top 5", "mistakes", "nobody tells you", "stop doing", "do this instead"],
    lengthHint: "20-50s or 70-130 words",
    ctaIdeas: [
      "Save for your next post",
      "Follow for part 2",
      "Comment which one you’ll try",
    ],
    steps: [
      {
        title: "Numbered Hook",
        goal: "Promise count + outcome.",
        prompt: "Lead with the number and the payoff; avoid weak adjectives.",
        example: "3 hooks that add 10% watch time—steal them.",
      },
      {
        title: "Beat 1",
        goal: "Deliver the first tip with a micro-proof.",
        prompt: "State the tip, then an example in 1 line.",
        example: "Front-load the outcome: 'Get X in Y time' beats 'How to get X'.",
      },
      {
        title: "Beat 2",
        goal: "Keep pace; avoid repeating the same type of tip.",
        prompt: "Switch angle (process, wording, visual).",
        example: "Swap 'I' for 'you'—direct address boosts retention.",
      },
      {
        title: "Beat 3",
        goal: "End on the strongest or most contrarian tip.",
        prompt: "Use a 'never do this' or 'do this instead' pattern.",
        example: "Never end with a question; end with the action you want.",
      },
      {
        title: "CTA",
        goal: "Keep it native to the platform.",
        prompt: "Ask for a quick action: save, follow, or comment a keyword.",
        example: "Comment 'hooks' and I’ll drop the script.",
      },
    ],
  },
] as const

export function getScriptwritingTechniques(): ScriptwritingTechnique[] {
  return techniques
}

export function getScriptwritingTechnique(id: string): ScriptwritingTechnique | undefined {
  return techniques.find((technique) => technique.id === id)
}

export function getScriptwritingTechniqueOptions(): ScriptwritingTechniqueOption[] {
  return techniques.map(({ id, name, summary, platforms, lengthHint }) => ({
    id,
    name,
    summary,
    platforms,
    lengthHint,
  }))
}

