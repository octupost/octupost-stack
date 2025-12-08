import { ApiRecord, Category, UseCase } from "./types";

const useCaseLabels: Record<UseCase, string> = {
  "vertical-ad": "Vertical ad",
  "talking-head": "Talking head",
  "podcast-clip": "Podcast clip",
  "product-demo": "Product demo",
  localization: "Localization/dubbing",
  "course-lesson": "Course/lesson",
  "social-clip": "Social clipper"
};

const categoryDefaults: Partial<Record<Category, UseCase[]>> = {
  visuals: ["product-demo", "vertical-ad"],
  video: ["vertical-ad", "social-clip"],
  audio: ["podcast-clip"],
  "data-sources": ["product-demo"],
  translation: ["localization"],
  utils: ["social-clip"]
};

const subcategoryMap: Record<string, UseCase[]> = {
  "Avatar Video": ["talking-head", "course-lesson"],
  "Talking Head": ["talking-head", "course-lesson"],
  "Text-to-Video": ["vertical-ad", "product-demo"],
  "Video Generation": ["vertical-ad", "product-demo"],
  "Image-to-Video": ["vertical-ad", "product-demo"],
  "Programmatic Editing": ["social-clip", "product-demo"],
  "Animation/Motion": ["vertical-ad", "social-clip"],
  "Lip Sync": ["talking-head", "localization"],
  "Transcription": ["podcast-clip", "social-clip"],
  "Captions/Rendering": ["podcast-clip", "social-clip"],
  Dubbing: ["localization"],
  "Text-to-Speech": ["course-lesson", "talking-head", "localization"],
  "Music/SFX": ["podcast-clip", "vertical-ad"],
  "Stock Images/Videos": ["product-demo", "social-clip"],
  "Stock Images": ["product-demo"],
  "Stock Images/Videos/Music": ["product-demo", "social-clip"],
  "GIFs/Stickers": ["social-clip"],
  "Editing Pipelines": ["social-clip", "product-demo"],
  "Video Transcoding": ["social-clip"],
  Delivery: ["vertical-ad", "social-clip"],
  Translation: ["localization", "course-lesson"],
  "Localization Management": ["localization"]
};

export const useCaseOptions: { value: UseCase; label: string }[] = Object.entries(useCaseLabels).map(
  ([value, label]) => ({
    value: value as UseCase,
    label
  })
);

export function formatUseCase(useCase: UseCase) {
  return useCaseLabels[useCase] ?? useCase;
}

export function deriveUseCases(api: ApiRecord): UseCase[] {
  if (api.useCases && api.useCases.length) return api.useCases;

  const fromSubcategory = subcategoryMap[api.subcategory] ?? [];
  const fromCategory = categoryDefaults[api.category] ?? [];
  const combined = new Set<UseCase>([...fromSubcategory, ...fromCategory]);

  return Array.from(combined);
}
