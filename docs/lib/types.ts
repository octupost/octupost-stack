export type Category = "visuals" | "video" | "audio" | "data-sources" | "utils" | "translation";

export type UseCase =
  | "vertical-ad"
  | "talking-head"
  | "podcast-clip"
  | "product-demo"
  | "localization"
  | "course-lesson"
  | "social-clip";

export interface ApiExample {
  curl?: string;
  typescript?: string;
  python?: string;
}

export interface FreeTier {
  limit: string;
  value: number;
  unit: string;
}

export type PricingTier = "free" | "freemium" | "paid";
export type PricingModel =
  | "per-request"
  | "per-character"
  | "per-minute"
  | "per-image"
  | "per-video"
  | "per-second"
  | "subscription"
  | "free";

export type Speed = "instant" | "fast" | "medium" | "slow";

export interface ApiRecord {
  id: string;
  name: string;
  category: Category;
  subcategory: string;
  useCases?: UseCase[];
  pricingTier: PricingTier;
  pricingModel: PricingModel;
  pricePerUnit?: number;
  priceUnit?: string;
  freeTier?: FreeTier | null;
  features: string[];
  quality: 1 | 2 | 3 | 4 | 5;
  speed: Speed;
  sdks: ("python" | "javascript" | "rest" | "curl" | "go")[];
  authType: "api-key" | "oauth" | "bearer" | "none";
  website: string;
  docs: string;
  description: string;
  examples: ApiExample;
  lastVerified?: string;
}
